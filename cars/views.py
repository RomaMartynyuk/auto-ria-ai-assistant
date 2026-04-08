from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from cars.models import Car
from cars.serializers.car_serializer import CarSerializer
from cars.services.car_service import filter_cars
from cars.tasks import process_car_search


class CarListView(APIView):
    def get(self, request):
        max_price = request.GET.get('max_price')
        min_year = request.GET.get('min_year')

        cars = filter_cars(max_price, min_year)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

class CarRecommendView(APIView):
    def get(self, request):
        max_price = request.GET.get('max_price')
        min_year = request.GET.get('min_year')

        process_car_search.delay(max_price, min_year)

        cars = filter_cars(max_price, min_year)
        cars = sorted(cars, key=lambda x: x.year, reverse=True)[:5]

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)