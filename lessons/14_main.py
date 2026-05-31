import os
import shutil
from typing import List, Optional
import aiofiles
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form


app = FastAPI()



UPLOAD_DIR = "./uploads"                # 업로드된 파일을 저장할 서버 내부 폴더 경로
os.makedirs(UPLOAD_DIR, exist_ok=True)  # uploads 폴더가 없으면 새로 만들고, 이미 있으면 에러 없이 그대로 사용합니다.

'''
이 블록은 업로드된 파일을 저장할 폴더를 준비하는 부분입니다.

UPLOAD_DIR = "./uploads"는 서버 프로젝트 안에 uploads라는 폴더를 파일 저장소로 사용하겠다는 뜻입니다.

os.makedirs(UPLOAD_DIR, exist_ok=True)는 해당 폴더가 없으면 새로 만듭니다. 이미 폴더가 있으면 에러를 내지 않고 그냥 넘어갑니다.

즉, 서버를 실행할 때 업로드 폴더가 없어서 파일 저장이 실패하는 상황을 미리 방지하는 코드입니다.
'''



##########################################
# --- 파일 업로드 엔드포인트 정의 ---
##########################################


# 1. 작은 파일 업로드
# bytes 방식은 업로드된 파일 전체를 한 번에 메모리에 올립니다.
# 그래서 아주 작은 파일을 받을 때는 간단하지만,
# 큰 파일을 받으면 메모리 부담이 커질 수 있습니다.
@app.post("/files/upload-bytes/")
async def upload_small_files(
    # File(...)은 이 값이 일반 JSON Body가 아니라 multipart/form-data로 업로드되는 파일이라는 것을 FastAPI에게 알려줍니다.
    # 타입이 bytes이므로, FastAPI는 업로드된 파일의 전체 내용을 file 변수에 bytes 형태로 넣어줍니다.
    file: bytes = File(..., description="Upload a small file ad bytes")
):
    # bytes는 len()으로 파일 크기를 확인할 수 있습니다.
    file_size = len(file)
    
    print(f"Received small file (bytes), size: {file_size} bytes")
    
    # 1MB보다 큰 파일이면 bytes 방식으로 처리하기에는 부담이 있을 수 있다는 경고
    if file_size > 1024 * 1024:
        print("Warning: File size is large for 'bytes' handling.")
    
    # 이 방식은 파일을 저장하지 않고, 파일 크기만 확인해서 응답합니다.
    return {"file_size": file_size, "message": "File received as bytes."}

'''
이 API는 업로드된 파일을 bytes로 받습니다.

여기서 핵심은 이 부분입니다.

file: bytes = File(...)

이렇게 쓰면 FastAPI는 업로드된 파일의 전체 내용을 한 번에 읽어서 file 변수에 넣습니다. 
즉, file 안에는 파일의 내용 전체가 bytes 형태로 들어갑니다.

예를 들어 아주 작은 텍스트 파일이나 작은 이미지라면 이 방식도 간단합니다. 
len(file)로 바로 파일 크기를 알 수 있습니다.

하지만 큰 파일에는 좋지 않습니다. 왜냐하면 파일 전체를 메모리에 한 번에 올리기 때문입니다.

예를 들어 200MB 파일을 업로드하면, 서버는 그 파일 전체를 메모리에 올려야 합니다. 
사용자가 여러 명이면 메모리 부담이 더 커집니다.

그래서 이 방식은 작은 파일을 간단히 받아서 크기만 확인하거나 바로 처리할 때 사용하는 방식으로 이해하면 됩니다.
'''



# 2. 단일 파일 업로드
# UploadFile 방식은 파일 업로드에서 더 권장되는 방식입니다.
# 파일명, 콘텐츠 타입 같은 메타데이터를 확인할 수 있고, 파일을 조금씩 읽어서 저장할 수 있습니다.
@app.post("/files/upload-single/")
async def upload_single_file(
    # UploadFile은 업로드된 파일을 다루기 위한 FastAPI의 파일 객체입니다.
    # file.filename, file.content_type, await file.read() 등을 사용할 수 있습니다.
    file: UploadFile = File(..., description="Upload a single file using UploadFile")
):
    print(f"Received file: {file.filename}")
    print(f"Content type: {file.content_type}")


    # 사용자가 보낸 파일명에는 경로 조작 문자가 들어갈 수 있습니다. -> 예: ../../danger.py
    # os.path.basename()은 경로를 제거하고 순수 파일명만 남깁니다.
    # 보안상 최소한의 방어입니다.
    safe_filename = os.path.basename(file.filename or "uploaded_file")

    # 서버에 저장할 최종 경로를 만듭니다.
    # 예: ./uploads/profile.png
    destination = os.path.join(UPLOAD_DIR, safe_filename)

    print(f"Saving file to: {destination}")

    try:
        # aiofiles.open()은 비동기 방식으로 파일을 열기 위한 도구입니다.
        # 'wb'는 write binary, 즉 바이너리 파일 쓰기 모드입니다.
        async with aiofiles.open(destination, 'wb') as out_file:
            # await file.read(1024 * 1024)는 파일을 한 번에 1MB씩 읽습니다.
            # 파일 전체를 한 번에 메모리에 올리지 않고, 조각 단위로 읽어서 저장하기 때문에 큰 파일 처리에 더 안전합니다.
            while content := await file.read(1024 * 1024):
                # 읽은 조각을 서버 파일에 씁니다.
                await out_file.write(content)
    except Exception as e:
        # 저장 중 문제가 생기면 서버 에러를 반환합니다.
        print(f"File saving error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {e}")
    finally:
        # 업로드 파일 객체를 닫아 리소스를 정리합니다.
        await file.close()

    # 저장이 성공한 경우에만 여기까지 내려옵니다.
    return {"filename": file.filename, "content_type": file.content_type, "save_path": destination}

'''
이 API는 업로드된 파일 하나를 UploadFile로 받습니다.

UploadFile은 파일 업로드에서 권장되는 방식입니다. 
bytes와 달리 파일 전체를 무조건 한 번에 메모리에 올리는 방식이 아니라, 파일을 조금씩 읽어서 처리할 수 있습니다.

file.filename은 클라이언트가 올린 원래 파일명입니다. 예를 들어 profile.png 같은 값입니다.
file.content_type은 파일의 MIME 타입입니다. 예를 들어 이미지 PNG라면 image/png, PDF라면 application/pdf처럼 들어올 수 있습니다.


safe_filename = os.path.basename(file.filename or "uploaded_file")

이 코드는 파일명에서 경로 부분을 제거합니다. 사용자가 악의적으로 ../../danger.py 같은 파일명을 보냈을 때 그대로 저장하면 위험할 수 있습니다. 
os.path.basename()을 쓰면 경로를 제거하고 마지막 파일명만 남깁니다.


destination = os.path.join(UPLOAD_DIR, safe_filename)

이 코드는 업로드 폴더와 파일명을 합쳐서 저장 경로를 만듭니다.

예를 들어:
UPLOAD_DIR = "./uploads"
safe_filename = "profile.png"

이면:
destination = "./uploads/profile.png"

가 됩니다.

[1MB씩 읽어서 저장하는 부분]
async with aiofiles.open(destination, 'wb') as out_file:
    while content := await file.read(1024 * 1024):
        await out_file.write(content)

이 부분이 이번 코드에서 가장 어렵습니다.

먼저:
aiofiles.open(destination, 'wb')

는 파일을 비동기 방식으로 열겠다는 뜻입니다. 'wb'는 write binary의 줄임말입니다. 
이미지, PDF, 동영상 같은 파일은 텍스트가 아니라 바이너리 데이터이므로 wb 모드로 저장합니다.

다음으로:
await file.read(1024 * 1024)

는 업로드된 파일에서 최대 1MB만 읽겠다는 뜻입니다.

1024 * 1024는 1,048,576 bytes, 즉 1MB입니다.

즉 이 코드는 파일 전체를 한 번에 읽지 않고, 1MB씩 나눠서 읽습니다.

while content := await file.read(1024 * 1024):

이 부분은 조금 낯설 수 있습니다. :=는 파이썬의 walrus operator입니다. 값을 변수에 넣으면서 동시에 조건 검사도 합니다.

쉽게 풀어 쓰면 이런 느낌입니다.

while True:
    content = await file.read(1024 * 1024)

    if not content:
        break

    await out_file.write(content)

즉 파일에서 1MB를 읽고, 읽은 내용이 있으면 저장 파일에 씁니다. 더 이상 읽을 내용이 없으면 반복을 멈춥니다.

정리하면 이 블록은:
업로드된 파일을 1MB씩 읽어서 서버의 uploads 폴더에 저장하는 코드입니다.


[try / except / finally 블록]
try:
    async with aiofiles.open(destination, 'wb') as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)
except Exception as e:
    print(f"File saving error: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {e}")
finally:
    return {"filename": file.filename, "content_type": file.content_type, "save_path": destination}

이 구조는 파일 저장 중 문제가 생겼을 때를 대비한 예외 처리입니다.

try 안에는 실제 파일 저장 코드가 들어 있습니다.

except는 저장 중 에러가 발생했을 때 실행됩니다. 
예를 들어 저장 권한이 없거나, 경로 문제가 있거나, 디스크 문제가 생기면 여기로 옵니다. 
이 경우 HTTPException으로 500 서버 에러를 반환합니다.

finally는 성공하든 실패하든 무조건 실행됩니다. 
'''


# 3. 다중 파일 업로드
# 여러 개의 파일을 한 번에 받을 때는 List[UploadFile]을 사용합니다.
@app.post("/files/upload-multiple/")
async def upload_multiple_files(
    # files라는 이름으로 여러 파일을 받습니다.
    # Swagger UI에서는 파일 여러 개를 선택할 수 있습니다.
    files: List[UploadFile] =File(..., description="Upload multiple files")
):
    
    # 각 파일의 저장 결과를 담을 리스트입니다.
    saved_files = []


    # 업로드된 파일들을 하나씩 처리합니다.
    for file in files:
        print(f"Processing file: {file.filename}")

         # 파일명에서 위험한 경로 부분을 제거합니다.
        safe_filename = os.path.basename(file.filename or f"Uploaded_file_{len(saved_files)}")

        # 저장할 파일 경로를 만듭니다.
        destination = os.path.join(UPLOAD_DIR, safe_filename)


        try:
            # 파일을 비동기 방식으로 열고,
            # 업로드 파일을 1MB씩 읽어서 저장합니다.
            async with aiofiles.open(destination, 'wb') as out_file:
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)

            # 저장 성공 정보를 리스트에 추가합니다.
            saved_files.append({"filename": file.filename, "save_path": destination})

        except Exception as e:
            # 특정 파일 저장에 실패해도 전체 요청을 중단하지 않고,
            # 실패 정보를 saved_files에 기록한 뒤 다음 파일 처리를 계속합니다.
            print(f"Error saving {file.filename}: {e}")
            saved_files.append({"filename": file.filename, "error": str(e)})
        
        finally:
            # 각 파일 처리가 끝나면 파일 객체를 닫습니다.

            await file.close()

    # 처리한 파일 개수와 파일별 결과를 응답합니다.
    return {"message": f"{len(saved_files)} files processed.", "details": saved_files}

'''
이 API는 여러 파일을 한 번에 받습니다.

핵심은 이 부분입니다.

files: List[UploadFile] = File(...)

UploadFile 하나가 아니라 List[UploadFile]입니다. 그래서 클라이언트가 파일 여러 개를 올리면 FastAPI가 리스트로 받아줍니다.


for file in files:

각 파일을 하나씩 반복하면서 저장합니다.

단일 파일 업로드와 저장 방식은 거의 같습니다. 파일명을 안전하게 만들고, 저장 경로를 만든 뒤, 1MB씩 읽어서 저장합니다.

차이점은 에러 처리 방식입니다.

하나의 파일 저장에 실패해도 전체 요청을 바로 중단하지 않고, 
해당 파일의 실패 정보를 saved_files에 추가한 뒤 다음 파일 처리를 계속합니다.

예를 들어 3개 파일 중 2개 성공, 1개 실패라면 응답이 이런 식으로 나올 수 있습니다.

{
  "message": "3 files processed.",
  "details": [
    {
      "filename": "a.png",
      "save_path": "./uploads/a.png"
    },
    {
      "filename": "b.pdf",
      "save_path": "./uploads/b.pdf"
    },
    {
      "filename": "c.mov",
      "error": "some error message"
    }
  ]
}

즉, 이 API는 여러 파일을 받아서 각각 저장하고, 파일별 처리 결과를 응답하는 예제입니다.
'''


# 4. 파일과 다른 폼 데이터 함께 받기
# 파일 업로드 요청은 multipart/form-data 형식입니다.
# 파일과 함께 notes 같은 일반 텍스트 값도 받을 수 있습니다.
@app.post("/files/upload-with-form/")
async def upload_file_and_form(
    # 업로드 파일
    file: UploadFile = File(...),

    # 파일과 함께 전송되는 폼 데이터
    # Form(None)을 써야 쿼리 파라미터가 아니라 form-data에서 값을 가져옵니다.
    notes: Optional[str] = None
):
    print(f"Received file: {file.filename}")

    if notes:
        print(f"Received notes: {notes}")

    # 안전한 파일명 만들기
    safe_filename = os.path.basename(file.filename or "uploaded_file")

    # 저장할 경로 만들기
    destination = os.path.join(UPLOAD_DIR, safe_filename)

    return {"filename": file.filename, "notes": notes, "save_path": "simulated_save"}

'''
이 API는 파일과 텍스트 데이터를 함께 받으려는 예제입니다.

예를 들어 클라이언트가 이런 데이터를 보낼 수 있습니다.

file = profile.png
notes = 프로필 이미지입니다.

파일 업로드 요청은 일반적으로 multipart/form-data 형식입니다. 파일과 텍스트 값을 같이 보낼 수 있습니다.

다만 원본 코드에서 notes는 이렇게 되어 있습니다.

notes: Optional[str] = None

파일과 함께 폼 데이터로 받으려면 아래처럼 쓰는 게 더 정확합니다.

notes: Optional[str] = Form(default=None)

그래야 FastAPI가 notes를 쿼리 파라미터가 아니라 form-data에서 찾습니다.

그리고 이 API는 실제로 파일 저장을 하지 않습니다.

return {"filename": file.filename, "notes": notes, "save_path": "simulated_save"}

save_path도 실제 경로가 아니라 "simulated_save"입니다. 즉, 저장을 흉내만 내는 예제입니다.

실제 저장까지 하려면 앞의 단일 파일 업로드처럼 aiofiles.open()으로 저장 코드를 추가해야 합니다.
'''