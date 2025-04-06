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

def update_team_victory_missions(db_session):
    """
    팀의 승리 횟수를 체크하고, 10승마다 해당 팀을 응원하는 유저들의 미션 카운트를 업데이트합니다.
    
    Args:
        db_session (Session): 데이터베이스 세션
    """
    logger.info("팀 승리 미션 업데이트 시작...")
    
    # 1. 미션 정보 가져오기 ("응원팀 10승당 우대금리" 미션)
    team_victory_mission = db_session.query(models.Mission).filter(
        models.Mission.MISSION_NAME.like("%10승당%")
    ).first()
    
    if not team_victory_mission:
        logger.warning("10승당 우대금리 미션을 찾을 수 없습니다.")
        return
    
    mission_id = team_victory_mission.MISSION_ID
    mission_max_count = team_victory_mission.MISSION_MAX_COUNT
    mission_rate = team_victory_mission.MISSION_RATE
    
    logger.info(f"미션 ID {mission_id}: {team_victory_mission.MISSION_NAME} 처리 중...")
    
    # 2. 모든 팀의 현재 승리 횟수 가져오기
    teams = db_session.query(models.Team).all()
    
    for team in teams:
        team_id = team.TEAM_ID
        team_name = team.TEAM_NAME
        total_wins = team.TOTAL_WIN
        
        logger.info(f"팀 {team_name}(ID: {team_id}) 처리 중...")
        logger.info(f"현재 총 승리 횟수: {total_wins}")
        
        # 3. 해당 팀을 응원하는 계정들 조회
        team_accounts = db_session.query(models.Account).filter(
            models.Account.TEAM_ID == team_id
        ).all()
        
        if not team_accounts:
            logger.info(f"팀 {team_name}을 응원하는 계정이 없습니다.")
            continue
            
        logger.info(f"팀 {team_name}을 응원하는 계정 수: {len(team_accounts)}")
        
        # 4. 각 계정별로 미션 업데이트
        for account in team_accounts:
            account_id = account.ACCOUNT_ID
            
            # 4.1. 해당 미션이 이미 등록되어 있는지 확인
            used_mission = db_session.query(models.UsedMission).filter(
                models.UsedMission.ACCOUNT_ID == account_id,
                models.UsedMission.MISSION_ID == mission_id
            ).first()
            
            if not used_mission:
                # 4.2. 미션이 등록되어 있지 않으면 새로 생성
                used_mission = models.UsedMission(
                    ACCOUNT_ID=account_id,
                    MISSION_ID=mission_id,
                    COUNT=0,  # 초기 카운트 0
                    MAX_COUNT=mission_max_count,
                    MISSION_RATE=mission_rate,
                    created_at=datetime.now()
                )
                db_session.add(used_mission)
                db_session.flush()
                logger.info(f"계정 ID {account_id}에 미션 신규 등록")
            
            # 4.3. 현재 미션 카운트 확인
            current_count = used_mission.COUNT
            
            # 4.4. 총 승리 횟수를 10으로 나눈 몫이 현재 카운트보다 크면 업데이트
            new_count = total_wins // 10  # 10승당 1 카운트
            
            if new_count > current_count:
                # 최대 카운트를 초과하지 않도록 체크
                if new_count > used_mission.MAX_COUNT:
                    new_count = used_mission.MAX_COUNT
                
                # 카운트가 실제로 증가했을 때만 기록 남기기
                if new_count > current_count:
                    old_count = current_count
                    used_mission.COUNT = new_count
                    logger.info(f"계정 ID {account_id}의 미션 카운트 업데이트: {old_count} -> {new_count}")
                    
                    # 최대 카운트에 도달했는지 체크
                    if new_count >= used_mission.MAX_COUNT:
                        logger.info(f"계정 ID {account_id}의 미션 카운트가 최대치({used_mission.MAX_COUNT})에 도달했습니다.")
    
    logger.info("팀 승리 미션 업데이트 완료")

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
        return
    
    logger.info(f"처리할 JSON 파일 수: {len(json_files)}")
    
    total_records = 0
    
    for json_file in json_files:
        file_path = os.path.join(json_dir_path, json_file)
        logger.info(f"파일 처리 중: {json_file}")
        
        try:
            # JSON 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                game_records_dict = json.load(f)
            
            # 날짜별로 기록 처리
            for game_date, records in game_records_dict.items():
                # 날짜 파싱
                try:
                    record_date = datetime.strptime(game_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    logger.warning(f"날짜 파싱 실패: {game_date}")
                    continue
                
                # 각 기록 처리
                for record in records:
                    # 필수 필드 확인
                    if not all(key in record for key in ['팀', '기록', '기록값']):
                        logger.warning(f"필수 필드가 없는 레코드 건너뜀: {record}")
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
    
    # 팀 승리 미션 업데이트 실행
    try:
        logger.info("팀 승리 관련 미션 업데이트 시작...")
        update_team_victory_missions(session)
        session.commit()
        logger.info("팀 승리 관련 미션 업데이트 완료")
    except Exception as e:
        logger.error(f"미션 업데이트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    try:
        # 명령줄 인자 처리
        import argparse
        parser = argparse.ArgumentParser(description='JSON 게임 로그 처리')
        parser.add_argument('--dir', type=str, help='JSON 파일 디렉토리 경로', default='baseball_data/json_data')
        args = parser.parse_args()
        
        process_json_game_logs(args.dir)
        logger.info("JSON 파일 처리가 완료되었습니다.")
        
        # 직접 미션 업데이트 함수 호출 추가
        logger.info("팀 승리 미션 직접 업데이트 시작...")
        update_team_victory_missions(session)
        logger.info("팀 승리 미션 직접 업데이트 완료")
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()