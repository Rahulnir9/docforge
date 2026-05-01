from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
router = APIRouter(prefix="/orders")

class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Address

class UserCreate(BaseModel):
    name: str
    email: str

class Order(BaseModel):
    id: int
    total: float
    user: User

@app.get("/users")
def get_users(limit: int = 10, skip: int = 0) -> List[User]:
    """Returns paginated list of users."""
    pass

@app.get("/users/{user_id}")
def get_user(user_id: int) -> User:
    """Returns a single user by ID."""
    pass

@app.post("/users")
def create_user(user: UserCreate) -> User:
    """Creates a new user."""
    pass

@router.get("/")
def get_orders() -> List[Order]:
    """Returns all orders."""
    pass

@router.get("/{order_id}")
def get_order(order_id: int) -> Order:
    """Returns a single order."""
    pass