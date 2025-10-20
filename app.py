import os
import requests
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
    'postgresql://postgres:password@db:5432/legislators_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Weather API configuration
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

# State capitals mapping
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
    'WI': 'Madison', 'WY': 'Cheyenne', 'DC': 'Washington'
}

class Legislator(db.Model):
    __tablename__ = 'legislators'
    
    govtrack_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # sen/rep
    state = db.Column(db.String(2), nullable=False)
    district = db.Column(db.String(10))
    party = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'govtrack_id': self.govtrack_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'gender': self.gender,
            'type': self.type,
            'state': self.state,
            'district': self.district,
            'party': self.party,
            'url': self.url,
            'notes': self.notes
        }
    
    def calculate_age(self):
        if not self.birthday:
            return None
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

@app.route('/api/legislators', methods=['GET'])
def get_legislators():
    """Get all legislators with optional filtering by state and party"""
    state = request.args.get('state')
    party = request.args.get('party')
    
    query = Legislator.query
    
    if state:
        query = query.filter(Legislator.state == state.upper())
    if party:
        query = query.filter(Legislator.party.ilike(f'%{party}%'))
    
    legislators = query.all()
    return jsonify([legislator.to_dict() for legislator in legislators])

@app.route('/api/legislators/<int:govtrack_id>', methods=['GET'])
def get_legislator(govtrack_id):
    """Get a specific legislator by govtrack_id"""
    legislator = Legislator.query.get(govtrack_id)
    if not legislator:
        return jsonify({'error': 'Legislator not found'}), 404
    
    return jsonify(legislator.to_dict())

@app.route('/api/legislators/<int:govtrack_id>/notes', methods=['PATCH'])
def update_legislator_notes(govtrack_id):
    """Update notes for a specific legislator"""
    legislator = Legislator.query.get(govtrack_id)
    if not legislator:
        return jsonify({'error': 'Legislator not found'}), 404
    
    data = request.get_json()
    if not data or 'note' not in data:
        return jsonify({'error': 'Note field is required'}), 400
    
    legislator.notes = data['note']
    db.session.commit()
    
    return jsonify({'message': 'Notes updated successfully', 'legislator': legislator.to_dict()})

@app.route('/api/stats/age', methods=['GET'])
def get_age_stats():
    """Get age statistics for all legislators"""
    legislators = Legislator.query.all()
    
    if not legislators:
        return jsonify({'error': 'No legislators found'}), 404
    
    ages = []
    for legislator in legislators:
        age = legislator.calculate_age()
        if age is not None:
            ages.append((age, legislator))
    
    if not ages:
        return jsonify({'error': 'No valid birth dates found'}), 404
    
    ages.sort(key=lambda x: x[0])
    
    youngest_age, youngest_legislator = ages[0]
    oldest_age, oldest_legislator = ages[-1]
    average_age = sum(age for age, _ in ages) / len(ages)
    
    return jsonify({
        'average_age': round(average_age, 2),
        'youngest_legislator': {
            'age': youngest_age,
            'legislator': youngest_legislator.to_dict()
        },
        'oldest_legislator': {
            'age': oldest_age,
            'legislator': oldest_legislator.to_dict()
        }
    })

@app.route('/api/legislators/<int:govtrack_id>/weather', methods=['GET'])
def get_legislator_weather(govtrack_id):
    """Get current weather for the capital city of a legislator's state"""
    if not WEATHER_API_KEY:
        return jsonify({'error': 'Weather API key not configured'}), 500
    
    legislator = Legislator.query.get(govtrack_id)
    if not legislator:
        return jsonify({'error': 'Legislator not found'}), 404
    
    state = legislator.state
    if state not in STATE_CAPITALS:
        return jsonify({'error': f'Capital city not found for state: {state}'}), 404
    
    capital_city = STATE_CAPITALS[state]
    
    try:
        # Call OpenWeatherMap API
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{capital_city},{state},US",
            'appid': WEATHER_API_KEY,
            'units': 'imperial'
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        
        weather_data = response.json()
        
        return jsonify({
            'legislator': legislator.to_dict(),
            'state_capital': capital_city,
            'weather': {
                'temperature': weather_data['main']['temp'],
                'description': weather_data['weather'][0]['description'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed']
            }
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch weather data: {str(e)}'}), 500
    except KeyError as e:
        return jsonify({'error': f'Unexpected weather API response format: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
