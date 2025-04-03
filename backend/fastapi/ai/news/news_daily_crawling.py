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
base_url = "https://sports.news.naver.com/kbaseball/news/index"

# 최대 페이지 수 계산
def get_max_page(date, team):
    url = base_url + f"?date={date}&team={team}&page=1&isphoto=N&type=team"
    driver.get(url)
    time.sleep(2)  # 페이지 로딩 대기

    try:
        pagination = driver.find_element(By.CLASS_NAME, "paginate")
        pages = pagination.find_elements(By.TAG_NAME, "a")
        return int(pages[-1].text) if pages else 1
    except:
        return 1

# 기사 목록 크롤링
def crawl_articles(date, team, max_page):
    articles = []
    
    for page in range(1, max_page + 1):
        url = base_url + f"?date={date}&team={team}&page={page}&isphoto=N&type=team"
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

        # 뉴스 목록 가져오기
        try:
            news_list = driver.find_elements(By.CSS_SELECTOR, "#_newsList > ul > li")
            for item in news_list:
                title_element = item.find_element(By.CSS_SELECTOR, ".title")
                article_url = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                articles.append({
                    'news_title': title_element.text.strip().replace("\\", ""),
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
        # 일반적인 기사 내용 추출 시도 (span.article_p)
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "span.article_p")
        if paragraphs:
            news_content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        # 내용이 비어있다면 동영상 기사일 수 있으므로 다른 선택자 시도
        if not news_content:
            # 동영상 기사 내용 추출 시도 (#comp_news_article > div)
            video_content = driver.find_element(By.CSS_SELECTOR, "#comp_news_article > div")
            if video_content:
                news_content = video_content.text.strip()

    except Exception as e:
        print(f"기사 내용 추출 중 오류 발생: {e}")
    
    # 여전히 내용이 없으면 메시지 설정
    if not news_content:
        news_content = "본문 추출 실패"
    
    return {
        'news_content': news_content
    }

# 뉴스 기사 크롤링
def crawl_news(date, team):
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

    max_page = get_max_page(date, team)
    print(f"날짜: {published_date}, 팀: {team_name}, 최대 페이지 수: {max_page}")
    
    all_articles = []
    articles = crawl_articles(date, team, max_page)
    for article in articles:
        content = get_article_content(article['article_url'])
        all_articles.append({
            'news_title': article['news_title'],
            'news_content': content['news_content'],
            'published_date': published_date
        })
    time.sleep(2)  # 요청 간 2초 대기
    
    return all_articles

# CSV 저장 함수
def save_to_csv(date, data, filename="news_results.csv"):
    df = pd.DataFrame(data)
    df.to_csv(f"news_csv/{date}/{filename}", index=False, encoding="utf-8-sig")  # 한글 깨짐 방지 위해 utf-8-sig 사용
    print(f"CSV 파일 저장 완료: {filename}")

# 디렉토리 생성 함수
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    date = input("크롤링할 날짜를 입력하세요 (YYYYMMDD 형식): ")

    # 디렉토리 없는 경우 생성
    for path in [f"news_json/{date}", f"news_csv/{date}"]:
        makedirs(path)

    # KIA 타이거즈: HT, 삼성 라이온즈: SS, 두산 베어스: OB, 롯데 자이언츠: LT, KT 위즈: KT, SSG 랜더스: SK, 한화 이글스: HH, NC 다이노스: NC, 키움 히어로즈: WO, LG 트윈스: LG
    for team in ["HT", "SS", "OB", "LT", "KT", "SK", "HH", "NC", "WO", "LG"]:
        results = crawl_news(date, team)
        
        with open(f"news_json/{date}/news_{date}_{team}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        save_to_csv(date, results, f"news_{date}_{team}.csv")
        
        print(f"{date} {team} 크롤링 완료. 총 {len(results)}개의 기사를 저장했습니다.")
    
    driver.quit()    

if __name__ == "__main__":
    main()
