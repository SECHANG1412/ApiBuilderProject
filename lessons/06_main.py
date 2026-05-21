import stat
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# ==============================
# 요청 본문 데이터 모델
# ==============================

# Item 모델은 클라이언트가 /items/ API로 보낼 JSON 데이터의 구조를 정의합니다.
# FastAPI는 요청 본문이 이 구조와 맞는지 자동으로 검사합니다.
class Item(BaseModel):

    # 상품명은 필수 입력값입니다.
    # 3자보다 짧거나 50자를 넘으면 FastAPI가 자동으로 422 에러를 반환합니다.
    name: str = Field(
        min_length=3, 
        max_length=50, 
        title="Item Name",
        description="The name of the item (3 to 50 characters).", 
        examples=["Gaming Keyboard"] 
    )

    # 상품 설명은 선택 입력값입니다.
    # 요청에서 description을 보내지 않아도 되고, 보내는 경우 최대 300자까지만 허용됩니다.
    description: Optional[str] = Field(
        default=None, 
        max_length=300, 
        title="Item Description",
        description="Optional description of the item (max 300 characters)."
    )

    # 가격은 필수 입력값입니다.
    # gt=0은 0보다 커야 한다는 뜻이고, le=100000.0은 100000 이하만 허용한다는 뜻입니다.
    price: float = Field(
        gt=0, 
        le=100000.0, 
        title="Price",
        description="The price of the item (must be positive and <= 100,000)."
    )

    # 세금은 선택 입력값입니다.
    # 요청에서 tax를 생략할 수 있지만, 입력한다면 0보다 큰 값이어야 합니다.
    tax: Optional[float] = Field(
        default=None,
        gt=0,
        title="Tax",
        description="Optional tax amount (must be positive)."
    )

    # 태그는 문자열 리스트입니다.
    # 예: ["keyboard", "gaming", "device"]
    # 최소 1개, 최대 5개의 태그만 허용합니다.
    tags: List[str] = Field(
        default=[], 
        min_length=1,
        max_length=5, 
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )


    # name 필드에만 적용되는 추가 검증 함수입니다.
    # Field 옵션만으로 처리하기 어려운 직접 만든 검증 규칙을 넣을 때 사용합니다.
    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v:str):

        # 상품명에 admin이라는 단어가 포함되어 있으면 요청을 거부합니다.
        # 대소문자 구분 없이 검사하기 위해 lower()를 사용합니다.
        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")
        
        # 검증을 통과한 이름은 Title Case 형태로 변환합니다.
        # 예: "gaming keyboard" -> "Gaming Keyboard"
        return v.title()
    



# ==============================
# FastAPI 앱 생성
# ==============================

# FastAPI 애플리케이션 객체입니다.
# 이 app 객체에 API 주소들을 등록합니다.
app = FastAPI()



# ==============================
# 임시 데이터 저장소
# ==============================

# 실제 데이터베이스 대신 사용하는 임시 저장소입니다.
items_db = {}




# ==============================
# 상품 생성 API
# ==============================

# 상품 데이터를 새로 생성하는 API입니다.
# 요청 본문은 Item 모델 형식의 JSON이어야 합니다.
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    # 여기까지 코드가 실행되었다는 것은
    # 클라이언트가 보낸 JSON 데이터가 Item 모델의 검증을 통과했다는 의미입니다.

    # 현재 저장된 상품 개수에 1을 더해서 새 ID를 만듭니다.
    # 예: 저장된 상품이 0개면 item_id는 1
    item_id = len(items_db) + 1

    # item은 Pydantic 모델 객체입니다.
    # 저장하기 쉽게 일반 dict 형태로 변환합니다
    items_db[item_id] = item.model_dump()
    
    print(f"아이템 생성 완료: ID={item_id}, Data={items_db[item_id]}")

    # 응답에는 생성된 item_id와 상품 데이터를 함께 담아 반환합니다.
    # **items_db[item_id]는 딕셔너리 안의 값을 풀어서 넣는 문법입니다.
    return {"item_id": item_id, **items_db[item_id]}




# ==============================
# 상품 조회 API
# ==============================

# item_id에 해당하는 상품 하나를 조회하는 API입니다.
@app.get("/items/{item_id}")
async def read_item(item_id: int):

    # items_db 안에 해당 item_id가 없으면
    # 존재하지 않는 상품을 조회한 것이므로 404 에러를 발생시킵니다.
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # 해당 item_id가 존재하면 상품 정보를 반환합니다.
    return {"item_id": item_id, **items_db[item_id]}