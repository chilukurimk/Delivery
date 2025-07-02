import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional,List

app = FastAPI()


class ItemModel(BaseModel):
    id: int
    name: str
    price: int
    description: Optional[str] = None
    available_quantity: int = 0  # Added quantity field with default 0

class ItemsResponse(BaseModel):
    item_list: List[ItemModel]

@app.get("/items/{id}")
def items(id : int) -> ItemsResponse:
    with open("sample.json", "r") as file:
        data = json.load(file)
    item_list = []
    for rest in data["rest_list"]:
        if rest["id"] == id:
            for item in rest["items"]:
                item_list.append(ItemModel(id = item["id"], name = item["name"], price = item["price"], description= item["description"], available_quantity=item["available_quantity"]))
    return ItemsResponse(item_list=item_list)


class RestaurantModel(BaseModel):
    id: int
    name: str
    location: str

class RestaurantsResponse(BaseModel):
    rest_list: List[RestaurantModel]

@app.get("/restaurants", response_model=RestaurantsResponse)
def restaurants() -> RestaurantsResponse:
    with open("sample.json", "r") as file:
        data = json.load(file)
    rest_list = []
    for restaurant in data["rest_list"]:
        rest_list.append(RestaurantModel(id = restaurant["id"], name = restaurant["name"], location= restaurant["location"]))
    return RestaurantsResponse(rest_list= rest_list)


@app.get("/")
def home():
    return FileResponse("index.html")

class RestaurantCreateModel(BaseModel):
    name: str
    location: str
    description: Optional[str] = None

@app.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreateModel) -> RestaurantCreateModel:
    with open("sample.json", "r") as file:
        data = json.load(file)
    data["rest_list"].append(restaurant.model_dump())
    with open("sample.json", "w") as file:
        json.dump(data, file, indent=4)
    return restaurant



# Update existing item endpoint
class ItemUpdateModel(BaseModel):
    name: Optional[str] = None  # Optional field for name update
    price: Optional[int] = None  # Optional field for price update
    description: Optional[str] = None  # Optional field for description update
    available_quantity: Optional[int] = None  # Optional field for quantity update

@app.put("/restaurants/{restaurant_id}/items/{item_id}")
def update_item(restaurant_id: int, item_id: int, item_update: ItemUpdateModel) -> ItemModel:
    with open("sample.json", "r") as file:
        data = json.load(file)
    
    # Find the restaurant by ID
    for rest in data["rest_list"]:
        if rest["id"] == restaurant_id:
            # Find the item by ID within this restaurant
            for item in rest["items"]:
                if item["id"] == item_id:
                    # Update fields if provided
                    if item_update.name is not None:
                        item["name"] = item_update.name
                    if item_update.price is not None:
                        item["price"] = item_update.price
                    if item_update.description is not None:
                        item["description"] = item_update.description
                    if item_update.available_quantity is not None:
                        item["available_quantity"] = item_update.available_quantity
                    
                    # Save back to file
                    with open("sample.json", "w") as file:
                        json.dump(data, file, indent=4)
                    
                    # Return the updated item
                    return ItemModel(
                        id=item["id"], 
                        name=item["name"], 
                        price=item["price"], 
                        description=item["description"],
                        available_quantity=item["available_quantity"]
                    )
            
            # Item not found in this restaurant
            raise HTTPException(status_code=404, detail="Item not found in this restaurant")
    
    # Restaurant not found
    raise HTTPException(status_code=404, detail="Restaurant not found")


# Import orders functionality
from orders import (
    OrderCreate, Order, OrdersResponse, OrderStatusUpdate, OrderStatus,
    create_order, get_all_orders, get_order_by_id, update_order_status,
    get_orders_by_restaurant, get_orders_by_status
)

# Orders endpoints
@app.post("/orders", response_model=Order)
def create_new_order(order: OrderCreate) -> Order:
    """Create a new order"""
    return create_order(order)

@app.get("/orders", response_model=OrdersResponse)
def get_orders() -> OrdersResponse:
    """Get all orders"""
    orders = get_all_orders()
    return OrdersResponse(orders=orders)

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int) -> Order:
    """Get a specific order by ID"""
    return get_order_by_id(order_id)

@app.put("/orders/{order_id}/status", response_model=Order)
def update_order_status_endpoint(order_id: int, status_update: OrderStatusUpdate) -> Order:
    """Update order status"""
    return update_order_status(order_id, status_update)

@app.get("/restaurants/{restaurant_id}/orders", response_model=OrdersResponse)
def get_restaurant_orders(restaurant_id: int) -> OrdersResponse:
    """Get all orders for a specific restaurant"""
    orders = get_orders_by_restaurant(restaurant_id)
    return OrdersResponse(orders=orders)

@app.get("/orders/status/{status}", response_model=OrdersResponse)
def get_orders_by_status_endpoint(status: OrderStatus) -> OrdersResponse:
    """Get all orders with a specific status"""
    orders = get_orders_by_status(status)
    return OrdersResponse(orders=orders)