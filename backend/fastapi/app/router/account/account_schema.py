from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime,date

# 계정 기본 모델
class AccountBase(BaseModel):
    TEAM_ID: Optional[int] = None
    FAVORITE_PLAYER_ID: Optional[int] = None
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
    FAVORITE_PLAYER_ID: Optional[int] = None
    INTEREST_RATE: Optional[float] = None
    SAVING_GOAL: Optional[int] = None
    DAILY_LIMIT: Optional[int] = None
    MONTH_LIMIT: Optional[int] = None
    SOURCE_ACCOUNT: Optional[str] = None
    TOTAL_AMOUNT: Optional[int] = None

# 계정 응답 모델
class AccountResponse(AccountBase):
    ACCOUNT_ID: int
    ACCOUNT_NUM:str
    TOTAL_AMOUNT: int
    INTEREST_RATE: float
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

# 계좌번호 초기 발급 응답 모델
class InitAccountResponse(BaseModel):
    ACCOUNT_ID: int
    ACCOUNT_NUM: str

# 계좌 설정 모델
class AccountSetup(BaseModel):
    TEAM_ID: int
    SAVING_GOAL: int
    DAILY_LIMIT: int
    MONTH_LIMIT: int
    SOURCE_ACCOUNT: str

    # 적금 규칙 설정 모델
# class SavingRuleRequest(BaseModel):
#     SAVING_RULE_TYPE_ID: int  # 기본 규칙(1), 투수(2), 타자(3), 상대팀(4)
#     RECORD_TYPE_ID: int  # 승리(1), 안타(2), 홈런(3) 등
#     PLAYER_ID: Optional[int] = None  # 선수 규칙의 경우만 필요
#     USER_SAVING_RULED_AMOUNT: int  # 적립 금액

class SavingRuleRequest(BaseModel):
    SAVING_RULE_DETAIL_ID: int  # SAVING_RULE_DETAIL_ID만 받음
    SAVING_RULED_AMOUNT: int  # 적립 금액

# 적금 가입 요청 모델
class AccountCreateRequest(BaseModel):
    TEAM_ID: int  # 응원 팀
    FAVORITE_PLAYER_ID: Optional[int] = None
    SAVING_GOAL: int  # 저축 목표액
    DAILY_LIMIT: int  # 일일 적립 한도
    MONTH_LIMIT: int  # 월 적립 한도
    SOURCE_ACCOUNT: str  # 출금 계좌
    saving_rules: List[SavingRuleRequest]  # 적금 규칙 목록

# 적금 가입 응답 모델
class AccountCreateResponse(BaseModel):
    ACCOUNT_ID: int
    ACCOUNT_NUM: str
    TEAM_ID: int
    SAVING_GOAL: int
    DAILY_LIMIT: int
    MONTH_LIMIT: int
    SOURCE_ACCOUNT: str
    TOTAL_AMOUNT: int = 0
    INTEREST_RATE: float
    created_at: str
    saving_rules: List[dict]  # 등록된 적금 규칙 정보

class SavingsAccountInfo(BaseModel):
    account_id: int
    account_num: str
    total_amount: int
    interest_rate: float
    saving_goal: int
    progress_percentage: float
    team_name: Optional[str] = None
    created_at: datetime

class SourceAccountInfo(BaseModel):
    account_num: str
    total_amount: int

class UserAccountsResponse(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    source_account: SourceAccountInfo
    savings_accounts: List[SavingsAccountInfo]


# 기존 코드에 추가
class MissionDetailResponse(BaseModel):
    """미션 상세 정보 응답 모델"""
    MISSION_ID: int
    MISSION_NAME: str
    MISSION_MAX_COUNT: int
    MISSION_RATE: float
    COUNT: int
    MAX_COUNT: int

class AccountDetailResponse(AccountResponse):
    base_interest_rate: float
    mission_interest_rate: float
    total_interest_rate: float
    active_missions: List[Dict[str, Any]]

    class Config:
        orm_mode = True
        from_attributes = True

class CompletedMissionDetail(BaseModel):
    MISSION_ID: int
    MISSION_NAME: str
    MISSION_RATE: float

class MissionInterestDetail(BaseModel):
    MISSION_ID: int
    MISSION_NAME: str
    MISSION_MAX_COUNT: int
    MISSION_RATE: float
    CURRENT_COUNT: int
    ADDITIONAL_RATE: float

class AccountInterestDetailResponse(BaseModel):
    base_interest_rate: float  # 기본 이자율
    total_mission_rate: float  # 모든 미션의 비례적 이자율
    mission_details: List[MissionInterestDetail]


# 거래 메시지 기본 모델
class TransactionMessageBase(BaseModel):
    ACCOUNT_ID: int
    TRANSACTION_DATE: date
    MESSAGE: str
    AMOUNT: int

# 거래 메시지 생성 모델 (요청)
class TransactionMessageCreate(TransactionMessageBase):
    pass

# 거래 메시지 업데이트 모델 (요청)
class TransactionMessageUpdate(BaseModel):
    TRANSACTION_DATE: Optional[date] = None
    MESSAGE: Optional[str] = None
    AMOUNT: Optional[int] = None

# 거래 메시지 응답 모델
class TransactionMessageResponse(TransactionMessageBase):
    TRANSACTION_ID: int
    CREATED_AT: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 거래 메시지 요약 모델
class TransactionMessageSummary(BaseModel):
    TRANSACTION_ID: int
    TRANSACTION_DATE: date
    MESSAGE: str
    AMOUNT: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 송금 요청 모델
class TransferWithMessageRequest(BaseModel):
    amount: int
    message: Optional[str] = None