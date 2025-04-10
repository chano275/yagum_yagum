import os
import json
import torch
from exaone_model import model, tokenizer

def summarize_news_item(news_title: str, news_content: str, max_new_tokens: int = 384) -> str:
    prompt = f"""
    다음 정보를 바탕으로 뉴스를 요약해서 정리해주세요.

    [입력 데이터]
    - 뉴스 제목: {news_title}
    - 뉴스 내용: {news_content}

    [작성 조건]
    - 생성되는 텍스트는 순수한 일반 텍스트 형식이어야 하며, 어떠한 마크다운 문법(예: **, ## 등)도 사용하지 말아주세요.
    - 군더더기 표현(중복·불필요한 수식) 없이 중요한 사실만 요약해야 합니다.
    - 지나치게 축약하여 의미가 손실되지 않도록 유의해주세요.
    - 5줄 이내로 핵심만 간결하게 요약해주세요.
    """

    messages = [
        {"role": "system", "content": "당신은 야구 뉴스를 요약해서 정리해주는 도우미입니다."},
        {"role": "user", "content": prompt}
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    output = model.generate(
        input_ids.to("cuda"),
        max_new_tokens=max_new_tokens,
        do_sample=False,
        eos_token_id=tokenizer.eos_token_id
    )

    # 캐시 정리
    if torch.cuda.is_available():
        torch.cuda.empty_cache()    
        torch.cuda.ipc_collect()

    result = tokenizer.decode(output[0], skip_special_tokens=True)
    if "[|assistant|]" in result:
        result = result.split("[|assistant|]")[-1].strip()
    return result

def add_summaries_in_place(date: str):
    date_folder = os.path.join("news_json", date)
    if not os.path.isdir(date_folder):
        print(f"폴더가 존재하지 않습니다: {date_folder}")
        return

    TEAM_CODES = ["HH", "HT", "KT", "LG", "LT", "NC", "OB", "SK", "SS", "WO"]

    for team_code in TEAM_CODES:
        json_path = os.path.join(date_folder, f"news_{date}_{team_code}.json")
        if not os.path.exists(json_path):
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        updated_data = []
        for news_item in data:
            title = news_item.get("news_title", "")
            content = news_item.get("news_content", "")

            if not title and not content:
                updated_data.append(news_item)
                continue

            summary = summarize_news_item(title, content)
            news_item["news_summary"] = summary
            updated_data.append(news_item)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        print(f"[완료] {json_path} 파일에 요약이 추가되었습니다.")

def main():
    date = input("요약할 날짜를 입력하세요 (YYYYMMDD): ")
    add_summaries_in_place(date)

if __name__ == "__main__":
    main()
