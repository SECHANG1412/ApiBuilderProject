from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


########################################################
# --- Pydantic 모델 정의 (고급 유효성 검사 추가) ---
########################################################

class Item(BaseModel):
    # Field를 사용하여 추가 제약 조건 설정
    name: str = Field (
        min_length=3,       # 최소 길이 3
        max_length=50,      # 최대 길이 50
        title="Item Name",  # 문서화를 위한 제목
        description="The name of the item (3 to 50 characters).",  # 문서화를 위한 설명
        examples=["Gaming Keyboard"]    # 문서화를 위한 예시
    )
    description: Optional[str] = Field(
        default=None,   # 기본값 설정
        max_length=300, # 최대 길이 300
        title="Item Description",
        description="Optional description of the item (max 300 characters)."
    )
    price: float = Field(
        gt=0,           # 0보다 커야 함 (greater than 0)
        le=100000.0,    # 100,000 보다 작거나 같아야 함 (less than or equal to 100,000)
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
        default=[],     # 기본값 빈 리스트
        min_length=1,   # 최소 1개의 태그 필요
        max_length=5,   # 최대 5개의 태그 가능
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )
    '''
    이 블록은 클라이언트가 아이템 생성 요청을 보낼 때, 요청 본문에 어떤 데이터가 들어와야 하는지 정의하는 부분입니다.

    Item 클래스는 BaseModel을 상속받고 있으므로 Pydantic 모델로 동작합니다. 
    FastAPI는 요청 본문으로 들어온 JSON 데이터를 이 Item 모델 기준으로 자동 검증합니다.

    name은 문자열이며, 최소 3글자 이상 최대 50글자 이하만 허용됩니다.
    description은 선택값입니다. 요청에 없어도 되고, 값이 있다면 최대 300자까지만 허용됩니다.
    price는 필수 숫자값입니다. gt=0 조건 때문에 0보다 커야 하고, le=100000.0 조건 때문에 100000 이하만 허용됩니다.
    tax는 선택 숫자값입니다. 요청에 없어도 되지만, 값이 들어온다면 0보다 커야 합니다.
    tags는 문자열 리스트입니다. 기본값은 빈 리스트이고, 값이 들어올 경우 최소 1개부터 최대 5개까지 허용하는 형태입니다.

    즉, 이 블록은 단순히 “어떤 필드가 있는지”만 정하는 것이 아니라, 
    각 필드가 어떤 조건을 만족해야 하는지까지 정하는 요청 본문 검증 설계 부분입니다.

    예를 들어 이런 요청은 정상적으로 통과할 수 있습니다.

    {
    "name": "Gaming Keyboard",
    "description": "Mechanical keyboard",
    "price": 80000,
    "tax": 8000,
    "tags": ["keyboard", "gaming"]
    }
    '''


    #################################
    # --- 커스텀 유효성 검사기 ---
    #################################

    # @field_validator를 사용하여 특정 필드에 대한 커스텀 검증 로직 추가 (Pydantic V2 방식)
    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v: str):
        # 'v'는 검증할 필드의 값입니다.

        # 유효성 검사 실패 시 ValueError 발생
        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")
        
        # 유효성 검사 통과 시 값을 그대로 또는 수정하여 반환
        # 이름을 Title Case로 변환하여 반환
        return v.title()
    '''
    이 블록은 name 필드에 대해 직접 만든 추가 검증 규칙입니다.

    앞에서 Field를 사용해 name의 길이를 제한했습니다. 
    하지만 “이름에 admin이라는 단어가 들어가면 안 된다” 같은 규칙은 단순 길이 제한만으로 처리하기 어렵습니다.

    그래서 @field_validator('name')를 사용해 name 필드 전용 검증 함수를 만든 것입니다.

    여기서 v는 클라이언트가 보낸 name 값입니다.
    예를 들어 "admin keyboard"라는 값이 들어오면, v.lower()로 소문자로 바꾼 뒤 "admin"이 포함되어 있는지 검사합니다. 
    포함되어 있으면 ValueError를 발생시키고 요청은 검증 실패가 됩니다.

    검증을 통과하면 v.title()을 반환합니다.
    그래서 "gaming keyboard"처럼 들어온 값은 "Gaming Keyboard"처럼 각 단어의 첫 글자가 대문자인 형태로 변환됩니다.

    즉, 이 블록은 기본 필드 조건으로 처리하기 어려운 서비스 전용 검증 규칙을 직접 추가하는 부분입니다.
    '''





##################################################
# --- FastAPI 애플리케이션 인스턴스 생성 ---
##################################################

app = FastAPI()



# 임시 데이터 저장소 (간단한 딕셔너리 사용)
items_db = {}





###################################
# --- API 엔드포인트 정의 ---
###################################


# 아이템 생성 API 블록
# 성공 시 201 Created 상태 코드 반환
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    # Pydantic 모델을 통과했다는 것은 데이터가 유효하다는 의미!

    item_id = len(items_db) + 1
    items_db[item_id] = item.model_dump() # Pydantic 모델을 dict로 변환하여 저장

    print(f"아이템 생성 완료: ID={item_id}, Data={items_db[item_id]}")
    return {"item_id": item_id, **items_db[item_id]}
'''
이 블록은 /items/ 경로로 POST 요청이 들어왔을 때 새로운 아이템을 생성하는 API입니다.

@app.post("/items/", status_code=201)는 /items/ 주소로 POST 요청이 들어오면 아래의 create_item() 함수를 실행하겠다는 의미입니다. 
status_code=201은 생성 성공 시 HTTP 상태 코드를 201 Created로 반환하겠다는 뜻입니다.

함수 매개변수에 item: Item이 있기 때문에 FastAPI는 요청 본문으로 들어온 JSON 데이터를 Item 모델 기준으로 자동 검증합니다. 
검증에 실패하면 함수 내부 코드가 실행되지 않고, FastAPI가 에러 응답을 반환합니다.


item_id = len(items_db) + 1
이 코드는 현재 저장된 아이템 개수를 기준으로 새 아이템 ID를 만드는 부분입니다. 저장된 아이템이 없으면 첫 번째 ID는 1이 됩니다.


items_db[item_id] = item.model_dump()
이 코드는 Pydantic 모델 객체인 item을 일반 딕셔너리로 바꿔서 items_db에 저장하는 부분입니다.
item.model_dump()를 쓰면 item.name, item.price처럼 객체 형태로 들어온 데이터를 딕셔너리 형태로 꺼낼 수 있습니다.

예를 들어 요청 본문이 이렇게 들어오면,
{
  "name": "gaming keyboard",
  "description": "Mechanical keyboard",
  "price": 80000,
  "tax": 8000,
  "tags": ["keyboard", "gaming"]
}

커스텀 검증기를 거친 뒤 저장소에는 대략 이런 형태로 저장됩니다.
{
  1: {
    "name": "Gaming Keyboard",
    "description": "Mechanical keyboard",
    "price": 80000,
    "tax": 8000,
    "tags": ["keyboard", "gaming"]
  }
}

마지막 반환 부분은 새로 생성된 item_id와 저장된 아이템 정보를 하나의 딕셔너리로 합쳐서 응답합니다.

return {"item_id": item_id, **items_db[item_id]}

응답은 이런 형태가 됩니다.

{
  "item_id": 1,
  "name": "Gaming Keyboard",
  "description": "Mechanical keyboard",
  "price": 80000,
  "tax": 8000,
  "tags": ["keyboard", "gaming"]
}

즉, 이 블록은 검증된 요청 데이터를 임시 저장소에 저장하고, 생성된 아이템 정보를 응답으로 반환하는 API입니다.
'''


# 아이템 조회 API 블록
@app.get("/items/{item_id}")
async def read_item(item_id: int):

    # 아이템이 없으면 404 Not Found 오류 발생
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"item_id": item_id, **items_db[item_id]}
'''
이 블록은 /items/{item_id} 경로로 GET 요청이 들어왔을 때 특정 아이템을 조회하는 API입니다.

item_id: int는 경로 매개변수입니다.
예를 들어 /items/1로 요청하면 URL 경로의 1이 item_id에 들어갑니다. 타입 힌트가 int이기 때문에 FastAPI는 이 값을 정수로 변환합니다.

먼저 아래 코드로 해당 ID의 아이템이 저장소에 있는지 확인합니다.
if item_id not in items_db:

해당 ID가 없으면 아래 코드가 실행됩니다.
raise HTTPException(status_code=404, detail="Item not found")

이 코드는 FastAPI에게 정상 응답 대신 404 Not Found 에러를 반환하라고 알려주는 코드입니다.


예상 응답은 이런 형태입니다.
{
  "detail": "Item not found"
}

반대로 해당 ID가 존재하면 저장된 아이템 데이터를 반환합니다.

return {"item_id": item_id, **items_db[item_id]}

여기서도 item_id와 저장된 아이템 딕셔너리를 하나로 합쳐 응답합니다.

즉, 이 블록은 아이템이 존재하면 조회 결과를 반환하고, 존재하지 않으면 404 에러를 반환하는 조회 API입니다.
'''