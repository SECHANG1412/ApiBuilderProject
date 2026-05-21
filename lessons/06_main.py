import stat
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# ==============================
# 요청 본문 데이터 모델
# ==============================

# Item 모델은 클라이언트가 /items/ API로 보낼 JSON 데이터의 구조를 정의합니다.

class Item(BaseModel):
    name: str = Field(
        min_length=3, 
        max_length=50, 
        title="Item Name",
        description="The name of the item (3 to 50 characters).", 
        examples=["Gaming Keyboard"] 
    )
    description: Optional[str] = Field(
        default=None, 
        max_length=300, 
        title="Item Description",
        description="Optional description of the item (max 300 characters)."
    )
    price: float = Field(
        gt=0, 
        le=100000.0, 
        title="Price",
        description="The price of the item (must be positive and <= 100,000)."
    )
    tax: Optional[float] = Field(
        default=None,
        gt=0,
        title="Tax",
        description="Optional tax amount (must be positive)."
    )
    tags: List[str] = Field(
        default=[], 
        min_length=1,
        max_length=5, 
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )


    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v:str):
        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")
        return v.title()
    

app = FastAPI()

items_db = {}


@app.post("/items/", status_code=201)
async def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item.model_dump()
    print(f"아이템 생성 완료: ID={item_id}, Data={items_db[item_id]}")
    return {"item_id": item_id, **items_db[item_id]}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, **items_db[item_id]}