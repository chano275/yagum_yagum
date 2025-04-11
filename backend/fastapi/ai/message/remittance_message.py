import os
import json
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ------------------------
# 환경 변수 로드 및 Gemini API 설정
# ------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------
# 계좌 정보에 뉴스 하이라이트 병합하는 함수
# ------------------------
def merge_news_highlights(accounts_data, news_data):
    """
    accounts_data의 각 계좌에서 'our_team' 값을 기준으로,
    news_data의 news_highlights에서 해당 팀에 해당하는 뉴스를 찾아
    계좌 정보에 "news_highlights" 필드로 추가

    만약 해당 팀에 대한 뉴스가 없다면 빈 리스트를 할당
    """
    for account in accounts_data.get("accounts", {}).values():
        team_name = account.get("our_team", "")
        # news_data에서 팀 이름과 일치하는 뉴스 목록 추출
        account["news_highlights"] = news_data.get("news_highlights", {}).get(team_name, [])
    
    return accounts_data

# ------------------------
# LLM 기반 송금 메시지 생성 함수
# ------------------------
def generate_remittance_message(account_id, account, report_date):
    """
    각 데이터를 기반으로 LLM 프롬프트를 작성하여 송금 메시지를 생성하여 JSON 형태로 반환
    """
    # 데이터 준비
    our_team = account["our_team"]
    opposing_team = account["opposing_team"]
    favorite_player = account["favorite_player"]
    saving_goal = account["saving_goal"]
    savings_rules = account["savings_rules"]
    game_results = account["game_results"]
    original_outcome = account["original_outcome"]
    real_outcome = account["real_outcome"]
    news_highlights = account["news_highlights"]

     # 목표 금액 -> 목표 이름 매핑
    saving_goal_mapping = {
        500000:  "유니폼 구매",
        1000000: "다음 시즌 직관",
        1500000: "시즌권 구매",
        3000000: "스프링캠프"
    }
    saving_goal_name = saving_goal_mapping.get(saving_goal, "잘못된 목표 금액")

    # 시스템 프롬프트 & 본문 프롬프트 구성
    system_instruction = (
        "너는 야구 적금 서비스의 송금 메시지를 작성하는 전문가야"
        "어제의 경기 결과와 뉴스 하이라이트, 적금액을 입력받아서, 송금한 내용을 의미있게 요약해주는 역할을 할거야"
    )
    
    prompt = f"""
    다음 정보를 바탕으로 송금 메시지를 작성해주세요.

    [입력 데이터]
    - 응원하는 팀 이름: {our_team}
    - 상대 팀 이름: {opposing_team}
    - 응원하는 선수 이름: {favorite_player}
    - 적금 목표 : {saving_goal_name}
    - 적금 규칙: {savings_rules}
    - 경기 결과 : {game_results}
    - 경기 결과에 따른 적금액 : {original_outcome}
    - 실제 송금액 : {real_outcome}
    - 뉴스 하이라이트 : {news_highlights}

    [작성 조건]
    - 첫 번째 문장: 오늘의 경기결과와 뉴스 하이라이트에서 우리 팀의 주요 성과를 요약하세요.
    - 두 번째 문장: 뉴스 하이라이틀르 바탕으로, 내가 응원하는 최애선수의 활약을 강조하고 적금액을 요약하세요.
    - 세 번째 문장: 적금 목표와 적금액을 요약하고 격려와 응원의 메세지를 작성하세요.
    - 전체 문장은 3문장으로 구성되어야 합니다.
    - 작성된 문장들을 바탕으로 아래 예시들을 참조하여 줄바꿈을 포함해 출력하세요.

    [예시]
    "LG가 8:5로 NC를 꺾으며 홈런 3개로 역전!
    오지환의 홈런에 힘입어 오늘은 26,000원 적립 성공!
    내년 직관 자금도 한 걸음 더 가까워졌어요!"
    ---
    "두산이 5:4로 롯데를 꺾으며 끝내기 홈런까지 터졌습니다!
    박건우 덕분에 오늘은 총 25,000원 적립 완료!
    새 유니폼 입는 날도 머지않았네요."
    ---
    "LG가 8:5로 NC를 누르며 3방의 홈런쇼!
    오지환 홈런 포함 총 26,000원 적립 완료!
    하루 만에 통장이 훌쩍 불어났네요."
    ---
    "삼성이 6:4로 키움을 제압했네요!
    이학주 2안타·도루로 맹활약해 적금액 32,500원 달성!
    활발한 타선만큼 통장도 든든해집니다."

    [출력 형식]
    "첫 번째 문장
    두 번째 문장
    세 번째 문장"
    """
        
    # 생성 요청
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=prompt
    )

    # 결과 추출
    remittance_message = response.candidates[0].content.parts[0].text

    # JSON 형태로 반환
    return {
        "account_id": account_id,
        "date": report_date,
        "text": remittance_message
    }

# ------------------------
# 메인 실행부
# ------------------------
def main():
    """
    예시 input_data 처리 후 결과 출력 및 파일 저장
    """
    account_data = {
        "accounts": {
            "1": {
                "our_team": "SSG 랜더스",
                "opposing_team": "KT 위즈",
                "favorite_player": "박성한",
                "saving_goal": 100000,
                "savings_rules": {
                    "우리팀_승리": 3000,
                    "우리팀_안타": 500,
                    "우리팀_홈런": 1000,
                    "선수_안타": 500,
                    "선수_홈런": 3000
                },
                "game_results": {
                    "우리팀_승리": 0,
                    "우리팀_안타": 0,
                    "우리팀_홈런": 0,
                    "선수_안타": 0,
                    "선수_홈런": 0
                },
                "original_outcome": 0,
                "real_outcome": 0
            },
            "2": {
                "our_team": "KIA 타이거즈",
                "opposing_team": "LG 트윈스",
                "favorite_player": "김도영",
                "saving_goal": 500000,
                "savings_rules": {
                    "우리팀_승리": 500
                },
                "game_results": {
                    "우리팀_승리": 0
                },
                "original_outcome": 0,
                "real_outcome": 0
            }
        },
        "date": "2025-04-05",
        "total_accounts": 2,
        "accounts_with_games": 2
    }

    news_data = {
        "news_highlights": {
            "KIA 타이거즈": [
                "KIA 위즈덤, 3경기 연속 홈런으로 팀 연패 탈출에 기여하며 류현진 무너뜨려",
                "KIA 조상우, 구속과 구위 향상 다짐하며 팀 불펜진 강화에 힘쓸 것을 약속",
                "KIA 김규성, 주전 유격수 공백을 메우며 남다른 노력으로 기회를 잡아"
            ],
            "KT 위즈": [
                "강백호, 2025년 첫 포수 선발 출전했지만 KT는 롯데와 연장 접전 끝에 무승부 기록",
                "쿠에바스, QS 19번에도 불구하고 올해도 승운 없어 팬들의 안타까움 자아내",
                "이강철 감독, 박영현 제구력 보완 필요성 지적하며 긍정적 평가와 함께 성장 기대"
            ],
            "SSG 랜더스": [
                "SSG, 한유섬 홈런과 문승원 호투로 키움에 8-2 승리하며 2연패 탈출",
                "문승원, 541일 만의 선발승으로 SSG 연패 끊고 성공적인 복귀",
                "한유섬, 시즌 첫 홈런으로 팀 승리 기여하며 동료들에게 격려 메시지 전달"
            ],
            "LG 트윈스": [
                "LG 김영우, 데뷔전서 157km 강속구로 2K 무실점 기록하며 성공적인 데뷔",
                "LG, 투타 조화로 창단 첫 개막 7연승 달성 및 KBO 역대 최다 연승 기록에 도전",
                "LG 오스틴 딘, 개인 타이틀보다 팀 우승 집중하며 3점 홈런으로 팀 승리 기여"
            ]
        }
    }
    
    # 계좌 정보와 뉴스 하이라이트 병합
    input_data = merge_news_highlights(account_data, news_data)

    # 데이터 추출
    report_date = input_data['date']

    # 결과 생성
    remittance_message = []
    for account_id, account in input_data['accounts'].items():
        remittance_message_message_output = generate_remittance_message(account_id, account, report_date)
        remittance_message.append(remittance_message_message_output)
        # 결과 확인
        print(remittance_message_message_output)

    # 최종 JSON 저장
    output_json = {"remittance_message": remittance_message}
    with open("test_json/remittance_message_output.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
