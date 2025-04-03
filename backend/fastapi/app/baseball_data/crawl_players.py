import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 팀 코드 : 팀 이름 매핑
team_mapping = {
    2002: 'KIA',
    1001: '삼성',
    5002: 'LG',
    6002: '두산',
    12001: 'KT',
    9002: 'SSG',
    3001: '롯데',
    7002: '한화',
    11001: 'NC',
    10001: '키움'
}

# 선수 데이터를 저장할 폴더 생성
folder_name = 'players'
os.makedirs(folder_name, exist_ok=True)  # 이미 존재해도 에러 발생하지 않음
print(f"'{folder_name}' 폴더 준비 완료")

# if not os.path.exists(folder_name):
#     os.makedirs(folder_name)
#     print(f"'{folder_name}' 폴더 생성 완료")
# else:
#     print(f"'{folder_name}' 폴더 이미 존재")

# 기본 URL
base_url = "https://statiz.sporki.com/team/?m=seasonBacknumber&t_code={}&year=2025"

# 각 팀의 선수 데이터를 크롤링하고 저장
for tcode, team_name in team_mapping.items():
    url = base_url.format(tcode)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 선수 정보 추출
    players = soup.find_all('div', class_='item away')
    player_data = []
    for player in players:
        number_span = player.find('span', class_='number')
        name_a = player.find('a')

        if number_span and name_a:
            number = number_span.get_text(strip=True)
            name = name_a.get_text(strip=True)
            player_data.append({'등번호': number, '이름': name})

    # DataFrame 생성 및 CSV 저장 (팀 이름 포함)
    df = pd.DataFrame(player_data)
    filename = f'{folder_name}/{team_name}_players.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"✅ {team_name} 선수 데이터 저장 완료: {filename}")
    time.sleep(1)  # 서버 과부하 방지를 위한 대기
