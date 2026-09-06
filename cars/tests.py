from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from cars.models import Car
from cars.parser.mapper import map_parsed_car_to_model, parse_mileage
from cars.services.ai_service import map_ai_response, parse_ai_json
from cars.services.query_normalizer import normalize_car_query


class QueryNormalizerTests(SimpleTestCase):
    def test_normalizes_supported_parameters(self):
        result = normalize_car_query(
            {
                "max_price": "15000",
                "min_year": "2015",
                "max_mileage": "120000",
                "brand": " BMW ",
                "ordering": "-year",
            }
        )

        self.assertEqual(result["max_price"], 15000)
        self.assertEqual(result["brand"], "BMW")
        self.assertEqual(result["ordering"], "-year")

    def test_rejects_invalid_ordering(self):
        with self.assertRaisesRegex(ValueError, "ordering must be one of"):
            normalize_car_query({"ordering": "unknown_field"})

    def test_rejects_non_positive_values(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            normalize_car_query({"max_price": "0"})


class MapperTests(SimpleTestCase):
    def test_converts_thousands_to_kilometres(self):
        self.assertEqual(parse_mileage("210 тис. км"), 210000)
        self.assertEqual(parse_mileage("12,5 тис. км"), 12500)

    def test_maps_valid_parser_result(self):
        result = map_parsed_car_to_model(
            {
                "title": "Mercedes-Benz C-Class 2010",
                "price": 9500,
                "mileage": "210 тис. км",
                "link": "https://auto.ria.com/example",
            }
        )

        self.assertEqual(result["brand"], "Mercedes-Benz")
        self.assertEqual(result["model"], "C-Class")
        self.assertEqual(result["year"], 2010)
        self.assertEqual(result["mileage"], 210000)

    def test_prefers_structured_listing_attributes(self):
        result = map_parsed_car_to_model(
            {
                "title": "Land Rover Range Rover Evoque 2018",
                "brand": "Land Rover",
                "model": "Range Rover Evoque",
                "year": "2018",
                "price": 27000,
                "mileage": "95 тис. км",
                "link": "https://auto.ria.com/example-2",
            }
        )

        self.assertEqual(result["brand"], "Land Rover")
        self.assertEqual(result["model"], "Range Rover Evoque")
        self.assertEqual(result["year"], 2018)


class AIServiceTests(SimpleTestCase):
    def test_parses_json_code_fence(self):
        self.assertEqual(
            parse_ai_json('```json\n[{"id": 1, "reason": "Good value"}]\n```'),
            [{"id": 1, "reason": "Good value"}],
        )

    def test_fills_short_ai_response_up_to_five_results(self):
        cars = [SimpleNamespace(id=index) for index in range(1, 7)]
        result = map_ai_response([{"id": "1", "reason": "AI choice"}], cars)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].reason, "AI choice")
        self.assertEqual(result[1].reason, "Selected by fallback ranking.")


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "car-finder-tests",
    }
}


@override_settings(CACHES=TEST_CACHES, AI_PROVIDER="none")
class RecommendationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        prices = [7800, 29500, 33000, 37000, 39500, 40500]
        for index, price in enumerate(prices):
            Car.objects.create(
                brand="Brand",
                model=f"Model-{index}",
                year=2018 + index,
                price=Decimal(price),
                mileage=100000 - (index * 5000),
                link=f"https://example.com/cars/{index}",
            )

    @patch("cars.views.enqueue_parse_cars", return_value="task-id")
    def test_recommendations_are_close_to_budget_and_limited_to_five(self, _enqueue):
        response = self.client.get("/api/recommend/", {"max_price": 41000})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
        self.assertTrue(all(28700 <= float(car["price"]) <= 41000 for car in response.data))
        self.assertEqual(float(response.data[0]["price"]), 40500)

    @patch("cars.views.enqueue_parse_cars", return_value="task-id")
    def test_returns_processing_when_relevant_data_is_not_available(self, _enqueue):
        response = self.client.get("/api/recommend/", {"max_price": 2000})

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["status"], "processing")
        self.assertEqual(response.data["task_id"], "task-id")

    def test_requires_max_price(self):
        response = self.client.get("/api/recommend/")
        self.assertEqual(response.status_code, 400)

    def test_rejects_invalid_query(self):
        response = self.client.get("/api/recommend/", {"max_price": "abc"})
        self.assertEqual(response.status_code, 400)


@override_settings(CACHES=TEST_CACHES)
class HealthAPITests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
