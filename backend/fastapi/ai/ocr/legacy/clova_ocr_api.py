import requests
from dotenv import load_dotenv
import os
import json
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS

# .env 파일로부터 환경변수 로드
load_dotenv()
X_OCR_SECRET = os.getenv("X_OCR_SECRET")

# Clova OCR API 엔드포인트
api_url = "https://cdy4ki81dz.apigw.ntruss.com/custom/v1/39333/d0906d026124254d068c1256857516561d16b27c7e6fae8fd5fe2f793d8ae8ee/general"

# 헤더에 인증 정보 입력
headers = {
    "X-OCR-SECRET": X_OCR_SECRET,  # 발급받은 Client Secret
    # "Content-Type": "application/json"  # 요청 데이터의 형식(application/json | multipart/form-data)
}

# 요청 바디 정보 입력
data = {
    "version": "V2",  # String, 버전 정보(V1 | V2)
    "requestId": "test",  # String, 임의의 API 호출 UUID
    "timestamp": 12345678,  # Integer, 임의의 API 호출 시각(Timestamp)
    # "lang": "ko, en",  # String, OCR 인식 요청 언어 정보(ko | en | ja | zh-CN)
    "images": [  # Array, images 세부 정보(이미지 크기: 최대 50MB)
        {
            "format": "jpg",  # String, 이미지 형식(jpg | png | pdf)
            "name": "test_image",  # String, 이미지 이름
            # "url": "BASE64_ENCODED_IMAGE_URL",  # String, 이미지 URL 주소(images.url | images.data)
            # "data": "BASE64_ENCODED_IMAGE_DATA"  # String, Base64 인코딩된 이미지 데이터(images.url | images.data)
        }
    ],
    # "enableTableDetection": False,  # Boolean, 문서 이미지 내 표(Table) 영역 인식 및 구조화된 형태 제공 여부(True | False)
}

# 이미지 파일 열기
image_folder = "image/"
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    image_format = image_file.split(".")[-1]

    files = {
        "file": open(image_path, "rb"),
        "message": (None, json.dumps(data), "application/json")
    }  # 파일과 JSON 데이터를 multipart 형식으로 함께 전송

    # POST 요청으로 API 호출
    response = requests.post(api_url, headers=headers, files=files, data=data)

    # 결과 출력 (JSON 형식)
    result = response.json()
    # print(result)

    # OCR 결과를 JSON 파일로 저장
    result_name = image_file.split(".")[0]
    with open(f"ocr_json/{result_name}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    ######################## OCR RESULT IMAGE #######################
    #################################################################

    # 이미지 파일 경로
    image = Image.open(image_path)

    # EXIF 정보 확인 및 회전 적용
    try:
        for orientation in [274]: # Orientation tag
            exif = image._getexif()
            if exif and orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
                break
    except (AttributeError, KeyError, IndexError):
        # EXIF 정보가 없거나 오류가 발생한 경우 무시
        pass

    draw = ImageDraw.Draw(image)

    # 폰트 설정 (한글 지원을 위해 malgun.ttf 사용, 없으면 기본 폰트 사용)
    try:
        font = ImageFont.truetype("malgun.ttf", size=15)
    except Exception as e:
        print("Custom font not found, using default.")
        font = ImageFont.load_default()

    # OCR 결과에서 첫 번째 이미지의 필드 리스트 가져오기
    fields = result["images"][0]["fields"]

    # 각 필드에 대해 bounding box와 텍스트를 그림
    for field in fields:
        # boundingPoly의 vertices 추출
        vertices = field["boundingPoly"]["vertices"]
        xs = [v.get("x", 0) for v in vertices]
        ys = [v.get("y", 0) for v in vertices]
        left, top, right, bottom = min(xs), min(ys), max(xs), max(ys)

        # 사각형 그리기 (경계 상자)
        draw.rectangle(((left, top), (right, bottom)), outline="lime", width=2)

    # OCR 결과 이미지 저장
    rgb_image = image.convert('RGB')
    rgb_image.save(f"ocr_image/{result_name}.jpg")