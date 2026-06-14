from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional

app = FastAPI()


#############################################
# --- 의존성 함수(Dependable) 정의 ---
#############################################

# 1. 공통 쿼리 파라미터 처리를 위한 의존성 함수
async def common_parameters(
        q: Optional[str] = None,    # 검색 쿼리 (선택적)
        skip: int = 0,              # 건너뛸 항목 수 (기본값 0)
        limit: int = 100            # 가져올 최대 항목 수 (기본값 100)
):
    # 딕셔너리 형태로 파라미터들을 묶어서 반환
    return {
        "q": q, 
        "skip": skip, 
        "limit": limit
    }

'''
이 블록은 여러 API에서 공통으로 사용할 쿼리 파라미터 처리 로직을 함수로 분리한 부분입니다.

q는 검색어처럼 사용할 수 있는 선택 쿼리 파라미터입니다.
skip은 몇 개를 건너뛸지 정하는 값이고, 기본값은 0입니다.
limit은 몇 개까지 가져올지 정하는 값이고, 기본값은 100입니다.

예를 들어 이런 요청이 들어오면,

/items/?q=phone&skip=0&limit=10

FastAPI는 q, skip, limit 값을 common_parameters() 함수에 넣어줍니다.
그리고 이 함수는 세 값을 하나의 딕셔너리로 묶어서 반환합니다.

{"q": "phone", "skip": 0, "limit": 10}

즉, 이 블록은 여러 API에서 반복될 수 있는 쿼리 파라미터 처리 코드를 재사용하기 위한 의존성 함수입니다.
'''



# 2. 간단한 API 키 확인을 위한 의존성 함수
# 실제로는 더 안전한 방식(예: 헤더 사용, 토큰 검증)을 사용해야 합니다!
async def verify_api_key(x_api_key: Optional[str] = None):

    # 이 예제에서는 간단히 'fakeapikey' 와 일치하는지 확인
    # 일치하지 않으면 403 Forbidden 오류 발생
    if x_api_key != "fakeapikey":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    # 유효하면 키 값을 반환 (또는 그냥 None을 반환해도 됨)
    return x_api_key

'''
이 블록은 요청으로 들어온 API 키가 올바른지 확인하는 의존성 함수입니다.

현재 코드에서는 x_api_key 값이 "fakeapikey"와 같은지 비교합니다.
값이 다르면 HTTPException을 발생시켜 403 Forbidden 응답을 반환합니다.

예를 들어 아래 요청은 통과합니다.
/secure-data/?x_api_key=fakeapikey

하지만 아래 요청은 실패합니다.
/secure-data/?x_api_key=wrongkey

실패하면 FastAPI는 대략 이런 응답을 반환합니다.

{
  "detail": "Invalid API Key"
}

중요한 점은, 이 의존성 함수에서 에러가 발생하면 실제 API 함수는 실행되지 않는다는 것입니다.

즉, 이 블록은 보호된 API에 들어오기 전에 먼저 인증 검사를 수행하는 문지기 역할을 합니다.
'''



# 3. 하위 의존성 예시: verify_api_key 의존성을 사용하는 또 다른 의존성
async def verify_admin_access(
        api_key: str = Depends(verify_api_key)  # verify_api_key의 반환값이 api_key 변수에 주입됩니다.
):
    
    # 이 예제에서는 키가 유효하기만 하면 관리자 접근을 허용한다고 가정합니다.
    # 실제로는 사용자 역할 등을 확인하는 로직이 추가되어야 합니다.
    print(f"관리자 접근 확인됨 (API 키: {api_key})")

    # 관리자임을 나타내는 정보를 반환할 수 있습니다.
    return {
        "is_admin": True
    }

'''
이 블록은 다른 의존성 함수 안에서 또 다른 의존성을 사용하는 예제입니다.

verify_admin_access()는 관리자 접근 권한을 확인하는 함수입니다.
그런데 이 함수는 내부에서 먼저 verify_api_key를 실행합니다.

api_key: str = Depends(verify_api_key)

이 부분 때문에 FastAPI는 verify_admin_access()를 실행하기 전에 먼저 verify_api_key()를 실행합니다.

API 키가 틀리면 verify_api_key()에서 바로 403 Forbidden 에러가 발생하고, verify_admin_access()는 실행되지 않습니다.

API 키가 맞으면 verify_api_key()의 반환값인 "fakeapikey"가 api_key 변수에 들어옵니다.
그다음 관리자 접근이 확인되었다고 보고 {"is_admin": True}를 반환합니다.

즉, 이 블록은 의존성 안에서 또 다른 의존성을 사용하는 하위 의존성 구조를 보여줍니다.

쉽게 말하면 흐름은 이렇습니다.

/admin-only/ 요청
→ verify_admin_access 실행 필요
→ 그 전에 verify_api_key 먼저 실행
→ API 키 통과
→ verify_admin_access 실행
→ admin_info 반환
→ 실제 API 함수 실행
'''
    


######################################################
# --- API 엔드포인트 정의 (의존성 주입 사용) ---
######################################################

# 공통 쿼리 파라미터를 사용하는 /items/ API 블록
@app.get("/items/")
async def read_items(
    # common_parameters 함수의 반환값({q, skip, limit} 딕셔너리)이
    # commons 파라미터에 주입됩니다.
    commons: dict = Depends(common_parameters)
):
    print(f"요청 파라미터: {commons}")

    items_data = [{"item_name": "Item 1"}, {"item_name": "Item 2"}]

    return {
        "message": "Reading items", 
        "params": commons, 
        "data": items_data
    }

'''
이 블록은 /items/ 경로로 GET 요청이 들어왔을 때 아이템 목록을 반환하는 API입니다.

여기서 핵심은 이 부분입니다.
commons: dict = Depends(common_parameters)

이 코드는 FastAPI에게 “이 API를 실행하기 전에 common_parameters() 함수를 먼저 실행하고, 
그 반환값을 commons에 넣어줘”라고 요청하는 것입니다.

예를 들어 아래처럼 요청하면,
/items/?q=laptop&skip=0&limit=10

common_parameters()가 먼저 실행되고, 결과는 이런 딕셔너리가 됩니다.

{"q": "laptop", "skip": 0, "limit": 10}

이 값이 commons에 들어갑니다.
그 후 read_items() 함수는 아이템 데이터와 함께 쿼리 파라미터 정보를 응답으로 반환합니다.

즉, 이 블록은 공통 쿼리 파라미터 처리 로직을 Depends로 주입받아 사용하는 API 예제입니다.

'''

# 같은 의존성을 재사용하는 /users/ API 블록
@app.get("/users/")
async def read_users(
    # 같은 의존성 함수를 다른 엔드포인트에서도 재사용!
    commons: dict = Depends(common_parameters)
):
    print(f"요청 파라미터: {commons}")
    users_data = [{"user_name": "User 1"}, {"user_name": "User 2"}] # 가상 데이터
    return {"message": "Reading users", "params": commons, "data": users_data}
'''
이 블록은 /users/ 경로로 GET 요청이 들어왔을 때 사용자 목록을 반환하는 API입니다.

앞의 /items/ API와 마찬가지로 common_parameters 의존성을 사용합니다.

즉, /items/와 /users/는 서로 다른 API지만, q, skip, limit을 처리하는 방식은 같습니다.
그래서 같은 의존성 함수를 재사용하고 있습니다.

이게 의존성 주입의 장점입니다.

공통 로직을 API마다 반복해서 쓰지 않고, 하나의 함수로 분리해 여러 곳에 꽂아 넣을 수 있습니다.
'''



# '/secure-data/' 경로는 API 키 검증이 필요하다고 가정
@app.get("/secure-data/")
async def read_secure_data(
    # verify_api_key 의존성을 주입받습니다.
    # 만약 verify_api_key에서 HTTPException이 발생하면 이 함수는 실행되지 않습니다.
    api_key: str = Depends(verify_api_key)
):
    print(f"보안 데이터 접근 허용됨 (API 키: {api_key})")
    return {"message": "This is secure data!", "requester_api_key": api_key}
'''
이 블록은 API 키 검증을 통과해야만 접근할 수 있는 보안 데이터 API입니다.

핵심은 이 부분입니다.
api_key: str = Depends(verify_api_key)

FastAPI는 /secure-data/ 요청이 들어오면 먼저 verify_api_key()를 실행합니다.
API 키가 틀리면 verify_api_key()에서 HTTPException이 발생하고, read_secure_data() 함수는 실행되지 않습니다.
API 키가 맞으면 verify_api_key()가 API 키 값을 반환하고, 그 값이 api_key 변수에 들어갑니다.

정상 요청 예시는 이렇게 됩니다.
/secure-data/?x_api_key=fakeapikey

정리하면, 이 블록은 API 본문 로직을 실행하기 전에 인증 검사를 먼저 수행하는 구조입니다.
'''


# '/admin-only/' 경로는 관리자 접근 검증이 필요하다고 가정
@app.get("/admin-only/")
async def read_admin_data(
    # verify_admin_access 의존성을 주입받습니다.
    # 이 의존성은 내부적으로 verify_api_key 의존성을 사용합니다 (하위 의존성).
    admin_info: dict = Depends(verify_admin_access)
):
    # admin_info에는 {"is_admin": True} 가 주입됩니다.
    print(f"관리자 데이터 접근 허용됨: {admin_info}")

    return {"message": "Welcome, Admin!", "access_level": admin_info}
'''
이 블록은 관리자만 접근할 수 있다고 가정한 API입니다.

여기서는 verify_admin_access 의존성을 사용합니다.

admin_info: dict = Depends(verify_admin_access)

그런데 verify_admin_access()는 내부적으로 다시 verify_api_key()를 사용합니다.

그래서 이 API의 실제 실행 흐름은 이렇습니다.

1. /admin-only/ 요청 들어옴
2. verify_admin_access 의존성 실행 필요
3. verify_admin_access 내부의 verify_api_key 먼저 실행
4. API 키가 틀리면 403 에러
5. API 키가 맞으면 verify_admin_access 실행
6. {"is_admin": True} 반환
7. 그 값이 admin_info에 들어감
8. read_admin_data() 실행

정상 요청은 이런 식입니다.

/admin-only/?x_api_key=fakeapikey

응답은 대략 이렇게 됩니다.

{
  "message": "Welcome, Admin!",
  "access_level": {
    "is_admin": true
  }
}

즉, 이 블록은 의존성 함수가 또 다른 의존성 함수를 사용하는 하위 의존성 구조를 보여주는 예제입니다.
'''