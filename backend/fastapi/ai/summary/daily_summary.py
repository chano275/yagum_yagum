import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ------------------------
# 환경변수 로드 및 Gemini API 설정
# ------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def compare_team_money(total_daily_saving, opponent_total_daily_saving):
    """
    우리 팀과 상대 팀의 송금액을 비교해 우세 여부 판단
    """
    if total_daily_saving > opponent_total_daily_saving:
        return "우리 팀 송금액 우세"
    elif total_daily_saving < opponent_total_daily_saving:
        return "상대 팀 송금액 우세"
    return "송금액 동일"

def generate_daily_message(team_data, report_date):
    """
    LLM 프롬프트로 데일리 메시지를 생성 후 JSON 형식 반환
    """
    # 데이터 준비
    team_id = team_data["team_id"]
    team_name = team_data["team"]
    opponent_name = team_data["opponent"]
    game_record = team_data["game_record"]
    total_daily_saving = team_data["total_daily_saving"]
    opponent_total_daily_saving = team_data["opponent_total_daily_saving"]

    money_comparison = compare_team_money(total_daily_saving, opponent_total_daily_saving)
    # favorite_player_news = extract_favorite_player_news(news_path, favorite_player)

    # 시스템 프롬프트 & 본문 프롬프트 구성
    system_instruction = (
        "너는 야구 적금 서비스의 데일리 메시지를 작성하는 전문가야"
        "어제의 팀 성적과, 팀의 전체 송금액을 비교하고 요약하여 팬들에게 메세지를 전달하는 역할을 할거야"
    )

    prompt = f"""
    다음 정보를 바탕으로 야구팀 데일리 메시지를 작성해주세요.

    [입력 데이터]
    - 우리 팀 이름: {team_name}
    - 상대 팀 이름: {opponent_name}
    - 경기 기록: {game_record}
    - 송금액 비교 결과: {money_comparison}
    - 우리 팀 송금액: {total_daily_saving}
    - 상대 팀 송금액: {opponent_total_daily_saving}

    [조건]
    1. 경기 기록(승리/패배/무승부)에 맞춰 메시지를 작성하세요.
    2. 송금액 비교 결과에 따라 팬들의 응원과 송금액 차이를 간접적으로 언급하세요.
    3. 한 줄의 문장으로 작성하되, 메시지는 긍정적이고 생동감있게 마무리하세요.
    4. 문장 시작은 반드시 우리 팀 이름으로 시작하세요.
    5. 송금액을 숫자로 직접 언급하지 말고, 차이가 있다는 느낌만 전달하세요.
    """
    
    # 생성 요청
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=prompt
    )

    # 결과 추출
    daily_text = response.candidates[0].content.parts[0].text

    # JSON 형태로 반환
    return {
        "team_id": team_id,
        "date": report_date,
        "daily_text": daily_text
    }

# ------------------------------------------------------------------
def main():
    # 예시 데이터 설정
    input_data = {
        "date": "2025-03-23",
        "teams_data": [
            {
                "team_id": 1,
                "team": "KIA 타이거즈",
                "opponent": "NC 다이노스",
                "game_record": "무승부",
                "total_daily_saving": 9000000,
                "opponent_total_daily_saving": 6000000
            },
            {
                "team_id": 2,
                "team": "삼성 라이온즈",
                "opponent": "키움 히어로즈",
                "game_record": "승리",
                "total_daily_saving": 3000000,
                "opponent_total_daily_saving": 7500000
            },
            {
                "team_id": 3,
                "team": "LG 트윈스",
                "opponent": "롯데 자이언츠",
                "game_record": "승리",
                "total_daily_saving": 1000000,
                "opponent_total_daily_saving": 5000000
            },
            {
                "team_id": 4,
                "team": "두산 베어스",
                "opponent": "SSG 랜더스",
                "game_record": "패배",
                "total_daily_saving": 6500000,
                "opponent_total_daily_saving": 2000000
            },
            {
                "team_id": 5,
                "team": "KT 위즈",
                "opponent": "한화 이글스",
                "game_record": "승리",
                "total_daily_saving": 4000000,
                "opponent_total_daily_saving": 1500000
            },
            {
                "team_id": 6,
                "team": "SSG 랜더스",
                "opponent": "두산 베어스",
                "game_record": "승리",
                "total_daily_saving": 2000000,
                "opponent_total_daily_saving": 6500000
            },
            {
                "team_id": 7,
                "team": "롯데 자이언츠",
                "opponent": "LG 트윈스",
                "game_record": "패배",
                "total_daily_saving": 5000000,
                "opponent_total_daily_saving": 1000000
            },
            {
                "team_id": 8,
                "team": "한화 이글스",
                "opponent": "KT 위즈",
                "game_record": "패배",
                "total_daily_saving": 1500000,
                "opponent_total_daily_saving": 4000000
            },
            {
                "team_id": 9,
                "team": "NC 다이노스",
                "opponent": "KIA 타이거즈",
                "game_record": "무승부",
                "total_daily_saving": 6000000,
                "opponent_total_daily_saving": 9000000
            },
            {
                "team_id": 10,
                "team": "키움 히어로즈",
                "opponent": "삼성 라이온즈",
                "game_record": "패배",
                "total_daily_saving": 7500000,
                "opponent_total_daily_saving": 3000000
            }
        ]
    }

    data_list = input_data["teams_data"]
    report_date = input_data["date"]

    reports = []
    for account in data_list:
        # 각 팀의 정보를 기반으로 데일리 메시지 생성
        daily_message_output = generate_daily_message(account, report_date)
        reports.append(daily_message_output)
        print(daily_message_output)

    output_json = {"reports": reports}
    with open("test_json/daily_message_output.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
