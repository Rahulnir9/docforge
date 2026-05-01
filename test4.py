from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/orders")

@router.get("/")
def get_orders():
    """Get all orders"""
    return []

@router.post("/")
def create_order():
    """Create order"""
    return {"status": "created"}

app.include_router(router)