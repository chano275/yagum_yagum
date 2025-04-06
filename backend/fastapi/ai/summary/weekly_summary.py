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
# 계산/비교 관련 함수들
# ------------------------
def compare_weekly_saving(weekly_saving, before_weekly_saving):
    """
    이번 주와 지난 주의 주간 적금액을 비교하여 증감 비율을 판단합니다.
    """
    if before_weekly_saving == 0:
        return "유지" if weekly_saving == 0 else "비교 불가 (이전 주 적금액이 0)"
    
    change = (weekly_saving - before_weekly_saving) / before_weekly_saving * 100
    percentage_change = round(abs(change))
    
    if change > 0:
        return f"{percentage_change}% 증가"
    elif change < 0:
        return f"{percentage_change}% 감소"
    else:
        return "유지"
    
def compare_weekly_records(weekly_record, before_weekly_record):
    """
    이번 주와 지난 주의 팀 성적을 비교하여 상승, 유지, 하락 여부를 판단합니다.
    """
    # 점수 계산: 승(win)=1점, 무승부(draw)=0점, 패배(lose)=-1점
    score = lambda x: x['win'] * 1 + x['lose'] * -1  # draw는 0점이므로 제외
    current_score, previous_score = score(weekly_record), score(before_weekly_record)
    
    if current_score > previous_score:
        return "상승"
    elif current_score == previous_score:
        return "유지"
    return "하락"
    
def is_target_achievable(target_amount, current_week, current_savings):
    """
    현재 주차와 누적 적금액을 기반으로 목표 달성 가능 여부와 필요한 추가 적금액을 계산
    """
    if current_week == 0:
        raise ValueError("현재 주차(current_week)는 1 이상이어야 합니다.")
    
    average_deposit = current_savings / current_week  # 현재까지의 주당 평균 적금액 계산
    remaining_weeks = 26 - current_week  # 남은 주차 수 계산
    projected_total = current_savings + remaining_weeks * average_deposit  # 남은 주차에도 동일한 금액을 적금한다고 가정할 때, 26주 후 누적 적금액
    required_weekly_saving = round((target_amount - current_savings) / remaining_weeks)  # 목표액을 달성하기 위해 필요한 최소 주당 적금액 계산
    
    if projected_total >= target_amount:
        return ("목표 달성 가능", 0)
    return ("목표 달성 불가능", required_weekly_saving)  # 목표 달성을 위한 최소 주당 적금액

# ------------------------
# LLM 기반 위클리 메시지 생성 함수
# ------------------------
def generate_weekly_message(account, report_date, current_week):
    """
    각 데이터를 기반으로 LLM 프롬프트를 작성하여 위클리 메시지를 생성하여 JSON 형태로 반환
    """
    # 데이터 준비
    account_id = account['account_id']
    user_name = account['user_name']
    team_name = account['team_name']
    weekly_saving = account['weekly_saving']
    before_weekly_saving = account['before_weekly_saving']
    weekly_record = account['weekly_record']
    before_weekly_record = account['before_weekly_record']
    current_savings = account['current_savings']
    target_amount = account['target_amount']

     # 목표 금액 -> 목표 이름 매핑
    target_mapping = {
        500000:  "유니폼 구매",
        1000000: "다음 시즌 직관",
        1500000: "시즌권 구매",
        3000000: "스프링캠프"
    }
    target_name = target_mapping.get(target_amount, "잘못된 목표 금액")

    # 데이터 비교/계산
    saving_comparison = compare_weekly_saving(weekly_saving, before_weekly_saving)
    records_comparison = compare_weekly_records(weekly_record, before_weekly_record)
    target_achievable, required_weekly_saving = is_target_achievable(target_amount, current_week, current_savings)

    # 시스템 프롬프트 & 본문 프롬프트 구성
    system_instruction = (
        "너는 야구 적금 서비스의 위클리 메시지를 작성하는 전문가야"
        "지난 주와 이번 주의 적금액 및 팀 성적을 비교하고, 적금 목표 달성을 위한 조언을 해주는 역할을 할거야"
    )
    
    # 목표 달성 여부에 따라 다른 메시지 템플릿 사용
    if target_achievable == "목표 달성 가능":
        prompt = f"""
        다음 정보를 바탕으로 야구팀 위클리 메시지를 작성해주세요.

        [입력 데이터]
        - 고객 이름: {user_name}
        - 응원하는 팀 이름: {team_name}
        - 주간 적금액: {weekly_saving}원
        - 주간 적금액 비교 : {saving_comparison}
        - 주간 성적: {weekly_record}
        - 주간 성적 비교 : {records_comparison}
        - 적금 목표 : {target_name}
        - 목표 달성 가능성 : {target_achievable}

        [작성 조건]
        - 첫 번째 문장: 이번 주 적금액이 지난 주 대비 어느 정도 변했는지({saving_comparison}), 그리고 팀 성적이 어떻게 변했는지({records_comparison})를 자연스럽게 연결해 주세요.
        - 두 번째 문장: 목표 달성을 위한 금액이 충분히 모이고 있다는 사실과, 이대로 계속 유지해달라는 점을 언급해주세요.
        - 예시 형식을 따라서 각각의 문장을 자연스럽고 생동감 있게 작성해주세요.
        - 문장의 시작은 무조건 고객 이름으로 시작해야 합니다.
        - 출력 형식에 맞춰서 문장별로 한 줄씩 출력하세요.

        [예시]
        - {user_name}님의 이번 주 적금액은 지난 주 대비 **{saving_comparison}** 했고, 지난 주와 비교해서 **{team_name}**의 성적이 **{records_comparison}**했습니다.
        - {user_name}님의 **{target_name}**를 위한 금액이 충분히 모이고 있습니다. 지금처럼만 계속 유지해서 **{target_name}** 달성해봐요!

        [출력 형식]
        - 첫 번째 문장
        - 두 번째 문장
        """
    else:
        prompt = f"""
        다음 정보를 바탕으로 야구팀 위클리 메시지를 작성해주세요.

        [입력 데이터]
        - 고객 이름: {user_name}
        - 주간 적금액: {weekly_saving}원
        - 주간 적금액 비교 : {saving_comparison}
        - 주간 성적: {weekly_record}
        - 주간 성적 비교 : {records_comparison}
        - 적금 목표 : {target_name}
        - 목표 달성 가능성 : {target_achievable}
        - 목표 달성을 위한 최소 적금액 : {required_weekly_saving}원

        [작성 조건]
        - 첫 번째 문장: 이번 주 적금액이 지난 주 대비 어느 정도 변했는지({saving_comparison}), 그리고 팀 성적이 어떻게 변했는지({records_comparison})를 자연스럽게 연결해 주세요.
        - 두 번째 문장: 현재 적금으로는 목표 달성이 어렵다는 점과, 목표를 위해 매주 {required_weekly_saving}원을 모아야 한다는 점을 강조해주세요.
        - 예시 형식을 따라서 각각의 문장을 자연스럽고 생동감 있게 작성해주세요.
        - 문장의 시작은 무조건 고객 이름으로 시작해야 합니다.
        - 출력 형식에 맞춰서 문장별로 한 줄씩 출력하세요.

        [예시]
        - {user_name}님의 이번 주 적금액은 지난 주 대비 **{saving_comparison}** 했고, 지난 주와 비교해서 **{team_name}**의 성적이 **{records_comparison}**했습니다.
        - {user_name}님의 **{target_name}**를 위한 금액이 부족할 것 같아요. 앞으로 매주 **{required_weekly_saving}원**을 적금해야 목표 달성이 가능하니, 적금 규칙을 조정해보는 것은 어떨까요?

        [출력 형식]
        - 첫 번째 문장
        - 두 번째 문장
         """
        
    # 생성 요청
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=prompt
    )

    # 결과 추출
    weekly_text = response.candidates[0].content.parts[0].text

    # JSON 형태로 반환
    return {
        "account_id": account_id,
        "date": report_date,
        "weekly_text": weekly_text
    }

# ------------------------
# 메인 실행부
# ------------------------
def main():
    """
    예시 input_data 처리 후 결과 출력 및 파일 저장
    """
    input_data = {
    "accounts_data": [
        {
        "account_id": 1,
        "user_name": "김의찬",
        "team_name": "SSG 랜더스",
        "weekly_saving": 34000,
        "before_weekly_saving": 25000,
        "weekly_record": {
            "win": 4,
            "lose": 2,
            "draw": 0
        },
        "before_weekly_record": {
            "win": 3,
            "lose": 3,
            "draw": 0
        },
        "current_savings": 120000,
        "target_amount": 1000000
        },
        {
        "account_id": 2,
        "user_name": "김수민",
        "team_name": "KIA 타이거즈",
        "weekly_saving": 15000,
        "before_weekly_saving": 17000,
        "weekly_record": {
            "win": 0,
            "lose": 6,
            "draw": 0
        },
        "before_weekly_record": {
            "win": 2,
            "lose": 4,
            "draw": 0
        },
        "current_savings": 20000,
        "target_amount": 500000
        }
    ],
    "total_accounts": 2,
    "report_date": "2025-04-05"
    }

    # 데이터 추출
    data_list = input_data['accounts_data']
    report_date = input_data['report_date']

    # 현재 적금 주차
    _, week_number, _ = date.today().isocalendar()
    current_week = week_number - 12

    # 결과 생성
    reports = []
    for account in data_list:
        weekly_message_output = generate_weekly_message(account, report_date, current_week)
        reports.append(weekly_message_output)
        print(weekly_message_output)

    # 최종 JSON 저장
    output_json = {"reports": reports}
    with open("test_json/weekly_message_output.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
