from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

import models
from router.account.account_schema import AccountCreate, AccountUpdate, BalanceUpdate

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

def create_account(db: Session, account: AccountCreate):
    """새로운 계정 생성"""
    db_account = models.Account(
        USER_ID=account.USER_ID,
        TEAM_ID=account.TEAM_ID,
        ACCOUNT_NUM=account.ACCOUNT_NUM,
        INTEREST_RATE=account.INTEREST_RATE,
        SAVING_GOAL=account.SAVING_GOAL,
        DAILY_LIMIT=account.DAILY_LIMIT,
        MONTH_LIMIT=account.MONTH_LIMIT,
        SOURCE_ACCOUNT=account.SOURCE_ACCOUNT,
        TOTAL_AMOUNT=0,  # 초기 잔액은 0으로 설정
        created_at=datetime.now()
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

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