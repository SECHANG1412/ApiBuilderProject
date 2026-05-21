from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


# --- Pydantic 모델 정의 ---
# BaseModel을 상속받아 데이터 모델 클래스를 만듭니다.
# 이 클래스는 요청 본문의 데이터 구조(스키마)를 정의합니다.
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


# --- FastAPI 애플리케이션 인스턴스 생성 ---
app = FastAPI()



# --- 요청 본문 처리 예제 ---


# 1. POST 요청으로 Item 데이터 생성
# 함수의 파라미터 'item'에 위에서 정의한 Item 모델 타입을 지정합니다.
@app.post("/items/")
async def create_item(item: Item):
    print(f"아이템 이름: {item.name}")
    print(f"아이템 설명: {item.description}")
    print(f"아이템 가격: {item.price}")
    print(f"아이템 세금: {item.tax}")

    # Pydantic 모델 객체를 그대로 반환하면 FastAPI가 자동으로 JSON으로 변환해줍니다.
    # item.model_dump()
    # Pydantic 모델 객체를 일반 파이썬 dict로 변환합니다.
    item_dict = item.model_dump()

    # 만약 세금 정보가 있다면 가격에 세금을 더해봅시다.
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})



# 2. PUT 요청으로 Item 데이터 업데이트 (경로 매개변수 + 요청 본문)
# item_id 경로 매개변수와 item 요청 본문을 함께 받습니다.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):

    # 실제로는 item_id로 데이터베이스에서 기존 아이템을 찾고,
    # 요청 본문(item)의 내용으로 업데이트하는 로직이 들어갑니다.
    print(f"업데이트 할 아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    return {"item_id": item_id, "updated_item_data": item.model_dump()}



# 3. 요청 본문 + 경로 매개변수 + 쿼리 매개변수 혼합 사용
@app.put("/items-complex/{item_id}")
async def update_item_complex(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"query_param_q": q})

    print(f"아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    if q: 
        print(f"쿼리 파라미터 q: {q}")

    return result