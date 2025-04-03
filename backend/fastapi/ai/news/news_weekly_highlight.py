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
[역할]
당신은 주간 뉴스를 요약해서 정리해주는 전문가입니다.

[작성 조건]
- 생성되는 텍스트는 순수한 일반 텍스트 형식이어야 하며, 어떠한 마크다운 문법(예: **, ## 등)도 사용하지 말아주세요.
- news_title, news_summary, published_date 정보를 포함한 JSON 형식의 데이터를 입력받아, 요약된 내용을 생성해주세요.
- 뉴스 중에서 중복되는 내용이 있는 경우에는 1개만 요약해야 합니다.
- 주간 뉴스 중에서 가장 중요한 내용 5가지를 각각 한 줄로 요약해야 하고, 뉴스 제목과 같은 형태로 요약된 내용을 반환해야 합니다.

[입력 데이터 형식]
{
    "news_title": "뉴스 제목",
    "news_summary": "뉴스 요약 내용",
    "published_date": "2025-03-22"
}

[출력 형식]
- 요약된 뉴스 내용 (생성된 텍스트)

[출력 예시]
- 김도영, 개막전서 햄스트링 부상으로 팬들에게 안타까운 사과와 빠른 복귀 다짐
- 윤도현, 김도영 부상으로 찾아온 기회 놓치지 않고 성장 발판 마련할 수 있을지 주목
- 개막전에서 NC에 9-2 역전승, 최형우 결승타와 한준수 쐐기 홈런으로 승리
- 네일, 개막전서 5이닝 무실점 쾌투에도 승리투수 되지 못했지만 팀 승리 발판 마련
- 개막 후 김도영의 부상에도 타선이 폭발하며 키움에 대승, 외국인 투수 올러가 데뷔 첫 승을 거둠
"""

model = genai.GenerativeModel(
    "models/gemini-2.0-flash", 
    system_instruction=instruction
)

def summarize_weekly_news(start_date, end_date, team):
    """주간 뉴스 요약"""
    all_news = []
    for current_date in range((end_date - start_date).days + 1):
        target_date = start_date + datetime.timedelta(days=current_date)
        json_file_path = f"news_json/{target_date.strftime('%Y%m%d')}/news_{target_date.strftime('%Y%m%d')}_{team}.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                # 각 뉴스 항목에서 필요한 필드만 추출
                for item in data:
                    extracted = {
                        "news_title": item.get("news_title", ""),
                        "news_summary": item.get("news_summary", ""),
                        "published_date": item.get("published_date", "")
                    }
                    all_news.append(extracted)

    if not all_news:
        return None

    prompt = f"""
    ## 뉴스 내용:
    {all_news}

    **주간 뉴스 요약된 결과**
    """

    response = model.generate_content(prompt)
    return response.text

def generate_weekly_summary_json(date, n_day=6):
    """주간 뉴스 요약을 JSON 파일로 생성"""
    target_date = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))
    start_date = target_date - datetime.timedelta(days=n_day - 1)

    result_json = {
        "header": {
            "date": target_date.strftime("%Y-%m-%d"),
        },
        "body": []
    }

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

    for team_code, team_name in team_mapping.items():
        summary = summarize_weekly_news(start_date, target_date, team_code)
        if summary:
            result_json["body"].append({
                "team": team_name,
                "news_summation": summary
            })

    return result_json

# 날짜 설정
date = input("요약할 기준 날짜를 입력하세요 (YYYYMMDD 형식): ")

# JSON 파일 생성 및 저장
result_json = generate_weekly_summary_json(date)

date_obj = datetime.datetime.strptime(date, "%Y%m%d")
week_number = date_obj.isocalendar()[1] - 12
file_name = f"news_weekly_highlight/news_weekly_highlight_{week_number}주차.json"

with open(file_name, "w", encoding="utf-8") as json_file:
    json.dump(result_json, json_file, ensure_ascii=False, indent=4)

print(f"{file_name} 파일이 생성되었습니다.")