from rest_framework import serializers
from .models import Legislator

class LegislatorSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Legislator
        fields = '__all__'

    def get_age(self, obj):
        return obj.calculate_age()

class NotesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislator
        fields = ['notes']