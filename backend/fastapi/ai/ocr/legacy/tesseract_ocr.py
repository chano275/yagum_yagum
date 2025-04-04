"""
Tesseract - OCR 프로그램 중 하나, 다양한 운영체제에서 사용할 수 있는 엔진, 무료 소프트웨어

이미지에 있는 텍스트 추출 과정
1. Tesseract-OCR 설치
2. Python에서 Tesseract 사용하기
"""

from PIL import Image
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image_path = 'image/test.jpg'
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
gray = cv2.medianBlur(gray, 3)
raw_text = pytesseract.image_to_string(gray, lang='kor+eng')
text = raw_text.replace(" ", "")

print(text)