# Clova OCR API -> json 파일을 전처리하는 코드

import json
import re

# json 파일 불러오기
json_path = "ocr_json/" + input("ocr_json 폴더 내 json 파일명을 입력하세요(예시: test): ") + ".json"
with open(json_path, "r", encoding="utf-8") as f:
    result = json.load(f)

# inferText 값을 모두 추출
infer_texts = []
for image in result.get("images", []):
    for field in image.get("fields", []):
        text = field.get("inferText")
        if text:
            infer_texts.append(text)

# 결과 출력
print("추출된 inferText 값들:")

ocr_text = " ".join(infer_texts)
for text in infer_texts:
    print(text)

# 티켓 번호, 좌석, 날짜 및 시간 정보 추출
print("\n" + "* OCR 결과로부터 추출된 티켓 정보")

ticket_numbers = re.findall(r'\b\d{10}\b', ocr_text)  # 티켓 번호 추출 (10자리 숫자)
ticket_numbers = [str(num) for num in ticket_numbers]
print("- 티켓 번호:", ticket_numbers)

seat_info = re.search(r'(\d+루.*?\d+블록.*?\d+번)', ocr_text)
seat = seat_info.group(0) if seat_info else None
print("- 좌석:", seat)

date_time_info = re.search(r'(\d{4}년 \d{2}월 \d{2}일\(.*?\) \d{2}:\d{2})', ocr_text)
date_time = date_time_info.group(0) if date_time_info else None
print("- 날짜 및 시간:", date_time)

# OCR 결과 TEXT 저장
result_name = json_path.split("/")[-1].split(".")[0]
with open(f"ocr_text/{result_name}.txt", "w", encoding="utf-8") as f:
    for text in infer_texts:
        f.write(text + "\n")
    f.write("\n" + "* OCR 결과로부터 추출된 티켓 정보" + "\n")
    f.write("- 티켓 번호: " + str(ticket_numbers) + "\n")
    f.write("- 좌석: " + str(seat) + "\n")
    f.write("- 날짜 및 시간: " + str(date_time) + "\n")