import json
import tempfile
import os
import shutil
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
from main import app

client = TestClient(app)

# Sample test data
SAMPLE_DATA = {
    "rest_list": [
        {
            "id": 1,
            "name": "Spice Villa",
            "location": "Banjara Hills",
            "items": [
                {
                    "id": 101,
                    "name": "Paneer Butter Masala",
                    "price": 220,
                    "description": "Creamy cottage cheese curry",
                    "available_quantity": 5
                },
                {
                    "id": 102,
                    "name": "Butter Naan",
                    "price": 40,
                    "description": "Soft and buttery Indian bread",
                    "available_quantity": 10
                }
            ]
        },
        {
            "id": 2,
            "name": "Grill & Chill",
            "location": "Madhapur",
            "items": [
                {
                    "id": 104,
                    "name": "Chicken Kebab",
                    "price": 250,
                    "description": "Grilled skewers with spices",
                    "available_quantity": 3
                }
            ]
        }
    ]
}

@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file with sample data for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(SAMPLE_DATA, temp_file, indent=4)
    temp_file.close()
    
    # Patch the file path in the main module
    with patch('main.open', side_effect=lambda file, mode: open(temp_file.name, mode)):
        yield temp_file.name
    
    # Clean up
    os.unlink(temp_file.name)

@pytest.fixture
def mock_sample_json():
    """Mock the sample.json file operations"""
    def mock_open_func(filename, mode):
        if 'r' in mode:
            return mock_open(read_data=json.dumps(SAMPLE_DATA)).return_value
        else:
            # For write operations, return a mock that captures the data
            mock_file = mock_open().return_value
            return mock_file
    
    with patch('builtins.open', side_effect=mock_open_func):
        yield

class TestHomeEndpoint:
    """Test cases for the home endpoint"""
    
    def test_home_returns_html_file(self):
        """Test that home endpoint returns the index.html file"""
        response = client.get("/")
        assert response.status_code == 200

class TestRestaurantsEndpoints:
    """Test cases for restaurant-related endpoints"""
    
    def test_get_restaurants_success(self, mock_sample_json):
        """Test successful retrieval of all restaurants"""
        response = client.get("/restaurants")
        assert response.status_code == 200
        
        data = response.json()
        assert "rest_list" in data
        assert len(data["rest_list"]) == 2
        
        # Check first restaurant
        first_restaurant = data["rest_list"][0]
        assert first_restaurant["id"] == 1
        assert first_restaurant["name"] == "Spice Villa"
        assert first_restaurant["location"] == "Banjara Hills"
        
        # Check second restaurant
        second_restaurant = data["rest_list"][1]
        assert second_restaurant["id"] == 2
        assert second_restaurant["name"] == "Grill & Chill"
        assert second_restaurant["location"] == "Madhapur"
    
    def test_create_restaurant_success(self, mock_sample_json):
        """Test successful creation of a new restaurant"""
        new_restaurant = {
            "name": "New Test Restaurant",
            "location": "Test Location",
            "description": "A test restaurant"
        }
        
        response = client.post("/restaurants", json=new_restaurant)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == new_restaurant["name"]
        assert data["location"] == new_restaurant["location"]
        assert data["description"] == new_restaurant["description"]
    
    def test_create_restaurant_without_description(self, mock_sample_json):
        """Test creating restaurant without optional description"""
        new_restaurant = {
            "name": "Simple Restaurant",
            "location": "Simple Location"
        }
        
        response = client.post("/restaurants", json=new_restaurant)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == new_restaurant["name"]
        assert data["location"] == new_restaurant["location"]
        assert data["description"] is None
    
    def test_create_restaurant_missing_required_fields(self):
        """Test creating restaurant with missing required fields"""
        incomplete_restaurant = {
            "name": "Incomplete Restaurant"
            # Missing location
        }
        
        response = client.post("/restaurants", json=incomplete_restaurant)
        assert response.status_code == 422  # Unprocessable Entity

class TestItemsEndpoints:
    """Test cases for item-related endpoints"""
    
    def test_get_items_by_restaurant_id_success(self, mock_sample_json):
        """Test successful retrieval of items for existing restaurant"""
        restaurant_id = 1
        response = client.get(f"/items/{restaurant_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "item_list" in data
        assert len(data["item_list"]) == 2
        
        # Check first item
        first_item = data["item_list"][0]
        assert first_item["id"] == 101
        assert first_item["name"] == "Paneer Butter Masala"
        assert first_item["price"] == 220
        assert first_item["description"] == "Creamy cottage cheese curry"
        assert first_item["available_quantity"] == 5
        
        # Check second item
        second_item = data["item_list"][1]
        assert second_item["id"] == 102
        assert second_item["name"] == "Butter Naan"
        assert second_item["price"] == 40
        assert second_item["available_quantity"] == 10
    
    def test_get_items_by_nonexistent_restaurant_id(self, mock_sample_json):
        """Test retrieval of items for non-existent restaurant"""
        restaurant_id = 999
        response = client.get(f"/items/{restaurant_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "item_list" in data
        assert len(data["item_list"]) == 0
    
    def test_get_items_by_restaurant_with_single_item(self, mock_sample_json):
        """Test retrieval of items for restaurant with single item"""
        restaurant_id = 2
        response = client.get(f"/items/{restaurant_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "item_list" in data
        assert len(data["item_list"]) == 1
        
        item = data["item_list"][0]
        assert item["id"] == 104
        assert item["name"] == "Chicken Kebab"
        assert item["price"] == 250
        assert item["available_quantity"] == 3

class TestUpdateItemEndpoint:
    """Test cases for item update endpoint"""
    
    def test_update_item_all_fields_success(self, mock_sample_json):
        """Test successful update of all item fields"""
        restaurant_id = 1
        item_id = 101
        update_data = {
            "name": "Updated Paneer Dish",
            "price": 250,
            "description": "Updated description",
            "available_quantity": 15
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        assert data["description"] == update_data["description"]
        assert data["available_quantity"] == update_data["available_quantity"]
    
    def test_update_item_partial_fields(self, mock_sample_json):
        """Test successful partial update of item fields"""
        restaurant_id = 1
        item_id = 101
        update_data = {
            "name": "Partially Updated Paneer",
            "price": 240
            # Not updating description and available_quantity
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
        # These should remain unchanged from original data
        assert data["description"] == "Creamy cottage cheese curry"
        assert data["available_quantity"] == 5
    
    def test_update_item_only_quantity(self, mock_sample_json):
        """Test updating only the quantity field"""
        restaurant_id = 2
        item_id = 104
        update_data = {
            "available_quantity": 20
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == item_id
        assert data["available_quantity"] == update_data["available_quantity"]
        # Other fields should remain unchanged
        assert data["name"] == "Chicken Kebab"
        assert data["price"] == 250
        assert data["description"] == "Grilled skewers with spices"
    
    def test_update_item_nonexistent_restaurant(self, mock_sample_json):
        """Test updating item in non-existent restaurant"""
        restaurant_id = 999
        item_id = 101
        update_data = {
            "name": "Should Not Update"
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 404
        assert "Restaurant not found" in response.json()["detail"]
    
    def test_update_item_nonexistent_item(self, mock_sample_json):
        """Test updating non-existent item in existing restaurant"""
        restaurant_id = 1
        item_id = 999
        update_data = {
            "name": "Should Not Update"
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 404
        assert "Item not found in this restaurant" in response.json()["detail"]
    
    def test_update_item_empty_update(self, mock_sample_json):
        """Test updating item with no fields provided"""
        restaurant_id = 1
        item_id = 101
        update_data = {}
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should return the item unchanged
        assert data["id"] == item_id
        assert data["name"] == "Paneer Butter Masala"
        assert data["price"] == 220
        assert data["description"] == "Creamy cottage cheese curry"
        assert data["available_quantity"] == 5
    
    def test_update_item_with_null_values(self, mock_sample_json):
        """Test updating item with null values for optional fields - should not update"""
        restaurant_id = 1
        item_id = 101
        update_data = {
            "description": None,
            "available_quantity": 0
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == item_id
        assert data["description"] == "Creamy cottage cheese curry"
        assert data["available_quantity"] == 0
        # Other fields should remain unchanged
        assert data["name"] == "Paneer Butter Masala"
        assert data["price"] == 220

class TestDataValidation:
    """Test cases for data validation"""
    
    def test_invalid_item_id_type(self, mock_sample_json):
        """Test with invalid item ID type"""
        response = client.get("/items/invalid")
        assert response.status_code == 422
    
    def test_invalid_restaurant_id_in_update(self, mock_sample_json):
        """Test update with invalid restaurant ID type"""
        response = client.put("/restaurants/invalid/items/101", json={"name": "Test"})
        assert response.status_code == 422
    
    def test_invalid_item_id_in_update(self, mock_sample_json):
        """Test update with invalid item ID type"""
        response = client.put("/restaurants/1/items/invalid", json={"name": "Test"})
        assert response.status_code == 422
    
    def test_invalid_price_type_in_update(self, mock_sample_json):
        """Test update with invalid price type"""
        update_data = {
            "price": "invalid_price"
        }
        response = client.put("/restaurants/1/items/101", json=update_data)
        assert response.status_code == 422
    
    def test_negative_quantity_in_update(self, mock_sample_json):
        """Test update with negative quantity (should be allowed as per model)"""
        restaurant_id = 1
        item_id = 101
        update_data = {
            "available_quantity": -5
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["available_quantity"] == -5

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_large_restaurant_id(self, mock_sample_json):
        """Test with very large restaurant ID"""
        large_id = 999999999
        response = client.get(f"/items/{large_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["item_list"]) == 0
    
    def test_zero_restaurant_id(self, mock_sample_json):
        """Test with zero restaurant ID"""
        response = client.get("/items/0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["item_list"]) == 0
    
    def test_update_with_very_long_strings(self, mock_sample_json):
        """Test update with very long string values"""
        restaurant_id = 1
        item_id = 101
        long_string = "A" * 1000
        
        update_data = {
            "name": long_string,
            "description": long_string
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == long_string
        assert data["description"] == long_string
    
    def test_update_with_unicode_characters(self, mock_sample_json):
        """Test update with unicode characters"""
        restaurant_id = 1
        item_id = 101
        unicode_name = "Pañeer Buttér Masàla 🍛"
        unicode_description = "Créamy cottage cheese curry with émojis 🧀✨"
        
        update_data = {
            "name": unicode_name,
            "description": unicode_description
        }
        
        response = client.put(f"/restaurants/{restaurant_id}/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == unicode_name
        assert data["description"] == unicode_description

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
