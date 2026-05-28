from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field


app = FastAPI()




# --- 가상 데이터 ---
items_db = {1: {"name": "Keyboard"}, 2: {"name": "Mouse"}}




#################################
# --- 커스텀 예외 정의 ---
#################################

# 파이썬 기본 Exception을 상속받아 내가 직접 만든 에러 타입을 정의한다.
# 예를 들어 "유니콘 관련 에러"라는 특별한 에러를 만들고 싶을 때 사용한다.

class UnicornException(Exception):
    def __init__(self, name: str, message: str = "A unicorn related error occurred"):
        self.name = name        # 에러가 발생한 유니콘 이름
        self.message = message  # 에러 메시지

'''
이 블록은 내가 직접 만든 예외 타입을 정의하는 부분입니다.

파이썬에는 기본적으로 ValueError, TypeError, Exception 같은 예외가 있습니다.
그런데 서비스마다 직접 표현하고 싶은 에러가 있을 수 있습니다.

예를 들어 이 예제에서는 “유니콘 관련 에러”를 표현하기 위해 UnicornException이라는 예외를 직접 만들었습니다.

여기서 중요한 점은 UnicornException이 Exception을 상속받는다는 것입니다.

class UnicornException(Exception):

이렇게 하면 UnicornException도 파이썬 예외처럼 raise로 발생시킬 수 있습니다.

raise UnicornException(name="sparkle")

self.name과 self.message는 예외가 발생했을 때 핸들러에서 사용할 정보를 저장해두는 값입니다.

쉽게 말하면:
커스텀 예외는 “내 서비스에서만 쓰는 특별한 에러 종류를 직접 만드는 것”입니다.
'''

#################################
# --- 커스텀 예외 핸들러 등록 ---
#################################

# 예외 핸들러는 에러가 발생했을 때 클라이언트에게 어떤 상태 코드와 어떤 메시지를 응답할지 정해두는 코드입니다.

# UnicornException이 발생했을 때 FastAPI가 어떤 응답을 보내야 하는지 정하는 함수

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # UnicornException이 발생하면 이 핸들러가 실행됨
    # request: 현재 들어온 요청 정보
    # exc: 실제로 발생한 UnicornException 객체

    # JSONResponse를 사용해서 직접 JSON 응답을 만든다.
    return JSONResponse(
        status_code=418,
        content={
            "error_type": "Unicorn Error",
            "failed_item_name": exc.name,    # 예외 객체 안에 저장해둔 name 값 사용
            "message": exc.message,          # 예외 객체 안에 저장해둔 message 값 사용
            "request_url": str(request.url)  # 어떤 URL 요청에서 에러가 발생했는지 추가 정보로 반환
        },
    )
'''
이 블록은 UnicornException이 발생했을 때 어떤 응답을 보낼지 정하는 부분입니다.

핵심은 이 코드입니다.

@app.exception_handler(UnicornException)

이 뜻은:

앱 전체에서 UnicornException이 발생하면
unicorn_exception_handler 함수를 실행해라.

입니다.

예를 들어 아래 코드에서 UnicornException이 발생하면,

raise UnicornException(name="sparkle", message="Sparkle caused a rainbow overload!")

FastAPI는 기본 500 에러를 내보내지 않고, 우리가 등록한 핸들러를 실행합니다.

그 결과 응답은 이런 형태가 됩니다.
{
  "error_type": "Unicorn Error",
  "failed_item_name": "sparkle",
  "message": "Sparkle caused a rainbow overload!",
  "request_url": "http://127.0.0.1:8000/unicorns/sparkle"
}

여기서 exc.name은 발생한 예외 객체 안에 들어 있던 name 값입니다.
exc.message는 예외를 발생시킬 때 넣어준 메시지입니다.
request.url은 현재 요청 URL입니다.

쉽게 말하면:
커스텀 예외 핸들러는 “특정 에러가 발생했을 때 응답 모양을 내가 직접 정하는 함수”입니다.
'''


##############################################################
# --- 기본 RequestValidationError 핸들러 재정의 ---
##############################################################

# Pydantic 유효성 검사 실패 시 기본 422 응답 대신 커스텀 응답 반환

# FastAPI는 요청 데이터 검증에 실패하면 기본적으로 422 응답을 보낸다.
# 여기서는 그 기본 응답 모양을 직접 바꾼다.

# 예를 들어 Pydantic 모델에서 value > 10 조건을 걸었는데
# 클라이언트가 value=5를 보내면 RequestValidationError가 발생한다.

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    
    # exc.errors()는 검증 실패 상세 내용을 리스트 형태로 반환한다.
    # 예: 어떤 필드가 문제인지, 왜 실패했는지 등이 들어 있다.
    error_details = []
    for error in exc.errors():
        field = " -> ".join(map(str, error['loc'])) # 오류 발생 필드 위치
        message = error['msg']                      # 오류 메시지
        error_details.append(f"Field '{field}': {message}")

    # PlainTextResponse로 단순 텍스트 응답을 보낼 수도 있다.
    # 지금은 사용하지 않고 JSONResponse를 사용한다.
    # return PlainTextResponse(
    #     f"Validation Error(s): {'; '.join(error_details)}",
    #     status_code=status.HTTP_400_BAD_REQUEST
    # )

    # 검증 실패 시 기본 422 대신 400 Bad Request로 응답한다.
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,    
        content={
            "message": "Invalid input provided.",
            
            "details": exc.errors() # Pydantic이 제공하는 원본 검증 오류 상세 정보

            # 위에서 만든 사람이 읽기 쉬운 요약 메시지도 넣을 수 있다.
            # "simplified_details": error_details

        }
    )
'''
이 블록이 가장 헷갈릴 수 있습니다.

FastAPI는 Pydantic 검증에 실패하면 기본적으로 422 Unprocessable Entity 응답을 보냅니다.

예를 들어 아래 모델이 있죠.

class InputData(BaseModel):
    value: int = Field(gt=10)

이 뜻은 value가 반드시 10보다 커야 한다는 것입니다.

그런데 클라이언트가 이렇게 요청하면,

{
  "value": 5
}

5는 10보다 크지 않으므로 검증 실패입니다.
이때 FastAPI 내부에서 RequestValidationError가 발생합니다.

원래는 FastAPI가 기본 에러 응답을 보내는데, 이 코드에서는 그 기본 응답 방식을 바꿨습니다.

@app.exception_handler(RequestValidationError)

이 뜻은:

요청 데이터 검증 실패가 발생하면
FastAPI 기본 응답 대신 validation_exception_handler를 실행해라.

입니다.


그래서 기본 422 대신 이 코드에서는 400 Bad Request로 응답합니다.

status_code=status.HTTP_400_BAD_REQUEST

응답 내용도 직접 정합니다.

{
  "message": "Invalid input provided.",
  "details": [...]
}

여기서 exc.errors()는 Pydantic이 알려주는 검증 실패 상세 정보입니다.

정리하면:

RequestValidationError 핸들러 재정의는 “Pydantic 검증 실패 응답을 FastAPI 기본 모양이 아니라 내가 원하는 모양으로 바꾸는 것”입니다.
'''


#################################
# --- API 엔드포인트 정의 ---
#################################

# 1. HTTPException 사용 예제
@app.get("/items/{item_id}")
async def read_item(item_id: int):

    # 요청 예:
    # GET /items/1  -> 정상
    # GET /items/999 -> items_db에 없으므로 404 에러

    # item_id가 items_db 안에 없으면 직접 404 에러를 발생시킨다.
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,              # 상태 코드 지정
            detail=f"Item with ID {item_id} not found.",        # 오류 메시지 지정
            headers={"X-Error-Source": "Read Item Endpoint"},   # 커스텀 헤더 (선택)
        )
    
    # item_id가 존재하면 정상 데이터 반환
    return items_db[item_id]
'''
이 블록은 가장 실무에서 자주 보는 에러 처리 방식입니다.

/items/{item_id}로 요청이 들어오면 item_id를 받아서 items_db 안에 해당 데이터가 있는지 확인합니다.

예를 들어:

GET /items/1

이 요청은 items_db에 1이 있으므로 정상 응답을 반환합니다.

{
  "name": "Keyboard"
}

반대로:

GET /items/999

이 요청은 items_db에 999가 없으므로 아래 코드가 실행됩니다.

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Item with ID {item_id} not found.",
    headers={"X-Error-Source": "Read Item Endpoint"},
)

이 코드는 정상 응답을 중단하고, 바로 404 에러 응답을 발생시킵니다.

응답은 대략 이렇게 됩니다.

{
  "detail": "Item with ID 999 not found."
}

즉, HTTPException은 API 함수 안에서 특정 상황이 발생했을 때 직접 에러 응답을 보내는 방법입니다.
'''



# 2. 커스텀 예외 발생 예제
@app.get("/unicorns/{name}")
async def generate_unicorn_error(name: str):

    # 요청 예:
    # GET /unicorns/abc      -> 정상
    # GET /unicorns/sparkle  -> UnicornException 발생
    # GET /unicorns/invalid  -> ValueError 발생

    if name == "sparkle":
        # 특정 조건에서 커스텀 예외 발생
        # 직접 만든 UnicornException을 발생시킨다.
        # 그러면 위에서 등록한 unicorn_exception_handler가 실행된다.
        raise UnicornException(name=name, message="Sparkle caused a rainbow overload!")
    
    elif name == "invalid":
        # ValueError는 따로 핸들러를 등록하지 않았기 때문에
        # FastAPI의 기본 500 Internal Server Error로 처리된다.
        raise ValueError("This is an unhandled ValueError")
    
    return {"unicorn_name": name, "status": "ok"}
'''

이 블록은 커스텀 예외가 실제로 어떻게 발생하는지 보여주는 API입니다.

요청에 따라 결과가 달라집니다.

GET /unicorns/tom

이 경우 name이 "sparkle"도 아니고 "invalid"도 아니므로 정상 응답입니다.

{
  "unicorn_name": "tom",
  "status": "ok"
}

그런데:

GET /unicorns/sparkle

이 요청은 아래 조건에 걸립니다.

if name == "sparkle":

그래서 UnicornException을 발생시킵니다.

raise UnicornException(name=name, message="Sparkle caused a rainbow overload!")

그러면 FastAPI는 위에서 등록한 이 핸들러를 실행합니다.

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(...)

결과적으로 직접 만든 JSON 에러 응답이 나갑니다.

반면:

GET /unicorns/invalid

이 요청은 ValueError를 발생시킵니다.

raise ValueError("This is an unhandled ValueError")

하지만 이 코드에는 ValueError 전용 예외 핸들러가 없습니다.
그래서 FastAPI는 이 에러를 처리하지 못한 서버 내부 오류로 보고 일반적으로 500 Internal Server Error를 반환합니다.

즉, 이 블록은 처리할 핸들러가 있는 예외와, 핸들러가 없는 예외의 차이를 보여줍니다.

----------------------------------------------------
name이 sparkle이면:
    내가 만든 UnicornException 에러를 발생시켜라.
    그러면 UnicornException 전용 핸들러가 응답한다.

name이 invalid이면:
    일반 ValueError를 발생시켜라.
    그런데 이건 전용 핸들러가 없으니 서버 에러가 된다.

둘 다 아니면:
    정상 응답을 반환한다.
----------------------------------------------------

----------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------

1. /unicorns/abc 요청 흐름

요청:
GET /unicorns/abc

실행 흐름:
1. 클라이언트가 /unicorns/abc 요청
2. FastAPI가 URL에서 abc를 꺼냄
3. name 변수에 "abc"를 넣음
4. generate_unicorn_error(name="abc") 실행
5. if name == "sparkle" 검사 → false
6. elif name == "invalid" 검사 → false
7. 마지막 return 실행
8. 정상 JSON 응답 반환

실제 코드 흐름은 이렇게 됩니다.

name = "abc"

if name == "sparkle":
    raise UnicornException(...)

elif name == "invalid":
    raise ValueError(...)

return {"unicorn_name": name, "status": "ok"}


결과 응답:
{
  "unicorn_name": "abc",
  "status": "ok"
}

즉, abc는 특별한 에러 조건에 걸리지 않으므로 정상 응답이 나갑니다.

-------------------------------------------------------------------

2. /unicorns/sparkle 요청 흐름

요청:
GET /unicorns/sparkle

실행 흐름:
1. 클라이언트가 /unicorns/sparkle 요청
2. FastAPI가 URL에서 sparkle을 꺼냄
3. name 변수에 "sparkle"을 넣음
4. generate_unicorn_error(name="sparkle") 실행
5. if name == "sparkle" 검사 → true
6. UnicornException 발생
7. 함수 실행이 즉시 중단됨
8. FastAPI가 UnicornException 전용 핸들러를 찾음
9. unicorn_exception_handler 실행
10. 커스텀 JSON 에러 응답 반환

핵심은 이 부분입니다.

if name == "sparkle":
    raise UnicornException(
        name=name,
        message="Sparkle caused a rainbow overload!"
    )

raise가 실행되는 순간, 아래 코드는 더 이상 실행되지 않습니다.

elif name == "invalid":
    ...
    
return {"unicorn_name": name, "status": "ok"}

즉, return {"unicorn_name": name, "status": "ok"}까지 가지 않습니다.

대신 이 예외 핸들러로 이동합니다.

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "error_type": "Unicorn Error",
            "failed_item_name": exc.name,
            "message": exc.message,
            "request_url": str(request.url)
        },
    )

여기서 exc에는 방금 발생한 UnicornException 객체가 들어옵니다.

즉:
exc.name 은 "sparkle"이고,
exc.message 는 "Sparkle caused a rainbow overload!"입니다.

결과 응답은 대략 이렇게 됩니다.

{
  "error_type": "Unicorn Error",
  "failed_item_name": "sparkle",
  "message": "Sparkle caused a rainbow overload!",
  "request_url": "http://127.0.0.1:8000/unicorns/sparkle"
}

상태 코드는 418입니다.

정리하면:
/unicorns/sparkle 요청은 정상 응답이 아니라, 
직접 만든 UnicornException을 발생시키고, 
그 예외를 커스텀 핸들러가 받아서 커스텀 에러 응답을 반환합니다.

-------------------------------------------------------------------

3. /unicorns/invalid 요청 흐름

요청:
GET /unicorns/invalid

실행 흐름:
1. 클라이언트가 /unicorns/invalid 요청
2. FastAPI가 URL에서 invalid를 꺼냄
3. name 변수에 "invalid"를 넣음
4. generate_unicorn_error(name="invalid") 실행
5. if name == "sparkle" 검사 → false
6. elif name == "invalid" 검사 → true
7. ValueError 발생
8. 함수 실행이 즉시 중단됨
9. 그런데 ValueError 전용 예외 핸들러가 없음
10. FastAPI는 처리되지 않은 서버 에러로 판단
11. 보통 500 Internal Server Error 응답 반환

실제 걸리는 코드는 이 부분입니다.

elif name == "invalid":
    raise ValueError("This is an unhandled ValueError")

여기서도 raise가 실행되는 순간 함수는 중단됩니다.

그런데 차이가 있습니다.

UnicornException은 전용 핸들러가 있었습니다. -> @app.exception_handler(UnicornException)

하지만 ValueError는 전용 핸들러가 없습니다.

즉, FastAPI 입장에서는:

UnicornException은 어떻게 응답할지 알고 있음
ValueError는 따로 정해둔 응답 방식이 없음

그래서 일반적으로 서버 내부 오류인 500 Internal Server Error로 처리됩니다.

정리하면:
/unicorns/invalid 요청은 ValueError를 발생시키지만, 이 예외를 처리할 핸들러가 없기 때문에 서버 내부 오류처럼 처리됩니다.
'''



# 3. 유효성 검사 오류 발생 예제 (RequestValidationError 재정의 테스트용)
# 요청 body의 value는 반드시 10보다 커야 한다.
# value가 10 이하이면 Pydantic 검증 실패가 발생한다.
class InputData(BaseModel):
    value: int = Field(gt=10)  


@app.post("/validate/")
async def validate_endpoint(data: InputData):

    # 요청 body 예:
    # {"value": 20} -> 정상
    # {"value": 5}  -> RequestValidationError 발생

    # 검증을 통과한 경우에만 이 함수 내부가 실행된다.
    return {"message": "Data is valid!", "received_value": data.value}
'''
이 블록은 요청 본문 검증 실패가 발생하는 상황을 보여주는 API입니다.

InputData 모델은 요청 본문에 value라는 숫자값이 들어와야 하고, 그 값은 반드시 10보다 커야 한다고 정의합니다.

정상 요청은 이런 형태입니다.

{
  "value": 20
}

이 경우 검증을 통과하므로 validate_endpoint() 함수가 실행되고 정상 응답을 반환합니다.

{
  "message": "Data is valid!",
  "received_value": 20
}

하지만 이런 요청은 실패합니다.

{
  "value": 5
}

5는 10보다 크지 않기 때문에 Pydantic 검증에 실패합니다.
그러면 validate_endpoint() 함수 내부는 실행되지 않습니다.

대신 RequestValidationError가 발생하고, 위에서 재정의한 핸들러가 실행됩니다.

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(...)

그래서 응답은 기본 422가 아니라, 우리가 만든 400 응답 형태로 나갑니다.
'''