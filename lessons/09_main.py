from email.policy import HTTP
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI()



######################################
# --- Pydantic 모델 정의 ---
######################################

# 클라이언트가 회원가입/사용자 생성 요청을 보낼 때 사용하는 입력 모델
# 비밀번호는 사용자를 만들 때 필요하므로 포함한다.
class UserIn(BaseModel):
    username: str
    password: str    # 입력 시에는 비밀번호가 필요
    email: EmailStr  # Pydantic의 EmailStr 타입으로 이메일 형식 검증
    full_name: Optional[str] = None



# 클라이언트에게 사용자 정보를 응답할 때 사용하는 출력 모델
# 외부에 비밀번호를 보여주면 안 되므로 password 필드는 제외한다.
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    # 'password' 필드는 여기에 정의되지 않았습니다!



# 서버 내부에서 아이템 정보를 저장할 때 사용하는 내부 모델
# owner_id, secret_code처럼 외부에 보여주고 싶지 않은 정보도 포함한다.
class ItemInternal(BaseModel):
    name: str
    price: float
    owner_id: int     # 내부적으로만 사용할 소유자 ID
    secret_code: str  # 외부에 노출하고 싶지 않은 비밀 코드



# 클라이언트에게 아이템 정보를 응답할 때 사용하는 출력 모델
# owner_id, secret_code는 외부에 노출하지 않기 위해 제외한다.
class ItemPublic(BaseModel):
    name: str
    price: float
    # 'owner_id' 와 'secret_code' 는 여기에 정의되지 않았습니다!





################################
# --- 가상 데이터베이스 ---
################################

# 실제 DB 대신 사용하는 임시 저장소
# username을 key로 하고, UserIn 모델 객체를 value로 저장한다.
fake_users_db = {} 

# 실제 DB 대신 사용하는 아이템 임시 데이터
# 내부 데이터이므로 owner_id, secret_code까지 가지고 있다.
fake_items_db = {
    1: ItemInternal(name="Keyboard", price=75.0, owner_id=1, secret_code="abc"),
    2: ItemInternal(name="Mouse", price=25.5, owner_id=1, secret_code="def"),
    3: ItemInternal(name="Monitor", price=300.0, owner_id=2, secret_code="ghi"),
}





################################
# --- API 엔드포인트 정의 ---
################################

# 기본 JSON 응답 예제
@app.get("/ping")
async def ping():
    # 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.
    return {"message": "pong"}



# 사용자 생성 API
# 요청은 UserIn으로 받는다. 즉 password까지 받는다.
# 응답은 UserOut으로 내보낸다. 즉 password는 응답에서 빠진다.
@app.post("/users", response_model=UserOut, status_code=201)
async def create_user(user: UserIn):

    print(f"Creating user: {user.username}, Password: {user.password}")

    # 내부 저장소에는 password가 포함된 UserIn 객체를 그대로 저장한다.
    fake_users_db[user.username] = user

    # 함수는 password가 포함된 user를 반환하지만,
    # response_model=UserOut 때문에 최종 응답에서는 password가 제거된다.
    return user
'''
이 블록이 이번 코드의 핵심입니다.

이 API는 사용자 생성 요청을 처리합니다.
함수 매개변수에 user: UserIn이 있으므로, 클라이언트가 보낸 요청 본문은 UserIn 모델 기준으로 검증됩니다.

즉, 요청에는 이런 데이터가 들어올 수 있습니다.
{
  "username": "sechang",
  "password": "1234",
  "email": "sechang@example.com",
  "full_name": "Lee Sechang"
}

여기서 password는 요청을 받을 때 필요합니다.

그런데 API 데코레이터에는 이렇게 되어 있습니다.

response_model=UserOut

이 뜻은:

최종 응답은 UserOut 모델 모양으로 내보내라.

입니다.

함수는 실제로 password가 포함된 user 객체를 반환합니다.

return user

하지만 FastAPI는 최종 응답을 내보내기 전에 UserOut 모델을 기준으로 필터링합니다.
UserOut에는 password가 없기 때문에 응답에서 password는 자동으로 빠집니다.

최종 응답은 이런 형태가 됩니다.

{
  "username": "sechang",
  "email": "sechang@example.com",
  "full_name": "Lee Sechang"
}

정리하면 이 API는 비밀번호를 입력으로는 받지만, 응답으로는 숨기는 예제입니다.
'''


# 특정 사용자 조회 API
# 내부 DB에는 UserIn, 즉 password 포함 객체가 저장되어 있지만
# 응답 모델이 UserOut이므로 password는 응답에서 제외된다.
@app.get("/users/{username}", response_model=UserOut)
async def read_user(username: str):

    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # DB에서 가져온 UserIn 객체 (비밀번호 포함)
    user_in_db = fake_users_db[username]

    return user_in_db
'''
이 API는 특정 사용자 정보를 조회합니다.

username은 경로 매개변수입니다.
예를 들어 /users/sechang으로 요청하면 username에는 "sechang"이 들어갑니다.

먼저 fake_users_db에 해당 사용자가 있는지 확인합니다.

없으면 HTTPException을 발생시켜 404 에러를 반환합니다.
있으면 fake_users_db에서 사용자 데이터를 꺼냅니다.

여기서 꺼낸 데이터는 UserIn 객체입니다.
즉, 내부적으로는 password를 포함하고 있습니다.

하지만 이 API에도 response_model=UserOut이 붙어 있습니다.

그래서 최종 응답에서는 password가 제거됩니다.

즉, 이 API는 DB에서 비밀번호가 포함된 사용자 데이터를 가져오더라도, 클라이언트에게는 비밀번호 없이 응답하는 예제입니다.
'''


# 아이템 목록 조회 API
# 내부 아이템에는 owner_id, secret_code가 있지만
# 응답은 List[ItemPublic]이므로 name, price만 나간다.
@app.get("/items/", response_model=List[ItemPublic])
async def read_items():

    # 실제 DB에서 가져온 ItemInternal 객체들의 리스트라고 가정
    internal_items_list = list(fake_items_db.values())

    # ItemInternal 객체 리스트를 반환하면, 각 객체가 ItemPublic 스키마에 맞춰 필터링됨
    return internal_items_list
'''
이 API는 아이템 목록을 조회합니다.

fake_items_db.values()는 딕셔너리에 저장된 ItemInternal 객체들을 가져옵니다.

즉, 내부 데이터는 이런 정보들을 가지고 있습니다.
{
  "name": "Keyboard",
  "price": 75.0,
  "owner_id": 1,
  "secret_code": "abc"
}

그런데 API에는 이렇게 되어 있습니다.

response_model=List[ItemPublic]


이 뜻은:

응답은 ItemPublic 형태의 데이터 여러 개가 담긴 리스트로 내보내라.

입니다.

ItemPublic에는 name, price만 있습니다.
그래서 각 아이템에서 owner_id, secret_code는 자동으로 빠집니다.

최종 응답은 이런 형태가 됩니다.

[
  {
    "name": "Keyboard",
    "price": 75.0
  },
  {
    "name": "Mouse",
    "price": 25.5
  },
  {
    "name": "Monitor",
    "price": 300.0
  }
]

즉, 이 API는 내부 아이템 리스트를 반환하더라도, 외부 공개용 필드만 필터링해서 응답하는 예제입니다.
'''


# 특정 아이템 조회 API
# 내부 데이터에는 secret_code가 있지만
# response_model=ItemPublic 때문에 응답에서는 숨겨진다.
@app.get("/items/{item_id}", response_model=ItemPublic)
async def read_single_item(item_id: int):

    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # DB에서 가져온 ItemInternal 객체 (secret_code 포함)
    internal_item = fake_items_db[item_id]

    # ItemInternal 객체를 반환해도 response_model=ItemPublic 에 의해 필터링됨
    return internal_item
'''
이 API는 특정 아이템 하나를 조회합니다.

item_id는 경로 매개변수입니다.
예를 들어 /items/1로 요청하면 item_id에는 정수 1이 들어갑니다.

먼저 fake_items_db 안에 해당 ID의 아이템이 있는지 확인합니다.

없으면 404 에러를 반환합니다.

있으면 ItemInternal 객체를 꺼냅니다.

ItemInternal에는 name, price, owner_id, secret_code가 모두 있습니다.

하지만 이 API에는 response_model=ItemPublic이 붙어 있습니다.

그래서 최종 응답에는 name, price만 포함됩니다.

예를 들어 /items/1 응답은 이렇게 나갑니다.

{
  "name": "Keyboard",
  "price": 75.0
}

즉, 이 API는 내부적으로는 비밀 정보가 포함된 아이템 객체를 사용하지만, 외부에는 공개 가능한 정보만 응답하는 예제입니다.
'''