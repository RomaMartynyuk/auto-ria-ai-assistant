import requests

BASE_URL = "http://127.0.0.1:8000/api"

def get_cars(params: dict):
    try:
        response = requests.get(f"{BASE_URL}/recommend/", params=params)

        if response.status_code == 200:
            return response.json()

        print("API ERROR:", response.status_code)
        return None

    except Exception as e:
        print("REQUEST ERROR:", e)
        return None