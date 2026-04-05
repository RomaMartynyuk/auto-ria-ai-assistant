from django.urls import path
from cars.views import CarListView, CarRecommendView

urlpatterns = [
    path('cars/', CarListView.as_view()),
    path('recommend/', CarRecommendView.as_view()),
]