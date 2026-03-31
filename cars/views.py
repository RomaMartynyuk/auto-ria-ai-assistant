from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from cars.models import Car
from cars.serializers.car_serializer import CarSerializer


class CarListView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)