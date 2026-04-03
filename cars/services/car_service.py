from cars.models import Car

def filter_cars(max_price=None, min_year=None):
    cars = Car.objects.all()

    if max_price:
        cars = cars.filter(price__lte=max_price)

    if min_year:
        cars = cars.filter(year__gte=min_year)

    return cars