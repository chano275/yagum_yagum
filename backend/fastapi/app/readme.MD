# DB / init_setting
1. init_team.py
2. init_player_type.py
3. init_player.py
4. init_record_type.py
5. init_saving_rule_type.py
6. init_saving_rule_list.py
7. init_saving_rule_detail.py
8. init_mission.py

순으로 실행하여 초기 데이터 세팅할것


# 스케줄링
1. 경기 및 선수기록 데이터 크롤링
2. 경기 및 선수기록 DB에 저장
3. 사용자별 입금 예상액 계산
4. 문장 생성
5. 적금 진행

1. 경기 및 선수기록 데이터 크롤링 - baseball_data/ def_crawl_gamelog.py, def_preprocessing.py, def_change_json.py
2. 경기 및 선수기록 DB에 저장 - utils/ update_game_log.py, save_player_record.py, update_daily_rank.py
3. 사용자별 입금 예상액 계산 - utils/ process_saving.py
4. 문장 생성 - GCP에서 결과값 받아오기
5. 적금 진행 - utils/ process_transfer.py
6. 일일 잔액 및 이자 DB에 저장 - utils/ update_daily_balances.py