from fastapi import FastAPI 
# FastAPI 클래스를 가져옵니다.

app = FastAPI() 
# FastAPI 애플리케이션 인스턴스를 생성합니다.


# 경로 "/"로 GET 요청이 오면 아래 함수를 실행합니다.
@app.get("/")
async def read_root():  # 비동기 함수로 정의합니다.
    return { "message": "Hello World"} # 딕셔너리 형태의 데이터를 반환합니다. FastAPI가 자동으로 JSON 응답으로 변환해줍니다.

"""
/ 경로로 GET 요청이 들어왔을 때 실행될 API 함수를 정의하는 부분입니다.
사용자가 http://127.0.0.1:8000/ 같은 기본 주소로 접속하면 read_root() 함수가 실행되고, 
{"message": "Hello World"}라는 딕셔너리를 반환합니다. FastAPI는 이 딕셔너리를 자동으로 JSON 응답으로 변환해줍니다.
"""