import sys
import os
import csv
import glob
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 위치를 기준으로 상위 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# models 및 database 모듈 가져오기
import models
from database import engine

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

# 팀 이름과 ID 매핑 (데이터베이스에 저장된 팀 ID와 일치해야 함)
TEAM_MAPPING = {
    "KIA": 1,
    "삼성": 2,
    "LG": 3,
    "두산": 4,
    "KT": 5,
    "SSG": 6,
    "롯데": 7,
    "한화": 8,
    "NC": 9,
    "키움": 10
}

# players 폴더 경로 설정 - 여러 가능한 경로 시도
possible_base_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'fastapi', 'app', 'baseball_data', 'players'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'baseball_data', 'players'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'baseball_data', 'players'),
    os.path.join(os.path.dirname(__file__), '..', 'fastapi', 'app', 'baseball_data', 'players'),
    os.path.join(os.path.dirname(__file__), 'baseball_data', 'players'),
    'fastapi/app/baseball_data/players'
]

# 유효한 경로 찾기
players_folder_path = None
for path in possible_base_paths:
    if os.path.exists(path) and os.path.isdir(path):
        players_folder_path = path
        break

if players_folder_path is None:
    print("오류: players 폴더를 찾을 수 없습니다. 다음 경로에서 폴더를 확인하세요:")
    for i, path in enumerate(possible_base_paths, 1):
        print(f"{i}. {path}")
    print("\n현재 작업 디렉토리:", os.getcwd())
    sys.exit(1)

print(f"players 폴더를 찾았습니다: {players_folder_path}")

try:
    # 폴더 내의 모든 CSV 파일 찾기
    csv_pattern = os.path.join(players_folder_path, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"오류: {players_folder_path} 폴더에서 CSV 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    print(f"총 {len(csv_files)}개의 CSV 파일을 찾았습니다.")
    
    # 각 CSV 파일 처리
    total_added_players = 0
    
    for csv_file_path in csv_files:
        # 파일 이름에서 팀 이름 추출
        file_name = os.path.basename(csv_file_path)
        team_prefix = file_name.split('_')[0]  # 예: "KIA_players.csv" -> "KIA"
        
        # 팀 ID 결정
        team_id = TEAM_MAPPING.get(team_prefix)
        if not team_id:
            print(f"경고: '{team_prefix}'에 해당하는 팀 ID를 찾을 수 없습니다. 이 파일은 건너뜁니다: {file_name}")
            continue
        
        print(f"\n[{file_name}] 처리 시작 (팀 ID: {team_id})")
        
        # 기존 팀 선수 데이터 확인 (중복 방지)
        existing_players = session.query(models.Player).filter(models.Player.TEAM_ID == team_id).all()
        existing_names = [player.PLAYER_NAME for player in existing_players]
        
        print(f"이미 DB에 존재하는 팀 ID {team_id}의 선수 수: {len(existing_names)}")
        
        # CSV 파일 읽기
        players = []
        new_player_count = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            # 첫 번째 줄 건너뛰기 (헤더)
            next(csv_reader, None)
            
            for row in csv_reader:
                if len(row) >= 2:  # 최소한 등번호, 이름이 있어야 함
                    # CSV 형식에 따라 인덱스 조정
                    number_str = row[0].strip()
                    name = row[1].strip() if len(row) > 1 else ""
                    if not number_str:continue
                    # 타입 결정 (2번째 인덱스가 있으면 그 값 사용, 없으면 기본값 2(타자))
                    # player_type = int(row[2].strip()) if len(row) > 2 and row[2].strip().isdigit() else 2
                    player_type_csv = row[2].strip()
                    if player_type_csv == "투수":
                        player_type = 1
                    else:
                        player_type = 2
                    
                    # 이름이 비어있지 않은 경우만 추가
                    if name and name not in existing_names:
                        new_player = models.Player(
                            TEAM_ID=team_id,
                            PLAYER_NUM=number_str,
                            PLAYER_TYPE_ID=player_type,
                            PLAYER_NAME=name,
                            PLAYER_IMAGE_URL=f"https://chano-s3-test.s3.us-east-2.amazonaws.com/{team_id}/{number_str}.jpg",  # 기본 이미지 URL
                            LIKE_COUNT=0
                        )
                        players.append(new_player)
                        existing_names.append(name)  # 동일 이름 중복 방지를 위해 추가
                        new_player_count += 1
        
        # 데이터 삽입
        if players:
            session.add_all(players)
            session.commit()
            print(f"[{file_name}] {new_player_count}명의 선수 데이터 삽입 완료")
            
            # 추가된 선수 정보 출력 (각 파일별 최대 5명만 출력)
            print(f"\n추가된 선수 목록 (최대 5명):")
            for idx, player in enumerate(players[:5], 1):
                print(f"{idx}. {player.PLAYER_NAME} (등번호: {player.PLAYER_NUM})")
            
            if len(players) > 5:
                print(f"그 외 {len(players) - 5}명 추가...")
                
            total_added_players += new_player_count
        else:
            print(f"[{file_name}] 추가할 새로운 선수가 없습니다.")
    
    print(f"\n모든 팀 처리 완료! 총 {total_added_players}명의 선수 데이터가 추가되었습니다.")
    
except Exception as e:
    session.rollback()
    print(f"데이터 처리 중 오류 발생: {e}")
finally:
    session.close()