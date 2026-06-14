from fastapi import FastAPI

app = FastAPI()


#########################
# --- GET 요청 처리 ---
#########################

# 1. 루트 경로 ("/") GET 요청 처리
@app.get("/")
async def read_root():
    return {
        "message": "Hello World from Root Path!"
    }




# 2. "/items" 경로 GET 요청 처리
# 아이템 목록을 조회하는 API 예시
@app.get("/items")
async def read_items():
    
    # 실제로는 데이터베이스에서 가져오겠지만, 여기서는 예시 리스트를 반환
    sample_items = ["맥북 프로", "아이폰 15", "에어팟 맥스", "매직 키보드"]
    
    return {
        "items": sample_items
    }




# 3. "/info" 경로 GET 요청 처리 (단순 문자열 반환 예시)
@app.get("/info")
async def get_information():
    return "이것은 FastAPI 강의 예제 API의 정보입니다."

'''
이 블록은 클라이언트가 서버에 데이터를 조회하기 위해 보내는 GET 요청을 처리하는 부분입니다.

@app.get("/")는 루트 경로(/)로 요청이 들어왔을 때 실행되는 API입니다.
브라우저에서 기본 주소로 접속하면 "Hello World from Root Path!" 메시지를 JSON 형태로 응답합니다.

@app.get("/items")는 /items 경로로 요청이 들어왔을 때 실행됩니다.
예제에서는 실제 데이터베이스를 사용하지 않고, sample_items라는 임시 리스트를 만들어서 아이템 목록처럼 반환합니다.

@app.get("/info")는 /info 경로로 요청이 들어왔을 때 단순 문자열을 반환하는 예제입니다.
FastAPI에서는 딕셔너리뿐만 아니라 문자열도 응답으로 반환할 수 있습니다.

정리하면 이 GET 블록은 서버에서 데이터를 조회하거나 정보를 가져오는 API 예제들입니다.
'''


#########################
# --- POST 요청 처리 ---
#########################

# 4. "/items" 경로 POST 요청 처리
# 새로운 아이템을 생성하는 API 예시
@app.post("/items")
async def create_item():

    # 지금은 단순히 성공 메시지만 반환
    # 실제로는 요청 본문(body)에서 데이터를 받아 처리해야 함
    return {
        "message": "새로운 아이템이 성공적으로 생성되었습니다."
    }

'''
이 블록은 클라이언트가 서버에 새로운 데이터를 생성하기 위해 보내는 POST 요청을 처리하는 부분입니다.

@app.post("/items")는 /items 경로로 POST 요청이 들어왔을 때 create_item() 함수를 실행합니다.
현재 코드는 실제로 요청 데이터를 받아 저장하지는 않고, “새로운 아이템이 생성되었다”는 성공 메시지만 반환합니다.

실제 서비스라면 이 부분에서 사용자가 보낸 요청 본문, 즉 request body 데이터를 받아서 데이터베이스에 저장하게 됩니다.

정리하면 이 POST 블록은 새로운 아이템을 생성하는 API의 기본 형태를 보여주는 예제입니다.
'''


#########################
# --- PUT 요청 처리 ---
#########################

# 5. "/items/update-status" 경로 PUT 요청 처리
# 아이템 상태를 업데이트하는 API 예시
@app.put("/items/update-status")
async def update_item_status():
    
    # 지금은 단순히 업데이트되었다는 상태만 반환
    # 실제로는 어떤 아이템을 어떻게 업데이트할지 정보가 필요함
    return {
        "status": "아이템 상태가 업데이트되었습니다."
    }

'''
이 블록은 클라이언트가 서버에 기존 데이터를 수정하기 위해 보내는 PUT 요청을 처리하는 부분입니다.

@app.put("/items/update-status")는 /items/update-status 경로로 PUT 요청이 들어왔을 때 update_item_status() 함수를 실행합니다.
현재는 실제로 특정 아이템을 찾아 수정하지는 않고, 상태가 업데이트되었다는 메시지만 반환합니다.

실제 서비스라면 어떤 아이템을 수정할지 식별자 값이 필요하고, 어떤 값으로 변경할지에 대한 요청 데이터도 필요합니다.

정리하면 이 PUT 블록은 기존 아이템의 상태를 수정하는 API의 기본 형태를 보여주는 예제입니다.
'''


#########################
# --- DELETE 요청 처리 ---
#########################

# 6. "/items/clear-all" 경로 DELETE 요청 처리
# 모든 아이템을 삭제하는 API 예시
@app.delete("/items/clear-all")
async def delete_all_items():

    # 지금은 단순히 삭제되었다는 메시지만 반환
    return {
        "message": "모든 아이템이 삭제되었습니다."
    }

'''
이 블록은 클라이언트가 서버에 기존 데이터를 삭제하기 위해 보내는 DELETE 요청을 처리하는 부분입니다.

@app.delete("/items/clear-all")는 /items/clear-all 경로로 DELETE 요청이 들어왔을 때 delete_all_items() 함수를 실행합니다.
현재는 실제 데이터를 삭제하지 않고, 모든 아이템이 삭제되었다는 메시지만 반환합니다.

실제 서비스라면 이 부분에서 데이터베이스에 접근해서 특정 데이터나 전체 데이터를 삭제하는 로직이 들어가게 됩니다.

정리하면 이 DELETE 블록은 아이템 데이터를 삭제하는 API의 기본 형태를 보여주는 예제입니다.
'''