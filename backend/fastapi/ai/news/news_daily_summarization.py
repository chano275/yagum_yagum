import os
import json
from news_summarizer import summarize_news_item

def add_summaries_in_place(date: str):
    """
    주어진 날짜(YYYYMMDD)에 대해,
    news_json/{date}/news_{date}_{team_code}.json 파일을 찾아
    각 뉴스 항목에 news_summary 필드로 요약문을 추가한 뒤
    기존 파일을 덮어쓴다.
    """
    # 1) 날짜별 폴더 경로
    date_folder = os.path.join("news_json", date)
    
    # 만약 폴더가 없으면 종료
    if not os.path.isdir(date_folder):
        print(f"폴더가 존재하지 않습니다: {date_folder}")
        return

    # 2) 팀 코드별로 파일 탐색
    # 팀 코드 목록
    TEAM_CODES = ["HH", "HT", "KT", "LG", "LT", "NC", "OB", "SK", "SS", "WO"]

    for team_code in TEAM_CODES:
        file_name = f"news_{date}_{team_code}.json"
        json_path = os.path.join(date_folder, file_name)

        # 해당 파일이 없으면 넘어감
        if not os.path.exists(json_path):
            continue

        # 3) 파일 열기
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        updated_data = []
        for news_item in data:
            news_title = news_item.get("news_title", "")
            news_content = news_item.get("news_content", "")

            # 제목과 본문이 비어있으면 요약 없이 그대로 유지
            if not news_title and not news_content:
                updated_data.append(news_item)
                continue

            # 4) EXAONE 모델로 요약 호출
            summary = summarize_news_item(news_title, news_content, max_new_tokens=512)
            
            # 5) news_item에 요약 결과를 news_summary 필드로 추가
            news_item["news_summary"] = summary
            updated_data.append(news_item)

        # 6) 기존 파일 덮어쓰기
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        print(f"[완료] {json_path} 파일에 요약이 추가되었습니다.")

if __name__ == "__main__":
    date = input("요약할 날짜를 입력하세요 (YYYYMMDD): ")
    add_summaries_in_place(date)
