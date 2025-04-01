from dotenv import load_dotenv
import os
import json
from google import genai
from google.genai import types
from datetime import date

# Gemini API 키 설정
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def compare_weekly_saving(weekly_saving, before_weekly_saving):
    """
    이번 주와 지난 주의 주간 적금액을 비교하여 증감 비율을 판단합니다.
    """
    if before_weekly_saving == 0:
        if weekly_saving == 0:
            return "유지"
        else:
            return "비교 불가 (이전 주 적금액이 0)"
    
    change = (weekly_saving - before_weekly_saving) / before_weekly_saving * 100
    percentage_change = round(abs(change))
    
    if change > 0:
        return f"{percentage_change}% 증가"
    elif change < 0:
        return f"{percentage_change}% 감소"
    else:
        return "유지"
    
def compare_weekly_records(weekly_record, before_weekly_record):
    # 점수 계산: 승(win)=1점, 무승부(draw)=0점, 패배(lose)=-1점
    current_score = (weekly_record['win'] * 1
                     + weekly_record['draw'] * 0
                     + weekly_record['lose'] * -1)
    previous_score = (before_weekly_record['win'] * 1
                      + before_weekly_record['draw'] * 0
                      + before_weekly_record['lose'] * -1)
    
    if current_score > previous_score:
        return "상승"
    elif current_score == previous_score:
        return "유지"
    else:
        return "하락"
    
def is_target_achievable(target_amount, current_week, current_savings):
    # current_week가 0이면 평균 계산이 불가능하므로 예외 처리
    if current_week == 0:
        raise ValueError("현재 주차는 0이 될 수 없습니다. 적어도 1주차 이상이어야 합니다.")
    
    # 현재까지의 주당 평균 적금액 계산
    average_deposit = current_savings / current_week
    
    # 남은 주차 수 계산 (26주에서 현재 주차를 빼줍니다)
    remaining_weeks = 26 - current_week
    
    # 남은 주차에도 동일한 금액을 적금한다고 가정할 때, 26주 후 누적 적금액
    projected_total = current_savings + remaining_weeks * average_deposit

    # 목표액을 달성하기 위해 필요한 최소 주당 적금액 계산
    required_weekly_saving = round((target_amount - current_savings) / remaining_weeks)
    
    if projected_total >= target_amount:
        return ("목표 달성 가능", 0)
    else:
        return ("목표 달성 불가능", required_weekly_saving)  # 목표 달성을 위한 최소 주당 적금액

def generate_weekly_message(user_name, team_name, weekly_saving, before_weekly_saving, weekly_record, before_weekly_record, target):
    """
    각 데이터를 기반으로 LLM 프롬프트를 작성하여 위클리 메시지를 생성합니다.
    """
    target_name = target["target_name"]
    target_amount = target["target_amount"] 

    saving_comparison = compare_weekly_saving(weekly_saving, before_weekly_saving)
    records_comparison = compare_weekly_records(weekly_record, before_weekly_record)
    target_achievable, required_weekly_saving = is_target_achievable(target_amount, current_week, current_savings)
    
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
        - 문장의 시작은 무조건 고객 이름이 들어가야 합니다.
        - 출력 형식에 맞춰서 문장을 출력하세요.

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
        - 두 번째 문장: 현재 적금으로는 목표 달성이 어렵다는 점과, 목표를 위해 매주 {required_weekly_saving}원을 모아야 한다는 점을 강조해 주세요.
        - 예시 형식을 따라서 각각의 문장을 자연스럽고 생동감 있게 작성해주세요.
        - 문장의 시작은 무조건 고객 이름이 들어가야 합니다.
        - 출력 형식에 맞춰서 문장을 출력하세요.

        [예시]
        - {user_name}님의 이번 주 적금액은 지난 주 대비 **{saving_comparison}** 했고, 지난 주와 비교해서 **{team_name}**의 성적이 **{records_comparison}**했습니다.
        - {user_name}님의 **{target_name}**를 위한 금액이 부족할 것 같아요. 앞으로 매주 **{required_weekly_saving}원**을 적금해야 목표 달성이 가능하니, 적금액을 늘려보는 건 어떨까요?

        [출력 형식]
        - 첫 번째 문장
        - 두 번째 문장
         """
        
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="너는 야구 적금 서비스의 위클리 메시지를 작성하는 전문가야. 지난 주와 이번주의 적금액과 성적을 비교하고, 적금 목표 달성을 위한 조언을 해주는 역할을 할거야."),
    contents=prompt
    )
    
    return response.candidates[0].content.parts[0].text

# ------------------------------------------------------------------
# 예시 데이터 설정

# 고객, 팀 이름
user_name = "전제후"
team_name = "LG 트윈스"

# 주간 적금액, 이전 주간 적금액
weekly_saving = 36000
before_weekly_saving = 30000

# 주간 성적, 이전 주간 성적
weekly_record = {
    "win": 4,
    "lose": 2,
    "draw": 0
}
before_weekly_record = {
    "win": 3,
    "lose": 3,
    "draw": 0
}

# 현재 누적 적금액
current_savings = 154000

# 현재 적금 주차
today = date.today()
year, week_number, weekday = today.isocalendar()
current_week = week_number - 12

# 목표와 적금액
target = {"target_name": "시즌권 구매",
          "target_amount": 1500000
}

# ------------------------------------------------------------------

# 위클리 메시지 생성
weekly_message = generate_weekly_message(user_name, team_name, weekly_saving, before_weekly_saving, weekly_record, before_weekly_record, target)
print(weekly_message)
