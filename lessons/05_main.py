from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional



###############################################
# --- Pydantic 모델 정의 ---
###############################################

# BaseModel을 상속받아 데이터 모델 클래스를 만듭니다.
# 이 클래스는 요청 본문의 데이터 구조(스키마)를 정의합니다.
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

'''
이 블록은 클라이언트가 요청 본문으로 보내야 할 데이터의 구조를 정의하는 부분입니다.

Item 클래스는 BaseModel을 상속받고 있습니다.
이렇게 작성하면 FastAPI는 요청 본문에 들어온 JSON 데이터를 Item 모델 기준으로 검사합니다.

여기서 name은 문자열이어야 하고, price는 실수형 숫자여야 합니다.
반면 description과 tax는 Optional이고 기본값이 None이기 때문에 요청에서 생략할 수 있습니다.

즉, 이 모델은 아래와 같은 JSON 요청을 받을 수 있다는 뜻입니다.

{
  "name": "맥북 프로",
  "description": "애플 노트북",
  "price": 3000000,
  "tax": 300000
}

또는 선택값을 제외하고 이렇게 보내도 됩니다.

{
  "name": "맥북 프로",
  "price": 3000000
}

정리하면, 이 블록은 요청 본문으로 받을 아이템 데이터의 스키마를 정의하는 코드입니다.
'''



###############################################
# --- FastAPI 애플리케이션 인스턴스 생성 ---
###############################################

app = FastAPI()

'''
FastAPI 애플리케이션 인스턴스를 생성하는 부분입니다.

이 app 객체를 기준으로 아래에서 @app.post, @app.put 같은 API 경로를 등록합니다.
쉽게 말하면, FastAPI 서버의 중심이 되는 객체를 만드는 코드입니다.
'''


###############################################
# --- 요청 본문 처리 예제 ---
###############################################

# 1. POST 요청으로 Item 데이터 생성
# 함수의 파라미터 'item'에 위에서 정의한 Item 모델 타입을 지정합니다.
@app.post("/items/")
async def create_item(item: Item):
    # FastAPI는 요청 본문을 읽어 Item 모델로 변환/검증합니다.
    # 함수 내부에서는 item을 Pydantic 모델 객체(파이썬 객체)로 바로 사용할 수 있습니다.

    print(f"아이템 이름: {item.name}")
    print(f"아이템 설명: {item.description}")
    print(f"아이템 가격: {item.price}")
    print(f"아이템 세금: {item.tax}")

    # Pydantic 모델 객체를 그대로 반환하면 FastAPI가 자동으로 JSON으로 변환해줍니다.
    # 예를 들어, 데이터베이스에 저장 후 저장된 객체를 반환할 수 있습니다.
    # Pydantic V2 방식: 모델을 dict로 변환 (이전 버전: item.dict())
    item_dict = item.model_dump()


    # 만약 세금 정보가 있다면 가격에 세금을 더해봅시다.
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    # 처리된 결과를 담은 딕셔너리 반환
    return item_dict

'''
이 블록은 /items/ 경로로 POST 요청이 들어왔을 때, 요청 본문에 담긴 아이템 데이터를 받아 처리하는 API입니다.

함수 매개변수에 item: Item이라고 작성했기 때문에 FastAPI는 클라이언트가 보낸 JSON 요청 본문을 자동으로 읽고, 
위에서 정의한 Item 모델로 변환합니다.

예를 들어 클라이언트가 아래와 같은 요청을 보내면,

{
  "name": "아이폰 15",
  "description": "스마트폰",
  "price": 1200000,
  "tax": 120000
}

FastAPI는 이 JSON을 Item 객체로 바꿔서 item 매개변수에 넣어줍니다.
그래서 함수 내부에서는 item.name, item.price, item.tax처럼 객체 속성에 접근하듯 사용할 수 있습니다.

item.model_dump()는 Pydantic 모델 객체를 일반 딕셔너리로 변환하는 코드입니다.

변환한 딕셔너리에 세금이 있으면 price_with_tax 값을 추가합니다.

마지막으로 item_dict를 반환하면 FastAPI가 자동으로 JSON 응답으로 변환해서 클라이언트에게 보내줍니다.

정리하면, 이 블록은 요청 본문으로 받은 아이템 데이터를 검증하고, 필요한 값을 추가한 뒤 응답으로 반환하는 POST API 예제입니다.
'''



# 2. PUT 요청으로 Item 데이터 업데이트 (경로 매개변수 + 요청 본문)
# item_id 경로 매개변수와 item 요청 본문을 함께 받습니다.
@app.put("/items/{item_id}")
async def update_item(
    item_id: int, 
    item: Item
):
    # item_id는 경로에서, item은 본문에서 옵니다.
    # 실제로는 item_id로 데이터베이스에서 기존 아이템을 찾고,
    # 요청 본문(item)의 내용으로 업데이트하는 로직이 들어갑니다.

    print(f"업데이트 할 아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    return {
        "item_id": item_id, 
        "updated_item_data": item.model_dump()
    }

'''
이 블록은 특정 아이템을 수정하는 API 예제입니다.

item_id는 /items/{item_id} 경로 안에 들어 있으므로 경로 매개변수입니다.
반면 item: Item은 경로에 없고 Pydantic 모델 타입으로 선언되어 있기 때문에 요청 본문에서 가져옵니다.

예를 들어 아래처럼 요청할 수 있습니다.

PUT /items/1

요청 본문은 이런 식으로 보낼 수 있습니다.

{
  "name": "수정된 맥북 프로",
  "description": "수정된 설명",
  "price": 2800000,
  "tax": 280000
}

이 경우 item_id에는 1이 들어가고, 요청 본문 데이터는 item 객체로 들어갑니다.

실제 서비스라면 item_id를 이용해 데이터베이스에서 기존 아이템을 찾고, 요청 본문으로 받은 값으로 수정하는 로직이 들어갑니다.
현재 예제에서는 실제 DB 수정 없이, 받은 item_id와 요청 본문 데이터를 그대로 응답으로 반환합니다.

정리하면, 이 블록은 경로 매개변수로 수정할 대상을 받고, 요청 본문으로 수정할 데이터를 받는 PUT API 예제입니다.
'''



# 3. 요청 본문 + 경로 매개변수 + 쿼리 매개변수 혼합 사용
@app.put("/items-complex/{item_id}")
async def update_item_complex(
    item_id: int, 
    item: Item, 
    q: Optional[str] = None
):

    # 경로 매개변수와 본문 내용을 합침
    result = {
        "item_id": item_id, 
        **item.model_dump()
    }

    # 쿼리 매개변수 q가 있다면 결과에 추가
    if q:
        result.update({"query_param_q": q})

    print(f"아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    if q: 
        print(f"쿼리 파라미터 q: {q}")

    return result

'''
이 블록은 하나의 API에서 경로 매개변수, 요청 본문, 쿼리 매개변수를 함께 사용하는 예제입니다.

item_id는 /items-complex/{item_id} 경로에 포함되어 있으므로 경로 매개변수입니다.
item: Item은 Pydantic 모델이므로 요청 본문에서 가져옵니다.
q: Optional[str] = None은 경로에 포함되어 있지 않고 기본값이 있으므로 선택적 쿼리 매개변수입니다.

예를 들어 아래처럼 요청할 수 있습니다.

PUT /items-complex/3?q=fastapi

요청 본문은 이렇게 보낼 수 있습니다.

{
  "name": "에어팟 맥스",
  "description": "무선 헤드폰",
  "price": 769000,
  "tax": 76900
}

이 요청에서 3은 item_id로 들어가고, q=fastapi는 쿼리 매개변수로 들어갑니다.
JSON 본문은 Item 모델 객체로 변환되어 item에 들어갑니다.

result = {"item_id": item_id, **item.model_dump()} 부분은 경로 매개변수인 item_id와 요청 본문 데이터를 하나의 딕셔너리로 합치는 코드입니다.

정리하면, 이 블록은 URL 경로로 수정 대상을 받고, 요청 본문으로 수정 데이터를 받고, 쿼리 매개변수로 추가 조건까지 받는 복합 API 예제입니다.
'''
    