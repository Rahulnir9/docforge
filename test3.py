from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/products")
def get_products(limit: int = Query(10)):
    """Get products with limit"""
    return []