from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World from Root Path!"}

@app.get("/items")
async def read_items():
    sample_items = ["맥북 프로", "아이폰 15", "에어팟 맥스", "매직 키보드"]
    return {"items": sample_items}

@app.get("/info")
async def get_information():
    return "이것은 FastAPI 강의 예제 API의 정보입니다."

