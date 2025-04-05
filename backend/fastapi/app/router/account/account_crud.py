from sqlalchemy.orm import Session
from datetime import datetime,date
from typing import Optional, List, Dict, Any
import os

import models
from router.account.account_schema import AccountCreate, AccountUpdate, BalanceUpdate,TransactionMessageCreate,TransactionMessageUpdate

def get_account_by_id(db: Session, account_id: int):
    """계정 ID로 계정 정보 조회"""
    return db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()

def get_account_by_account_num(db: Session, account_num: str):
    """계좌번호로 계정 정보 조회"""
    return db.query(models.Account).filter(models.Account.ACCOUNT_NUM == account_num).first()

def get_accounts_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """사용자 ID로 해당 사용자의 모든 계정 조회"""
    return db.query(models.Account).filter(models.Account.USER_ID == user_id).offset(skip).limit(limit).all()

def get_accounts_by_team_id(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """팀 ID로 해당 팀에 속한 모든 계정 조회"""
    return db.query(models.Account).filter(models.Account.TEAM_ID == team_id).offset(skip).limit(limit).all()

def get_all_accounts(db: Session, skip: int = 0, limit: int = 100):
    """모든 계정 조회"""
    return db.query(models.Account).offset(skip).limit(limit).all()

async def create_account(db: Session, user_id: int, team_id: Optional[int], saving_goal: int, 
                        daily_limit: int, month_limit: int, source_account: str, user_key: str):
    """새로운 계정 생성"""
    try:
        # 금융 API를 통해 계좌번호 생성
        from router.user.user_ssafy_api_utils import create_demand_deposit_account
        SAVING_CODE = os.getenv("SAVING_CODE")
        account_num = await create_demand_deposit_account(user_key,SAVING_CODE)
        
        # 기본 이자율 설정
        BASE_INTEREST_RATE = 2.5  # 시스템에서 정의한 기본 이자율
        
        # 계정 생성
        db_account = models.Account(
            USER_ID=user_id,
            TEAM_ID=team_id,
            ACCOUNT_NUM=account_num,
            INTEREST_RATE=BASE_INTEREST_RATE,
            SAVING_GOAL=saving_goal,
            DAILY_LIMIT=daily_limit,
            MONTH_LIMIT=month_limit,
            SOURCE_ACCOUNT=source_account,
            TOTAL_AMOUNT=0,
            created_at=datetime.now()
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    except Exception as e:
        db.rollback()
        raise e

def update_account(db: Session, account_id: int, account_update: AccountUpdate):
    """계정 정보 업데이트"""
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return None
    
    update_data = account_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    """계정 삭제"""
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return False
    
    db.delete(db_account)
    db.commit()
    return True

def update_account_balance(db: Session, account_id: int, balance_update: BalanceUpdate):
    """계정 잔액 업데이트 (입금 또는 출금)"""
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return None
    
    # 출금인 경우 (음수 금액) 잔액 검사
    if balance_update.amount < 0 and db_account.TOTAL_AMOUNT + balance_update.amount < 0:
        return False
    
    # 잔액 업데이트
    db_account.TOTAL_AMOUNT += balance_update.amount
    
    # 일일 거래 기록 (DailyBalances) 생성 또는 업데이트
    today = datetime.now().date()
    daily_balance = db.query(models.DailyBalances).filter(
        models.DailyBalances.ACCOUNT_ID == account_id,
        models.DailyBalances.DATE == today
    ).first()
    
    if not daily_balance:
        daily_balance = models.DailyBalances(
            ACCOUNT_ID=account_id,
            DATE=today,
            CLOSING_BALANCE=db_account.TOTAL_AMOUNT,
            DAILY_INTEREST=0
        )
        db.add(daily_balance)
    else:
        daily_balance.CLOSING_BALANCE = db_account.TOTAL_AMOUNT
    
    db.commit()
    db.refresh(db_account)
    return db_account

def get_account_daily_balances(db: Session, account_id: int, start_date=None, end_date=None):
    """계정의 일일 잔액 내역 조회"""
    query = db.query(models.DailyBalances).filter(models.DailyBalances.ACCOUNT_ID == account_id)
    
    if start_date:
        query = query.filter(models.DailyBalances.DATE >= start_date)
    if end_date:
        query = query.filter(models.DailyBalances.DATE <= end_date)
    
    return query.order_by(models.DailyBalances.DATE.desc()).all()

def get_account_savings(db: Session, account_id: int, start_date=None, end_date=None):
    """계정의 적금 내역 조회"""
    query = db.query(models.DailySaving).filter(models.DailySaving.ACCOUNT_ID == account_id)
    
    if start_date:
        query = query.filter(models.DailySaving.DATE >= start_date)
    if end_date:
        query = query.filter(models.DailySaving.DATE <= end_date)
    
    return query.order_by(models.DailySaving.DATE.desc()).all()

def get_account_saving_rules(db: Session, account_id: int):
    """계정의 적금 규칙 설정 조회"""
    return db.query(models.UserSavingRule).filter(models.UserSavingRule.ACCOUNT_ID == account_id).all()

async def transfer_to_saving_account(db: Session, account_id: int, amount: int):
    """
    입출금 계좌에서 적금 계좌로 송금
    
    Args:
        db (Session): 데이터베이스 세션
        account_id (int): 적금 계정 ID
        amount (int): 송금 금액
    
    Returns:
        dict: 송금 결과 및 계정 정보
    """
    try:
        # 계정 정보 조회
        account = get_account_by_id(db, account_id)
        if not account:
            raise Exception("계정을 찾을 수 없습니다")
        
        # 사용자 정보 조회
        user = db.query(models.User).filter(models.User.USER_ID == account.USER_ID).first()
        if not user:
            raise Exception("사용자 정보를 찾을 수 없습니다")
        
        # 금융 API를 통해 송금 처리
        from router.user.user_ssafy_api_utils import transfer_money
        
        transfer_result = await transfer_money(
            user_key=user.USER_KEY,
            withdrawal_account=account.SOURCE_ACCOUNT,  # 출금 계좌 (입출금 계좌)
            deposit_account=account.ACCOUNT_NUM,        # 입금 계좌 (적금 계좌)
            amount=amount
        )
        
        # 계정 잔액 업데이트
        balance_update = BalanceUpdate(amount=amount, description="입출금 계좌에서 적금")
        updated_account = update_account_balance(db, account_id, balance_update)
        
        return {
            "transfer_result": transfer_result,
            "account": updated_account
        }
    
    except Exception as e:
        db.rollback()
        raise e
    
# account_crud.py에 추가

def get_transaction_message_by_id(db: Session, transaction_id: int):
    """트랜잭션 메시지 ID로 조회"""
    return db.query(models.TransactionMessage).filter(models.TransactionMessage.TRANSACTION_ID == transaction_id).first()

def get_transaction_messages_by_account(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    """계정 ID로 트랜잭션 메시지 조회"""
    return db.query(models.TransactionMessage).filter(
        models.TransactionMessage.ACCOUNT_ID == account_id
    ).order_by(
        models.TransactionMessage.TRANSACTION_DATE.desc(), 
        models.TransactionMessage.CREATED_AT.desc()
    ).offset(skip).limit(limit).all()

def get_transaction_messages_by_date_range(db: Session, account_id: int, start_date: date, end_date: date):
    """계정 ID와 날짜 범위로 트랜잭션 메시지 조회"""
    return db.query(models.TransactionMessage).filter(
        models.TransactionMessage.ACCOUNT_ID == account_id,
        models.TransactionMessage.TRANSACTION_DATE >= start_date,
        models.TransactionMessage.TRANSACTION_DATE <= end_date
    ).order_by(
        models.TransactionMessage.TRANSACTION_DATE.desc(), 
        models.TransactionMessage.CREATED_AT.desc()
    ).all()

def create_transaction_message(db: Session, transaction: TransactionMessageCreate):
    """트랜잭션 메시지 생성"""
    db_transaction = models.TransactionMessage(
        ACCOUNT_ID=transaction.ACCOUNT_ID,
        TRANSACTION_DATE=transaction.TRANSACTION_DATE,
        MESSAGE=transaction.MESSAGE,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction_message(db: Session, transaction_id: int, transaction: TransactionMessageUpdate):
    """트랜잭션 메시지 업데이트"""
    db_transaction = get_transaction_message_by_id(db, transaction_id)
    if not db_transaction:
        return None
    
    update_data = transaction.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction_message(db: Session, transaction_id: int):
    """트랜잭션 메시지 삭제"""
    db_transaction = get_transaction_message_by_id(db, transaction_id)
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True

# 송금 처리 함수 확장 - 트랜잭션 메시지 저장 기능 추가
async def transfer_to_saving_account_with_message(db: Session, account_id: int, amount: int, message: str = None):
    """
    입출금 계좌에서 적금 계좌로 송금하고 메시지 저장
    
    Args:
        db (Session): 데이터베이스 세션
        account_id (int): 적금 계정 ID
        amount (int): 송금 금액
        message (str, optional): 거래 메시지. 지정하지 않으면 기본 메시지 사용
        
    Returns:
        dict: 송금 결과 및 계정 정보
    """
    try:
        # 계정 정보 조회
        account = get_account_by_id(db, account_id)
        if not account:
            raise Exception("계정을 찾을 수 없습니다")
        
        # 사용자 정보 조회
        user = db.query(models.User).filter(models.User.USER_ID == account.USER_ID).first()
        if not user:
            raise Exception("사용자 정보를 찾을 수 없습니다")
        
        # 기본 메시지 설정
        default_message = f"적금 이체: {amount}원"
        transaction_message = message if message else default_message
        
        # 금융 API를 통해 송금 처리
        from router.user.user_ssafy_api_utils import transfer_money
        
        transfer_result = await transfer_money(
            user_key=user.USER_KEY,
            withdrawal_account=account.SOURCE_ACCOUNT,  # 출금 계좌 (입출금 계좌)
            deposit_account=account.ACCOUNT_NUM,        # 입금 계좌 (적금 계좌)
            amount=amount,
            llm_text=transaction_message
        )
        
        # 계정 잔액 업데이트
        balance_update = BalanceUpdate(amount=amount, description=transaction_message)
        updated_account = update_account_balance(db, account_id, balance_update)
        
        # 트랜잭션 메시지 저장
        transaction_data = TransactionMessageCreate(
            ACCOUNT_ID=account_id,
            TRANSACTION_DATE=datetime.now().date(),
            MESSAGE=transaction_message,
            AMOUNT=amount
        )
        transaction = create_transaction_message(db, transaction_data)
        
        return {
            "transfer_result": transfer_result,
            "account": updated_account,
            "transaction": transaction
        }
    
    except Exception as e:
        db.rollback()
        raise e