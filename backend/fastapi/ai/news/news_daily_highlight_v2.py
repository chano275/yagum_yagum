import os
import json
import re
import torch
import time
from exaone_model import model, tokenizer

# 뉴스 요약 인스트럭션 정의
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

def generate_content(all_news: list, max_new_tokens: int = 384) -> str:
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": f"다음은 뉴스 요약 정보입니다:\n{json.dumps(all_news, ensure_ascii=False, indent=2)}\n요약 결과를 JSON 형식으로 반환해주세요."}
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id
        )

    result = tokenizer.decode(output[0], skip_special_tokens=True)
    if "[|assistant|]" in result:
        result = result.split("[|assistant|]")[-1].strip()
    return result

def summarize_daily_news(date, team):
    all_news = []
    json_file_path = f"news_json/{date}/news_{date}_{team}.json"

    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            for item in data:
                all_news.append({
                    "news_title": item.get("news_title", ""),
                    "news_summary": item.get("news_summary", ""),
                    "published_date": item.get("published_date", "")
                })

    if not all_news:
        return ""

    return generate_content(all_news)

def generate_daily_summary_json(date):
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

    all_team_highlights = {}

    for team_code, team_name in team_mapping.items():
        raw_result = summarize_daily_news(date, team_code)
        json_regex = re.compile(r"(\{.*\})", re.DOTALL)
        match = json_regex.search(raw_result)

        if match:
            try:
                highlights = json.loads(match.group(1)).get("news_highlight", [])
            except json.JSONDecodeError:
                highlights = []
        else:
            highlights = []

        all_team_highlights[team_name] = highlights
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        time.sleep(1)

    return {"news_highlights": all_team_highlights}

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    date = input("요약할 기준 날짜를 입력하세요 (YYYYMMDD 형식): ")
    final_json = generate_daily_summary_json(date)

    json_path = "news_daily_highlight"
    makedirs(json_path)

    file_path = os.path.join(json_path, f"news_daily_highlight_{date}.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(final_json, json_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
