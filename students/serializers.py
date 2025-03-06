from rest_framework import serializers
from homeworks.models import Homework

class HomeworksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ['week_number'] 
