import os
import sys
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date

# 현재 파일 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # app 폴더의 상위 폴더로 이동

# 프로젝트 루트 경로를 파이썬 경로에 추가
sys.path.append(project_root)

# 환경 변수 설정을 위한 dotenv 불러오기
from dotenv import load_dotenv
load_dotenv()

# models 모듈 import
import models
from database import engine

# 데이터베이스 연결 설정
Session = sessionmaker(bind=engine)
session = Session()

# 팀 약자를 팀 ID로 매핑하는 딕셔너리
team_mapping = {
    'KIA': 1,  # KIA 타이거즈
    '삼성': 2,  # 삼성 라이온즈
    'LG': 3,   # LG 트윈스
    '두산': 4,  # 두산 베어스
    'KT': 5,   # KT 위즈
    'SSG': 6,  # SSG 랜더스
    '롯데': 7,  # 롯데 자이언츠
    '한화': 8,  # 한화 이글스
    'NC': 9,   # NC 다이노스
    '키움': 10  # 키움 히어로즈
}

# 기록 유형 매핑 (CSV 컬럼 -> 레코드 타입 ID)
record_type_mapping = {
    'H': 4,     # 안타
    'HR': 5,    # 홈런
    # 'R': 6,     # 득점
    'SO': 8,    # 삼진
    'BB': 9,    # 볼넷/몸맞공
    # 'GDP': 11,  # 병살타
}

def process_game_data_folder():
    """
    baseball_data/game_data 폴더 내의 모든 날짜 폴더를 처리하여 선수 기록을 DB에 저장
    """
    # 게임 데이터 폴더 경로
    game_data_path = os.path.join(project_root, 'baseball_data', 'game_data')
    
    if not os.path.exists(game_data_path):
        print(f"게임 데이터 폴더를 찾을 수 없습니다: {game_data_path}")
        return
    
    # 날짜 폴더 목록 가져오기
    date_folders = [f for f in os.listdir(game_data_path) if os.path.isdir(os.path.join(game_data_path, f)) and f.isdigit()]
    
    total_records = 0
    
    for date_folder in date_folders:
        folder_path = os.path.join(game_data_path, date_folder)
        
        # 날짜 파싱 (YYYYMMDD 형식)
        try:
            game_date = datetime.strptime(date_folder, '%Y%m%d').date()
            print(f"\n날짜 {game_date} 처리 중...")
        except ValueError:
            print(f"유효하지 않은 날짜 폴더명: {date_folder}, 건너뜁니다.")
            continue
        
        # 폴더 내의 모든 CSV 파일 처리
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and '_batting.csv' in f]
        
        folder_records = 0
        
        for csv_file in csv_files:
            file_path = os.path.join(folder_path, csv_file)
            
            # 파일명에서 팀 정보 추출 (예: NC-KIA_batting.csv -> NC, KIA)
            try:
                teams = csv_file.split('_')[0].split('-')
                print(f"처리 중인 파일: {csv_file}, 팀: {teams}")
            except Exception as e:
                print(f"파일명 파싱 오류: {csv_file}, 오류: {str(e)}")
                continue
            
            try:
                # CSV 파일 읽기
                df = pd.read_csv(file_path, encoding='utf-8')
                
                # 첫 번째 행이 컬럼명인지 확인하고 처리
                if '팀' in df.columns[0] or '이름' in df.columns[1]:
                    # 컬럼명이 있는 경우, 그대로 사용
                    pass
                else:
                    # 컬럼명이 없는 경우, 첫 번째 행을 컬럼명으로 사용
                    df.columns = df.iloc[0]
                    df = df.drop(0)
                
                # 컬럼명 확인 및 필요한 컬럼 추출
                required_columns = ['팀', '이름', 'H', 'HR', 'R', 'SO', 'BB', 'GDP']
                
                # 컬럼명 매핑 (실제 파일의 컬럼명과 필요한 컬럼명 매핑)
                column_mapping = {}
                for col in df.columns:
                    col_str = str(col).strip()
                    if '팀' in col_str:
                        column_mapping[col] = '팀'
                    elif '이름' in col_str or '선수' in col_str:
                        column_mapping[col] = '이름'
                    elif col_str in ['H', 'HR', 'R', 'SO', 'BB', 'GDP']:
                        column_mapping[col] = col_str
                
                # 컬럼명 변경
                if column_mapping:
                    df = df.rename(columns=column_mapping)
                
                # 필요한 컬럼이 있는지 확인
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"필요한 컬럼이 없습니다: {missing_columns}, 파일: {csv_file}")
                    print(f"사용 가능한 컬럼: {df.columns.tolist()}")
                    continue
                
                # 각 선수별 기록 처리
                for _, row in df.iterrows():
                    team_name = str(row['팀']).strip()
                    player_name = str(row['이름']).strip()
                    
                    # NC,1, 박민우, 처럼 되어 있는 경우 처리
                    if ',' in team_name:
                        parts = team_name.split(',')
                        team_name = parts[0].strip()
                        if len(parts) > 2 and player_name == '':
                            player_name = parts[2].strip()
                    
                    # 팀명이 team_mapping에 없는 경우 처리
                    if team_name not in team_mapping:
                        # 팀명 일부 매칭 시도
                        matched_team = None
                        for key in team_mapping.keys():
                            if key in team_name:
                                matched_team = key
                                break
                        
                        if matched_team:
                            team_name = matched_team
                        else:
                            print(f"알 수 없는 팀명: {team_name}, 선수: {player_name}, 건너뜁니다.")
                            continue
                    
                    team_id = team_mapping[team_name]
                    
                    # 선수 ID 찾기
                    player = session.query(models.Player).filter(
                        models.Player.PLAYER_NAME == player_name,
                        models.Player.TEAM_ID == team_id
                    ).first()
                    
                    if not player:
                        # 이름이 비슷한 선수 찾기
                        players = session.query(models.Player).filter(
                            models.Player.TEAM_ID == team_id
                        ).all()
                        
                        matched_player = None
                        for p in players:
                            if player_name in p.PLAYER_NAME or p.PLAYER_NAME in player_name:
                                matched_player = p
                                break
                        
                        if matched_player:
                            player = matched_player
                        else:
                            print(f"선수를 찾을 수 없음: {player_name}, 팀: {team_name}, 건너뜁니다.")
                            continue
                    
                    # 각 기록 유형별로 처리
                    for record_col, record_type_id in record_type_mapping.items():
                        if record_col in df.columns:
                            try:
                                # 기록값 추출 및 변환
                                record_value = row[record_col]
                                
                                # 값이 비어있거나 NaN인 경우 0으로 처리
                                if pd.isna(record_value) or record_value == '':
                                    record_value = 0
                                else:
                                    # 문자열인 경우 숫자로 변환
                                    record_value = int(float(record_value))
                                
                                # 0인 경우 스킵
                                if record_value == 0:
                                    continue
                                
                                # 이미 동일한 날짜, 선수, 팀, 기록 유형의 레코드가 있는지 확인
                                existing_record = session.query(models.PlayerRecord).filter(
                                    models.PlayerRecord.DATE == game_date,
                                    models.PlayerRecord.PLAYER_ID == player.PLAYER_ID,
                                    models.PlayerRecord.TEAM_ID == team_id,
                                    models.PlayerRecord.RECORD_TYPE_ID == record_type_id
                                ).first()
                                
                                if existing_record:
                                    # 기존 레코드 업데이트
                                    existing_record.COUNT = record_value
                                    print(f"기존 레코드 업데이트: 날짜={game_date}, 선수={player_name}, 기록={record_col}, 값={record_value}")
                                else:
                                    # 새 레코드 생성
                                    new_record = models.PlayerRecord(
                                        DATE=game_date,
                                        PLAYER_ID=player.PLAYER_ID,
                                        TEAM_ID=team_id,
                                        RECORD_TYPE_ID=record_type_id,
                                        COUNT=record_value
                                    )
                                    session.add(new_record)
                                    print(f"새 레코드 추가: 날짜={game_date}, 선수={player_name}, 기록={record_col}, 값={record_value}")
                                    
                                    folder_records += 1
                                    total_records += 1
                            except Exception as e:
                                print(f"레코드 처리 중 오류: 선수={player_name}, 기록={record_col}, 오류: {str(e)}")
                                continue
                
                # 변경사항 커밋
                session.commit()
                
            except Exception as e:
                session.rollback()
                print(f"파일 {csv_file} 처리 중 오류 발생: {str(e)}")
                continue
        
        print(f"날짜 {game_date} 처리 완료: {folder_records}개 레코드 추가됨")
    
    print(f"\n총 {total_records}개의 레코드가 데이터베이스에 추가되었습니다.")

if __name__ == "__main__":
    try:
        process_game_data_folder()
        print("데이터 처리가 완료되었습니다.")
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()