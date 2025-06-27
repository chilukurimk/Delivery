import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional,List

app = FastAPI()

class ItemModel(BaseModel):
    id: int
    name: str
    price: int
    description: Optional[str] = None


class ItemsResponse(BaseModel):
    item_list: List[ItemModel]


@app.get("/items")
def items() -> ItemsResponse:
    item_list = [
        ItemModel(id=1, name="Veg Biryani", price=180, description="Spicy and flavorful"),
        ItemModel(id=2, name="Paneer Tikka", price=220, description="Grilled cottage cheese"),
        ItemModel(id=3, name="Butter Naan", price=40)
    ]
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
