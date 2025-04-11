from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import pandas as pd
import os

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUI 없이 실행 (필요하면 제거)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 로그 관련 오류 메시지 비활성화를 위한 옵션 추가
chrome_options.add_argument("--log-level=3")  # 가장 심각한 오류만 표시
chrome_options.add_argument("--silent")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-in-process-stack-traces")
chrome_options.add_argument("--disable-crash-reporter")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# ChromeDriver를 자동으로 다운로드 및 설정
service = Service(ChromeDriverManager().install())
service.log_path = "NUL"  # 로그 출력 무시
driver = webdriver.Chrome(service=service, options=chrome_options)

# 크롤링할 URL
base_url = "https://m.sports.naver.com/kbaseball/news"

# 기사 목록 크롤링 (1페이지만, 최대 60개)
def crawl_articles(date, team):
    articles = []
    
    url = base_url + f"?sectionId=kbo&team={team}&sort=latest&date={date}&isPhoto=N"
    driver.get(url)
    time.sleep(2)  # 페이지 로딩 대기

    # 뉴스 목록 가져오기
    try:
        news_list = driver.find_elements(By.CSS_SELECTOR, "#content > div > div.NewsList_comp_news_list__oXAbN > ul > li")
        for item in news_list:
            title_element = item.find_element(By.CSS_SELECTOR, "a > div.NewsItem_info_area__Dj4oW > em")
            article_url = item.find_element(By.CSS_SELECTOR, "a.NewsItem_link_news__tD7x3").get_attribute("href")

            articles.append({
                'news_title': title_element.text.strip(),
                'article_url': article_url
            })
    except:
        pass

    return articles

# 본문 내용 추출
def get_article_content(article_url):
    driver.get(article_url)
    time.sleep(2)  # 페이지 로딩 대기

    news_content = ""
    
    try:
        # 일반적인 기사 내용 추출 시도
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "#comp_news_article > div")
        news_content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])

    except Exception as e:
        print(f"기사 내용 추출 중 오류 발생: {e}")
    
    # 내용이 없으면 메시지 설정
    if not news_content:
        news_content = "본문 추출 실패"
    
    return {
        'news_content': news_content
    }

# 뉴스 기사 크롤링
def crawl_news(date: str, team: str) -> list:
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

    published_date = date[:4] + "-" + date[4:6] + "-" + date[6:]
    team_name = team_mapping.get(team, team)

    print(f"날짜: {published_date}, 팀: {team_name},")
    
    all_articles = []
    articles = crawl_articles(date, team)
    for article in articles:
        content = get_article_content(article['article_url'])
        all_articles.append({
            'news_title': article['news_title'],
            'news_content': content['news_content'],
            'published_date': published_date
        })
    time.sleep(2)  # 요청 간 2초 대기
    
    return all_articles

# 디렉토리 생성 함수
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# json 파일로 저장하는 함수
def save_to_json(date: str, team: str, data: list):
    json_path = os.path.join("news_json", date)
    makedirs(json_path)
    file_path = os.path.join(json_path, f"news_{date}_{team}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON 파일 저장 완료: {file_path}")

def main():
    date = input("크롤링할 날짜를 입력하세요 (YYYYMMDD 형식): ")

    # KIA 타이거즈: HT, 삼성 라이온즈: SS, 두산 베어스: OB, 롯데 자이언츠: LT, KT 위즈: KT, SSG 랜더스: SK, 한화 이글스: HH, NC 다이노스: NC, 키움 히어로즈: WO, LG 트윈스: LG
    for team in ["HT", "SS", "OB", "LT", "KT", "SK", "HH", "NC", "WO", "LG"]:
        results = crawl_news(date, team)
        save_to_json(date, team, results)
        print(f"{date} {team} 크롤링 완료. 총 {len(results)}개의 기사를 저장했습니다.")
    
    driver.quit()    

if __name__ == "__main__":
    main()
