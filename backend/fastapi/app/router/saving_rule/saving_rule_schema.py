from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# 적금 규칙 타입 기본 모델
class SavingRuleTypeBase(BaseModel):
    SAVING_RULE_TYPE_NAME: str

# 적금 규칙 타입 생성 모델 (요청)
class SavingRuleTypeCreate(SavingRuleTypeBase):
    pass

# 적금 규칙 타입 업데이트 모델 (요청)
class SavingRuleTypeUpdate(SavingRuleTypeBase):
    pass

# 적금 규칙 타입 응답 모델
class SavingRuleTypeResponse(SavingRuleTypeBase):
    SAVING_RULE_TYPE_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 기록 타입 응답 모델
class RecordTypeResponse(BaseModel):
    RECORD_TYPE_ID: int
    RECORD_NAME: str
    RECORD_COMMENT: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# 적금 규칙 기본 모델
class SavingRuleListBase(BaseModel):
    SAVING_RULE_TYPE_ID: int
    RECORD_TYPE_ID: int

# 적금 규칙 생성 모델 (요청)
class SavingRuleListCreate(SavingRuleListBase):
    pass

# 적금 규칙 업데이트 모델 (요청)
class SavingRuleListUpdate(BaseModel):
    SAVING_RULE_TYPE_ID: Optional[int] = None
    RECORD_TYPE_ID: Optional[int] = None

# 적금 규칙 응답 모델
class SavingRuleListResponse(SavingRuleListBase):
    SAVING_RULE_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 적금 규칙 상세 응답 모델 (규칙 타입 및 기록 타입 정보 포함)
class SavingRuleListDetailResponse(SavingRuleListResponse):
    saving_rule_type: SavingRuleTypeResponse
    record_type: RecordTypeResponse
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 타입 응답 모델
class PlayerTypeResponse(BaseModel):
    PLAYER_TYPE_ID: int
    PLAYER_TYPE_NAME: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 적금 규칙 상세 기본 모델
class SavingRuleDetailBase(BaseModel):
    SAVING_RULE_TYPE_ID: int
    PLAYER_TYPE_ID: int
    SAVING_RULE_ID: int

# 적금 규칙 상세 생성 모델 (요청)
class SavingRuleDetailCreate(SavingRuleDetailBase):
    pass

# 적금 규칙 상세 업데이트 모델 (요청)
class SavingRuleDetailUpdate(BaseModel):
    SAVING_RULE_TYPE_ID: Optional[int] = None
    PLAYER_TYPE_ID: Optional[int] = None
    SAVING_RULE_ID: Optional[int] = None

# 적금 규칙 상세 응답 모델
class SavingRuleDetailResponse(SavingRuleDetailBase):
    SAVING_RULE_DETAIL_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 적금 규칙 상세 확장 응답 모델 (규칙 타입, 선수 타입, 규칙 정보 포함)
class SavingRuleDetailExtendedResponse(SavingRuleDetailResponse):
    saving_rule_type: SavingRuleTypeResponse
    player_type: PlayerTypeResponse
    saving_rule: SavingRuleListResponse
    
    class Config:
        orm_mode = True
        from_attributes = True

# 사용자 적금 규칙 기본 모델
class UserSavingRuleBase(BaseModel):
    ACCOUNT_ID: int
    SAVING_RULE_TYPE_ID: int
    SAVING_RULE_DETAIL_ID: int
    PLAYER_TYPE_ID: Optional[int] = None  # Optional로 변경
    USER_SAVING_RULED_AMOUNT: int
    PLAYER_ID: Optional[int] = None  # Optional로 변경

# 사용자 적금 규칙 생성 모델 (요청)
class UserSavingRuleCreate(UserSavingRuleBase):
    pass

# 사용자 적금 규칙 업데이트 모델 (요청)
class UserSavingRuleUpdate(BaseModel):
    SAVING_RULE_TYPE_ID: Optional[int] = None
    SAVING_RULE_DETAIL_ID: Optional[int] = None
    PLAYER_TYPE_ID: Optional[int] = None
    USER_SAVING_RULED_AMOUNT: Optional[int] = None
    PLAYER_ID: Optional[int] = None

# 사용자 적금 규칙 응답 모델
class UserSavingRuleResponse(UserSavingRuleBase):
    USER_SAVING_RULED_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 기본 정보 모델 (간단한 정보만 포함)
class PlayerBasicInfo(BaseModel):
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_NUM: Optional[int] = None
    PLAYER_IMAGE_URL: Optional[str] = None

# 사용자 적금 규칙 상세 응답 모델 (모든 관련 정보 포함)
class UserSavingRuleDetailResponse(UserSavingRuleResponse):
    account_num: Optional[str] = None
    saving_rule_type_name: Optional[str] = None
    player_type_name: Optional[str] = None
    player_name: Optional[str] = None
    record_name: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# 일일 적금 기본 모델
class DailySavingBase(BaseModel):
    ACCOUNT_ID: int
    DATE: date
    SAVING_RULED_DETAIL_ID: int
    SAVING_RULED_TYPE_ID: int
    COUNT: int
    DAILY_SAVING_AMOUNT: int

# 일일 적금 생성 모델 (요청)
class DailySavingCreate(DailySavingBase):
    pass

# 일일 적금 응답 모델
class DailySavingResponse(DailySavingBase):
    DAILY_SAVING_ID: int
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# 일일 적금 상세 응답 모델 (계정, 규칙, 선수 정보 포함)
class DailySavingDetailResponse(DailySavingResponse):
    account_num: Optional[str] = None
    saving_rule_type_name: Optional[str] = None
    record_name: Optional[str] = None
    player_name: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 기록 모델 (일일 적금액 계산용)
class PlayerRecordModel(BaseModel):
    PLAYER_ID: int
    RECORD_TYPE_ID: int
    COUNT: int = Field(ge=0)
    DATE: date

# 적금 규칙 조합 응답 모델
class SavingRuleCombinationResponse(BaseModel):
    SAVING_RULE_DETAIL_ID: int
    SAVING_RULE_TYPE_ID: int
    SAVING_RULE_TYPE_NAME: str
    PLAYER_TYPE_ID: int
    PLAYER_TYPE_NAME: str
    SAVING_RULE_ID: int
    RECORD_TYPE_ID: int
    RECORD_NAME: str
    players: Optional[List[PlayerBasicInfo]] = None

# 계정 적금 요약 정보 응답 모델
class AccountSavingSummaryResponse(BaseModel):
    account_id: int
    account_num: str
    total_amount: int
    period_saving: int
    daily_avg_saving: float
    rule_type_stats: Dict[str, int]
    daily_trend: Dict[str, int]
    start_date: date
    end_date: date

# 선수별 적립 통계 응답 모델
class PlayerSavingStatsResponse(BaseModel):
    player_id: int
    player_name: Optional[str] = None
    total_saving: int
    account_count: int
    date_range: Dict[str, Any]
    daily_trend: Dict[str, int]
    account_stats: Dict[int, Dict[str, Any]]
    record_type_stats: Dict[str, int]

# 적립 한도 확인 요청 모델
class SavingLimitCheckRequest(BaseModel):
    ACCOUNT_ID: int
    AMOUNT: int

# 적립 한도 확인 응답 모델
class SavingLimitCheckResponse(BaseModel):
    account_id: int
    amount: int
    daily_limit: int
    monthly_limit: int
    is_within_daily_limit: bool
    is_within_monthly_limit: bool
    remaining_daily_limit: int
    remaining_monthly_limit: int

# 적금 규칙 필터 모델
class SavingRuleFilterParams(BaseModel):
    saving_rule_type_id: Optional[int] = None
    record_type_id: Optional[int] = None
    player_type_id: Optional[int] = None
    skip: int = 0
    limit: int = 100

# 일일 적금 필터 모델
class DailySavingFilterParams(BaseModel):
    account_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 100

    # 규칙 생성을 위한 새로운 스키마
class UserSavingRuleCreateSimplified(BaseModel):
    ACCOUNT_ID: int
    SAVING_RULE_TYPE_ID: int  # 예: 1=기본 규칙, 2=투수, 3=타자, 4=상대팀
    RECORD_TYPE_ID: int  # 예: 1=승리, 2=안타, 3=홈런 등
    PLAYER_ID: Optional[int] = None  # 선수 규칙의 경우에만 필요
    USER_SAVING_RULED_AMOUNT: int  # 적립 금액