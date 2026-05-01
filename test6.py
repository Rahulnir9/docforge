from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    id: int
    name: str
    address: Address

@app.get("/profile", response_model=User)
def get_profile():
    """Get profile"""
    return {
        "id": 1,
        "name": "Rahul",
        "address": {
            "city": "Hyderabad",
            "zip_code": "500001"
        }
    }