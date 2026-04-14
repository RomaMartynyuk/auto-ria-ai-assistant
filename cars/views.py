from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from cars.models import Car, SearchRequest
from cars.serializers.car_serializer import CarSerializer
from cars.services.car_service import filter_cars
from cars.services.query_normalizer import normalize_car_query
from cars.tasks import process_car_search, parse_cars_task


class CarListView(APIView):
    def get(self, request):
        max_price = request.GET.get('max_price')
        min_year = request.GET.get('min_year')

        cars = filter_cars(max_price, min_year)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

class CarRecommendView(APIView):
    def get(self, request):
        params = normalize_car_query(request.GET)

        SearchRequest.objects.create(
            max_price=params["max_price"],
            min_year=params["min_year"]
        )

        process_car_search.delay(
            params["max_price"],
            params["min_year"]
        )

        parse_cars_task.delay(params["max_price"])

        cars = filter_cars(
            params["max_price"],
            params["min_year"]
        )

        cars = sorted(cars, key=lambda x: x.year, reverse=True)[:5]

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)