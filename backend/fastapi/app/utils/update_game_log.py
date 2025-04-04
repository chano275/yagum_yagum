import os
import json
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# 현재 스크립트 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))  # app/DB 폴더
project_root = os.path.dirname(current_dir)

# 환경 변수 설정을 위한 dotenv 불러오기
from dotenv import load_dotenv
load_dotenv()

# 프로젝트 루트 경로를 파이썬 경로에 추가
sys.path.append(project_root)

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

# 기록 유형 매핑 (JSON 필드 -> 레코드 타입 ID)
record_type_mapping = {
    'W': 1,     # 승리
    'L': 2,     # 패배
    'D': 3,     # 무승부
    'H': 4,     # 안타
    'HR': 5,    # 홈런
    'R': 6,     # 득점
    'SO': 8,    # 삼진
    'BB': 9,    # 볼넷/몸맞공
    'GDP': 11,  # 병살타
    '실책': 12,   # 실책
    '도루': 13,   # 도루
    '경기결과': None  # 이 값은 처리 시 변경됩니다
}

def process_json_game_logs(json_dir="baseball_data/json_data"):
    """
    JSON 파일을 처리하여 게임 로그 정보를 DB에 저장
    
    Args:
        json_dir (str): JSON 파일이 위치한 디렉토리 경로
    """
    # JSON 파일이 있는 디렉토리 경로 (기본값으로 프로젝트 루트의 json_data 폴더 사용)
    json_dir_path = os.path.join(os.path.dirname(current_dir), json_dir)
    
    if not os.path.exists(json_dir_path):
        logger.error(f"JSON 데이터 디렉토리를 찾을 수 없습니다: {json_dir_path}")
        return
    
    # JSON 파일 목록 가져오기 (파일명이 날짜 형식인 play_log.json 파일)
    json_files = [f for f in os.listdir(json_dir_path) if f.endswith('-play_log.json') or f.endswith('_play_log.json') or f.endswith('play_log.json')]
    
    if not json_files:
        logger.warning(f"{json_dir_path} 내에 처리할 JSON 파일이 없습니다.")
        json_files = [f for f in os.listdir(json_dir_path) if f.endswith('.json')]
        if json_files:
            logger.info(f"다음 JSON 파일을 찾았습니다: {json_files}")
        return
    
    logger.info(f"처리할 JSON 파일 수: {len(json_files)}")
    
    total_records = 0
    
    for json_file in json_files:
        file_path = os.path.join(json_dir_path, json_file)
        logger.info(f"파일 처리 중: {json_file}")
        
        try:
            # 파일명에서 날짜 추출 (예: 20250330-play_log.json -> 2025-03-30)
            file_date_str = None
            for date_format in ['%Y%m%d', '%Y-%m-%d']:
                try:
                    # 파일명의 처음 8자가 날짜인 경우 (YYYYMMDD)
                    if json_file[:8].isdigit():
                        file_date_str = json_file[:8]
                        game_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                        break
                    # 날짜 형식이 YYYY-MM-DD인 경우
                    elif '-' in json_file[:10] and len(json_file[:10].split('-')) == 3:
                        file_date_str = json_file[:10]
                        game_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()
                        break
                except (ValueError, IndexError):
                    continue
            
            # 날짜를 추출하지 못한 경우
            if file_date_str is None:
                logger.warning(f"파일명에서 날짜를 추출할 수 없습니다: {json_file}, 현재 날짜로 처리합니다.")
                game_date = date.today()
            
            # JSON 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                game_records = json.load(f)
            
            # 게임 기록 처리 (리스트 형태)
            # 파일명에서 추출한 날짜 사용
            record_date = game_date
            logger.info(f"날짜 {record_date}의 기록 처리 중...")
                    
            # 각 기록 처리
            for record in game_records:
                # 필수 필드 확인
                if '팀' not in record or '기록' not in record or '기록값' not in record:
                    logger.warning(f"필수 필드가 없는 레코드가 발견되었습니다: {record}")
                    continue
                
                # 팀 정보 처리
                team_name = record['팀']
                if team_name not in team_mapping:
                    logger.warning(f"알 수 없는 팀: {team_name}, 건너뜁니다.")
                    continue
                
                team_id = team_mapping[team_name]
                
                # 기록 유형 처리
                record_type = record['기록']
                record_value = record['기록값']
                
                # 경기결과 처리
                if record_type == '경기결과':
                    if record_value == 'W':
                        record_type_id = 1  # 승리
                    elif record_value == 'L':
                        record_type_id = 2  # 패배
                    elif record_value == 'D':
                        record_type_id = 3  # 무승부
                    else:
                        logger.warning(f"알 수 없는 경기 결과 값: {record_value}, 건너뜁니다.")
                        continue
                    
                    # 팀 테이블 업데이트
                    team = session.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
                    if team:
                        if record_value == 'W':
                            team.TOTAL_WIN += 1
                            logger.info(f"{team_name} 팀 승리 기록 추가")
                        elif record_value == 'L':
                            team.TOTAL_LOSE += 1
                            logger.info(f"{team_name} 팀 패배 기록 추가")
                        elif record_value == 'D':
                            team.TOTAL_DRAW += 1
                            logger.info(f"{team_name} 팀 무승부 기록 추가")
                        
                        session.commit()
                    
                    # 기록값은 항상 1로 설정 (경기 수)
                    count = 1
                else:
                    # 일반 기록 타입 처리
                    if record_type not in record_type_mapping or record_type_mapping[record_type] is None:
                        logger.warning(f"알 수 없는 기록 유형: {record_type}, 건너뜁니다.")
                        continue
                    
                    record_type_id = record_type_mapping[record_type]
                    
                    # 기록값을 숫자로 변환
                    try:
                        count = int(float(record_value))
                    except (ValueError, TypeError):
                        # 숫자가 아닌 경우 1로 처리 (발생 횟수)
                        count = 1
                
                # 이미 동일한 날짜, 팀, 기록 유형의 게임 로그가 있는지 확인
                existing_log = session.query(models.GameLog).filter(
                    models.GameLog.DATE == record_date,
                    models.GameLog.TEAM_ID == team_id,
                    models.GameLog.RECORD_TYPE_ID == record_type_id
                ).first()
                
                if existing_log:
                    # 기존 로그 업데이트
                    existing_log.COUNT = count
                    logger.info(f"기존 로그 업데이트: 날짜={record_date}, 팀={team_name}, 기록={record_type}, 값={count}")
                else:
                    # 새 로그 생성
                    new_log = models.GameLog(
                        DATE=record_date,
                        TEAM_ID=team_id,
                        RECORD_TYPE_ID=record_type_id,
                        COUNT=count
                    )
                    session.add(new_log)
                    logger.info(f"새 로그 추가: 날짜={record_date}, 팀={team_name}, 기록={record_type}, 값={count}")
                    
                    total_records += 1
            # 변경사항 커밋
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"파일 {json_file} 처리 중 오류 발생: {str(e)}")
    
    logger.info(f"총 {total_records}개의 기록이 처리되었습니다.")

if __name__ == "__main__":
    try:
        # 명령줄 인자 처리
        import argparse
        parser = argparse.ArgumentParser(description='JSON 게임 로그 처리')
        parser.add_argument('--dir', type=str, help='JSON 파일 디렉토리 경로', default='baseball_data/json_data')
        args = parser.parse_args()
        
        process_json_game_logs(args.dir)
        logger.info("JSON 파일 처리가 완료되었습니다.")
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()