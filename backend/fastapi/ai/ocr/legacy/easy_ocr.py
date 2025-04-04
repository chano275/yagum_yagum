import easyocr
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import ImageFont, ImageDraw, Image

image_path = 'image/test.jpg'

reader = easyocr.Reader(['en', 'ko'], gpu=True)
result = reader.readtext(image_path)

img = cv2.imread(image_path)
img = Image.fromarray(img)
font = ImageFont.truetype("malgun.ttf", 10)
draw = ImageDraw.Draw(img)

for i in result:
  x = i[0][0][0]
  y = i[0][0][1]
  w = i[0][1][0] - i[0][0][0]
  h = i[0][2][1] - i[0][1][1]

  draw.rectangle(((x, y), (x+w, y+h)), outline="blue", width=2)
  draw.text((int((x+x+w)/2), y-40), str(i[1]), font=font, fill="blue")

plt.imshow(img)
plt.show()

print(result)