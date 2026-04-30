from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    age: int

@app.get("/users")
def get_users(skip: int = 0, limit: int = 10):
    """Returns a paginated list of all users."""
    pass

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Returns a single user by their ID."""
    pass

@app.post("/users")
def create_user(user: UserCreate):
    """Creates a new user account."""
    pass

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Permanently deletes a user by their ID."""
    pass