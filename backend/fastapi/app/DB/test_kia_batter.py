import sys
import os
import csv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일의 상위 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# models 및 database 모듈 가져오기
import models
from database import engine

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

# KIA 타이거즈 팀 ID
KIA_TEAM_ID = 1

# CSV 파일 경로 설정 - 여러 가능한 경로 시도
possible_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'fastapi', 'app', 'data', 'players', 'KIA_players.csv'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'players', 'KIA_players.csv'),
    os.path.join(os.path.dirname(__file__), '..', 'data', 'players', 'KIA_players.csv'),
    'fastapi/app/data/players/KIA_players.csv'
]

csv_file_path = None
for path in possible_paths:
    if os.path.exists(path):
        csv_file_path = path
        break

if csv_file_path is None:
    print("오류: CSV 파일을 찾을 수 없습니다. 다음 경로에서 파일을 확인하세요:")
    for i, path in enumerate(possible_paths, 1):
        print(f"{i}. {path}")
    print("\n현재 작업 디렉토리:", os.getcwd())
    sys.exit(1)

print(f"CSV 파일을 찾았습니다: {csv_file_path}")

try:
    # CSV 파일 읽기
    players = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if len(row) >= 2:  # 최소한 등번호, 이름이 있어야 함
                # CSV 형식에 따라 인덱스 조정
                number_str = row[0].strip()
                name = row[1].strip() if len(row) > 1 else ""
                
                # 모든 선수를 타자로 설정 (player_type_id = 2)
                player_type = 2
                
                # 이름이 비어있지 않은 경우만 추가
                if name:
                    players.append({
                        "number": number_str,  # 원본 문자열 그대로 유지
                        "name": name,
                        "type": player_type
                    })
    
    print(f"CSV에서 읽은 선수 수: {len(players)}")
    
    # 읽어들인 선수 정보 출력
    print("\n읽어들인 선수 정보:")
    for idx, player in enumerate(players, 1):
        print(f"{idx}. {player['name']} - 등번호: '{player['number']}'")
    
    # 기존 선수 데이터 확인 (중복 방지)
    existing_players = session.query(models.Player).filter(models.Player.TEAM_ID == KIA_TEAM_ID).all()
    existing_names = [player.PLAYER_NAME for player in existing_players]
    
    print(f"이미 DB에 존재하는 KIA 선수 수: {len(existing_names)}")
    
    # 중복되지 않는 선수만 추가
    new_players = []
    for player in players:
        if player["name"] and player["name"] not in existing_names:
            new_player = models.Player(
                TEAM_ID=KIA_TEAM_ID,
                PLAYER_NUM=player["number"],  # 문자열 그대로 저장 (이제 PLAYER_NUM은 String 타입)
                PLAYER_TYPE_ID=player["type"],
                PLAYER_NAME=player["name"],
                PLAYER_IMAGE_URL="",  # 기본 이미지 URL
                LIKE_COUNT=0
            )
            new_players.append(new_player)
            existing_names.append(player["name"])  # 동일 이름 중복 방지를 위해 추가
    
    # 데이터 삽입
    if new_players:
        session.add_all(new_players)
        session.commit()
        print(f"{len(new_players)}명의 타자 데이터 삽입 완료")
        
        # 추가된 선수 정보 출력
        print("\n추가된 선수 목록:")
        for idx, player in enumerate(new_players, 1):
            print(f"{idx}. {player.PLAYER_NAME} (등번호: '{player.PLAYER_NUM}')")
    else:
        print("추가할 새로운 선수가 없습니다.")
    
except Exception as e:
    session.rollback()
    print(f"데이터 처리 중 오류 발생: {e}")
finally:
    session.close()