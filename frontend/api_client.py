import requests

from config import API_BASE_URL


class APIClient:

    def __init__(self, token: str | None = None):
        self.token = token

    @property
    def headers(self):
        if self.token:
            return {
                "Authorization": f"Bearer {self.token}"
            }

        return {}

    def login(self, email: str, password: str):
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={
                "username": email,
                "password": password,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def get(self, endpoint: str):
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def post(self, endpoint: str, data: dict):
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()