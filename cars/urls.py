from django.urls import path
from cars.views import CarListView, CarRecommendView, HealthView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('cars/', CarListView.as_view()),
    path('recommend/', CarRecommendView.as_view()),
]
