from rest_framework import serializers
from cars.models import Car

class CarSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(read_only=True)

    class Meta:
        model = Car
        fields = '__all__'