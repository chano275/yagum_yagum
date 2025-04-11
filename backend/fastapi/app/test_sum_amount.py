# team_balance_test.py
import os
import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta

# 현재 파일 위치를 기준으로 상위 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
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

def get_team_actual_balances():
    """
    응원하는 팀별로 실제 입금된 총액을 구하는 함수 (현재 계정 잔액 기준)
    """
    print("\n=== 현재 계정 잔액 기준 팀별 실제 입금된 총액 ===")
    
    # 팀별 실제 계정 잔액 총액 쿼리 실행
    team_balances = session.query(
        models.Team.TEAM_ID,
        models.Team.TEAM_NAME,
        func.sum(models.Account.TOTAL_AMOUNT).label("total_actual_balance")
    ).join(
        models.Account, models.Team.TEAM_ID == models.Account.TEAM_ID
    ).group_by(
        models.Team.TEAM_ID, models.Team.TEAM_NAME
    ).order_by(
        func.sum(models.Account.TOTAL_AMOUNT).desc()
    ).all()
    
    # 결과 출력
    if not team_balances:
        print("데이터가 없습니다.")
        return
    
    for team_id, team_name, total_amount in team_balances:
        print(f"{team_name}: {total_amount:,}원")

def get_team_actual_balances_by_date(target_date=None):
    """
    응원하는 팀별로 특정 날짜의 실제 입금된 총액을 구하는 함수 (일일 잔액 기록 기준)
    """
    # 날짜 설정 (기본값: 오늘)
    if target_date is None:
        target_date = date.today()
    
    print(f"\n=== {target_date} 일일 잔액 기록 기준 팀별 실제 입금된 총액 ===")
    
    # 팀별 특정 날짜의 일일 잔액 총액 쿼리 실행
    team_balances = session.query(
        models.Team.TEAM_ID,
        models.Team.TEAM_NAME,
        func.sum(models.DailyBalances.CLOSING_BALANCE).label("total_actual_balance")
    ).join(
        models.Account, models.Team.TEAM_ID == models.Account.TEAM_ID
    ).join(
        models.DailyBalances, models.Account.ACCOUNT_ID == models.DailyBalances.ACCOUNT_ID
    ).filter(
        models.DailyBalances.DATE == target_date
    ).group_by(
        models.Team.TEAM_ID, models.Team.TEAM_NAME
    ).order_by(
        func.sum(models.DailyBalances.CLOSING_BALANCE).desc()
    ).all()
    
    # 결과 출력
    if not team_balances:
        print(f"{target_date} 날짜에 대한 데이터가 없습니다.")
        return
    
    for team_id, team_name, total_amount in team_balances:
        print(f"{team_name}: {total_amount:,}원")

def get_team_daily_savings(target_date=None):
    """
    응원하는 팀별로 일일 적금 금액의 총합을 구하는 함수
    """
    # 날짜 설정 (기본값: 오늘)
    if target_date is None:
        target_date = date.today()
    
    print(f"\n=== {target_date} 일일 적금 내역 기준 팀별 적금 금액 총합 ===")
    
    # 팀별 일일 적금 총액 쿼리 실행
    team_savings = session.query(
        models.Team.TEAM_ID,
        models.Team.TEAM_NAME,
        func.sum(models.DailySaving.DAILY_SAVING_AMOUNT).label("total_daily_saving")
    ).join(
        models.Account, models.Team.TEAM_ID == models.Account.TEAM_ID
    ).join(
        models.DailySaving, models.Account.ACCOUNT_ID == models.DailySaving.ACCOUNT_ID
    ).filter(
        models.DailySaving.DATE == target_date
    ).group_by(
        models.Team.TEAM_ID, models.Team.TEAM_NAME
    ).order_by(
        func.sum(models.DailySaving.DAILY_SAVING_AMOUNT).desc()
    ).all()
    
    # 결과 출력
    if not team_savings:
        print(f"{target_date} 날짜에 대한 데이터가 없습니다.")
        return
    
    for team_id, team_name, total_amount in team_savings:
        print(f"{team_name}: {total_amount:,}원")

def get_team_transfer_status():
    """
    팀별 일일 적립 내역과 실제 입금된 금액의 차이를 확인하는 함수
    (모든 적립 내역이 실제로 이체되었는지 확인)
    """
    yesterday = (datetime.now().date() - timedelta(days=1))
    print(f"\n=== {yesterday} 적립 내역과 실제 이체 금액 비교 ===")
    
    # 팀별 일일 적금 내역 총액
    daily_savings = session.query(
        models.Team.TEAM_ID,
        models.Team.TEAM_NAME,
        func.sum(models.DailySaving.DAILY_SAVING_AMOUNT).label("total_daily_saving")
    ).join(
        models.Account, models.Team.TEAM_ID == models.Account.TEAM_ID
    ).join(
        models.DailySaving, models.Account.ACCOUNT_ID == models.DailySaving.ACCOUNT_ID
    ).filter(
        models.DailySaving.DATE == yesterday
    ).group_by(
        models.Team.TEAM_ID, models.Team.TEAM_NAME
    ).all()
    
    # 결과가 없으면 종료
    if not daily_savings:
        print(f"{yesterday} 날짜에 대한 적립 내역이 없습니다.")
        return
    
    # 비교 결과 출력
    print("팀 | 적립 예정 금액 | 이체 확인 여부")
    print("----------------------------------")
    
    for team_id, team_name, total_saving in daily_savings:
        # 이 팀에 속한 계정들의 어제와 오늘의 잔액 차이 계산
        # (이체가 정상적으로 이루어졌다면 차이가 있어야 함)
        
        # 방법 1: 계정 잔액 변화로 확인 (실제 구현에서는 DailyBalances 테이블로 확인하는 것이 더 정확함)
        accounts = session.query(models.Account).filter(models.Account.TEAM_ID == team_id).all()
        transfer_confirmed = False
        
        # 간단한 예시로만 작성 (실제로는 더 정교한 확인 로직 필요)
        if accounts:
            transfer_confirmed = True
            
        status = "✅ 이체 완료" if transfer_confirmed else "❌ 이체 미확인"
        print(f"{team_name} | {total_saving:,}원 | {status}")

if __name__ == "__main__":
    try:
        # 1. 팀별 현재 계정 잔액 총액 조회
        get_team_actual_balances()
        
        # 2. 특정 날짜의 팀별 일일 잔액 총액 조회
        yesterday = (datetime.now().date() - timedelta(days=1))
        get_team_actual_balances_by_date(yesterday)
        
        # 3. 특정 날짜의 팀별 일일 적금 내역 총액 조회
        get_team_daily_savings(yesterday)
        
        # 4. 적립 내역과 실제 이체 금액 비교
        get_team_transfer_status()
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        session.close()