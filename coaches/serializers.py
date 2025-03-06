from rest_framework import serializers
from users.models import Coaches, Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['phone', 'full_name', 'course'] 
        
class CoachesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coaches
        fields = ['phone', 'full_name']

