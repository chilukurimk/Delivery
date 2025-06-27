
# from fastapi import FastAPI
# from routers import restaurants
# app = FastAPI()
# app.include_router(restaurants.router)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

class MessageResponse(BaseModel):
    message: int =0
    name: Optional[str] = None
    # Declare that message must be an int

@app.get("/", response_model=MessageResponse)
def say_hi() -> MessageResponse:
    return MessageResponse(message=5)


@app.get("/name", response_model=MessageResponse)
def name() -> MessageResponse:
    return MessageResponse(name = "Kiran")
