0. `pip install -r requirements.txt` 명령어 실행

[파일 실행 순서]
1. `crawl_gamelog.py` (데이터 크롤링)
- 결과물 cralwed_data 폴더에 저장됨
2. `game_preprocessing.py` (데이터 전처리)
- 결과물 processed_data 폴더에 저장됨
3. `change_json.py` (json 파일 변환)
- 결과물 json_data 폴더에 저장됨

위 코드는 모두 **하루 전** 데이터 기준으로 데이터 크롤링/전처리/json 변환됨


`crawl_2025_season.py`
- 2025 시즌 전 경기 크롤링 코드

`crawl_players.py`
- 선수 등번호 크롤링 코드

`crawl_gamelog.py`
- 경기 기록 크롤링 코드

`team_rank.py`
- 일일 팀 순위 표 초기 세팅

`game_preprocessing.py`
- 경기 기록 전처리 코드
- 경기 기록 전처리 진행하여 porcessed_data 폴더에 저장
- 일일 팀 순위 갱신 저장하여 daily_rank 폴더에 저장

`change_json.py`
- csv 파일 json으로 변환