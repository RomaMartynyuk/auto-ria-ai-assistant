from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from cars.models import Car
from cars.serializers.car_serializer import CarSerializer


class CarListView(APIView):
    def get(self, request):
        cars = Car.objects.all()

        max_price = request.GET.get('max_price')
        min_year = request.GET.get('min_year')

        if max_price:
            cars = cars.filter(price__lte=max_price)

        if min_year:
            cars = cars.filter(year__gte=min_year)

        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)