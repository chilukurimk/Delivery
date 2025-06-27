# Delivery

- popups
- list 
    - restaurants
    - food item
        - price
        - Delivery time
        - ratings
        - reviews
- cart
- payment methods
- Delivery Status
---
## v1
We will target Showing Restaurants and food items

GET /restaurants
[
    {
        "id":"789",
        "name":"Biryani House"
        "rating": 5
    }
]

GET /restaurants/<id>
{
    "id":"789",
    "description":"Delicious!",
    "foods" :[
        {
            "id":"123",
            "name":"Biryani",
            "price":"299",
            "rating":"4.3"
        }
        {
            "id":"124",
            "name":"SP CB",
            "price":"399",
            "rating":"4.5"
        }
    ]
}



