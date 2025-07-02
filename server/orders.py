import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int
    subtotal: float

class OrderCreateItem(BaseModel):
    item_id: int
    quantity: int

class OrderCreate(BaseModel):
    restaurant_id: int
    items: List[OrderCreateItem]
    customer_name: str
    customer_phone: str
    delivery_address: str
    special_instructions: Optional[str] = None

class Order(BaseModel):
    id: int
    restaurant_id: int
    restaurant_name: str
    items: List[OrderItem]
    customer_name: str
    customer_phone: str
    delivery_address: str
    special_instructions: Optional[str] = None
    total_amount: float
    status: OrderStatus
    created_at: str
    estimated_delivery_time: Optional[str] = None

class OrdersResponse(BaseModel):
    orders: List[Order]

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    estimated_delivery_time: Optional[str] = None

def load_restaurant_data():
    """Load restaurant data from sample.json"""
    try:
        with open("sample.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"rest_list": []}

def save_restaurant_data(data):
    """Save restaurant data to sample.json"""
    with open("sample.json", "w") as file:
        json.dump(data, file, indent=4)

def load_orders_data():
    """Load orders data from orders.json"""
    try:
        with open("orders.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"orders": []}

def save_orders_data(data):
    """Save orders data to orders.json"""
    with open("orders.json", "w") as file:
        json.dump(data, file, indent=4)

def get_next_order_id():
    """Get the next available order ID"""
    data = load_orders_data()
    if "orders" not in data:
        data["orders"] = []
        save_orders_data(data)
        return 1
    
    if not data["orders"]:
        return 1
    
    return max(order["id"] for order in data["orders"]) + 1

def find_restaurant_by_id(restaurant_id: int):
    """Find restaurant by ID"""
    data = load_restaurant_data()
    for restaurant in data["rest_list"]:
        if restaurant["id"] == restaurant_id:
            return restaurant
    return None

def find_item_in_restaurant(restaurant, item_id: int):
    """Find item in restaurant by ID"""
    for item in restaurant["items"]:
        if item["id"] == item_id:
            return item
    return None

def create_order(order_data: OrderCreate) -> Order:
    """Create a new order"""
    # Find restaurant
    restaurant = find_restaurant_by_id(order_data.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Validate items and calculate total
    order_items = []
    total_amount = 0.0
    
    for order_item in order_data.items:
        item = find_item_in_restaurant(restaurant, order_item.item_id)
        if not item:
            raise HTTPException(
                status_code=404, 
                detail=f"Item with ID {order_item.item_id} not found in restaurant"
            )
        
        if order_item.quantity <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Quantity must be greater than 0"
            )
        
        # Check availability - item must have sufficient quantity
        if item["available_quantity"] < order_item.quantity:
            raise HTTPException(
                status_code=404, 
                detail=f"Item not available - available_quantity: {item['available_quantity']}"
            )
        
        subtotal = item["price"] * order_item.quantity
        total_amount += subtotal
        
        order_items.append(OrderItem(
            item_id=item["id"],
            name=item["name"],
            price=item["price"],
            quantity=order_item.quantity,
            subtotal=subtotal
        ))
    
    # All validations passed, now update inventory
    # Load fresh restaurant data and update available quantities
    restaurant_data = load_restaurant_data()
    for order_item in order_data.items:
        for restaurant in restaurant_data["rest_list"]:
            if restaurant["id"] == order_data.restaurant_id:
                for item in restaurant["items"]:
                    if item["id"] == order_item.item_id:
                        item["available_quantity"] -= order_item.quantity
                        break
                break
    
    # Save updated restaurant data
    save_restaurant_data(restaurant_data)
    
    # Create order
    order_id = get_next_order_id()
    created_at = datetime.now().isoformat()
    
    # Estimate delivery time (30-45 minutes from now)
    from datetime import timedelta
    estimated_delivery = datetime.now() + timedelta(minutes=35)
    
    new_order = Order(
        id=order_id,
        restaurant_id=restaurant["id"],
        restaurant_name=restaurant["name"],
        items=order_items,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        special_instructions=order_data.special_instructions,
        total_amount=round(total_amount, 2),
        status=OrderStatus.PENDING,
        created_at=created_at,
        estimated_delivery_time=estimated_delivery.isoformat()
    )
    
    # Add order to orders data
    orders_data = load_orders_data()
    if "orders" not in orders_data:
        orders_data["orders"] = []
    
    orders_data["orders"].append(new_order.model_dump())
    
    # Save updated orders data
    save_orders_data(orders_data)
    
    return new_order

def get_all_orders() -> List[Order]:
    """Get all orders"""
    data = load_orders_data()
    if "orders" not in data:
        return []
    
    orders = []
    for order_data in data["orders"]:
        orders.append(Order(**order_data))
    
    return orders

def get_order_by_id(order_id: int) -> Order:
    """Get order by ID"""
    data = load_orders_data()
    if "orders" not in data:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for order_data in data["orders"]:
        if order_data["id"] == order_id:
            return Order(**order_data)
    
    raise HTTPException(status_code=404, detail="Order not found")

def update_order_status(order_id: int, status_update: OrderStatusUpdate) -> Order:
    """Update order status"""
    data = load_orders_data()
    if "orders" not in data:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for i, order_data in enumerate(data["orders"]):
        if order_data["id"] == order_id:
            # Update status
            order_data["status"] = status_update.status.value
            
            # Update estimated delivery time if provided
            if status_update.estimated_delivery_time:
                order_data["estimated_delivery_time"] = status_update.estimated_delivery_time
            
            # Save changes
            save_orders_data(data)
            
            return Order(**order_data)
    
    raise HTTPException(status_code=404, detail="Order not found")

def get_orders_by_restaurant(restaurant_id: int) -> List[Order]:
    """Get all orders for a specific restaurant"""
    data = load_orders_data()
    if "orders" not in data:
        return []
    
    orders = []
    for order_data in data["orders"]:
        if order_data["restaurant_id"] == restaurant_id:
            orders.append(Order(**order_data))
    
    return orders

def get_orders_by_status(status: OrderStatus) -> List[Order]:
    """Get all orders with a specific status"""
    data = load_orders_data()
    if "orders" not in data:
        return []
    
    orders = []
    for order_data in data["orders"]:
        if order_data["status"] == status.value:
            orders.append(Order(**order_data))
    
    return orders