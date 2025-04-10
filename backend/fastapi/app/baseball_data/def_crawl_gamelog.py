import os
from datetime import datetime, timedelta
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# 날짜 관련 함수
def get_yesterday_date():
    """어제 날짜를 반환"""
    return datetime.now() - timedelta(days=1)

def format_date(date, format='%Y-%m-%d'):
    """날짜를 지정된 형식으로 포맷팅"""
    return date.strftime(format)

# 폴더 생성 함수
def create_date_folder(date):
    """날짜별 폴더 생성"""
    base_folder = 'crawled_data'
    folder_name = date.strftime('%Y%m%d')
    target_folder = os.path.join(base_folder, folder_name)
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"'{target_folder}' 폴더 생성 완료")
    else:
        print(f"'{target_folder}' 폴더 이미 존재")
    
    return target_folder

# 웹드라이버 설정 함수
def setup_webdriver():
    """크롬 웹드라이버 설정 및 반환"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 박스스코어 링크 가져오기 함수
def get_boxscore_links(driver):
    """페이지에서 박스스코어 링크 추출"""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.LINK_TEXT, "박스스코어"))
        )
        links = driver.find_elements(By.LINK_TEXT, "박스스코어")
        return [link.get_attribute('href') for link in links]
    except TimeoutException:
        print("시간 초과 발생! 박스스코어 링크 찾기")
        return []

# URL 로딩 재시도 함수
def retry_get(driver, url, retries=3, delay=5):
    """URL 로딩 실패 시 재시도"""
    for attempt in range(retries):
        try:
            driver.get(url)
            return True
        except WebDriverException as e:
            print(f"URL 로딩 실패: {e}. {attempt + 1}/{retries} 재시도 중...")
            time.sleep(delay)
    print(f"최대 재시도 횟수 초과: {url}")
    return False

# 타격 데이터 처리 함수
def process_batting_data(soup):
    """박스스코어에서 타격 데이터 추출 및 처리"""
    tables = soup.find_all('table')
    
    team_names = []
    box_heads = soup.find_all('div', class_='box_head')
    for box_head in box_heads:
        text = box_head.get_text(strip=True)
        if "타격기록" in text:
            team_name = text.split("(")[-1].replace(")", "").strip()
            team_names.append(team_name)

    away_team, home_team = team_names[0], team_names[1]
    
    print(f"원정팀: {away_team}, 홈팀: {home_team}")
    
    tables_1_2 = tables[:2]
    rows_1_2 = []
    for idx, table in enumerate(tables_1_2):
        headers = [th.get_text(strip=True) for th in table.find('tr').find_all('th')]
        headers.append('팀 이름')
        for row in table.find_all('tr')[1:]:
            cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
            cols.append(away_team if idx == 0 else home_team)
            rows_1_2.append(cols)

    df_batting = pd.DataFrame(rows_1_2, columns=headers)
    
    # 팀 이름 컬럼을 첫 번째로 이동
    df_batting = move_team_name_first(df_batting)
    
    # 팀 합계 행 처리
    df_batting_modified = shift_team_total_rows(df_batting, '타순')
    
    return df_batting_modified, away_team, home_team

# 팀 이름 컬럼 이동 함수
def move_team_name_first(df):
    """팀 이름 컬럼을 첫 번째로 이동"""
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('팀 이름')))
    return df[cols]

# 팀 합계 행 처리 함수
def shift_team_total_rows(df, order_col):
    """타순이 '팀 합계'인 행 데이터 처리"""
    shifted_rows = []
    current_team_name = None
    for idx, row in df.iterrows():
        if row['팀 이름']:
            current_team_name = row['팀 이름']
        
        if row[order_col] == '팀 합계':
            shifted_row = row.copy()
            shifted_row.iloc[4:] = row.iloc[2:-2].values
            shifted_row.iloc[2:4] = ''
            shifted_row['팀 이름'] = current_team_name
            shifted_rows.append(shifted_row)
        else:
            shifted_rows.append(row)
    return pd.DataFrame(shifted_rows, columns=df.columns)

# 로그 박스 데이터 처리 함수
def process_log_boxes(log_boxes, team_names=None, prefix=None):
    """로그 박스 데이터 추출 및 처리"""
    log_data = []
    max_div_count = 0

    for idx, log_box in enumerate(log_boxes):
        row_data = {}
        if team_names:
            team_name = team_names[idx] if idx < len(team_names) else f"팀명 없음 {idx + 1}"
            row_data['팀명'] = team_name

        log_divs = log_box.find_all('div', class_='log_div', recursive=False)
        for div_idx, log_div in enumerate(log_divs, start=1):
            div_text = " ".join(log_div.stripped_strings)
            row_data[f'{prefix}{div_idx}'] = div_text

        max_div_count = max(max_div_count, len(log_divs))
        log_data.append(row_data)

    columns_order = ['팀명'] + [f'{prefix}{i}' for i in range(1, max_div_count + 1)] if team_names else [f'{prefix}{i}' for i in range(1, max_div_count + 1)]
    return pd.DataFrame(log_data, columns=columns_order)

# 데이터 저장 함수
def save_data_to_csv(df, file_path):
    """데이터프레임을 CSV 파일로 저장"""
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"✅ 데이터 저장 완료: {file_path}")

# 메인 크롤링 함수
def crawl_gamelog(date=None):
    """특정 날짜의 게임 로그 크롤링"""
    if date is None:
        date = get_yesterday_date()
    
    formatted_date = format_date(date)
    url = f"https://statiz.sporki.com/schedule/?m=daily&date={formatted_date}"
    
    driver = None
    try:
        driver = setup_webdriver()
        driver.get(url)
        print(f"메인 페이지 로딩 완료: {url}")
        time.sleep(3)
        
        boxscore_links = get_boxscore_links(driver)
        print('box', boxscore_links)
        
        if not boxscore_links:
            print("박스스코어 링크 찾을 수 없음!")
            return False
        
        folder_name = create_date_folder(date)
        
        for href in boxscore_links:
            print('here', href)
            
            if retry_get(driver, href):
                try:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # 타격 데이터 처리
                    df_batting, away_team, home_team = process_batting_data(soup)
                    file_path_batting = f'{folder_name}/{away_team}-{home_team}_batting.csv'
                    save_data_to_csv(df_batting, file_path_batting)
                    
                    # 로그 박스 데이터 처리
                    log_boxes_1_2 = soup.find_all('div', class_='log_box')[:2]
                    log_boxes_4_6 = soup.find_all('div', class_='log_box')[4:6]
                    
                    team_names = [away_team, home_team]
                    df_log_box_1_2 = process_log_boxes(log_boxes_1_2, team_names, prefix="타자기록")
                    df_log_box_4_6 = process_log_boxes(log_boxes_4_6, prefix="수비기록")
                    
                    df_log_box_combined = pd.concat([df_log_box_1_2, df_log_box_4_6], axis=1)
                    file_path_combined_log_box = f'{folder_name}/{away_team}-{home_team}_log_boxes.csv'
                    save_data_to_csv(df_log_box_combined, file_path_combined_log_box)
                    
                except Exception as e:
                    print(f"{href} 이동 중 오류 발생: {e}")
            
            time.sleep(2)
        
        print(f"✅ {formatted_date} 날짜의 모든 경기 데이터 저장이 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False
    finally:
        if driver:
            driver.quit()

# 스크립트를 직접 실행할 때만 실행
if __name__ == "__main__":
    crawl_gamelog()
