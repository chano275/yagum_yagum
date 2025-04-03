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

# 현재 날짜 설정
current_date = datetime.now()

# 어제 날짜 계산 (days=1)로 고정
yesterday = current_date - timedelta(days=1)

# URL 형식에 맞게 날짜 포맷팅 (YYYY-MM-DD)
formatted_date = yesterday.strftime('%Y-%m-%d')

# URL 생성
url = f"https://statiz.sporki.com/schedule/?m=daily&date={formatted_date}"

# 날짜별 폴더 생성 함수
def create_date_folder(date):
    # 기본 폴더 경로 설정
    base_folder = 'crawled_data'
    
    # 날짜별 폴더 이름 생성
    folder_name = date.strftime('%Y%m%d')  # 폴더 이름을 YYYYMMDD 형식으로 생성
    
    # 최종 경로 설정
    target_folder = os.path.join(base_folder, folder_name)
    
    # 날짜별 폴더 생성
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"'{target_folder}' 폴더 생성 완료")
    else:
        print(f"'{target_folder}' 폴더 이미 존재")
    
    return target_folder

try:
    # 크롬 드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")  # Headless 모드 추가 (브라우저 창을 띄우지 않음)
    chrome_options.page_load_strategy = 'eager'  # 페이지 로드 전략 설정
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    
    # 새 WebDriver 인스턴스 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 메인 페이지 접속
    driver.get(url)
    print(f"메인 페이지 로딩 완료: {url}")
    
    time.sleep(3)  # 페이지 로딩 대기

    # '박스스코어' 텍스트를 가진 모든 a 태그의 링크를 가져오는 함수
    def get_boxscore_links(driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.LINK_TEXT, "박스스코어"))
            )
            links = driver.find_elements(By.LINK_TEXT, "박스스코어")
            return [link.get_attribute('href') for link in links]
        except TimeoutException:
            print("시간 초과 발생! 박스스코어 링크 찾기")
            return []
    
    # 링크 가져오기
    boxscore_links = get_boxscore_links(driver)
    print('box', boxscore_links)
    
    if not boxscore_links:
        print("박스스코어 링크 찾을 수 없음!")
    else:
        print("찾은 박스스코어 링크:")
        
        # 날짜별 폴더 생성
        folder_name = create_date_folder(yesterday)
        
        for href in boxscore_links:
            print('here', href)
    
            # 각 링크로 이동 (재시도 메커니즘 포함)
            def retry_get(driver, url, retries=3, delay=5):
                for attempt in range(retries):
                    try:
                        driver.get(url)
                        return True
                    except WebDriverException as e:
                        print(f"URL 로딩 실패: {e}. {attempt + 1}/{retries} 재시도 중...")
                        time.sleep(delay)
                print(f"최대 재시도 횟수 초과: {url}")
                return False

            if retry_get(driver, href):
                try:
                    # BeautifulSoup으로 HTML 파싱
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # --- 박스스코어 데이터 처리 ---
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
                        headers.append('팀 이름')  # 팀 이름 컬럼 추가
                        for row in table.find_all('tr')[1:]:
                            cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
                            cols.append(away_team if idx == 0 else home_team)  # 팀 이름 추가
                            rows_1_2.append(cols)

                    df_batting = pd.DataFrame(rows_1_2, columns=headers)

                    def move_team_name_first(df):
                        cols = df.columns.tolist()
                        cols.insert(0, cols.pop(cols.index('팀 이름')))
                        return df[cols]

                    df_batting = move_team_name_first(df_batting)

                    # 타순이 '팀 합계'인 행만 데이터를 두 칸 오른쪽으로 이동하고 팀 이름 추가하는 함수 정의
                    def shift_team_total_rows(df, order_col):
                        shifted_rows = []
                        current_team_name = None  # 현재 팀명을 저장할 변수
                        for idx, row in df.iterrows():
                            if row['팀 이름']:
                                current_team_name = row['팀 이름']  # 현재 행의 팀명 저장
                    
                            if row[order_col] == '팀 합계':
                                shifted_row = row.copy()
                                shifted_row.iloc[4:] = row.iloc[2:-2].values  # 정확히 두 칸 이동
                                shifted_row.iloc[2:4] = ''  # 빈칸 처리 (선수명과 포지션 등)
                                shifted_row['팀 이름'] = current_team_name  # 명시적으로 팀 이름 설정
                                shifted_rows.append(shifted_row)
                            else:
                                shifted_rows.append(row)
                        return pd.DataFrame(shifted_rows, columns=df.columns)
                    
                    df_batting_modified = shift_team_total_rows(df_batting, '타순')

                    file_path_batting = f'{folder_name}/{away_team}-{home_team}_batting.csv'
                    df_batting_modified.to_csv(file_path_batting, index=False, encoding='utf-8-sig')
                    
                    print(f"✅ 박스스코어 데이터 저장 완료: {file_path_batting}")

                    # --- log_box 데이터 처리 ---
                    
                    # log_boxes[:2]와 log_boxes[4:6] 데이터 처리
                    log_boxes_1_2 = soup.find_all('div', class_='log_box')[:2]
                    log_boxes_4_6 = soup.find_all('div', class_='log_box')[4:6]
                    
                    # 데이터 처리 함수 정의
                    def process_log_boxes(log_boxes, team_names=None, prefix=None):
                        log_data = []
                        max_div_count = 0
                    
                        for idx, log_box in enumerate(log_boxes):
                            row_data = {}
                            # 팀명은 [:2]에서만 추가, [4:6]에서는 추가하지 않음
                            if team_names:
                                team_name = team_names[idx] if idx < len(team_names) else f"팀명 없음 {idx + 1}"
                                row_data['팀명'] = team_name
                    
                            # log_divs를 가져올 때 중복을 방지하기 위해 최상위 div만 선택
                            log_divs = log_box.find_all('div', class_='log_div', recursive=False)  # recursive=False로 중첩 방지
                            for div_idx, log_div in enumerate(log_divs, start=1):
                                div_text = " ".join(log_div.stripped_strings)
                                row_data[f'{prefix}{div_idx}'] = div_text  # 항목 이름에 prefix 추가
                    
                            max_div_count = max(max_div_count, len(log_divs))
                            log_data.append(row_data)
                    
                        # 팀명이 없으면 '팀명' 컬럼을 제외
                        columns_order = ['팀명'] + [f'{prefix}{i}' for i in range(1, max_div_count + 1)] if team_names else [f'{prefix}{i}' for i in range(1, max_div_count + 1)]
                        return pd.DataFrame(log_data, columns=columns_order)
                    
                    # 각각의 데이터프레임 생성
                    df_log_box_1_2 = process_log_boxes(log_boxes_1_2, team_names[:2], prefix="타자기록")  # '타자기록'으로 항목 이름 변경
                    df_log_box_4_6 = process_log_boxes(log_boxes_4_6, prefix="수비기록")  # '수비기록'으로 항목 이름 변경
                    
                    # 두 데이터프레임을 가로로 병합
                    df_log_box_combined = pd.concat([df_log_box_1_2, df_log_box_4_6], axis=1)
                    
                    # 병합된 데이터 저장
                    file_path_combined_log_box = f'{folder_name}/{away_team}-{home_team}_log_boxes.csv'
                    df_log_box_combined.to_csv(file_path_combined_log_box, index=False, encoding='utf-8-sig')
                    
                    print(f"✅ 병합된 로그 박스 데이터 저장 완료: {file_path_combined_log_box}")
                    # log_boxes = soup.find_all('div', class_='log_box')[:2]

                    # log_data = []
                    # max_div_count = 0

                    # for idx, log_box in enumerate(log_boxes):
                    #     row_data = {}
                    #     team_name = team_names[idx] if idx < len(team_names) else f"팀명 없음 {idx + 1}"
                    #     row_data['팀명'] = team_name

                    #     log_divs = log_box.find_all('div', class_='log_div')
                    #     for div_idx, log_div in enumerate(log_divs, start=1):
                    #         div_text = " ".join(log_div.stripped_strings)
                    #         row_data[f'항목{div_idx}'] = div_text

                    #     max_div_count = max(max_div_count, len(log_divs))
                    #     log_data.append(row_data)

                    # columns_order = ['팀명'] + [f'항목{i}' for i in range(1, max_div_count + 1)]
                    # df_log_box = pd.DataFrame(log_data, columns=columns_order)

                    # def calculate_stolen_bases(row):
                    #     for col in row.index:
                    #         if isinstance(row[col], str) and '도루성공' in row[col]:
                    #             stolen_bases_section = row[col].split('도루성공 : ')[-1]
                    #             players = [p.strip() for p in stolen_bases_section.split(')') if p.strip()]
                    #             return len(players)
                    #     return 0

                    # df_log_box['도루'] = df_log_box.apply(calculate_stolen_bases, axis=1)

                    # file_path_log_box = f'{folder_name}/{away_team}-{home_team}_log_boxes.csv'
                    # df_log_box.to_csv(file_path_log_box, index=False, encoding='utf-8-sig')
                    
                    # print(f"✅ 로그 박스 데이터 저장 완료: {file_path_log_box}")

                except Exception as e:
                    print(f"{href} 이동 중 오류 발생: {e}")
            
            time.sleep(2)  # 대기 시간 조정 가능

            # 모든 경기 데이터 저장 완료 메시지 출력 (추가된 부분)
            print(f"✅ {yesterday.strftime('%Y-%m-%d')} 날짜의 모든 경기 데이터 저장이 완료되었습니다!")
    
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    # 항상 드라이버를 종료
    if 'driver' in locals():
        driver.quit()
