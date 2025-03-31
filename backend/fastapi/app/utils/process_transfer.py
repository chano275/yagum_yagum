# process_transfers.py
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
from database import engine
# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, 'transfers.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def process_actual_transfers(db, date_param=None):
    """
    특정 날짜(기본값: 오늘)의 daily_saving 내역을 기준으로 실제 적금 이체를 처리합니다.
    일일 한도와 월간 한도를 고려하여 이체 금액을 제한합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        date_param (date, optional): 처리할 날짜. 기본값은 오늘.
    
    Returns:
        dict: 처리 결과 요약 정보
    """
    # 날짜 설정 (기본값: 오늘)
    if date_param is None:
        date_param = datetime.now().date()
    
    # 월의 시작일과 끝일 계산 (월간 한도 확인용)
    month_start = date_param.replace(day=1)
    if date_param.month == 12:
        next_month = date_param.replace(year=date_param.year + 1, month=1, day=1)
    else:
        next_month = date_param.replace(month=date_param.month + 1, day=1)
    month_end = next_month - timedelta(days=1)
    
    logger.info(f"[{date_param}] daily_saving 내역 기반 실제 적금 이체 처리 시작...")
    
    # 처리 결과 요약용 변수
    total_transferred = 0
    processed_accounts = 0
    skipped_accounts = 0
    failed_accounts = 0
    
    try:
        # 1. 날짜별 계정별 daily_saving 내역 집계
        account_savings = db.query(
            models.DailySaving.ACCOUNT_ID,
            func.sum(models.DailySaving.DAILY_SAVING_AMOUNT).label("total_amount")
        ).filter(
            models.DailySaving.DATE == date_param
        ).group_by(
            models.DailySaving.ACCOUNT_ID
        ).all()
        
        logger.info(f"총 {len(account_savings)}개 계정의 적립 내역이 있습니다.")
        
        # 2. 이체 이력 테이블 확인 (실제 구현에서는 별도 테이블 생성 필요)
        # 여기서는 DailySaving 테이블에서 TRANSFER_COMPLETE 필드가 있다고 가정
        # 실제 환경에서는 테이블 생성이나 필드 추가 필요
        
        # 3. 각 계정별로 이체 처리
        for account_id, saving_amount in account_savings:
            try:
                # 계정 정보 조회
                account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
                if not account:
                    logger.warning(f"계정 ID {account_id}를 찾을 수 없습니다. 이체를 건너뜁니다.")
                    skipped_accounts += 1
                    continue
                
                # 사용자 정보 조회
                user = db.query(models.User).filter(models.User.USER_ID == account.USER_ID).first()
                if not user:
                    logger.warning(f"계정 ID {account_id}의 사용자 정보를 찾을 수 없습니다. 이체를 건너뜁니다.")
                    skipped_accounts += 1
                    continue
                
                # 3.1. 일일 한도 확인
                # 해당 날짜에 이미 이체된 금액 확인
                # 실제 구현 시 이체 이력 테이블에서 조회해야 함
                # 여기서는 간단한 구현을 위해 0으로 가정
                already_transferred_today = 0
                
                if already_transferred_today + saving_amount > account.DAILY_LIMIT:
                    # 일일 한도 초과 시 한도 내로 조정
                    original_amount = saving_amount
                    saving_amount = account.DAILY_LIMIT - already_transferred_today
                    logger.warning(f"계정 ID {account_id}: 일일 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                
                # 3.2. 월간 한도 확인
                # 해당 월에 이미 이체된 금액 확인
                # 실제 구현 시 이체 이력 테이블에서 조회해야 함
                # 여기서는 간단한 구현을 위해 0으로 가정
                already_transferred_this_month = 0
                
                if already_transferred_this_month + saving_amount > account.MONTH_LIMIT:
                    # 월간 한도 초과 시 한도 내로 조정
                    original_amount = saving_amount
                    saving_amount = account.MONTH_LIMIT - already_transferred_this_month
                    logger.warning(f"계정 ID {account_id}: 월간 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                
                # 이체할 금액이 0 이하라면 건너뜀
                if saving_amount <= 0:
                    logger.warning(f"계정 ID {account_id}: 이체 금액이 0원 이하여서 이체를 건너뜁니다.")
                    skipped_accounts += 1
                    continue
                
                # 3.3. 실제 이체 처리
                try:
                    # 금융 API를 통한 이체 처리
                    from router.user.user_ssafy_api_utils import transfer_money
                    
                    logger.info(f"계정 ID {account_id}: {saving_amount}원 이체 시작 (출금계좌: {account.SOURCE_ACCOUNT}, 입금계좌: {account.ACCOUNT_NUM})")
                    
                    transfer_result = await transfer_money(
                        user_key=user.USER_KEY,
                        withdrawal_account=account.SOURCE_ACCOUNT,  # 출금 계좌 (입출금 계좌)
                        deposit_account=account.ACCOUNT_NUM,        # 입금 계좌 (적금 계좌)
                        amount=saving_amount,
                        llm_text="" # 입출금 메시지
                    )
                    
                    # 이체 성공 시 계정 잔액 업데이트
                    account.TOTAL_AMOUNT += saving_amount
                    
                    
                    total_transferred += saving_amount
                    processed_accounts += 1
                    
                    logger.info(f"계정 ID {account_id}: {saving_amount}원 이체 성공")
                    
                except Exception as e:
                    logger.error(f"계정 ID {account_id} 이체 처리 중 오류: {str(e)}")
                    failed_accounts += 1
                    continue
                    
            except Exception as e:
                logger.error(f"계정 ID {account_id} 처리 중 오류: {str(e)}")
                failed_accounts += 1
                continue
        
        # 변경사항 커밋
        db.commit()
        
        summary = {
            "date": date_param,
            "total_transferred": total_transferred,
            "processed_accounts": processed_accounts,
            "skipped_accounts": skipped_accounts,
            "failed_accounts": failed_accounts
        }
        
        logger.info(f"[{date_param}] 이체 처리 완료: {processed_accounts}개 계정 성공, {skipped_accounts}개 건너뜀, {failed_accounts}개 실패, 총 {total_transferred}원 이체")
        return summary
        
    except Exception as e:
        db.rollback()
        logger.error(f"이체 처리 중 오류 발생: {str(e)}")
        raise

async def process_transfers_for_range(start_date=None, end_date=None, db_session=None):
    """
    지정된 날짜 범위의 daily_saving 내역에 대해 이체를 처리합니다.
    
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
        Session = sessionmaker(bind=engine)
        db_session = Session()
        close_session = True
    
    results = []
    try:
        current_date = start_date
        while current_date <= end_date:
            logger.info(f"날짜 {current_date} 처리 시작")
            result = await process_actual_transfers(db_session, current_date)
            results.append(result)
            current_date += timedelta(days=1)
            
        return results
    finally:
        if close_session:
            db_session.close()

async def main():
    parser = argparse.ArgumentParser(description='Daily Saving 내역 기반 적금 이체 처리')
    parser.add_argument('--date', type=str, help='처리할 날짜 (YYYY-MM-DD 형식, 기본값: 어제)')
    parser.add_argument('--start-date', type=str, help='처리 시작 날짜 (YYYY-MM-DD 형식)')
    parser.add_argument('--end-date', type=str, help='처리 종료 날짜 (YYYY-MM-DD 형식)')
    
    args = parser.parse_args()
    
    # 데이터베이스 연결
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        if args.date:
            # 특정 날짜 처리
            try:
                process_date = datetime.strptime(args.date, '%Y-%m-%d').date()
                await process_actual_transfers(db, process_date)
            except ValueError:
                logger.error("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.")
        elif args.start_date and args.end_date:
            # 날짜 범위 처리
            try:
                start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
                await process_transfers_for_range(start_date, end_date, db)
            except ValueError:
                logger.error("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.")
        else:
            # 기본값: 어제 날짜 처리
            yesterday = datetime.now().date() - timedelta(days=1)
            await process_actual_transfers(db, yesterday)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())