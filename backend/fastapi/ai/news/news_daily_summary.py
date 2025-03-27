import os
import json
from dotenv import load_dotenv
import datetime

import google.generativeai as genai

# 환경변수 로드 및 GEMINI_API_KEY 가져오기
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

instruction = """
당신은 일일 뉴스를 요약해서 정리해주는 전문가입니다.
생성되는 텍스트는 순수한 일반 텍스트 형식이어야 하며, 어떠한 마크다운 문법(예: **, ## 등)도 사용하지 말아주세요.
news_title, news_content, published_date 정보를 포함한 JSON 형식의 데이터를 입력받아, 요약된 내용을 생성해주세요.
뉴스 중에서 중복되는 내용이 있는 경우에는 1개만 요약해야 합니다.
일일 뉴스 중에서 가장 중요한 내용 4~5가지를 각각 한 줄로 요약해야 하고, 뉴스 제목과 같은 형태로 요약된 내용을 반환해야 합니다.

**데이터 예시**
{
    "news_title": "뉴스 제목",
    "news_content": "뉴스 내용",
    "published_date": "2025-03-22"
}

**응답 형태**
- 요약된 뉴스 내용 (생성된 텍스트)

**응답 예시**
- KIA 김도영, 개막전서 햄스트링 부상으로 팬들에게 안타까운 사과와 빠른 복귀 다짐
- KIA 윤도현, 김도영 부상으로 찾아온 기회 놓치지 않고 성장 발판 마련할 수 있을지 주목
- KIA, 개막전에서 NC에 9-2 역전승, 최형우 결승타와 한준수 쐐기 홈런으로 승리
- KIA 네일, 개막전서 5이닝 무실점 쾌투에도 승리투수 되지 못했지만 팀 승리 발판 마련
- KIA, 개막 후 김도영의 부상에도 타선이 폭발하며 키움에 대승, 외국인 투수 올러가 데뷔 첫 승을 거둠
"""

model = genai.GenerativeModel(
    "models/gemini-2.0-flash", 
    system_instruction=instruction
)

def summarize_daily_news(date, team):
    """일일 뉴스 요약"""
    json_file_path = f"news_json/{date}/news_{date}_{team}.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

    prompt = f"""
    ## 뉴스 내용:
    {data}

    **일일 뉴스 요약된 결과**
    """

    response = model.generate_content(prompt)
    return response.text

# 팀 코드와 팀 이름 매핑
team_mapping = {
    "HT": "KIA",
    "SS": "삼성",
    "OB": "두산",
    "LT": "롯데",
    "KT": "KT",
    "SK": "SSG",
    "HH": "한화",
    "NC": "NC",
    "WO": "키움",
    "LG": "LG"
}

# 날짜 설정
date = input("요약할 기준 날짜를 입력하세요 (YYYYMMDD 형식): ")
team = input("요약할 팀 코드를 입력하세요 (예: HT): ")

# 요약된 결과 생성
result = summarize_daily_news(date, team)
team_mapping[team] + " " + result
print(f"{date[:4]}-{date[4:6]}-{date[6:]} " + team_mapping[team] + " 뉴스 요약\n" + result)