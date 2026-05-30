from fastapi import FastAPI, HTTPException, status, Response 
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


###################################
# --- 가상 데이터베이스 ---
###################################

items_db = {1: {"name": "Laptop", "price": 1200.0}, 2: {"name": "Keyboard", "price": 75.0}}
item_next_id = 3



###################################
# --- Pydantic 모델 ---
###################################

# 요청 본문과 응답 데이터의 기본 구조를 정의하는 모델
# name은 문자열, price는 실수형 숫자여야 한다.
class Item(BaseModel):
    name: str
    price: float

'''
이 블록은 아이템 데이터의 기본 구조를 정의합니다.

Item은 Pydantic 모델입니다.
요청 본문으로 들어오는 데이터가 이 구조에 맞는지 FastAPI가 검증합니다.

즉, 아이템은 반드시 name과 price를 가져야 합니다.

정상 요청 예시는 이런 형태입니다.

{
  "name": "Mouse",
  "price": 25.5
}

name은 문자열이어야 하고, price는 숫자여야 합니다.
'''


###################################
# --- API 엔드포인트 정의 ---
###################################


# 1. 아이템 생성 API
# POST 요청으로 새 아이템을 생성한다.
# status_code=201은 "새 리소스가 생성되었다"는 의미이다.
@app.post("/items/", status_code=status.HTTP_201_CREATED, response_model=Item)
async def create_item(item: Item):

    # 전역 변수 item_next_id 값을 함수 안에서 수정하기 위해 global 사용
    global item_next_id

    # 요청 본문으로 받은 Pydantic 모델 객체를 dict로 바꿔서 저장한다.
    items_db[item_next_id] = item.model_dump()

    # 생성된 아이템 정보를 확인하기 위해 id까지 합쳐서 만든다.
    # 단, response_model=Item에는 id가 없으므로 최종 응답에서는 id가 빠질 수 있다.
    created_item_info = {"id": item_next_id, **item.model_dump()}

    # 다음 아이템 생성을 위해 ID 값을 1 증가시킨다.
    item_next_id += 1

    print(f"아이템 생성됨: {created_item_info}")

    # FastAPI는 반환값을 response_model=Item 기준으로 필터링해서 응답한다.
    return created_item_info


'''
이 API는 새 아이템을 생성합니다.

@app.post("/items/")이므로 클라이언트가 /items/ 경로로 POST 요청을 보내면 이 함수가 실행됩니다.

status_code=status.HTTP_201_CREATED

이 설정은 성공 응답 상태 코드를 201 Created로 보내겠다는 뜻입니다.
POST로 새 데이터를 생성할 때 자주 쓰는 상태 코드입니다.

item: Item

이 부분 때문에 요청 본문은 Item 모델 기준으로 검증됩니다.

예를 들어 클라이언트가 이렇게 보내면:

{
  "name": "Monitor",
  "price": 300.0
}

FastAPI는 이 데이터를 Item 객체로 만들어 item에 넣어줍니다.

items_db[item_next_id] = item.model_dump()

이 코드는 Pydantic 모델 객체를 딕셔너리로 바꿔서 items_db에 저장합니다.

created_item_info = {"id": item_next_id, **item.model_dump()}

이 코드는 새로 생성된 아이템 ID와 요청 본문 데이터를 하나의 딕셔너리로 합칩니다.

예를 들어 item_next_id가 3이고 요청 데이터가 {"name": "Monitor", "price": 300.0}이면, created_item_info는 이렇게 됩니다.

{
  "id": 3,
  "name": "Monitor",
  "price": 300.0
}

다만 이 API에는 response_model=Item이 붙어 있습니다.

response_model=Item

Item 모델에는 id가 없습니다.

class Item(BaseModel):
    name: str
    price: float

그래서 함수가 id까지 반환하더라도 최종 응답에서는 id가 빠지고, 보통 아래처럼 나갈 수 있습니다.

{
  "name": "Monitor",
  "price": 300.0
}

즉, 이 블록은 POST 요청으로 아이템을 생성하고, 성공 시 201 상태 코드를 반환하는 예제입니다.
'''


# 2. 아이템 삭제 API
# DELETE 요청으로 특정 아이템을 삭제한다.
# status_code=204는 "요청은 성공했지만 응답 본문은 없다"는 의미이다.
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):

     # 삭제할 item_id가 DB에 있으면 삭제한다.
    if item_id in items_db:
        print(f"아이템 삭제됨: ID={item_id}")
        del items_db[item_id]

        # 204 No Content는 응답 본문을 보내면 안 된다.
        # None을 반환하면 FastAPI가 빈 응답 본문으로 처리한다.
        return None
    
    else:
        # 삭제하려는 아이템이 없으면 404 Not Found 에러를 발생시킨다.
        # HTTPException은 데코레이터의 기본 status_code보다 우선한다.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
'''
이 API는 특정 아이템을 삭제합니다.

예를 들어 아래처럼 요청할 수 있습니다.

DELETE /items/1

그러면 item_id에는 1이 들어갑니다.

먼저 items_db 안에 해당 ID가 있는지 확인합니다.

if item_id in items_db:

있으면 해당 아이템을 삭제합니다.

del items_db[item_id]

이 API의 성공 상태 코드는 204 No Content입니다.

status_code=status.HTTP_204_NO_CONTENT

204는 요청은 성공했지만 응답 본문은 없다는 의미입니다.
그래서 성공 시에는 보통 아무 내용도 반환하지 않습니다.

return None

FastAPI는 204 상태 코드에서 None을 반환하면 빈 응답 본문으로 처리합니다.

반대로 삭제하려는 아이템이 없으면:
raise HTTPException(status_code=404, detail="Item not found")

404 에러를 반환합니다.

중요한 점은 HTTPException이 발생하면 데코레이터의 status_code=204보다 에러의 404가 우선한다는 것입니다.

즉, 성공하면 204, 실패하면 404입니다.
'''



# 3. 아이템 수정 API
# PUT 요청으로 특정 아이템을 수정한다.
# 상황에 따라 200 OK 또는 304 Not Modified를 반환한다.
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    
    # 수정하려는 아이템이 없으면 404 에러를 발생시킨다.
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    

    # 기존 데이터와 새로 들어온 데이터가 완전히 같으면
    # 실제로 변경된 내용이 없다고 판단한다.
    if items_db[item_id] == item.model_dump():

        # 304 Not Modified는 "변경 사항 없음"을 의미한다.
        # Response 객체를 직접 반환하면 response_model 처리는 적용되지 않는다.
        print(f"아이템 변경 없음: ID={item_id}")
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    

    # 기존 데이터와 다르면 새 데이터로 업데이트한다.
    else: 
        items_db[item_id] = item.model_dump()
        print(f"아이템 업데이트됨: ID={item_id}, Data={items_db[item_id]}")

        # 여기서는 dict를 반환한다.
        # FastAPI가 response_model=Item 기준으로 응답을 처리한다.
        return items_db[item_id]

'''
이 API는 특정 아이템을 수정합니다.

예를 들어 아래처럼 요청합니다.

PUT /items/1

요청 본문은 이런 형태입니다.

{
  "name": "Laptop",
  "price": 1200.0
}

먼저 수정하려는 아이템이 존재하는지 확인합니다.

if item_id not in items_db:

없으면 404 에러를 반환합니다.

그다음 기존 데이터와 새로 들어온 데이터를 비교합니다.

if items_db[item_id] == item.model_dump():

예를 들어 기존 1번 아이템이 이미 아래와 같은 상태인데:

{"name": "Laptop", "price": 1200.0}

요청도 똑같이 들어오면 실제로 바뀐 내용이 없습니다.

이때는 아래 응답을 반환합니다.

return Response(status_code=status.HTTP_304_NOT_MODIFIED)

304 Not Modified는 “수정된 내용이 없다”는 의미입니다.
이 경우 Response 객체를 직접 반환합니다.

여기서 중요한 점은:

return Response(...)

처럼 Response 객체를 직접 반환하면 response_model=Item 처리가 적용되지 않습니다.

반대로 변경 사항이 있으면:

items_db[item_id] = item.model_dump()
return items_db[item_id]

아이템을 업데이트하고, 업데이트된 데이터를 반환합니다.

이 경우에는 일반 딕셔너리를 반환하므로 response_model=Item이 적용됩니다.

즉, 이 API는 상황에 따라 다르게 응답합니다.

상황	        응답
아이템 없음	    404 Not Found
데이터 같음	    304 Not Modified
데이터 변경됨	200 OK + 수정된 아이템 JSON
'''


# 4. Response 객체 직접 반환 예제
# JSON이 아니라 XML 문자열을 직접 응답으로 보낸다.
@app.get("/legacy-data", response_model=Item)
async def get_legacy_data():
    legacy_content = "<legacy><name>Old Data</name><price>10.0</price></legacy>"

    # Response 객체를 직접 반환하면 FastAPI의 자동 JSON 변환이나 response_model 필터링이 적용되지 않는다.
    # 여기서는 XML 문자열을 application/xml 타입으로 직접 반환한다.
    return Response(content=legacy_content, media_type="application/xml", status_code=200)

'''
이 API는 JSON이 아니라 XML을 직접 반환합니다.

보통 FastAPI에서 딕셔너리를 반환하면 JSON으로 변환됩니다.
하지만 여기서는 Response 객체를 직접 만들었습니다.

return Response(
    content=legacy_content,
    media_type="application/xml",
    status_code=200
)

이 뜻은:

응답 본문은 legacy_content로 하고,
응답 형식은 application/xml로 하고,
상태 코드는 200으로 보내라.

입니다.

중요한 점은 이 API에 response_model=Item이 붙어 있다는 것입니다.

@app.get("/legacy-data", response_model=Item)

하지만 함수가 Response 객체를 직접 반환하고 있기 때문에 response_model=Item은 실제 응답 처리에 적용되지 않습니다.

즉, FastAPI가 Item 모델 기준으로 검증하거나 필터링하지 않습니다.

최종 응답은 JSON이 아니라 XML 문자열입니다.

<legacy><name>Old Data</name><price>10.0</price></legacy>

이 블록은 Response 객체를 직접 반환하면 FastAPI의 자동 응답 처리와 response_model 필터링을 우회한다는 점을 보여줍니다.
'''