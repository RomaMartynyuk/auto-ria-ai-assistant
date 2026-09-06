from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from cars.models import SearchRequest
from cars.serializers.car_serializer import CarSerializer
from cars.services.ai_service import get_ai_top_cars, map_ai_response
from cars.services.car_service import filter_cars, recommendation_price_floor
from cars.services.query_normalizer import normalize_car_query
from cars.tasks import enqueue_parse_cars


def parse_query_params(request):
    try:
        return normalize_car_query(request.GET), None
    except ValueError as exc:
        return None, Response(
            {"error": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
            cache.set("health-check", "ok", timeout=10)
            if cache.get("health-check") != "ok":
                raise RuntimeError("Redis cache check failed")
        except Exception as exc:
            return Response(
                {"status": "unhealthy", "detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"status": "ok"})

class CarListView(APIView):
    def get(self, request):
        params, error = parse_query_params(request)
        if error:
            return error

        cars = filter_cars(**params)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

class CarRecommendView(APIView):
    def get(self, request):
        params, error = parse_query_params(request)
        if error:
            return error

        if not params["max_price"]:
            return Response(
                {"error": "max_price is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SearchRequest.objects.create(
            max_price=params["max_price"],
            min_year=params["min_year"],
            max_mileage=params["max_mileage"],
            brand=params["brand"],
            ordering=params["ordering"],
        )

        min_price = recommendation_price_floor(params["max_price"])
        task_id = enqueue_parse_cars(params["max_price"], min_price)

        cars = filter_cars(
            params["max_price"],
            min_price=min_price,
            min_year=params["min_year"],
            max_mileage=params["max_mileage"],
            brand=params["brand"],
            ordering=params["ordering"],
        )

        if not cars:
            return Response(
                {
                    "status": "processing",
                    "message": "Data is being parsed. Please retry in a few seconds.",
                    "task_id": task_id,
                    "price_range": {"min": min_price, "max": params["max_price"]},
                },
                status=status.HTTP_202_ACCEPTED,
            )

        # Prefer cars closer to requested budget, then newer models.
        if params["max_price"]:
            target_price = params["max_price"]
            cars = sorted(
                cars,
                key=lambda car: (
                    abs(float(car.price) - target_price),
                    -int(car.year),
                    int(car.mileage),
                ),
            )
        else:
            cars = sorted(cars, key=lambda c: int(c.year), reverse=True)

        # Keep a candidate pool for AI, then return top 5.
        cars = cars[:15]

        ai_result = get_ai_top_cars(cars)
        cars = map_ai_response(ai_result, cars)

        cars = cars[:5]

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)
