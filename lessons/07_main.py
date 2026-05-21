from fastapi import FastAPI, Depends, HTTPException, status 
from typing import Optional

app = FastAPI()


# ==============================
# 의존성 함수 정의
# ==============================

# 여러 API에서 공통으로 사용할 쿼리 파라미터를 모아주는 함수입니다.
# 예: /items/?q=keyboard&skip=0&limit=10
async def common_parameters(
    q: Optional[str] = None,  # 검색어. 없으면 None
    skip: int = 0,            # 몇 개를 건너뛸지. 기본값 0
    limit: int = 100          # 최대 몇 개를 가져올지. 기본값 100
):
    # q, skip, limit 값을 하나의 딕셔너리로 묶어서 반환합니다.
    # 이 반환값이 Depends를 통해 API 함수의 commons 변수에 들어갑니다.
    return {"q": q, "skip": skip, "limit": limit}




# API 키가 올바른지 검사하는 의존성 함수입니다.
# 이 함수가 성공해야 보안 API가 실행됩니다.
async def verify_api_key(x_api_key: Optional[str] = None):
    # 현재 코드는 x_api_key를 쿼리 파라미터로 받습니다.
    # 예: /secure-data/?x_api_key=fakeapikey

    # API 키가 fakeapikey가 아니면 접근을 막습니다.
    if x_api_key != "fakeapikey":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    # 검증에 성공하면 API 키 값을 반환합니다.
    # 이 반환값이 Depends를 통해 api_key 변수에 들어갑니다.
    return x_api_key




# 관리자 접근 여부를 확인하는 의존성 함수입니다.
# 이 함수는 내부에서 verify_api_key를 먼저 실행합니다.
async def verify_admin_access(
    # verify_api_key가 먼저 실행되고,
    # 그 반환값이 api_key 변수에 들어옵니다.
    api_key: str = Depends(verify_api_key)
):
    # 여기까지 왔다는 것은 API 키 검증이 성공했다는 뜻입니다.
    print(f"관리자 접근 확인됨 (API 키: {api_key})")

    # 실제 서비스라면 여기서 사용자의 권한이 admin인지 추가로 검사합니다.
    # 지금은 예제이므로 관리자라고 가정합니다.
    return {"is_admin": True}




# ==============================
# API 엔드포인트
# ==============================


# 상품 목록 조회 API
@app.get("/items/")
async def read_items(
    # common_parameters 함수를 먼저 실행하고,
    # 그 반환값을 commons 변수에 넣어줍니다.
    commons: dict = Depends(common_parameters)
):
    print(f"요청 파라미터: {commons}")

    # 예제용 상품 데이터입니다.
    items_data = [
        {"item_name": "Item 1"},
        {"item_name": "Item 2"}
    ]

    # 공통 파라미터와 상품 데이터를 함께 응답합니다.
    return {
        "message": "Reading items",
        "params": commons,
        "data": items_data
    }



# 사용자 목록 조회 API
@app.get("/users/")
async def read_users(
    # /items/ API와 같은 common_parameters 의존성을 재사용합니다.
    commons: dict = Depends(common_parameters)
):
    print(f"요청 파라미터: {commons}")

    # 예제용 사용자 데이터입니다.
    users_data = [
        {"user_name": "User 1"},
        {"user_name": "User 2"}
    ]

    return {
        "message": "Reading users",
        "params": commons,
        "data": users_data
    }




# 보안 데이터 조회 API
@app.get("/secure-data/")
async def read_secure_data(
    # verify_api_key를 먼저 실행합니다.
    # API 키가 틀리면 HTTPException이 발생하고,
    # read_secure_data 함수는 실행되지 않습니다.
    api_key: str = Depends(verify_api_key)
):
    # 여기까지 왔다는 것은 API 키 검증이 성공했다는 뜻입니다.
    print(f"보안 데이터 접근 허용됨 (API 키: {api_key})")

    return {
        "message": "This is secure data!",
        "requester_api_key": api_key
    }




# 관리자 전용 데이터 조회 API
@app.get("/admin-only/")
async def read_admin_data(
    # verify_admin_access를 먼저 실행합니다.
    # verify_admin_access 내부에서는 verify_api_key도 먼저 실행됩니다.
    admin_info: dict = Depends(verify_admin_access)
):
    # admin_info에는 verify_admin_access의 반환값이 들어옵니다.
    # 예: {"is_admin": True}
    print(f"관리자 데이터 접근 허용됨: {admin_info}")

    return {
        "message": "Welcome, Admin!",
        "access_level": admin_info
    }