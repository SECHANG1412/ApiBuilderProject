from fastapi import FastAPI
from typing import Optional, List

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id_received": item_id}

@app.get("/items/typed/{item_id}")
async def read_item_typed(item_id: int):
    return {"item_id": item_id, "type":str(type(item_id))}



@app.get("/users/me")
async def read_current_user():
    return {"user_id": "현재 로그인한 사용자 (me)"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}



fake_items_db = [{"item_name": "맥북 프로"}, {"item_name": "아이폰 15"}, {"item_name": "에어팟 맥스"}]

@app.get("/items-query/")
async def read_items_with_query(skip: int = 0, limit: int = 10):
    return {"query_params": {"skip": skip, "limit": limit}, "items": fake_items_db[skip : skip + limit]}

@app.get("/items-optional/")
async def read_items_optional(q: Optional[str] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q":q})
    return results

@app.get("/items-validation/")
async def read_items_with_validation(description: str, price: float, is_offer: Optional[bool] = None):
    item_info = {"description": description, "price": price}
    if is_offer is not None:
        item_info.update({"is_offer": is_offer})
    return item_info

@app.get("/users/{user_id}/orders")
async def read_user_orders(user_id: int, status: Optional[str] = None):
    result = {"user_id": user_id, "orders": [{"order_id": 1, "item": "Laptop"}, {"order_id": 2, "item": "Mouse"}]}
    if status:
        result.update({"filter_status": status})
    return result