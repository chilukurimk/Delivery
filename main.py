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


@app.get("/items/{id}")
def items(id : int) -> ItemsResponse:
    with open("sample.json", "r") as file:
        data = json.load(file)
    item_list = []
    for rest in data["rest_list"]:
        if rest["id"] == id:
            for item in rest["items"]:
                item_list.append(ItemModel(id = item["id"], name = item["name"], price = item["price"], description= item["description"]))
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
