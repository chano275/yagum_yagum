import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date
import sys

# 현재 스크립트 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # app 폴더의 상위 폴더로 이동

# 환경 변수 설정을 위한 dotenv 불러오기
from dotenv import load_dotenv
load_dotenv()

# 프로젝트 루트 경로를 파이썬 경로에 추가
sys.path.append(project_root)

# models 모듈 import
import models

# 데이터베이스 연결 설정
DATABASE_URL = f'{os.getenv("DATABASE_TYPE")}://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_IP")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_DB")}?charset=utf8mb4'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 팀 약자를 팀 ID로 매핑하는 딕셔너리
team_mapping = {
    'KIA': 1,  # KIA 타이거즈
    '삼성': 2,   # 삼성 라이온즈
    'LG': 3,   # LG 트윈스
    '두산': 4,  # 두산 베어스
    'KT': 5,   # KT 위즈
    'SSG': 6,  # SSG 랜더스
    '롯데': 7,  # 롯데 자이언츠
    '한화': 8,  # 한화 이글스
    'NC': 9,   # NC 다이노스
    '키움': 10, # 키움 히어로즈
}

# 기록 유형 약자를 기록 유형 ID로 매핑하는 딕셔너리
record_mapping = {
    'W': 1,     # 승리
    'L': 2,     # 패배
    'D': 3,     # 무승부
    'H': 4,     # 안타
    'HR': 5,    # 홈런
    'R': 6,     # 득점
    'SO': 8,   # 삼진
    '사구': 9,    # 볼넷/몸맞공
    'GDP': 11,  # 병살타
    '실책': 12,   # 실책
    '도루': 13,    # 도루는 안타로 간주
    '경기결과': None  # 이 값은 처리 시 변경됩니다
}

def process_csv_files():
    # CSV 파일 목록 가져오기
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv') and f.startswith('2025')]
    
    print(f"처리할 CSV 파일 수: {len(csv_files)}")
    
    total_records = 0
    
    for csv_file in csv_files:
        file_path = os.path.join(csv_dir, csv_file)
        print(f"파일 처리 중: {csv_file}")
        
        try:
            # 파일명에서 날짜 추출 (예: 20250322-play_log.csv -> 2025-03-22)
            file_date_str = csv_file.split('-')[0]
            game_date = datetime.strptime(file_date_str, '%Y%m%d').date()
            
            # CSV 파일 읽기
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # 첫 번째 행이 헤더인지 확인
            if '날짜' in df.columns[0]:
                # 헤더가 있는 경우 처리
                df = pd.read_csv(file_path, encoding='utf-8', skiprows=0)
            else:
                # 헤더가 없는 경우 열 이름 지정
                df = pd.read_csv(file_path, encoding='utf-8', names=['날짜', '팀', '기록', '기록값'])
            
            # 각 행 처리
            for _, row in df.iterrows():
                # NaN 값 체크
                if pd.isna(row['날짜']) or pd.isna(row['팀']) or pd.isna(row['기록']) or pd.isna(row['기록값']):
                    continue
                
                # 날짜 파싱
                try:
                    # CSV에 날짜가 있는 경우 (YYYY-MM-DD 형식)
                    row_date = datetime.strptime(str(row['날짜']), '%Y-%m-%d').date()
                except:
                    # 파일명에서 추출한 날짜 사용
                    row_date = game_date
                
                # 팀 ID 찾기
                team_name = row['팀']
                if team_name not in team_mapping:
                    print(f"알 수 없는 팀: {team_name}, 건너뜁니다.")
                    continue
                
                team_id = team_mapping[team_name]
                
                # 기록 유형 찾기
                record_type = row['기록']
                record_type_id = None
                
                # 경기결과인 경우 값에 따라 record_type_id 결정
                if record_type == '경기결과':
                    result_value = row['기록값']
                    if result_value == 'W':
                        record_type_id = 1  # 승리
                    elif result_value == 'L':
                        record_type_id = 2  # 패배
                    elif result_value == 'D':
                        record_type_id = 3  # 무승부
                    else:
                        print(f"알 수 없는 경기 결과 값: {result_value}, 건너뜁니다.")
                        continue
                        
                    # 함수 호출하여 Team 테이블도 업데이트
                    process_game_result(team_name, result_value, row_date)
                else:
                    # 일반 기록 유형
                    if record_type not in record_mapping or record_mapping[record_type] is None:
                        print(f"알 수 없는 기록 유형: {record_type}, 건너뜁니다.")
                        continue
                    record_type_id = record_mapping[record_type]
                
                # 기록값 변환 (숫자 또는 문자)
                try:
                    if record_type == '경기결과':
                        # 경기결과는 항상 1로 설정 (발생 횟수)
                        count = 1
                    else:
                        # 일반 기록은 숫자로 변환
                        count = int(float(row['기록값']))
                except:
                    # 숫자가 아닌 경우 1로 처리 (발생 횟수)
                    count = 1
                
                # 이미 동일한 날짜, 팀, 기록 유형의 게임 로그가 있는지 확인
                existing_log = session.query(models.GameLog).filter(
                    models.GameLog.DATE == row_date,
                    models.GameLog.TEAM_ID == team_id,
                    models.GameLog.RECORD_TYPE_ID == record_type_id
                ).first()
                
                if existing_log:
                    # 기존 로그 업데이트
                    existing_log.COUNT = count
                    print(f"기존 로그 업데이트: 날짜={row_date}, 팀={team_name}, 기록={record_type}, 값={count}")
                else:
                    # 새 로그 생성
                    new_log = models.GameLog(
                        DATE=row_date,
                        TEAM_ID=team_id,
                        RECORD_TYPE_ID=record_type_id,
                        COUNT=count
                    )
                    session.add(new_log)
                    print(f"새 로그 추가: 날짜={row_date}, 팀={team_name}, 기록={record_type}, 값={count}")
                    
                total_records += 1
            
            # 변경사항 커밋
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"파일 {csv_file} 처리 중 오류 발생: {str(e)}")
    
    print(f"총 {total_records}개의 기록이 처리되었습니다.")

def process_game_result(team_name, result, game_date):
    """
    경기 결과를 처리하여 팀의 승패 기록 업데이트
    게임 로그 테이블에는 이미 이전 코드에서 저장했으므로 
    여기서는 Team 테이블만 업데이트
    """
    team_id = team_mapping.get(team_name)
    if not team_id:
        print(f"알 수 없는 팀: {team_name}, 경기 결과 처리를 건너뜁니다.")
        return
    
    # 팀 정보 조회
    team = session.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
    if not team:
        print(f"팀 ID {team_id}를 찾을 수 없습니다.")
        return
    
    # 승패 기록 업데이트 (Team 테이블)
    if result == 'W':
        team.TOTAL_WIN += 1
        print(f"{team_name} 팀 승리 기록 추가")
    elif result == 'L':
        team.TOTAL_LOSE += 1
        print(f"{team_name} 팀 패배 기록 추가")
    elif result == 'D':
        team.TOTAL_DRAW += 1
        print(f"{team_name} 팀 무승부 기록 추가")
    else:
        print(f"알 수 없는 경기 결과: {result}")
    
    # 변경사항 커밋
    session.commit()

if __name__ == "__main__":
    # CSV 파일이 있는 디렉토리 경로
    csv_dir = os.path.join(project_root, 'data', 'processed_data')
    
    try:
        process_csv_files()
        print("CSV 파일 처리가 완료되었습니다.")
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()