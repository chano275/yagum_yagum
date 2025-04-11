import os
import sys
import csv
import argparse
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 위치 기준으로 프로젝트 루트 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 프로젝트 루트 경로를 시스템 경로에 추가
sys.path.append(project_root)

# 환경 변수 및 모델 import
from dotenv import load_dotenv
load_dotenv()

import models
from database import engine

# 팀 이름 매핑
TEAM_NAME_MAPPING = {
    '기아': 'KIA 타이거즈', 
    'KIA': 'KIA 타이거즈',
    '삼성': '삼성 라이온즈', 
    'LG': 'LG 트윈스', 
    '두산': '두산 베어스', 
    'SSG': 'SSG 랜더스', 
    '한화': '한화 이글스', 
    'KT': 'KT 위즈', 
    '롯데': '롯데 자이언츠', 
    'NC': 'NC 다이노스', 
    '키움': '키움 히어로즈'
}

def process_daily_rank_file(file_path):
    """
    일일 순위 CSV 파일을 처리하고 데이터베이스에 저장
    
    Args:
        file_path (str): 일일 순위 CSV 파일 경로
    
    Returns:
        dict: 처리 결과 정보
    """
    # 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 파일명에서 날짜 추출 (예: 20250325-rank.csv)
        filename = os.path.basename(file_path)
        date_str = filename.split('-rank')[0]
        rank_date = datetime.strptime(date_str, '%Y%m%d').date()
        
        # CSV 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # 헤더 건너뛰기 (있는 경우)
            
            # 결과 저장용 변수
            processed_records = 0
            
            # 각 행 처리
            for row_index, row in enumerate(reader, 1):
                # 팀 이름 (첫 번째 열) 추출
                team_name = row[0].strip()
                
                # 전체 팀 이름으로 변환
                if team_name not in TEAM_NAME_MAPPING:
                    print(f"알 수 없는 팀명: {team_name}")
                    print("현재 매핑된 팀명:", list(TEAM_NAME_MAPPING.keys()))
                    continue
                
                full_team_name = TEAM_NAME_MAPPING[team_name]
                
                # 데이터베이스에서 해당 팀 찾기
                team = session.query(models.Team).filter(
                    models.Team.TEAM_NAME == full_team_name
                ).first()
                
                if not team:
                    print(f"데이터베이스에서 팀을 찾을 수 없음: {full_team_name}")
                    continue
                
                # 이미 해당 날짜의 순위가 있는지 확인
                existing_rating = session.query(models.TeamRating).filter(
                    models.TeamRating.TEAM_ID == team.TEAM_ID,
                    models.TeamRating.DATE == rank_date
                ).first()
                
                # 순위 정보 (1부터 시작하는 인덱스)
                daily_ranking = row_index
                
                if existing_rating:
                    # 기존 레코드 업데이트
                    existing_rating.DAILY_RANKING = daily_ranking
                    print(f"팀 {full_team_name}의 {rank_date} 순위 업데이트: {daily_ranking}위")
                else:
                    # 새 레코드 생성
                    team_rating = models.TeamRating(
                        TEAM_ID=team.TEAM_ID,
                        DAILY_RANKING=daily_ranking,
                        DATE=rank_date
                    )
                    session.add(team_rating)
                    print(f"팀 {full_team_name}의 {rank_date} 순위 새로 생성: {daily_ranking}위")
                
                processed_records += 1
            
            # 변경사항 커밋
            session.commit()
            
            print(f"{filename} 파일 처리 완료: {processed_records}개 팀 순위 저장")
            
            return {
                "filename": filename,
                "date": rank_date,
                "processed_records": processed_records
            }
    
    except Exception as e:
        session.rollback()
        print(f"오류 발생: {str(e)}")
        raise
    
    finally:
        session.close()

def find_rank_file(data_folder, target_date):
    """
    특정 날짜의 순위 파일 찾기
    
    Args:
        data_folder (str): 순위 파일이 있는 폴더 경로
        target_date (date): 찾고자 하는 날짜
    
    Returns:
        str or None: 파일 경로, 없으면 None
    """
    target_filename = f"{target_date.strftime('%Y%m%d')}-rank.csv"
    file_path = os.path.join(data_folder, target_filename)
    print(file_path)
    print(os.path.exists(file_path))
    return file_path if os.path.exists(file_path) else None

def main():
    # 데이터 폴더 경로 설정
    data_folder = os.path.join(project_root,'baseball_data', 'daily_rank')
    
    # 인자 파서 설정
    parser = argparse.ArgumentParser(description='일일 팀 순위 데이터베이스 업데이트')
    parser.add_argument('--date', type=str, help='YYYYMMDD 형식의 날짜 (미입력 시 전일)', default=None)
    
    # 인자 파싱
    args = parser.parse_args()
    
    # 날짜 설정
    if args.date:
        # 사용자가 날짜 입력한 경우
        try:
            target_date = datetime.strptime(args.date, '%Y%m%d').date()
        except ValueError:
            print("날짜 형식은 YYYYMMDD여야 합니다.")
            return
    else:
        # 날짜 미입력 시 전일 사용
        target_date = datetime.now().date() - timedelta(days=1)
    
    # 해당 날짜의 순위 파일 찾기
    rank_file = find_rank_file(data_folder, target_date)
    
    if rank_file:
        # 파일 존재 시 처리
        process_daily_rank_file(rank_file)
    else:
        print(f"{target_date} 날짜의 순위 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()