import pytest
import json
import os
from fastapi.testclient import TestClient
from main import app
from orders import OrderStatus

client = TestClient(app)

# Test data
test_order_data = {
    "restaurant_id": 1,
    "items": [
        {"item_id": 101, "quantity": 2},
        {"item_id": 102, "quantity": 1}
    ],
    "customer_name": "John Doe",
    "customer_phone": "+1234567890",
    "delivery_address": "123 Main St, City, State 12345",
    "special_instructions": "Ring the doorbell twice"
}

def setup_module():
    """Setup test environment"""
    # Ensure we have fresh files for testing
    pass

def test_create_order():
    """Test creating a new order"""
    response = client.post("/orders", json=test_order_data)
    assert response.status_code == 200
    
    order = response.json()
    assert order["restaurant_id"] == 1
    assert order["customer_name"] == "John Doe"
    assert order["status"] == "pending"
    assert len(order["items"]) == 2
    assert order["total_amount"] > 0

def test_get_all_orders():
    """Test getting all orders"""
    # First create an order
    client.post("/orders", json=test_order_data)
    
    response = client.get("/orders")
    assert response.status_code == 200
    
    orders_response = response.json()
    assert "orders" in orders_response
    assert len(orders_response["orders"]) >= 1

def test_get_order_by_id():
    """Test getting a specific order by ID"""
    # Create an order first
    create_response = client.post("/orders", json=test_order_data)
    order_id = create_response.json()["id"]
    
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    
    order = response.json()
    assert order["id"] == order_id
    assert order["customer_name"] == "John Doe"

def test_update_order_status():
    """Test updating order status"""
    # Create an order first
    create_response = client.post("/orders", json=test_order_data)
    order_id = create_response.json()["id"]
    
    # Update status
    status_update = {
        "status": "confirmed",
        "estimated_delivery_time": "2025-07-02T15:30:00"
    }
    
    response = client.put(f"/orders/{order_id}/status", json=status_update)
    assert response.status_code == 200
    
    order = response.json()
    assert order["status"] == "confirmed"
    assert order["estimated_delivery_time"] == "2025-07-02T15:30:00"

def test_get_orders_by_restaurant():
    """Test getting orders by restaurant"""
    # Create an order first
    client.post("/orders", json=test_order_data)
    
    response = client.get("/restaurants/1/orders")
    assert response.status_code == 200
    
    orders_response = response.json()
    assert "orders" in orders_response
    for order in orders_response["orders"]:
        assert order["restaurant_id"] == 1

def test_get_orders_by_status():
    """Test getting orders by status"""
    # Create an order first
    client.post("/orders", json=test_order_data)
    
    response = client.get("/orders/status/pending")
    assert response.status_code == 200
    
    orders_response = response.json()
    assert "orders" in orders_response
    for order in orders_response["orders"]:
        assert order["status"] == "pending"

def test_create_order_invalid_restaurant():
    """Test creating order with invalid restaurant ID"""
    invalid_order_data = {
        **test_order_data,
        "restaurant_id": 999
    }
    
    response = client.post("/orders", json=invalid_order_data)
    assert response.status_code == 404
    assert "Restaurant not found" in response.json()["detail"]

def test_create_order_invalid_item():
    """Test creating order with invalid item ID"""
    invalid_order_data = {
        **test_order_data,
        "items": [{"item_id": 999, "quantity": 1}]
    }
    
    response = client.post("/orders", json=invalid_order_data)
    assert response.status_code == 404
    assert "not found in restaurant" in response.json()["detail"]

def test_create_order_zero_quantity():
    """Test creating order with zero quantity"""
    invalid_order_data = {
        **test_order_data,
        "items": [{"item_id": 101, "quantity": 0}]
    }
    
    response = client.post("/orders", json=invalid_order_data)
    assert response.status_code == 400
    assert "Quantity must be greater than 0" in response.json()["detail"]

def test_get_nonexistent_order():
    """Test getting a non-existent order"""
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

def test_update_nonexistent_order_status():
    """Test updating status of non-existent order"""
    status_update = {"status": "confirmed"}
    
    response = client.put("/orders/999/status", json=status_update)
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
