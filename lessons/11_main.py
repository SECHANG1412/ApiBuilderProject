from fastapi import FastAPI, status
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    JSONResponse,
)


app = FastAPI()


###################################################
# --- 다양한 Response 클래스 사용 예제 ---
###################################################

# 1. HTML 응답 반환하기
# response_class를 HTMLResponse로 지정
@app.get("/html", response_model=HTMLResponse)
async def read_html():
    html_content = """
    <html>
        <head>
            <title>FastAPI HTML Response</title>
            <style>
                body { font-family: sans-serif; }
                h1 { color: green; }
            </style>
        </head>
        <body>
            <h1>Hello from FastAPI! 👋</h1>
            <p>This is an HTML response.</p>
        </body>
    </html>
    """
    # HTML 문자열을 직접 반환하면 response_class에 의해 HTMLResponse로 변환됨
    return html_content
'''
이 API는 /html로 요청이 들어오면 HTML 문서를 반환합니다.

여기서 중요한 부분은 이겁니다.

response_class=HTMLResponse

이 설정 때문에 함수에서 문자열을 반환하더라도 FastAPI는 이 문자열을 일반 텍스트가 아니라 HTML 문서로 응답합니다.

그래서 브라우저에서 /html에 접속하면 JSON이 아니라 실제 웹페이지처럼 보입니다.
'''


# 2. PlainText 응답 반환하기
@app.get("/text")
async def read_text():
    # PlainTextResponse 객체를 직접 생성하여 반환
    return PlainTextResponse(content="This is a plain text response from FastAPI.", status_code=200)
'''
이 API는 일반 텍스트 응답을 직접 만들어서 반환합니다.

응답 본문은 그냥 이 문자열입니다.

This is a plain text response from FastAPI.

JSON도 아니고 HTML도 아닙니다.
브라우저나 클라이언트에게 “이건 그냥 순수 텍스트야”라고 보내는 방식입니다.
'''


# 3. Redirect 응답 반환하기
@app.get("/redirect/docs")
async def redirect_to_docs():
    # /docs 경로로 리디렉션 (307 Temporary Redirect)
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
'''
이 API는 /redirect/docs로 요청이 오면 사용자를 /docs로 이동시킵니다.

흐름은 이렇게 됩니다.

GET /redirect/docs 요청
→ 서버가 /docs로 이동하라고 응답
→ 브라우저가 /docs로 이동

즉, 이 API는 직접 데이터를 보여주는 게 아니라 다른 주소로 보내는 역할을 합니다.
'''

@app.get("/redirect/external")
async def redirect_external():
    # 외부 URL로 리디렉션 (302 Found - 임시 리디렉션의 일반적인 코드)
    return RedirectResponse(url="<https://fastapi.tiangolo.com/>", status_code=status.HTTP_302_FOUND)
'''
이 API는 사용자를 외부 사이트로 이동시킵니다.

예를 들어 /redirect/external에 접속하면 FastAPI 공식 문서 사이트로 이동합니다.

302 Found는 임시 리디렉션에서 자주 쓰이는 상태 코드입니다.
'''


# 4. JSONResponse 명시적 사용 (기본 동작과 유사하지만, 직접 제어 가능)
# response_class 사용 예시
@app.get("/json/custom", response_class=JSONResponse) 
async def read_custom_json():
    # 딕셔너리를 반환하면 response_class에 의해 JSONResponse로 변환됨
    return {"message": "This is a custom JSON response using response_class"}
'''
이 API는 JSON 응답을 반환합니다.

사실 FastAPI는 딕셔너리를 반환하면 기본적으로 JSON으로 바꿔주기 때문에, 이 예제는 기본 동작과 거의 비슷합니다.

즉 아래처럼 써도 기본적으로 JSON 응답입니다.

return {"message": "hello"}

하지만 response_class=JSONResponse를 쓰면 이 API가 JSON 응답이라는 것을 명시적으로 보여줄 수 있습니다.
'''

@app.post("/json/created", status_code=status.HTTP_201_CREATED)
async def create_resource():
    # JSONResponse를 직접 반환하여 상태 코드 등을 명시적으로 제어
    return JSONResponse(
        content={"resource_id": 123, "status": "created"},
        status_code=status.HTTP_201_CREATED
    )
'''
이 API는 리소스 생성 성공 응답을 직접 만듭니다.

JSONResponse를 직접 반환하면 응답 내용과 상태 코드를 더 명시적으로 제어할 수 있습니다.

응답 본문은 이렇게 나갑니다.

{
  "resource_id": 123,
  "status": "created"
}

상태 코드는 201 Created입니다.

다만 여기서는 데코레이터에도 status_code=201이 있고, JSONResponse에도 status_code=201이 있어서 중복입니다.
직접 JSONResponse를 반환할 거면 JSONResponse의 상태 코드가 실제 응답에 사용된다고 보면 됩니다.
'''


# 5. response_class와 Response 객체 직접 반환 혼용 시
# 기본은 PlainText
@app.get("/mixed-response", response_class=PlainTextResponse)
async def mixed_response(return_html: bool = False):
    if return_html:
        # HTMLResponse 객체를 직접 반환하면 response_class보다 우선함
        return HTMLResponse("<h1>This is HTML overriding PlainText</h1>")
    else:
        # 문자열만 반환하면 response_class(PlainTextResponse)가 적용됨
        return "This is the default PlainText response."
'''
이 API는 조금 중요합니다.

기본 응답 형식은 PlainTextResponse입니다.

response_class=PlainTextResponse

그래서 아래처럼 문자열만 반환하면 일반 텍스트로 응답합니다.

return "This is the default PlainText response."

요청:
GET /mixed-response

응답:
This is the default PlainText response.

그런데 쿼리 파라미터로 return_html=true를 보내면:

GET /mixed-response?return_html=true

이 조건에 걸립니다.

if return_html:
    return HTMLResponse("<h1>This is HTML overriding PlainText</h1>")

이때는 response_class=PlainTextResponse보다 직접 반환한 HTMLResponse가 우선합니다.

즉, 기본값은 PlainText지만, 상황에 따라 HTMLResponse로 덮어쓸 수 있다는 예제입니다.
'''