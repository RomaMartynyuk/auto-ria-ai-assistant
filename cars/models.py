from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    mileage = models.IntegerField()

    def __str__(self):
        return f"{self.brand} {self.model} {str(self.year)}"

class SearchRequest(models.Model):
    max_price = models.DecimalField(decimal_places=2, max_digits=10)
    min_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

