from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from cars.models import Car, SearchRequest
from cars.serializers.car_serializer import CarSerializer
from cars.services.car_service import filter_cars
from cars.services.ai_service import get_ai_top_cars, map_ai_response
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
            min_year=params["min_year"],
            max_mileage=params["max_mileage"],
            brand=params["brand"],
            ordering=params["ordering"],
        )

        process_car_search.delay(
            params["max_price"],
            params["min_year"],
            # params["max_mileage"],
            # params["brand"],
            # params["ordering"]
        )
        parse_cars_task.delay(params["max_price"])

        cars = filter_cars(
            params["max_price"],
            params["min_year"],
            # params["max_mileage"],
            # params["brand"],
            # params["ordering"]
        )

        if not cars:
            return Response(
                {
                    "status": "processing",
                    "message": "Data is being parsed. Please retry in a few seconds.",
                },
                status=202,
            )

        # Prefer cars closer to requested budget, then newer models.
        if params["max_price"]:
            target_price = float(params["max_price"])
            cars = sorted(
                cars,
                key=lambda c: (abs(float(c.price) - target_price), -int(c.year))
            )
        else:
            cars = sorted(cars, key=lambda c: int(c.year), reverse=True)

        # Keep a candidate pool for AI, then return top 5.
        cars = cars[:15]

        try:
            ai_result = get_ai_top_cars(cars)
            cars = map_ai_response(ai_result, cars)
        except Exception as e:
            print("AI ERROR:", e)

        cars = cars[:5]

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)
