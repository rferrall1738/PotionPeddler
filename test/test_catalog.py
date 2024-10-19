import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.catalog import app, db

client = TestClient(app)

class TestCatalogEndpoint(unittest.TestCase):
    
    def setUp(self):
        # Mock the database connection
        self.mock_connection = patch('src.api.catalog.db.engine.begin').start()

    def tearDown(self):
        # Stop all patches after the test completes
        patch.stopall()

    def test_get_catalog_with_data(self):
        # Mock database results for potions with quantities
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (10, 5, 3, 7, 2, 4)  # Simulated potion data
        
        # Mock the execution of the query and return the mock result
        self.mock_connection.return_value.__enter__.return_value.execute.return_value = mock_result
        
        # Simulate a GET request to the /catalog/ endpoint
        response = client.get("/catalog/")
        
        # Verify the status code
        self.assertEqual(response.status_code, 200)
        
        # Verify the response body contains the expected catalog items
        expected_catalog = [
            {"sku": "GREEN_POTION_0", "name": "green potion", "quantity": 10, "price": 20, "potion_type": [0, 100, 0, 0]},
            {"sku": "RED_POTION_0", "name": "red potion", "quantity": 5, "price": 20, "potion_type": [100, 0, 0, 0]},
            {"sku": "BLUE_POTION_0", "name": "blue potion", "quantity": 3, "price": 20, "potion_type": [0, 0, 100, 0]},
            {"sku": "PURPLE_POTION_0", "name": "purple potion", "quantity": 7, "potion_type": [50, 0, 50, 0]},
            {"sku": "YELLOW_POTION_0", "name": "yellow potion", "quantity": 2, "potion_type": [0, 50, 50, 0]},
            {"sku": "DARK_POTION_0", "name": "dark potion", "quantity": 4, "potion_type": [0, 0, 0, 100]},
        ]
        
        # Verify the response matches the expected catalog
        self.assertEqual(response.json(), expected_catalog)
    
    def test_get_catalog_empty(self):
        # Mock database results with no potions available (all zero)
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0, 0, 0, 0, 0, 0)  # Simulated empty inventory
        
        # Mock the execution of the query and return the mock result
        self.mock_connection.return_value.__enter__.return_value.execute.return_value = mock_result
        
        # Simulate a GET request to the /catalog/ endpoint
        response = client.get("/catalog/")
        
        # Verify the status code
        self.assertEqual(response.status_code, 200)
        
        # Verify the response body contains an empty catalog
        expected_catalog = [
            {"sku": "GREEN_POTION_0", "name": "green potion", "quantity": 0, "price": 20, "potion_type": [0, 100, 0, 0]},
            {"sku": "RED_POTION_0", "name": "red potion", "quantity": 0, "price": 20, "potion_type": [100, 0, 0, 0]},
            {"sku": "BLUE_POTION_0", "name": "blue potion", "quantity": 0, "price": 20, "potion_type": [0, 0, 100, 0]},
            {"sku": "PURPLE_POTION_0", "name": "purple potion", "quantity": 0, "potion_type": [50, 0, 50, 0]},
            {"sku": "YELLOW_POTION_0", "name": "yellow potion", "quantity": 0, "potion_type": [0, 50, 50, 0]},
            {"sku": "DARK_POTION_0", "name": "dark potion", "quantity": 0, "potion_type": [0, 0, 0, 100]},
        ]
        
        # Verify the response matches the expected empty catalog
        self.assertEqual(response.json(), expected_catalog)

if __name__ == "__main__":
    unittest.main()