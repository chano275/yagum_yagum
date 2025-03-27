import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import date, datetime
import sys

# 현재 스크립트 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
csv_file_path = os.path.join(project_root, 'data', 'game_data', 'NC-KIA_batting.csv')

print(f"파일을 찾았습니다: {csv_file_path}")

# CSV 파일 읽기
df = pd.read_csv(csv_file_path)
print(f"CSV 파일을 성공적으로 읽었습니다. 행 개수: {len(df)}")

# NaN 값 확인 및 처리
print("NaN 값이 있는 행:")
print(df[df['이름'].isna()])

# NaN 값을 가진 행 제거 (팀 합계 행 등)
df = df.dropna(subset=['이름'])
print(f"NaN 값을 제거한 후 행 개수: {len(df)}")

# 데이터베이스 연결
from dotenv import load_dotenv
load_dotenv()

# 데이터베이스 연결 설정
DATABASE_URL = f'{os.getenv("DATABASE_TYPE")}://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_IP")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_DB")}?charset=utf8mb4'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# models 모듈 import
sys.path.append(project_root)
import models

# 기록 유형 ID 매핑 (record_type 테이블 기준)
record_type_mapping = {
    'H': 2,   # 안타
    'HR': 3,  # 홈런
    'RBI': 8, # 타점
    'BB': 9,  # 볼넷
    'SO': 10  # 삼진
}

# 팀 ID 매핑 (team 테이블 기준)
team_mapping = {
    'NC': 9,    # NC 다이노스
    'KIA': 1    # KIA 타이거즈
}

# 경기 날짜 설정 (예: 오늘 날짜)
game_date = date.today()

# 팀별 통계 집계용 딕셔너리 및 출전 선수 목록
team_stats = {}
appeared_players = set()  # 출전 선수 집합 (중복 방지)

# 각 행을 처리
for _, row in df.iterrows():
    team_name = row['팀 이름']
    player_name = row['이름']
    
    # NaN 값 확인 (추가 안전장치)
    if pd.isna(player_name) or pd.isna(team_name):
        print(f"경고: 팀 이름 또는 선수 이름이 NaN입니다. 이 행은 건너뜁니다.")
        continue
    
    # 팀 ID 조회
    team_id = team_mapping.get(team_name)
    if not team_id:
        print(f"팀 {team_name}을 찾을 수 없습니다.")
        continue
    
    # 해당 팀의 통계 초기화
    if team_id not in team_stats:
        team_stats[team_id] = {record_id: 0 for record_id in record_type_mapping.values()}
    
    # 선수 ID 조회
    player = session.query(models.Player).filter(
        models.Player.TEAM_ID == team_id,
        models.Player.PLAYER_NAME == player_name
    ).first()
    
    if not player:
        print(f"선수 {player_name}을 찾을 수 없습니다. DB에 추가합니다.")
        # 새 선수 추가 (포지션에 따라 선수 타입 설정)
        player_type_id = 2  # 타자
        new_player = models.Player(
            TEAM_ID=team_id,
            PLAYER_NUM=0,  # 임시 번호
            PLAYER_TYPE_ID=player_type_id,
            PLAYER_NAME=player_name,
            PLAYER_IMAGE_URL="",
            LIKE_COUNT=0
        )
        session.add(new_player)
        session.flush()
        player = new_player
    
    # 출전 선수 집합에 추가 (count 값과 관계없이 모든 선수 기록)
    appeared_players.add((player.PLAYER_ID, team_id))
    
    # 선수의 기록 저장
    for stat_name, record_type_id in record_type_mapping.items():
        if stat_name in row and not pd.isna(row[stat_name]):
            count = int(row[stat_name])
            
            # count가 0인 경우 player_record 테이블에는 저장하지 않음
            if count <= 0:
                continue
                
            # 팀 통계에 추가
            team_stats[team_id][record_type_id] += count
            
            # count > 0 인 경우만 player_record에 저장
            player_record = models.PlayerRecord(
                DATE=game_date,
                PLAYER_ID=player.PLAYER_ID,
                TEAM_ID=team_id,
                RECORD_TYPE_ID=record_type_id,
                COUNT=count
            )
            session.add(player_record)
            print(f"선수 {player_name}의 {record_type_id} 기록 {count}개 저장")

# 팀 통계를 game_log에 저장
for team_id, stats in team_stats.items():
    for record_type_id, count in stats.items():
        if count <= 0:  # count가 0인 경우 저장하지 않음
            continue
            
        game_log = models.GameLog(
            DATE=game_date,
            TEAM_ID=team_id,
            RECORD_TYPE_ID=record_type_id,
            COUNT=count
        )
        session.add(game_log)
        print(f"팀 {team_id}의 {record_type_id} 기록 {count}개 저장")

# 출전 선수를 run_player 테이블에 저장
for player_id, team_id in appeared_players:
    # 이미 동일한 날짜에 해당 선수의 출전 기록이 있는지 확인
    existing_record = session.query(models.RunPlayer).filter(
        models.RunPlayer.DATE == game_date,
        models.RunPlayer.PLAYER_ID == player_id
    ).first()
    
    if not existing_record:
        run_player_record = models.RunPlayer(
            DATE=game_date,
            PLAYER_ID=player_id
        )
        session.add(run_player_record)
        player_name = session.query(models.Player.PLAYER_NAME).filter(models.Player.PLAYER_ID == player_id).scalar()
        print(f"선수 {player_name}(ID: {player_id}) 출전 기록 저장")

# 세션에 추가된 새 객체 수 확인
new_objects = len(session.new)
print(f"세션에 추가된 새 객체 수: {new_objects}")

# 변경사항 커밋
try:
    session.commit()
    print("데이터 저장 완료!")
except Exception as e:
    session.rollback()
    print(f"데이터 저장 중 오류 발생: {str(e)}")
    raise
finally:
    session.close()