import requests
from dotenv import load_dotenv
import os
import json
import re
import cv2
import pyzbar.pyzbar as pyzbar

# .env 파일로부터 환경변수 로드
load_dotenv()
X_OCR_SECRET = os.getenv("X_OCR_SECRET")

# Clova OCR API 엔드포인트
API_URL = "https://cdy4ki81dz.apigw.ntruss.com/custom/v1/39333/d0906d026124254d068c1256857516561d16b27c7e6fae8fd5fe2f793d8ae8ee/general"
API_TIMESTAMP = 12345678

# 헤더에 인증 정보 입력
HEADERS = {
    "X-OCR-SECRET": X_OCR_SECRET,  # 발급받은 Client Secret
    # "Content-Type": "application/json"  # 요청 데이터의 형식(application/json | multipart/form-data)
}

def decode_qr_and_barcodes(image_path):
    """이미지 파일에서 QR 코드 및 바코드를 인식하고 텍스트를 반환합니다."""
    try:
        # 이미지 파일 로드
        image = cv2.imread(image_path)

        # 이미지를 grayscale로 변환 (인식 성능 향상)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # QR 코드 및 바코드 디코딩
        decoded_objects = pyzbar.decode(gray)
        # print(decoded_objects)

        if not decoded_objects:
            return None

        # 디코딩된 정보 출력
        results = []
        seen_data = set()  # 중복 데이터 추적을 위한 set
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")  # 바이트 데이터를 문자열로 변환
            if data not in seen_data:  # 중복 데이터 확인
                seen_data.add(data)
                results.append(data)

        return "\n".join(results)

    except Exception as e:
        print(f"QR/바코드 디코딩 오류: {e}")
        return None
    
def clova_ocr(image_path):
    """Clova OCR API를 사용하여 이미지에서 텍스트를 추출하고 티켓 번호를 반환합니다."""
    try:
        # 요청 바디 정보 입력
        data = {
            "version": "V2",  # String, 버전 정보(V1 | V2)
            "requestId": "test",  # String, 임의의 API 호출 UUID
            "timestamp": API_TIMESTAMP,  # Integer, 임의의 API 호출 시각(Timestamp)
            # "lang": "ko, en",  # String, OCR 인식 요청 언어 정보(ko | en | ja | zh-CN)
            "images": [  # Array, images 세부 정보(이미지 크기: 최대 50MB)
                {
                    "format": image_path.split(".")[-1],  # String, 이미지 형식(jpg | png | pdf)
                    "name": "test_image",  # String, 이미지 이름
                    # "url": "BASE64_ENCODED_IMAGE_URL",  # String, 이미지 URL 주소(images.url | images.data)
                    # "data": "BASE64_ENCODED_IMAGE_DATA"  # String, Base64 인코딩된 이미지 데이터(images.url | images.data)
                }
            ],
            # "enableTableDetection": False,  # Boolean, 문서 이미지 내 표(Table) 영역 인식 및 구조화된 형태 제공 여부(True | False)
        }

        files = {
            "file": open(image_path, "rb"),
            "message": (None, json.dumps(data), "application/json")
        }  # 파일과 JSON 데이터를 multipart 형식으로 함께 전송

        # POST 요청으로 API 호출
        response = requests.post(API_URL, headers=HEADERS, files=files, data=data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # 결과 출력 (JSON 형식)
        result = response.json()

        # OCR 결과에서 텍스트 추출
        infer_texts = []
        for image in result.get("images", []):
            for field in image.get("fields", []):
                text = field.get("inferText")
                if text:
                    infer_texts.append(text)
        
        ocr_text = " ".join(infer_texts)

        # 정규 표현식으로 패턴 찾기
        ticket_numbers = re.findall(r'T\d{10}', ocr_text)  # 티켓 번호 추출 (T로 시작하는 10자리 숫자)

        # 결과 출력
        if ticket_numbers:
            return ticket_numbers[0]
        else:
            print("Ticket Number 패턴을 찾을 수 없습니다.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Clova OCR API 호출 오류: {e}")
        return None
    except Exception as e:
        print(f"Clova OCR 처리 오류: {e}")
        return None
    
# 이미지 파일 경로 설정
image_path = "image/" + input("이미지 파일 이름을 입력하세요: ")

# QR 코드 및 바코드 디코딩 시도
decoded_text = decode_qr_and_barcodes(image_path)

if decoded_text:
    print(decoded_text)
else:
    # Clova OCR 사용
    ticket_number = clova_ocr(image_path)
    if ticket_number:
        print(ticket_number)
    else:
        print("티켓 번호를 찾을 수 없습니다.")
