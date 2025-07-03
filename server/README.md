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
{
    rest_list
}
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


Phase2

Ratings, Reviews(food and rest)




order(post)
{
  "restaurant_id": 1,
  "items": [
    {"item_id": 101, "quantity": 9}
  ],
  "customer_name": "John Doe",
  "customer_phone": "+1234567890",
  "delivery_address": "123 Main St, City, State 12345",
  "special_instructions": "Ring the doorbell twice"
}


uvicorn main:app
