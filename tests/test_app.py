import os
import tempfile
import unittest

os.environ["TECHMANAGER_DB"] = os.path.join(tempfile.gettempdir(), "techmanager_test.db")

from app import app, generate_recommendation


class RecommendationEngineTests(unittest.TestCase):
    def test_small_team_architecture(self):
        r = generate_recommendation("Portfolio", 2, "Low")
        self.assertEqual(r["architecture"], "Simple Monolithic Architecture")

    def test_medium_team_architecture(self):
        r = generate_recommendation("Education", 4, "Medium")
        self.assertEqual(r["architecture"], "Modular Monolithic Architecture")

    def test_large_team_architecture(self):
        r = generate_recommendation("E-Commerce", 8, "High", "100,000+", "High", "High")
        self.assertEqual(r["architecture"], "Scalable Microservices Architecture")
        self.assertGreaterEqual(r["scalability"], 80)

    def test_high_security_adds_controls(self):
        r = generate_recommendation("Banking", 5, "High", "10,000–100,000", "Critical", "High")
        self.assertIn("Audit logging", r["security"])
        self.assertIn("Rate limiting", r["security"])

    def test_explainability_outputs(self):
        r = generate_recommendation("Hospital", 4, "High")
        self.assertTrue(r["decision_summary"])
        self.assertTrue(r["factors"])
        self.assertGreaterEqual(r["rule_fit_score"], 0)
        self.assertLessEqual(r["rule_fit_score"], 100)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_api_docs(self):
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["version"], "2.0")

    def test_api_recommendation(self):
        response = self.client.post("/api/recommend", json={
            "project_type": "Education",
            "team_size": 4,
            "budget": "Medium",
            "expected_users": "10,000–100,000",
            "security_level": "High",
            "scalability_need": "High",
            "team_experience": "Intermediate",
            "deadline": "Standard"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendation", response.get_json())


if __name__ == "__main__":
    unittest.main()
