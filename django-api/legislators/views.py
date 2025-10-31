from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import connection
from .models import Legislator
from .serializers import LegislatorSerializer, LegislatorUpdateSerializer
import requests
import os

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat()
     })

@api_view(['GET'])
def legislators_list(request):
    legislators = Legislator.objects.all()

    #Filtering by state and party
    state = request.GET.get('state')
    party = request.GET.get('party')

    if state:
        legislators = legislators.filter(state=state)
    if party:
        legislators = legislators.filter(party=party)

    serializer = LegislatorSerializer(legislators, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def legislator_detail(request, govtrack_id):
    legislator = get_object_or_404(Legislator, govtrack_id=govtrack_id)
    serializer = LegislatorSerializer(legislator)
    return Response(serializer.data)

@api_view(['PATCH'])
def update_notes(request, govtrack_id):
    legislator = get_object_or_404(Legislator, govtrack_id=govtrack_id)
    serializer = LegislatorUpdateSerializer(legislator, data=request.data, partial=True)

    if serializer.is_valid():
        new_notes = serializer.validated_data.get('notes', legislator.notes)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE legislators SET notes = %s WHERE govtrack_id = %s",
                [new_notes, govtrack_id]
            )

        legislator.refresh_from_db()
        
        return Response({
            'legislator': LegislatorSerializer(legislator).data,
            'message': 'Notes updated successfully'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def age_stats(request):
    items = list(Legislator.objects.all())
    if not items:
        return Response({'error': 'No legislators found'}, status=404)

    ages = [(obj.calculate_age(), obj) for obj in items if obj.birthday]
    if not ages:
        return Response({'error': 'No valid birth dates found'}, status=404)

    ages.sort(key=lambda x: x[0])
    youngest_age, youngest = ages[0]
    oldest_age, oldest = ages[-1]
    average_age = sum(a for a, _ in ages) / len(ages)

    def to_dict_with_age(legislator, age):
        return {
            'govtrack_id': legislator.govtrack_id,
            'first_name': legislator.first_name,
            'last_name': legislator.last_name,
            'birthday': str(legislator.birthday) if legislator.birthday else None,
            'gender': legislator.gender,
            'type': legislator.type,
            'state': legislator.state,
            'district': legislator.district,
            'party': legislator.party,
            'url': legislator.url,
            'notes': legislator.notes,
            'age': age  # calculated age
        }
    
    youngest_data = to_dict_with_age(youngest, youngest_age)
    oldest_data = to_dict_with_age(oldest, oldest_age)

    return Response({
        'average_age': round(average_age, 2),
        'youngest_legislator': youngest_data,
        'oldest_legislator': oldest_data
    })

@api_view(['GET'])
def weather_info(request, govtrack_id):
    legislator = get_object_or_404(Legislator, govtrack_id=govtrack_id)

    STATE_CAPITALS = {
        'AL': 'Montgomery', 'AK': 'Juneau', 'AZ': 'Phoenix', 'AR': 'Little Rock',
        'CA': 'Sacramento', 'CO': 'Denver', 'CT': 'Hartford', 'DE': 'Dover',
        'FL': 'Tallahassee', 'GA': 'Atlanta', 'HI': 'Honolulu', 'ID': 'Boise',
        'IL': 'Springfield', 'IN': 'Indianapolis', 'IA': 'Des Moines', 'KS': 'Topeka',
        'KY': 'Frankfort', 'LA': 'Baton Rouge', 'ME': 'Augusta', 'MD': 'Annapolis',
        'MA': 'Boston', 'MI': 'Lansing', 'MN': 'Saint Paul', 'MS': 'Jackson',
        'MO': 'Jefferson City', 'MT': 'Helena', 'NE': 'Lincoln', 'NV': 'Carson City',
        'NH': 'Concord', 'NJ': 'Trenton', 'NM': 'Santa Fe', 'NY': 'Albany',
        'NC': 'Raleigh', 'ND': 'Bismarck', 'OH': 'Columbus', 'OK': 'Oklahoma City',
        'OR': 'Salem', 'PA': 'Harrisburg', 'RI': 'Providence', 'SC': 'Columbia',
        'SD': 'Pierre', 'TN': 'Nashville', 'TX': 'Austin', 'UT': 'Salt Lake City',
        'VT': 'Montpelier', 'VA': 'Richmond', 'WA': 'Olympia', 'WV': 'Charleston',
        'WI': 'Madison', 'WY': 'Cheyenne'
    }

    capital = STATE_CAPITALS.get(legislator.state)
    if not capital:
        return Response({'error': f'Capital city not found for state: {legislator.state}'}, status=404)

    weather_api_key = os.getenv('WEATHER_API_KEY')
    if not weather_api_key:
        return Response({'error': 'Weather API key not configured'}, status=500)

    weather_url = os.getenv('WEATHER_API_URL')
    params = {
        'q': capital,
        'appid': weather_api_key,
        'units': 'imperial'
    }

    try:
        response = requests.get(weather_url, params=params)
        weather_data = response.json()

        return Response({
            'legislator': LegislatorSerializer(legislator).data,
            'state_capital': capital,
            'weather': {
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed'],
                'description': weather_data['weather'][0]['description']
            }
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)