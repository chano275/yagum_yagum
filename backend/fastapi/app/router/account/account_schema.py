from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 계정 기본 모델
class AccountBase(BaseModel):
    USER_ID: int
    TEAM_ID: Optional[int] = None
    ACCOUNT_NUM: str
    INTEREST_RATE: float
    SAVING_GOAL: int
    DAILY_LIMIT: int
    MONTH_LIMIT: int
    SOURCE_ACCOUNT: str

# 계정 생성 모델 (요청)
class AccountCreate(AccountBase):
    pass

# 계정 업데이트 모델 (요청)
class AccountUpdate(BaseModel):
    TEAM_ID: Optional[int] = None
    INTEREST_RATE: Optional[float] = None
    SAVING_GOAL: Optional[int] = None
    DAILY_LIMIT: Optional[int] = None
    MONTH_LIMIT: Optional[int] = None
    SOURCE_ACCOUNT: Optional[str] = None
    TOTAL_AMOUNT: Optional[int] = None

# 계정 응답 모델
class AccountResponse(AccountBase):
    ACCOUNT_ID: int
    TOTAL_AMOUNT: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 계정 요약 정보 응답 모델
class AccountSummary(BaseModel):
    ACCOUNT_ID: int
    ACCOUNT_NUM: str
    TEAM_ID: Optional[int] = None
    TOTAL_AMOUNT: int
    INTEREST_RATE: float
    SAVING_GOAL: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 계정 잔액 업데이트 모델
class BalanceUpdate(BaseModel):
    amount: int
    description: Optional[str] = None