0. `pip install -r requirements.txt` 명령어 실행
1. `crawl_gamelog.py` -> `game_preprocessing.py` 파일 실행


`crawl_2025_season.py`
- 2025 시즌 전 경기 크롤링 코드

`crawl_players.py`
- 선수 등번호 크롤링 코드

`crawl_gamelog.py`
- 경기 기록 크롤링 코드

`game_preprocessing.py`
- 경기 기록 전처리 코드
- 경기 기록 전처리 진행하여 porcessed_data 폴더에 저장
- 일일 팀 순위 갱신 저장하여 daily_rank 폴더에 저장

`team_rank.py`
- 일일 팀 순위 표.ver0


`change_json.py`
- csv 파일 json으로 변환