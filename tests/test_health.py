import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealth(unittest.TestCase):
    def test_health(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
