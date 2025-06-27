
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional,List

app = FastAPI()


class ItemModel(BaseModel):
    id: int
    name: str
    price: float
    description: str = None

class RestaurantModel(BaseModel):
    id: int
    name: str
    location: str

class RestaurantsResponse(BaseModel):
    rest_list: List[RestaurantModel]

@app.get("/restaurants", response_model=RestaurantsResponse)
def restaurants() -> RestaurantsResponse:
    rest_list = [
        RestaurantModel(id=1, name="Spice Villa", location="Banjara Hills"),
        RestaurantModel(id=2, name="Grill & Chill", location="Madhapur"),
        RestaurantModel(id=3, name="Saffron Bite", location="Kukatpally")
    ]
    return RestaurantsResponse(rest_list = rest_list)
