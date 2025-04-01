from dotenv import load_dotenv
import os
import json
from google import genai
from google.genai import types

# Gemini API 키 설정
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def compare_team_money(total_daily_saving, opponent_total_daily_saving):
    """
    우리팀 송금액과 상대팀 송금액을 비교하여 우세 여부 판단
    """
    if total_daily_saving > opponent_total_daily_saving:
        return "우리 팀 송금액 우세"
    elif total_daily_saving < opponent_total_daily_saving:
        return "상대 팀 송금액 우세"
    else:
        # 동일한 경우
        return "송금액 동일"

'''
def extract_favorite_player_news(news_path, favorite_player):
    """
    JSON 형태의 뉴스 데이터에서 news_title에 favorite_player의 이름이 포함된 기사들을 추출합니다.
    존재하는 경우, 첫 번째 기사(또는 요약된 내용을) 반환하고, 없으면 빈 문자열을 반환합니다.
    """
    with open(news_path, "r", encoding="utf-8") as f:
        news_data = json.load(f)

    articles = [article for article in news_data if favorite_player.lower() in article["news_title"].lower()]
    if articles:
        return articles
    else:
            return ""
'''

def generate_daily_message(team, opponent, game_record, total_daily_saving, opponent_total_daily_saving):
    """
    각 데이터를 기반으로 LLM 프롬프트를 작성하여 데일리 메시지를 생성
    """
    money_comparison = compare_team_money(total_daily_saving, opponent_total_daily_saving)
    # favorite_player_news = extract_favorite_player_news(news_path, favorite_player)

    # 최애선수 뉴스가 존재하지 않는 경우
    prompt = f"""
    다음 정보를 바탕으로 야구팀 데일리 메시지를 작성해주세요.

    [입력 데이터]
    - 경기 기록: {game_record}
    - 팀 송금액 비교: {money_comparison} 
    - 우리 팀: {team}
    - 상대 팀: {opponent}

    [조건]
    1. 경기 기록에 따라 승리, 패배, 무승부에 맞는 메시지를 작성합니다.
    2. 팀 송금액 비교 결과에 따라 팬들의 응원과 송금액의 차이가 경기 결과에 미친 영향을 언급합니다.
    3. 메시지는 각 야구팀의 특성을 살려 친근하면서도 생동감 있게 작성되어야 합니다.

    최종 메시지를 한 문장으로 작성해주세요.

    [예시]
    1. 승리 & 우리 팀 송금액 우세
    - {team}의 승리를 축하합니다! 쏟아지는 응원과 함께 우리 팀의 두둑한 송금액이 승리를 더욱 빛나게 하네요! {team} 최고!
    - 승리의 함성! 오늘, {team}은 승리와 함께 팬들의 사랑을 한 몸에 받았습니다! 압도적인 송금액이 보여주듯, 우리 팀을 향한 열정은 그 누구도 따라올 수 없죠!

    2. 승리 & 상대 팀 송금액 우세
    - 승리의 기쁨, 아쉬운 뒷맛! 승리를 거머쥐었지만, 상대 팀의 뜨거운 응원 열기에 송금액은 아쉽게도 뒤처졌네요. 다음 경기에는 더욱 뜨거운 함성으로 우리 선수들에게 힘을 실어주세요!
    - 승리했지만, 아직 목마르다! 값진 승리에도 불구하고, 송금액은 상대 팀의 벽을 넘지 못했습니다. 우리 선수들이 더욱 힘낼 수 있도록, 팬 여러분의 뜨거운 응원이 필요합니다!

    3. 패배 & 우리 팀 송금액 우세
    - 패배 속 빛나는 팬심! 비록 경기는 아쉽게 졌지만, 우리 팀을 향한 팬들의 뜨거운 마음은 송금액으로 증명되었습니다! 다음 경기, 이 뜨거운 응원을 승리로 이어갈 수 있도록 함께 응원해요!
    - 패배에도 고개 숙이지 않는다! 아쉬운 패배에도 불구하고, 우리 팀의 송금액은 상대 팀을 압도했습니다! 이 뜨거운 응원, 우리 선수들에게 큰 힘이 될 겁니다!

    4. 패배 & 상대 팀 송금액 우세
    - 쓴 패배, 더욱 뜨거운 응원! 오늘은 아쉽게 패배했지만, 우리 선수들은 팬들의 응원을 잊지 않을 겁니다! 다음 경기, 더욱 뜨거운 함성으로 우리 선수들에게 힘을 불어넣어 주세요!
    - 패배는 쓰지만, 희망은 버리지 않는다! 오늘 패배는 아쉽지만, 우리 팀은 더욱 강해질 겁니다! 팬 여러분의 응원이 있다면, 어떤 어려움도 이겨낼 수 있습니다!
    - 패배의 눈물, 승리의 다짐! 오늘 패배를 발판 삼아, 우리 선수들은 더욱 강해질 겁니다! 다음 경기, 더욱 발전된 경기력을 보여줄 수 있도록 응원 부탁드립니다.

    5. 무승부 & 우리 팀 송금액 우세
    - {team}과 {opponent}의 치열한 접전 끝에 무승부로 경기가 종료되었습니다! 상대 팀보다 높은 송금액은, 팬 여러분의 응원이 얼마나 뜨거웠는지 보여줍니다! 다음 경기도 뜨거운 응원 부탁드립니다!
    - 무승부의 아쉬움, 승리의 염원! 오늘 경기는 무승부로 끝났지만, 우리 팀의 송금액은 상대 팀을 압도했습니다! 다음 경기에는 더욱 좋은 결과를 기대해봅니다.

    6. 무승부 & 상대 팀 송금액 우세
    - {team}과 {opponent}의 치열한 접전 끝에 무승부로 경기가 종료되었습니다! 아쉽게도 송금액은 상대 팀이 앞섰지만, 다음 경기에는 더욱 뜨거운 응원으로 우리 선수들에게 힘을 실어주세요!
    - 양 팀 모두 최선을 다했지만, 승부를 가리지 못했습니다! 송금액 경쟁에서는 아쉽게 뒤처졌지만, 다음 경기에는 더욱 뜨거운 함성으로 우리 선수들을 응원합시다!
    """
    
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="너는 야구 적금 서비스의 데일리 메시지를 작성하는 전문가야"),
    contents=prompt
    )
    
    return response.candidates[0].content.parts[0].text

# ------------------------------------------------------------------
# 예시 데이터 설정

# 우리 팀과 상대팀 이름
team = "LG 트윈스"
opponent = "한화 이글스"

# 경기 기록
game_record = "승리"

# 팀 송금액 (숫자 데이터)
total_daily_saving = 1500000
opponent_total_daily_saving = 1500000

# ------------------------------------------------------------------
# 데일리 메시지 생성
daily_message = generate_daily_message(team, opponent, game_record, total_daily_saving, opponent_total_daily_saving)
print(daily_message)
