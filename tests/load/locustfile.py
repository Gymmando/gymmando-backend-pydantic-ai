"""
Locust load test for Gymmando API - Token endpoint.

Run with: locust -f locustfile.py --host=http://localhost:8000
"""
import random

from locust import HttpUser, between, task


class TokenUser(HttpUser):
    """Simulates a user requesting LiveKit tokens."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Called when a simulated user starts."""
        # Generate a unique user ID for this user
        self.user_id = f"test_user_{random.randint(1000, 9999)}_{id(self)}"

    @task
    def get_token(self):
        """Test the /token endpoint with a user_id parameter."""
        with self.client.get(
            f"/token?user_id={self.user_id}", name="/token", catch_response=True
        ) as response:
            if response.status_code == 200:
                # Check if response contains a token
                try:
                    data = response.json()
                    if "token" in data and data["token"]:
                        response.success()
                    else:
                        response.failure("Response missing token field")
                except Exception as e:
                    response.failure(f"Failed to parse JSON: {e}")
            elif response.status_code == 0:
                response.failure("Connection refused - is the API running?")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
