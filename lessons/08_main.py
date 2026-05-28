import time, asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#####################################
# --- CORS 미들웨어 설정 ---
#####################################

# 웹 브라우저에서 실행되는 프론트엔드 Javascript 코드로부터의 요청을 허용하기 위함


# 허용할 출처(origin) 목록 - 실제 환경에서는 '*' 대신 구체적인 도메인 명시 권장
origins = [
    "http://localhost",       # 예: 로컬 개발 환경
    "http://localhost:3000",  # 예: React 개발 서버 포트
    "http://localhost:8080",  # 예: Vue 개발 서버 포트
    # "https://your-frontend-domain.com", # 실제 서비스 도메인 추가
]

# app.add_middleware를 사용하여 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # origins 목록에 있는 출처의 요청만 허용
    allow_credentials=True,     # 요청 시 쿠키/인증 정보 포함 허용 여부
    allow_methods=["*"],        # 허용할 HTTP 메서드 (GET, POST, PUT 등 모두 허용)
    allow_headers=["*"]         # 허용할 HTTP 요청 헤더 (모든 헤더 허용)
)
'''
이 블록은 FastAPI 백엔드에 요청을 보낼 수 있도록 허용할 프론트엔드 주소 목록을 정하는 부분입니다.

예를 들어 React 개발 서버는 보통 http://localhost:3000에서 실행되고, Vue 개발 서버는 http://localhost:8080에서 실행되는 경우가 많습니다.

브라우저는 보안상 다른 출처에서 API 요청을 보내는 것을 기본적으로 제한합니다.
그래서 FastAPI 서버가 “이 주소에서 오는 요청은 허용해도 된다”라고 알려줘야 합니다.

이 허용 목록이 바로 origins입니다.

쉽게 말하면:

localhost:3000에서 실행 중인 React 앱은 내 FastAPI API에 요청해도 된다.
localhost:8080에서 실행 중인 Vue 앱도 요청해도 된다.

이런 의미입니다.
'''



#####################################
# --- 커스텀 미들웨어 정의 ---
#####################################

# 모든 HTTP 요청에 대해 처리 시간을 측정하고 응답 헤더에 추가하는 미들웨어


# HTTP 요청/응답 사이클에 적용될 미들웨어임을 명시
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    
    # 1. 요청 처리 전 로직 (선택 사항)
    start_time = time.time()
    print(f"Request received: {request.method} {request.url.path}")

    # 2. 다음 미들웨어 또는 경로 작동 함수 호출 (필수!)
    # call_next 함수는 다음 처리 단계(다른 미들웨어 또는 실제 엔드포인트 함수)로 요청을 전달하고,
    # 그 결과를 (Response 객체) 받아옵니다. 반드시 await 해주어야 합니다.
    response = await call_next(request)

    # 3. 응답 처리 후 로직 (선택 사항)
    process_time = time.time() - start_time

    # 응답 헤더에 'X-Process-Time' 이라는 커스텀 헤더 추가
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(f"Response sent. Process time: {process_time:.4f} sec")

    # 4. 최종 응답 반환 (필수!)
    return response
'''
이 블록은 직접 만든 커스텀 미들웨어입니다.

@app.middleware("http")는 모든 HTTP 요청에 대해 이 함수를 미들웨어로 실행하겠다는 의미입니다.

요청이 들어오면 먼저 이 함수가 실행됩니다.
start_time = time.time()

여기서 요청 시작 시간을 기록합니다.
print(f"Request received: {request.method} {request.url.path}")

이 코드는 요청 메서드와 요청 경로를 출력합니다.

예를 들어 /ping으로 GET 요청이 들어오면 이런 식으로 로그가 찍힙니다.
Request received: GET /ping

그다음 핵심은 이 부분입니다.
response = await call_next(request)

call_next(request)는 요청을 다음 단계로 넘기는 코드입니다.
다음 단계는 다른 미들웨어일 수도 있고, 실제 API 엔드포인트 함수일 수도 있습니다.

즉, 이 코드가 실행되어야 /, /ping 같은 실제 API 함수가 실행됩니다.

그 후 API 응답이 만들어지면 다시 미들웨어로 돌아옵니다.
process_time = time.time() - start_time

요청 시작 시간과 현재 시간의 차이를 계산해서 전체 처리 시간을 구합니다.

response.headers["X-Process-Time"] = f"{process_time:.4f}"

응답 헤더에 X-Process-Time이라는 값을 추가합니다.
이걸 보면 해당 요청을 처리하는 데 몇 초가 걸렸는지 확인할 수 있습니다.

마지막으로:
return response

최종 응답을 클라이언트에게 반환합니다.

이 블록의 전체 흐름은 이렇게 보면 됩니다.

요청 들어옴
→ 시작 시간 기록
→ 요청 로그 출력
→ 실제 API 함수 실행
→ 처리 시간 계산
→ 응답 헤더에 처리 시간 추가
→ 응답 반환
'''


#####################################
# --- 간단한 API 엔드포인트 정의 ---
#####################################


@app.get("/")
async def read_root():
    # 미들웨어가 이 함수 실행 전후로 작동합니다.
    # CORS 설정에 따라 다른 출처의 프론트엔드에서 호출 가능합니다.
    return {"message": "Hello World with Middleware and CORS!"}
'''
이 블록은 / 경로로 GET 요청이 들어왔을 때 실행되는 기본 API입니다.

브라우저나 Swagger에서 / 주소로 요청하면 메시지를 JSON 형태로 반환합니다.

중요한 점은 이 API도 미들웨어의 영향을 받는다는 것입니다.

즉, / 요청이 들어오면 바로 read_root()가 실행되는 것이 아니라, 먼저 커스텀 미들웨어가 실행됩니다.

흐름은 이렇게 됩니다.

GET /
→ add_process_time_header 미들웨어 실행
→ read_root 함수 실행
→ 응답 생성
→ 미들웨어에서 처리 시간 헤더 추가
→ 최종 응답 반환
'''

@app.get("/ping")
async def ping():
    # 간단한 health check 또는 테스트용 엔드포인트
    # 역시 미들웨어와 CORS의 영향을 받습니다.
    # 잠시 지연을 주어 처리 시간 헤더 확인 (예시)
    await asyncio.sleep(0.1)
    return {"message": "pong"}
'''
이 블록은 /ping 경로로 GET 요청이 들어왔을 때 실행되는 테스트용 API입니다.

보통 /ping은 서버가 살아있는지 확인하는 간단한 health check 용도로 자주 사용합니다.

여기서는 일부러 아래 코드를 넣었습니다.
await asyncio.sleep(0.1)

이 코드는 0.1초 동안 비동기적으로 기다리게 합니다.
그래서 미들웨어에서 측정한 X-Process-Time 값을 확인하기 좋습니다.

예상 응답 본문은 이렇게 됩니다.
{
  "message": "pong"
}

그리고 응답 헤더에는 대략 이런 값이 추가됩니다.

X-Process-Time: 0.1000

정확한 값은 실행 환경에 따라 조금씩 달라질 수 있습니다.
'''


'''
예시 1. 사용자가 /ping API를 호출하는 경우

브라우저나 Swagger에서 이렇게 요청한다고 해볼게요.
GET http://127.0.0.1:8000/ping
그러면 바로 ping() 함수가 실행되는 게 아닙니다.

실제 흐름은 이렇게 됩니다.

GET /ping 요청 들어옴
→ CORS 미들웨어 통과
→ 커스텀 미들웨어 실행
→ start_time 기록
→ 요청 로그 출력
→ call_next(request) 실행
→ 실제 /ping API 함수 실행
→ asyncio.sleep(0.1) 대기
→ {"message": "pong"} 응답 생성
→ 다시 커스텀 미들웨어로 돌아옴
→ 처리 시간 계산
→ 응답 헤더에 X-Process-Time 추가
→ 최종 응답 반환

-------------------------------------------------------------------------------

1. 요청이 들어오면 미들웨어가 먼저 실행됨

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

/ping 요청이 들어오면 FastAPI가 이 미들웨어를 먼저 실행합니다.

여기서 request에는 현재 요청 정보가 들어 있습니다.

예를 들면:
request.method → GET
request.url.path → /ping

-------------------------------------------------------------------------------

2. 요청 처리 시작 시간을 기록함
start_time = time.time()
print(f"Request received: {request.method} {request.url.path}")

이 코드가 실행되면 서버 터미널에 이런 로그가 찍힙니다.

Request received: GET /ping

아직 /ping 함수는 실행되지 않았습니다.
지금은 미들웨어 안에서 요청을 먼저 가로채서 보고 있는 상태입니다.

-------------------------------------------------------------------------------

3. 실제 API 함수로 요청을 넘김
response = await call_next(request)

이 줄이 핵심입니다.

call_next(request)는 쉽게 말해서:

이제 다음 단계로 요청을 넘겨줘.
즉, 실제 /ping API 함수를 실행해줘.

라는 뜻입니다.

그래서 이 줄에서 실제로 아래 함수가 실행됩니다.

@app.get("/ping")
async def ping():
    await asyncio.sleep(0.1)
    return {"message": "pong"}

-------------------------------------------------------------------------------

4. /ping 함수 내부 실행

await asyncio.sleep(0.1)

이건 0.1초 동안 기다리는 코드입니다.
다만 time.sleep(0.1)처럼 서버 전체를 멈추는 게 아니라, 
이 요청만 잠깐 기다리게 하고 서버는 다른 요청을 처리할 수 있는 상태로 둡니다.

그다음 응답을 만듭니다.

return {"message": "pong"}

이 응답이 만들어지면 다시 미들웨어의 이 줄로 돌아옵니다.

response = await call_next(request)

이제 response 변수에는 /ping API가 만든 응답이 들어 있습니다.

-------------------------------------------------------------------------------

5. 미들웨어가 응답에 처리 시간을 추가함

process_time = time.time() - start_time
response.headers["X-Process-Time"] = f"{process_time:.4f}"

처음 요청이 들어온 시간부터 응답이 만들어진 시간까지 계산합니다.

/ping 안에 await asyncio.sleep(0.1)이 있었으니까 대략 0.1초 근처가 나옵니다.

응답 헤더에는 이런 값이 추가됩니다.

X-Process-Time: 0.1008

-------------------------------------------------------------------------------

6. 최종 응답 반환

return response

마지막으로 미들웨어가 수정한 응답을 클라이언트에게 돌려줍니다.

최종 응답 body는 이렇습니다.
{
  "message": "pong"
}

그리고 응답 header에는 이런 값이 추가되어 있습니다.

X-Process-Time: 0.1008
'''