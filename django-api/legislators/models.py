from django.db import models
from datetime import date

class Legislator(models.Model):
    govtrack_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField()
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    state = models.CharField(max_length=2)
    district = models.CharField(max_length=10, null=True, blank=True)
    party = models.CharField(max_length=50)
    url = models.CharField(max_length=500)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'legislators'
        managed = False
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['party']),
            models.Index(fields=['type']),
            models.Index(fields=['birthday']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))