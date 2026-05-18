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



@app.post("/items")
async def create_item():
    return {"message": "새로운 아이템이 성공적으로 생성되었습니다."}



@app.put("/items/update-status")
async def update_item_status():
    return {"status": "아이템 상태가 업데이트되었습니다."}



@app.delete("/items/clear-all")
async def delete_all_items():
    return {"message": "모든 아이템이 삭제되었습니다."}