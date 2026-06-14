from unittest import result
from fastapi import FastAPI
from typing import Optional, List

app = FastAPI()


##########################################
# --- 경로 매개변수 (Path Parameters) ---
##########################################

# 1. 기본적인 경로 매개변수 사용
# /items/{item_id} 형태로 요청을 받습니다. {item_id} 부분이 경로 매개변수입니다.
@app.get("/items/{item_id}")
async def read_item(item_id):   # 데코레이터의 경로 매개변수 이름과 함수 인자 이름이 같아야 합니다!

    return {
        "item_id_received": item_id
    }

'''
이 코드는 /items/{item_id} 형태의 주소에서 item_id 값을 받아오는 예제입니다.

예를 들어 사용자가 /items/abc로 요청을 보내면, FastAPI는 abc 부분을 item_id라는 변수에 담아서 read_item() 함수에 전달합니다.

여기서 중요한 점은 데코레이터에 작성한 {item_id} 이름과 함수 매개변수 이름 item_id가 같아야 한다는 것입니다.
그래야 FastAPI가 경로에서 꺼낸 값을 함수 인자로 정확히 연결할 수 있습니다.
'''


# 2. 타입 힌트를 사용한 경로 매개변수
# item_id가 정수(int) 타입이어야 함을 명시합니다.
@app.get("/items/typed/{item_id}")  
async def read_item_typed(item_id: int):   # 타입 힌트: int
    
    # FastAPI가 자동으로 문자열 경로를 정수로 변환하고, 변환 불가능하면 오류를 반환합니다.
    return {
        "item_id": item_id, 
        "type": str(type(item_id))
    }

'''
이 코드는 경로 매개변수 item_id를 정수 타입으로 받는 예제입니다.

주소로 들어오는 값은 원래 문자열이지만, item_id: int라고 작성하면 FastAPI가 해당 값을 정수로 변환하려고 시도합니다.

예를 들어 /items/typed/10으로 요청하면 "10"이라는 문자열이 정수 10으로 변환됩니다.
반대로 /items/typed/abc처럼 정수로 바꿀 수 없는 값이 들어오면 FastAPI가 자동으로 오류 응답을 반환합니다.

즉, 이 블록은 경로 매개변수에도 타입 검증과 자동 변환을 적용할 수 있다는 것을 보여줍니다.
'''


# 3. 경로 순서의 중요성 예시
# 고정 경로가 동적 경로보다 먼저 와야 합니다.
@app.get("/users/me")
async def read_current_user():
    return {
        "user_id": "현재 로그인한 사용자 (me)"
    }

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {
        "user_id": user_id
    }

'''
이 코드는 FastAPI에서 경로를 등록할 때 순서가 중요하다는 것을 보여주는 예제입니다.

/users/me는 고정된 경로이고, /users/{user_id}는 동적인 경로입니다.
만약 /users/{user_id}가 먼저 등록되어 있다면, /users/me 요청이 들어왔을 때 FastAPI가 me를 user_id 값으로 인식할 수 있습니다.

그래서 더 구체적인 고정 경로인 /users/me를 먼저 작성하고, 더 넓게 매칭되는 동적 경로 /users/{user_id}를 나중에 작성하는 것이 좋습니다.

정리하면, 고정 경로는 동적 경로보다 먼저 작성해야 의도한 API가 실행됩니다.
'''



##########################################
# --- 경로 매개변수 (Path Parameters) ---
##########################################

# 가상의 아이템 데이터베이스 (간단한 리스트)
fake_items_db = [
    {"item_name": "맥북 프로"}, 
    {"item_name": "아이폰 15"}, 
    {"item_name": "에어팟 맥스"}
]



# 4. 기본적인 쿼리 매개변수 사용 (기본값 설정으로 선택적 매개변수 만들기)
# /items-query/?skip=0&limit=10 형태로 요청을 받습니다.
@app.get("/items-query/")
async def read_items_with_query(skip: int = 0, limit: int = 10): 
    # skip, limit은 경로에 없으므로 쿼리 매개변수가 됩니다. 기본값을 설정했습니다.
    
    # 기본값이 있으므로 클라이언트가 skip이나 limit을 제공하지 않아도 오류가 발생하지 않습니다.
    return {
        "query_params": {"skip": skip, "limit": limit}, 
        "items": fake_items_db[skip : skip + limit]
    }

'''
이 코드는 skip과 limit이라는 쿼리 매개변수를 받는 예제입니다.

skip과 limit은 경로 안에 {skip}, {limit}처럼 들어가 있지 않습니다.
그래서 FastAPI는 이 값들을 자동으로 쿼리 매개변수로 판단합니다.

예를 들어 아래와 같이 요청할 수 있습니다.

/items-query/?skip=0&limit=2

이 요청은 “0번째부터 시작해서 2개만 가져오겠다”는 의미입니다.

skip: int = 0, limit: int = 10처럼 기본값이 있기 때문에, 사용자가 쿼리 값을 보내지 않아도 오류가 발생하지 않습니다.
값을 보내지 않으면 skip은 0, limit은 10으로 처리됩니다.

즉, 이 블록은 목록 조회 API에서 페이지네이션처럼 일부 데이터만 가져오는 기본 구조를 보여줍니다.
'''



# 5. 선택적(Optional) 쿼리 매개변수
# q라는 쿼리 매개변수를 받지만, 필수는 아닙니다.
@app.get("/items-optional/")
async def read_items_optional(q: Optional[str] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}

    # q가 제공되었다면 (None이 아니라면) 결과에 q를 추가합니다.
    if q:
        results.update({"q": q})
    return results
'''
이 코드는 q라는 선택적 쿼리 매개변수를 받는 예제입니다.

q: Optional[str] = None은 q 값이 문자열일 수도 있고, 아예 없을 수도 있다는 뜻입니다.
사용자가 /items-optional/처럼 요청하면 q는 None이 됩니다.

반대로 아래처럼 요청하면,

/items-optional/?q=fastapi

q 값에는 "fastapi"가 들어갑니다.

코드에서는 if q: 조건문을 사용해서 q가 있을 때만 결과에 q 값을 추가합니다.

즉, 이 블록은 검색어처럼 있어도 되고 없어도 되는 쿼리 매개변수를 처리하는 방식을 보여줍니다.
'''


# 6. 쿼리 매개변수 타입 변환 및 필수 매개변수
# price 쿼리 매개변수는 float 타입이어야 하고, is_offer는 boolean 타입이어야 합니다.
# description은 필수 쿼리 매개변수입니다.(기본값이 없으므로)
@app.get("/items-validation/")
async def read_items_with_validation(description: str, price: float, is_offer: Optional[bool] = None):
    # FastAPI가 자동으로 타입을 검증하고 변환해줍니다.
    # description이 제공되지 않거나 price가 float으로 변환될 수 없으면 오류가 발생합니다.

    item_info = {"description": description, "price": price}

    # is_offer가 제공되었다면 결과에 추가
    if is_offer is not None:
        item_info.update({"is_offer": is_offer})
    return item_info
'''
이 코드는 쿼리 매개변수의 타입 변환과 필수값 검증을 보여주는 예제입니다.

description: str과 price: float는 기본값이 없기 때문에 필수 쿼리 매개변수입니다.
따라서 사용자가 description이나 price를 보내지 않으면 FastAPI가 자동으로 오류를 반환합니다.

예를 들어 정상 요청은 이런 형태입니다.

/items-validation/?description=keyboard&price=99000&is_offer=true

price: float라고 작성했기 때문에 "99000"처럼 문자열로 들어온 쿼리 값도 FastAPI가 실수형 숫자로 변환해줍니다.

is_offer: Optional[bool] = None은 선택값입니다.
사용자가 보내면 boolean 값으로 변환되고, 보내지 않으면 None으로 처리됩니다.

즉, 이 블록은 FastAPI가 쿼리 매개변수의 필수 여부, 타입 변환, 검증을 자동으로 처리해준다는 것을 보여줍니다.
'''



####################################################
# --- 경로 매개변수와 쿼리 매개변수 함께 사용 ---
####################################################

# 7. 경로 매개변수와 쿼리 매개변수 동시 사용
# /users/{user_id}/orders?status=pending 형태로 요청
@app.get("/users/{user_id}/orders")
async def read_user_orders(user_id: int, status: Optional[str] = None):  # user_id는 경로 매개변수, status는 쿼리 매개변수
    result = {"user_id": user_id, "orders": [{"order_id": 1, "item": "Laptop"}, {"order_id": 2, "item": "Mouse"}]}
    if status:
        result.update({"filter_status": status})
        # 실제로는 status 값으로 주문 목록을 필터링하는 로직이 들어갑니다.
    return result
'''
이 코드는 경로 매개변수와 쿼리 매개변수를 함께 사용하는 예제입니다.

user_id는 /users/{user_id}/orders 경로 안에 들어있기 때문에 경로 매개변수입니다.
반면 status는 경로 안에 없고 함수 매개변수로만 선언되어 있기 때문에 쿼리 매개변수입니다.

예를 들어 아래처럼 요청할 수 있습니다.

/users/1/orders?status=pending

여기서 1은 user_id로 들어가고, pending은 status로 들어갑니다.

실제 서비스라면 이 API는 특정 사용자의 주문 목록을 조회하면서, status 값에 따라 대기 중인 주문, 완료된 주문, 취소된 주문 등을 필터링하는 형태로 발전할 수 있습니다.

즉, 이 블록은 URL 경로로는 대상을 지정하고, 쿼리 매개변수로는 조회 조건을 추가하는 구조를 보여줍니다.
'''