from django.urls import path
from cars.views import CarListView

urlpatterns = [
    path('cars/', CarListView.as_view()),
]