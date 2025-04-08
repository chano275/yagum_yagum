import os
import json
import re
from dotenv import load_dotenv

import google.generativeai as genai

# 환경변수 로드 및 GEMINI_API_KEY 가져오기
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

# 뉴스 요약에 사용할 instruction 문자열
instruction = """
[역할]
당신은 일일 뉴스를 요약해서 정리해주는 전문가입니다.

[작성 조건]
- 생성되는 텍스트는 순수한 일반 텍스트 형식이어야 하며, 어떠한 마크다운 문법(예: **, ## 등)도 사용하지 말아주세요.
- news_title, news_summary, published_date 정보를 포함한 JSON 형식의 데이터를 입력받아, 요약된 내용을 생성해주세요.
- 뉴스 중에서 중복되는 내용이 있는 경우에는 1개만 요약해야 합니다.
- 일일 뉴스 중에서 가장 중요한 내용 3가지를 각각 한 줄로 요약해야 하고, 뉴스 제목과 같은 형태로 요약된 내용을 반환해야 합니다.
- 출력 예시 형태와 동일한 형태로 출력하세요.

[입력 데이터 형식]
{
    "news_title": "뉴스 제목",
    "news_summary": "뉴스 요약 내용",
    "published_date": "2025-03-22"
}

[출력 형식]
- 요약된 뉴스 내용 리스트 (출력은 반드시 JSON 형식의 리스트여야 합니다.)

[출력 예시]
{
  "news_highlight": [
    "김도영, 개막전서 햄스트링 부상으로 팬들에게 안타까운 사과와 빠른 복귀 다짐",
    "윤도현, 김도영 부상으로 찾아온 기회 놓치지 않고 성장 발판 마련할 수 있을지 주목",
    "개막전에서 NC에 9-2 역전승, 최형우 결승타와 한준수 쐐기 홈런으로 승리"
  ]
}
"""

# Gemini 모델 인스턴스 생성
model = genai.GenerativeModel(
    "models/gemini-2.0-flash", 
    system_instruction=instruction
)

def summarize_daily_news(date, team):
    """일일 뉴스 요약"""
    all_news = []
    json_file_path = f"news_json/{date}/news_{date}_{team}.json"
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

    prompt = f"""
    ## 뉴스 내용:
    {all_news}

    **일일 뉴스 요약된 결과**
    """

    response = model.generate_content(prompt)
    return response.text

def generate_daily_summary_json(date):
    """일일 뉴스 요약을 JSON 파일로 생성"""
    # 팀 코드와 팀 이름 매핑
    team_mapping = {
        "HT": "KIA 타이거즈",
        "SS": "삼성 라이온즈",
        "OB": "두산 베어스",
        "LT": "롯데 자이언츠",
        "KT": "KT 위즈",
        "SK": "SSG 랜더스",
        "HH": "한화 이글스",
        "NC": "NC 다이노스",
        "WO": "키움 히어로즈",
        "LG": "LG 트윈스"
    }

    # 모든 팀의 요약 결과를 저장할 딕셔너리
    all_team_highlights = {}

    for team_code, team_name in team_mapping.items():
        # 팀별 뉴스 요약
        raw_result = summarize_daily_news(date, team_code)
        
        # 모델 응답에서 JSON 부분 파싱
        json_regex = re.compile(r"(\{.*\})", re.DOTALL)
        match = json_regex.search(raw_result)
        
        if match:
            json_str = match.group(1).strip()
            try:
                parsed = json.loads(json_str)
                # parsed는 {"news_highlight": [...]} 형태일 것
                highlights = parsed.get("news_highlight", [])
            except json.JSONDecodeError:
                # JSON 파싱 실패 시, 빈 리스트로 처리
                highlights = []
        else:
            # JSON 객체를 찾지 못했을 때도 빈 리스트로
            highlights = []
        
        # 현재 팀 이름을 키로, 하이라이트 리스트를 값으로 저장
        all_team_highlights[team_name] = highlights

    # 최종 결과 구조
    result_json = {
        "news_highlights": all_team_highlights
    }

    return result_json

# 디렉토리 생성 함수
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    # 일일 뉴스 하이라이트를 추출할 날짜 입력
    date = input("요약할 기준 날짜를 입력하세요 (YYYYMMDD 형식): ")

    # 모든 팀의 뉴스 요약 결과를 JSON 구조로 생성
    final_json = generate_daily_summary_json(date)
    json_path = os.path.join("news_daily_highlight", date)
    makedirs(json_path)
    file_path = os.path.join(json_path, f"news_daily_highlight_{date}.json")
    
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(final_json, json_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
