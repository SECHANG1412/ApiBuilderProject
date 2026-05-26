from fastapi import FastAPI 
# FastAPI 클래스를 가져옵니다.

app = FastAPI() 
# FastAPI 애플리케이션 인스턴스를 생성합니다.


# 경로 "/"로 GET 요청이 오면 아래 함수를 실행합니다.
@app.get("/")
async def read_root():  # 비동기 함수로 정의합니다.
    return { "message": "Hello World"} # 딕셔너리 형태의 데이터를 반환합니다. FastAPI가 자동으로 JSON 응답으로 변환해줍니다.