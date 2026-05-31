import asyncio
import os
import mimetypes
from xml.etree.ElementTree import QName
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse


app = FastAPI()


# 다운로드할 파일들이 저장되어 있는 서버 내부 폴더
# 예: ./downloadables/report.pdf
DOWNLOAD_DIR = "./downloadables/"

'''
이 블록은 다운로드 가능한 파일들이 들어 있는 서버 내부 폴더를 정하는 부분입니다.

예를 들어 서버 프로젝트 안에 이런 파일들이 있다고 가정합니다.

./downloadables/report.pdf
./downloadables/image.png
./downloadables/sample.txt

그러면 클라이언트는 API를 통해 이 폴더 안의 파일을 다운로드할 수 있습니다.

다만 중요한 점은 사용자가 서버의 아무 파일이나 다운로드하면 안 된다는 것입니다.
그래서 뒤에서 DOWNLOAD_DIR 안에 있는 파일만 접근 가능하도록 검사합니다.
'''


############################################
# --- 기본 파일 다운로드 엔드포인트 ---
############################################


@app.get("/downloadables/basic/{file_name}")
async def download_basic(file_name: str):

    # 클라이언트가 요청한 파일 이름을 경로 매개변수로 받습니다.
    # 예: GET /downloadables/basic/report.pdf
    # 그러면 file_name = "report.pdf" 가 됩니다.

    # 사용자가 file_name에 "../secret.txt" 같은 위험한 값을 넣을 수 있습니다.
    # os.path.basename()은 경로 부분을 제거하고 파일명만 남깁니다.

    # 예:
    # "../../secret.txt" -> "secret.txt"
    # "report.pdf" -> "report.pdf
    safe_base_filename = os.path.basename(file_name)

    # 다운로드 폴더와 안전하게 정리한 파일명을 합쳐 실제 파일 경로를 만듭니다.
    # 예: ./downloadables/report.pdf
    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)


    # 파일 존재 여부 확인 -> “그 파일이 실제로 존재하냐?”

    # os.path.isfile(file_path)는 해당 경로에 실제 파일이 있는지 확인합니다.
    # 파일이 없으면 404 Not Found 에러를 발생시킵니다.
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "File not found")
    


    # 파일 경로가 의도한 디렉토리 내에 있는지 확인 (경로 조작 방어) -> “그 파일 경로가 다운로드 허용 폴더 안에 있냐?”

    # 이 코드는 사용자가 다운로드 허용 폴더 밖의 파일에 접근하지 못하게 하려는 목적입니다.
    # 이건 파일 존재 여부가 아니라 접근 권한 검사입니다.
    # 즉, ./downloadables/ 안의 파일만 다운로드되도록 제한하려는 검사입니다.


    # file_path가 DOWNLOAD_DIR 폴더 안에 있는 파일인지 확인하는 코드
    # 즉, 사용자가 다운로드 허용 폴더 밖의 파일에 접근하려는지 검사합니다.

    # 예를 들어 허용된 폴더가 "./downloadables/"라면,
    # 다운로드할 파일은 반드시 이 폴더 안에 있어야 합니다.

    # 정상 예:
    # ./downloadables/report.pdf
    #
    # 위험한 예:
    # ./downloadables/../../secret.txt
    # → downloadables 폴더 밖의 secret.txt에 접근하려는 시도

    # startswith()는 문자열이 특정 문자열로 시작하는지 확인합니다.
    # 여기서는 file_path가 DOWNLOAD_DIR의 절대 경로로 시작하는지 확인하려는 의도입니다.

    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):

        # 허용된 다운로드 폴더 밖의 파일에 접근하려는 상황이므로 로그 출력
        print(f"Error: Access denied to path {file_path}")

        # 403 Forbidden 에러 발생
        # 403은 "파일이 없어서 못 주는 것"이 아니라,
        # "접근 권한이 없어서 줄 수 없다"는 의미입니다.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    

    print(f"Serving file: {file_path}")


    # FileResponse는 서버에 있는 파일을 클라이언트에게 응답으로 보내줍니다.
    # 파일 전체를 메모리에 한 번에 올리지 않고 효율적으로 전송합니다.
    return FileResponse(path=file_path)

'''
이 API는 가장 기본적인 파일 다운로드 API입니다.

예를 들어 사용자가 이렇게 요청한다고 해볼게요.

GET /downloadables/basic/report.pdf

그러면 file_name에는 "report.pdf"가 들어갑니다.

먼저 이 코드가 실행됩니다.

safe_base_filename = os.path.basename(file_name)

이 코드는 사용자가 보낸 값에서 파일명만 뽑습니다.

예를 들어:
report.pdf → report.pdf
../../secret.txt → secret.txt

이렇게 경로 부분을 제거합니다.

그다음:
file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)

다운로드 폴더와 파일명을 합쳐 실제 파일 경로를 만듭니다.

예를 들어:
DOWNLOAD_DIR = "./downloadables/"
safe_base_filename = "report.pdf"

이면 결과는:
./downloadables/report.pdf

입니다.


그다음 파일이 실제로 있는지 확인합니다.

if not os.path.isfile(file_path):

파일이 없으면 404 Not Found를 반환합니다.
파일이 있으면 마지막에 이 코드가 실행됩니다.


return FileResponse(path=file_path)

이 코드는 해당 경로의 파일을 클라이언트에게 응답으로 보냅니다.
즉, 이 API는 요청받은 파일명을 기준으로 서버 폴더에서 파일을 찾아 다운로드시키는 API입니다.


[FileResponse(path=file_path) 의미]

return FileResponse(path=file_path)

이 코드가 파일 다운로드의 핵심입니다.

일반 API에서는 보통 이렇게 JSON을 반환하죠.

return {"message": "hello"}

그러면 클라이언트는 JSON 데이터를 받습니다.

그런데 FileResponse를 반환하면 클라이언트는 JSON이 아니라 파일 응답을 받습니다.

서버에 있는 파일
→ FileResponse가 파일 응답으로 포장
→ 브라우저가 파일을 받음

브라우저는 파일 종류에 따라 다르게 동작할 수 있습니다.

이미지 파일 → 브라우저에서 바로 표시될 수 있음
PDF 파일 → 브라우저에서 열릴 수 있음
ZIP 파일 → 다운로드될 수 있음
'''



#########################################################
# --- 파일 다운로드 응답 커스터마이징 엔드포인트 ---
#########################################################

@app.get("/downloadables/custom/{file_name}")
async def download_custom(file_name: str):
    # 이 API는 기본 다운로드보다 응답 정보를 더 세밀하게 지정합니다.
    
    # 기본 다운로드와 다른 점:
    # 1. media_type을 지정합니다.
    # 2. 다운로드될 때 보여줄 filename을 지정합니다.
    
    # 예:
    # GET /downloadables/custom/report.pdf
    
    # 서버는 report.pdf를 찾아서
    # downloaded_report.pdf 라는 이름으로 다운로드되도록 응답할 수 있습니다.


    # 사용자가 입력한 파일명에서 경로 부분을 제거합니다.
    safe_base_filename = os.path.basename(file_name)

    # 실제 파일 경로를 만듭니다.
    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)


    # 파일이 없으면 404 에러
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    # 다운로드 허용 폴더 밖의 파일이면 403 에러
    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    


    # 파일 확장자로부터 MIME 타입 추측
    
    # MIME 타입은 브라우저에게 "이 파일이 어떤 종류인지" 알려주는 정보입니다.
    
    # 예:
    # .txt  -> text/plain
    # .pdf  -> application/pdf
    # .png  -> image/png
    # .zip  -> application/zip
    media_type, _ = mimetypes.guess_type(file_path)


    # mimetypes가 파일 타입을 추측하지 못한 경우 application/octet-stream을 기본값으로 사용합니다.
    # application/octet-stream은 "일반적인 바이너리 파일" 정도로 이해하면 됩니다.
    if media_type is None:
        media_type = 'application/octet-stream'



    # 다운로드될 때 사용자에게 보여줄 파일 이름 설정
    # 예:
    # 원래 파일명: report.pdf
    # 다운로드 파일명: downloaded_report.pdf
    download_filename = f"downloaded_{safe_base_filename}"

    print(f"Serving file: {file_path} as {download_filename} with type {media_type}")

    # FileResponse로 파일을 응답합니다.
    return FileResponse(
        path=file_path,             # path: 서버 내부의 실제 파일 경로

        filename=download_filename, # filename: 브라우저가 다운로드할 때 제안받는 파일명
                                    # Content-Disposition 헤더 설정 (다운로드 파일명 제안)

        media_type=media_type       # media_type: 응답 파일의 종류를 알려주는 값
                                    # Content-Type 헤더 설정 (파일 종류 명시)
    )

'''
이 API는 기본 다운로드와 거의 비슷하지만, 응답 정보를 조금 더 자세히 지정합니다.

차이는 여기입니다.

media_type, _ = mimetypes.guess_type(file_path)

이 코드는 파일 확장자를 보고 파일 종류를 추측합니다.

예를 들어:
report.pdf → application/pdf
image.png → image/png
memo.txt → text/plain

이 값은 브라우저가 파일을 어떻게 처리할지 판단하는 데 도움을 줍니다.


만약 파일 타입을 알 수 없으면:
media_type = 'application/octet-stream'

을 사용합니다.

application/octet-stream은 쉽게 말해 일반 파일 데이터라는 뜻입니다.
브라우저 입장에서는 정확히 뭔지는 모르지만 파일로 처리하면 됩니다.


그다음:
download_filename = f"downloaded_{safe_base_filename}"

이 코드는 사용자가 다운로드할 때 보게 될 파일명을 정합니다.

예를 들어 요청한 파일이:
report.pdf

라면 다운로드 이름은:
downloaded_report.pdf

가 됩니다.


마지막 FileResponse는 이렇게 동작합니다.

return FileResponse(
    path=file_path,
    filename=download_filename,
    media_type=media_type
)

path는 서버 내부 실제 파일 경로입니다.
filename은 브라우저가 다운로드할 때 보여줄 파일명입니다.
media_type은 파일 종류입니다.

즉, 이 API는 파일을 보내면서 브라우저에게 파일명과 파일 타입까지 알려주는 다운로드 API입니다.


[path, filename, media_type 차이]

return FileResponse(
    path=file_path,
    filename=download_filename,
    media_type=media_type
)

이 세 개가 헷갈릴 수 있습니다.

항목 	     의미
path	     서버 안에서 실제 파일이 있는 위치
filename	 사용자가 다운로드할 때 보게 될 파일 이름
media_type	 이 파일이 어떤 종류인지 알려주는 값

예를 들어:

path="./downloadables/abc123.pdf"
filename="downloaded_report.pdf"
media_type="application/pdf"

이면 서버는 내부적으로 abc123.pdf를 보내지만, 사용자는 downloaded_report.pdf라는 이름으로 받을 수 있습니다.
'''



#########################################################
# --- (참고) StreamingResponse 사용 예시 (개념) ---
#########################################################

# 이 예시는 실제 파일을 읽는 대신, 간단한 텍스트를 청크로 생성하여 스트리밍합니다.

async def fake_data_streamer():
    # 간단한 비동기 제너레이터입니다.
    
    # 제너레이터는 값을 한 번에 전부 반환하지 않고,
    # yield를 통해 조금씩 내보냅니다.
    
    # 여기서는 10줄짜리 텍스트 데이터를 한 줄씩 만들어냅니다.

    for i in range(10):
        # yield는 데이터를 하나씩 내보내는 역할입니다.
        
        # return은 함수가 값을 반환하고 끝나지만,
        # yield는 값을 하나 내보낸 뒤 다음 반복을 계속할 수 있습니다.
        
        # StreamingResponse는 이 yield 결과들을 하나씩 받아서 클라이언트에게 보냅니다.

        yield f"Line {i+1}: Some data chunk\\n" # 각 yield 가 하나의 청크가 됨

        # 실제 I/O 작업이 있다면 여기서 await 사용
        #
        # 예를 들어 DB에서 데이터를 조금씩 읽거나,
        # 외부 API를 기다리거나,
        # 파일 일부를 읽는 상황이라면 await를 사용할 수 있습니다.
        # await asyncio.sleep(0.1)

'''
이 함수는 실제 파일을 읽는 함수가 아닙니다.

대신 텍스트 데이터를 한 줄씩 만들어내는 함수입니다.

여기서 핵심은 yield입니다.

return은 값을 한 번에 반환하고 끝납니다.

return "hello"

하지만 yield는 값을 하나씩 내보냅니다.

yield "Line 1"
yield "Line 2"
yield "Line 3"

이 코드에서는 for i in range(10)이므로 총 10줄을 만들어냅니다.

Line 1: Some data chunk
Line 2: Some data chunk
...
Line 10: Some data chunk

즉, 이 함수는 다운로드할 내용을 한 번에 만드는 게 아니라, 조금씩 만들어내는 역할입니다.
'''


@app.get("/download/stream")
async def download_stream():
    # StreamingResponse 를 사용하여 동적으로 생성된 데이터를 스트리밍합니다.
    
    # FileResponse:
    #   이미 서버에 존재하는 파일을 보내는 데 적합
    
    # StreamingResponse:
    #   데이터를 그때그때 만들어서 조금씩 보내는 데 적합
    
    # 이 예제에서는 fake_data_streamer()가 만들어내는 텍스트 줄들을
    # streamed_data.txt 파일처럼 다운로드하게 만듭니다.

    stream = fake_data_streamer()
    return StreamingResponse(
        content=stream,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=streamed_data.txt"} 
    )

'''
이 API는 StreamingResponse를 사용합니다.

먼저:
stream = fake_data_streamer()

이 코드는 조금씩 데이터를 만들어내는 스트림을 준비합니다.

그다음:
return StreamingResponse(
    content=stream,
    media_type="text/plain",
    headers={"Content-Disposition": "attachment; filename=streamed_data.txt"} 
)

이 응답은 stream에서 나오는 데이터를 클라이언트에게 조금씩 보냅니다.
media_type="text/plain"은 이 응답이 일반 텍스트라는 뜻입니다.

그리고 이 헤더가 중요합니다.
headers={"Content-Disposition": "attachment; filename=streamed_data.txt"}

이 뜻은 브라우저에게:
이 응답을 streamed_data.txt라는 이름의 첨부파일로 다운로드해라.

라고 알려주는 것입니다.

즉, 이 API는 실제 파일이 없어도, 서버가 즉석에서 만든 텍스트 데이터를 streamed_data.txt 파일처럼 다운로드하게 만드는 예제입니다.
'''