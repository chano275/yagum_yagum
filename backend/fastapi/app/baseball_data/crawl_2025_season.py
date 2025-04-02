import requests
from bs4 import BeautifulSoup
import csv

# Base URL
base_url = "https://statiz.sporki.com/schedule/?year=2025&month="

# Months to iterate over
months = [3, 4, 5, 6, 7, 8]

# Data storage
all_game_data = []

# Iterate over months
for month in months:
    url = base_url + str(month)
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text

    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    days = soup.find_all('td')  # 날짜별 데이터를 포함한 td 태그 찾기

    for day in days:
        # 날짜 추출
        date_span = day.find('span', class_='day')
        if not date_span:
            continue  # 날짜가 없는 경우 건너뜀
        day_number = date_span.text.strip()  # 날짜 숫자 추출 (예: "1", "22")
        date = "25" + str(month).zfill(2) + day_number.zfill(2)  # 날짜 형식: YYYYMMDD (예: 250401)

        # 경기 정보 추출
        games = day.find_all('li')  # 경기 정보를 포함한 li 태그 찾기
        for game in games:
            teams = game.find_all('span', class_='team')  # 팀 이름을 포함한 span 태그 찾기
            if len(teams) == 2:  # 원정팀과 홈팀이 있는 경우만 처리
                away_team = teams[0].text.strip()  # 원정팀 이름 추출
                home_team = teams[1].text.strip()  # 홈팀 이름 추출
                all_game_data.append({"날짜": date, "원정": away_team, "홈": home_team})

# Save to CSV
csv_filename = "2025_season_games.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["날짜", "원정", "홈"])
    writer.writeheader()  # 헤더 작성
    writer.writerows(all_game_data)  # 데이터 작성

print(f"'{csv_filename}'파일 저장 완료!")
