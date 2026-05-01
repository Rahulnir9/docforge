from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/users")
def get_users():
    """Get all users"""
    return []

@app.post("/users")
def create_user(user: User):
    """Create a user"""
    return user