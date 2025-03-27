# update_daily_balances.py
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import date, datetime, timedelta
import asyncio
import logging
import argparse

# 현재 스크립트 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 데이터베이스 연결
from dotenv import load_dotenv
load_dotenv()

# 모듈 import를 위한 경로 설정
import sys
sys.path.append(project_root)
import models

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, 'daily_balances.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def update_daily_balances(db, date_param=None):
    """
    모든 계정의 일일 잔액을 daily_balances 테이블에 기록합니다.
    해당 날짜의 기록이 이미 있으면 업데이트하고, 없으면 새로 생성합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        date_param (date, optional): 잔액 기록 날짜. 기본값은 오늘.
    
    Returns:
        dict: 처리 결과 요약 정보
    """
    # 날짜 설정 (기본값: 오늘)
    if date_param is None:
        date_param = datetime.now().date()
    
    logger.info(f"[{date_param}] 일일 잔액 기록 시작...")
    
    processed_accounts = 0
    new_records = 0
    updated_records = 0
    
    try:
        # 모든 계정 조회
        accounts = db.query(models.Account).all()
        
        for account in accounts:
            # 해당 날짜의 기존 기록 조회
            daily_balance = db.query(models.DailyBalances).filter(
                models.DailyBalances.ACCOUNT_ID == account.ACCOUNT_ID,
                models.DailyBalances.DATE == date_param
            ).first()
            
            # 기본 이자 금액은 0으로 설정 (이자 계산은 별도 함수에서 처리)
            daily_interest = 0
            
            if daily_balance:
                # 기존 기록이 있으면 업데이트
                daily_balance.CLOSING_BALANCE = account.TOTAL_AMOUNT
                updated_records += 1
                logger.debug(f"계정 ID {account.ACCOUNT_ID}: 잔액 기록 업데이트 ({daily_balance.CLOSING_BALANCE}원)")
            else:
                # 기존 기록이 없으면 새로 생성
                daily_balance = models.DailyBalances(
                    ACCOUNT_ID=account.ACCOUNT_ID,
                    DATE=date_param,
                    CLOSING_BALANCE=account.TOTAL_AMOUNT,
                    DAILY_INTEREST=daily_interest
                )
                db.add(daily_balance)
                new_records += 1
                logger.debug(f"계정 ID {account.ACCOUNT_ID}: 새 잔액 기록 생성 ({account.TOTAL_AMOUNT}원)")
            
            processed_accounts += 1
        
        # 변경사항 커밋
        db.commit()
        
        summary = {
            "date": date_param,
            "processed_accounts": processed_accounts,
            "new_records": new_records,
            "updated_records": updated_records
        }
        
        logger.info(f"[{date_param}] 일일 잔액 기록 완료: {processed_accounts}개 계정 처리 ({new_records}개 신규, {updated_records}개 업데이트)")
        return summary
        
    except Exception as e:
        db.rollback()
        logger.error(f"일일 잔액 기록 중 오류 발생: {str(e)}")
        raise

async def calculate_daily_interest(db, date_param=None):
    """
    모든 계정의 일일 이자를 계산하고 daily_balances 테이블에 기록합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        date_param (date, optional): 처리할 날짜. 기본값은 오늘.
    
    Returns:
        dict: 처리 결과 요약 정보
    """
    # 날짜 설정 (기본값: 오늘)
    if date_param is None:
        date_param = datetime.now().date()
    
    logger.info(f"[{date_param}] 일일 이자 계산 시작...")
    
    processed_accounts = 0
    total_interest = 0
    
    try:
        # 해당 날짜에 잔액 기록이 있는 모든 계정 조회
        daily_balances = db.query(models.DailyBalances).filter(
            models.DailyBalances.DATE == date_param
        ).all()
        
        for daily_balance in daily_balances:
            # 계정 정보 조회
            account = db.query(models.Account).filter(
                models.Account.ACCOUNT_ID == daily_balance.ACCOUNT_ID
            ).first()
            
            if not account:
                logger.warning(f"계정 ID {daily_balance.ACCOUNT_ID}를 찾을 수 없습니다.")
                continue
            
            # 이자율 조회 (실제 이자율은 계정 정보와 미션 달성에 따라 계산)
            interest_rate = account.INTEREST_RATE
            
            # 일일 이자 계산 (연이율 / 365 * 잔액)
            daily_interest_rate = interest_rate / 100 / 365
            daily_interest_amount = round(daily_balance.CLOSING_BALANCE * daily_interest_rate)
            
            # daily_balances 테이블 업데이트
            daily_balance.DAILY_INTEREST = daily_interest_amount
            
            processed_accounts += 1
            total_interest += daily_interest_amount
            
            logger.info(f"계정 ID {daily_balance.ACCOUNT_ID}: 잔액 {daily_balance.CLOSING_BALANCE}원, 이자율 {interest_rate}%, 일일 이자 {daily_interest_amount}원")
        
        # 변경사항 커밋
        db.commit()
        
        summary = {
            "date": date_param,
            "processed_accounts": processed_accounts,
            "total_interest": total_interest
        }
        
        logger.info(f"[{date_param}] 일일 이자 계산 완료: {processed_accounts}개 계정, 총 {total_interest}원 이자 발생")
        return summary
        
    except Exception as e:
        db.rollback()
        logger.error(f"일일 이자 계산 중 오류 발생: {str(e)}")
        raise

async def update_balances_for_range(start_date=None, end_date=None, db_session=None):
    """
    지정된 날짜 범위의 모든 계정 잔액을 daily_balances 테이블에 기록합니다.
    
    Args:
        start_date (date, optional): 시작 날짜. 기본값은 어제.
        end_date (date, optional): 종료 날짜. 기본값은 어제.
        db_session (Session, optional): 데이터베이스 세션. None이면 새 세션 생성.
    
    Returns:
        list: 각 날짜별 처리 결과 요약 정보
    """
    # 날짜 설정 (기본값: 어제)
    if start_date is None:
        start_date = datetime.now().date() - timedelta(days=1)
    if end_date is None:
        end_date = start_date
    
    # DB 세션 설정
    close_session = False
    if db_session is None:
        DATABASE_URL = f'{os.getenv("DATABASE_TYPE")}://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_IP")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_DB")}?charset=utf8mb4'
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        close_session = True
    
    results = []
    try:
        current_date = start_date
        while current_date <= end_date:
            logger.info(f"날짜 {current_date} 처리 시작")
            
            # 일일 잔액 기록
            balance_result = await update_daily_balances(db_session, current_date)
            
            # 일일 이자 계산
            interest_result = await calculate_daily_interest(db_session, current_date)
            
            # 결과 병합
            combined_result = {
                "date": current_date,
                "balances": balance_result,
                "interest": interest_result
            }
            
            results.append(combined_result)
            current_date += timedelta(days=1)
            
        return results
    finally:
        if close_session:
            db_session.close()

async def main():
    parser = argparse.ArgumentParser(description='일일 계좌 잔액 및 이자 기록')
    parser.add_argument('--date', type=str, help='처리할 날짜 (YYYY-MM-DD 형식, 기본값: 어제)')
    parser.add_argument('--start-date', type=str, help='처리 시작 날짜 (YYYY-MM-DD 형식)')
    parser.add_argument('--end-date', type=str, help='처리 종료 날짜 (YYYY-MM-DD 형식)')
    parser.add_argument('--balances-only', action='store_true', help='잔액 기록만 수행 (이자 계산은 하지 않음)')
    parser.add_argument('--interest-only', action='store_true', help='이자 계산만 수행 (잔액 기록은 하지 않음)')
    
    args = parser.parse_args()
    
    # 데이터베이스 연결
    DATABASE_URL = f'{os.getenv("DATABASE_TYPE")}://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_IP")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_DB")}?charset=utf8mb4'
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 날짜 변수 설정
        process_date = None
        start_date = None
        end_date = None
        
        # 입력된 날짜 파싱
        if args.date:
            try:
                process_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            except ValueError:
                logger.error("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.")
                return
        else:
            # 기본값: 어제 날짜
            process_date = datetime.now().date() - timedelta(days=1)
            
        if args.start_date and args.end_date:
            try:
                start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            except ValueError:
                logger.error("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.")
                return
        
        # 처리 분기
        if args.start_date and args.end_date:
            # 날짜 범위 처리
            if args.balances_only:
                # 잔액 기록만 처리
                current_date = start_date
                while current_date <= end_date:
                    await update_daily_balances(db, current_date)
                    current_date += timedelta(days=1)
            elif args.interest_only:
                # 이자 계산만 처리
                current_date = start_date
                while current_date <= end_date:
                    await calculate_daily_interest(db, current_date)
                    current_date += timedelta(days=1)
            else:
                # 전체 처리
                await update_balances_for_range(start_date, end_date, db)
        else:
            # 단일 날짜 처리
            if args.balances_only:
                # 잔액 기록만 처리
                await update_daily_balances(db, process_date)
            elif args.interest_only:
                # 이자 계산만 처리
                await calculate_daily_interest(db, process_date)
            else:
                # 전체 처리
                await update_daily_balances(db, process_date)
                await calculate_daily_interest(db, process_date)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())