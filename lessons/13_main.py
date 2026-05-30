from fastapi import FastAPI, Response, Cookie, status
from typing import Optional

app = FastAPI()


# 응답 헤더에 커스텀 헤더를 추가하는 API
@app.get("/headers/set-custom")
async def set_custom_header(response: Response):
    # response.headers는 응답 헤더를 담고 있는 객체입니다.
    # 딕셔너리처럼 "헤더 이름" = "헤더 값" 형태로 추가할 수 있습니다.

    # X-Custom-Header-1이라는 이름의 커스텀 헤더를 응답에 추가
    response.headers["X-Custom-Header-1"] = "Hello from custom header!"

    # 또 다른 커스텀 헤더 추가
    response.headers["X-Another-Header"] = "FastAPI is awesome"

    # Server 헤더를 직접 지정하는 예시
    # 다만 실제 운영 환경에서는 서버/프록시 설정에 의해 덮어씌워질 수 있습니다.
    response.headers["Server"] = "My Custom FastAPI Server"

    # 응답 본문은 일반 JSON으로 반환
    # 헤더는 개발자 도구 Network 탭에서 확인할 수 있습니다.
    return {"message": "Check the response headers in your browser's developer tools!"}

'''
이 API는 응답에 커스텀 헤더를 추가하는 예제입니다.

핵심은 이 부분입니다.

response.headers["X-Custom-Header-1"] = "Hello from custom header!"

response.headers는 응답 헤더들을 담고 있는 객체입니다. 딕셔너리처럼 헤더 이름과 헤더 값을 넣을 수 있습니다.

즉 이 코드는 최종 응답에 아래와 같은 헤더를 추가합니다.

X-Custom-Header-1: Hello from custom header!
X-Another-Header: FastAPI is awesome
Server: My Custom FastAPI Server

응답 본문은 JSON으로 나가지만, 그 응답에 부가 정보로 헤더들이 같이 붙는 구조입니다.

브라우저에서 확인하려면 개발자 도구의 Network 탭에서 해당 요청을 클릭하고 Response Headers를 보면 됩니다.
'''


# 간단한 쿠키를 설정하는 API
@app.post("/cookies/set-simple")
async def set_simple_cookie(response: Response):

    # 서버가 브라우저에게 simple_cookie라는 쿠키를 저장하라고 지시합니다.
    # 실제 응답 헤더에는 Set-Cookie가 포함됩니다.
    response.set_cookie(key="simple_cookie", value="hello_fastapi")

    return {"message": "Simple cookie has been set. Close your browser and see if it persists!"}

'''
이 API는 브라우저에 간단한 쿠키를 저장시키는 예제입니다.

핵심은 이 부분입니다.

response.set_cookie(key="simple_cookie", value="hello_fastapi")

이 코드는 서버가 브라우저에게 이렇게 말하는 것과 같습니다.

simple_cookie라는 이름으로 hello_fastapi 값을 저장해둬.

실제 HTTP 응답에는 이런 헤더가 붙습니다.

Set-Cookie: simple_cookie=hello_fastapi

브라우저는 이 응답을 받으면 쿠키 저장소에 simple_cookie를 저장합니다.

그다음 같은 서버로 요청을 보낼 때 조건이 맞으면 브라우저가 쿠키를 자동으로 함께 보냅니다.
'''


# 여러 옵션이 들어간 쿠키를 설정하는 API
@app.post("/cookies/set-options")
async def set_cookie_with_options(response: Response):

    # user_session_id라는 쿠키를 설정합니다.
    # 로그인 세션 ID나 토큰을 쿠키에 저장하는 상황을 흉내 낸 예제입니다.
    response.set_cookie(
        key="user_session_id",          # 쿠키 이름
        value="abc123xyz789",           # 쿠키 값
        max_age=60 * 60 * 24 * 7,       # 쿠키 유지 시간: 60초 * 60분 * 24시간 * 7일 = 7일

        path="/",                       # 이 쿠키가 적용될 경로 
                                        # "/"이면 현재 도메인의 모든 경로 요청에 쿠키가 포함될 수 있습니다.

        # domain=".example.com",        # 쿠키를 적용할 도메인 
                                        # 지금은 주석 처리되어 있으므로 현재 도메인 기준으로 동작합니다.

        secure=True,                    # HTTPS 연결에서만 쿠키를 전송합니다. 
                                        # 로컬 http 테스트에서는 쿠키가 안 보이거나 안 보내질 수 있습니다.

        httponly=True,                  # JavaScript에서 document.cookie로 이 쿠키를 읽지 못하게 합니다. 
                                        # XSS로 인한 토큰 탈취 위험을 줄이는 데 사용합니다.

        samesite="lax"                  # 다른 사이트에서 오는 요청에 쿠키를 얼마나 허용할지 정합니다.
                                        # lax는 기본적인 보안과 사용성을 적당히 절충한 옵션입니다.
    )

    return {"message": "Cookie 'user_session_id' set with options!"}

'''
이 API는 user_session_id라는 쿠키를 더 자세한 옵션과 함께 설정합니다.

key는 쿠키 이름입니다.

key="user_session_id"

value는 쿠키에 저장할 값입니다.

value="abc123xyz789"

max_age는 쿠키가 얼마나 오래 유지될지 정합니다.

max_age=60 * 60 * 24 * 7

이건 7일을 의미합니다.

path="/"는 이 쿠키가 어떤 경로에 적용될지 정합니다. /로 설정하면 거의 전체 경로에서 이 쿠키가 사용될 수 있습니다.

secure=True는 HTTPS에서만 쿠키를 보내겠다는 뜻입니다. 그래서 로컬에서 HTTP로 테스트하면 쿠키가 제대로 안 보일 수 있습니다.

httponly=True는 JavaScript에서 이 쿠키를 읽지 못하게 합니다. 로그인 토큰이나 세션 ID 같은 민감한 값을 쿠키에 넣을 때 중요합니다.

samesite="lax"는 다른 사이트에서 오는 요청에 쿠키를 무작정 보내지 않도록 제한하는 설정입니다. CSRF 공격을 줄이는 데 도움을 줍니다.

즉, 이 API는 로그인 세션 쿠키를 설정하는 상황과 비슷한 예제입니다.
'''




# 클라이언트가 요청에 담아 보낸 쿠키를 읽는 API
@app.get("/cookies/get")
async def get_cookie_value(

    # Cookie(default=None)는 요청 쿠키 중 user_session_id 값을 꺼내옵니다.
    # 쿠키가 없으면 None이 들어갑니다.
    user_session_id: Optional[str] = Cookie(default=None)
):
    
    # 브라우저가 user_session_id 쿠키를 보내온 경우
    if user_session_id:
        print(f"Received user_session_id cookie: {user_session_id}")
        return {"cookie_value": user_session_id}
    
    # 브라우저가 해당 쿠키를 보내지 않은 경우
    else:
        print("user_session_id cookie not found.")
        return {"message": "Cookie 'user_session_id' not found in request."}
    
'''
이 API는 브라우저가 요청에 담아 보낸 쿠키를 서버에서 읽는 예제입니다.

핵심은 이 부분입니다.

user_session_id: Optional[str] = Cookie(default=None)

이 코드는 요청 쿠키 중에서 user_session_id라는 이름의 쿠키를 찾아서 user_session_id 변수에 넣습니다.

브라우저가 요청을 보낼 때 이런 쿠키를 함께 보내면:

Cookie: user_session_id=abc123xyz789

FastAPI는 이 값을 꺼내서 함수 매개변수에 넣어줍니다.

user_session_id = "abc123xyz789"

쿠키가 있으면 응답은 이렇게 됩니다.
{
  "cookie_value": "abc123xyz789"
}

쿠키가 없으면 None이 들어가고, 아래 응답이 나갑니다.
{
  "message": "Cookie 'user_session_id' not found in request."
}

즉, 이 API는 브라우저가 보낸 쿠키를 서버에서 확인하는 방법을 보여줍니다.
'''



# user_session_id 쿠키를 삭제하는 API
@app.delete("/cookies/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_cookie(response: Response):
    print("Deleting user_session_id cookie.")

    # 브라우저에게 user_session_id 쿠키를 삭제하라고 지시합니다.
    # 삭제할 때도 설정할 때와 path/domain 조건이 맞아야 제대로 삭제됩니다.
    response.delete_cookie(key="user_session_id", path="/", domain=None)

    # 204 No Content 응답은 본문이 없어야 하므로 None 반환
    return None

'''
이 API는 브라우저에 저장된 user_session_id 쿠키를 삭제시키는 예제입니다.

핵심은 이 부분입니다.

response.delete_cookie(key="user_session_id", path="/", domain=None)

이 코드는 서버가 브라우저에게 이렇게 말하는 것입니다.

user_session_id 쿠키 삭제해.

쿠키 삭제도 실제로는 응답 헤더를 통해 이루어집니다. 서버가 만료된 쿠키 정보를 보내면 브라우저가 해당 쿠키를 지웁니다.

status_code=status.HTTP_204_NO_CONTENT는 삭제가 성공했지만 응답 본문은 없다는 뜻입니다. 그래서 return None을 사용합니다.

주의할 점은 쿠키를 삭제할 때도 설정할 때의 path, domain 조건이 맞아야 합니다. 설정할 때 path="/"였다면 삭제할 때도 path="/"로 맞춰주는 게 좋습니다.
'''