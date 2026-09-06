from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    mileage = models.IntegerField()
    link = models.URLField(unique=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=["price"], name="car_price_idx"),
            models.Index(fields=["year"], name="car_year_idx"),
            models.Index(fields=["mileage"], name="car_mileage_idx"),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} {str(self.year)}"

class SearchRequest(models.Model):
    max_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    min_year = models.IntegerField(null=True, blank=True)
    max_mileage = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    ordering = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"], name="search_created_idx"),
        ]
