from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 미션 기본 모델
class MissionBase(BaseModel):
    MISSION_NAME: str
    MISSION_MAX_COUNT: int
    MISSION_RATE: float

# 미션 생성 모델 (요청)
class MissionCreate(MissionBase):
    pass

# 미션 업데이트 모델 (요청)
class MissionUpdate(BaseModel):
    MISSION_NAME: Optional[str] = None
    MISSION_MAX_COUNT: Optional[int] = None
    MISSION_RATE: Optional[float] = None

# 미션 응답 모델
class MissionResponse(MissionBase):
    MISSION_ID: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 사용된 미션 기본 모델
class UsedMissionBase(BaseModel):
    ACCOUNT_ID: int
    MISSION_ID: int
    COUNT: Optional[int] = 0

# 사용된 미션 생성 모델 (요청)
class UsedMissionCreate(UsedMissionBase):
    pass

# 사용된 미션 업데이트 모델 (요청)
class UsedMissionUpdate(BaseModel):
    COUNT: Optional[int] = None
    MAX_COUNT: Optional[int] = None
    MISSION_RATE: Optional[float] = None

# 사용된 미션 응답 모델
class UsedMissionResponse(BaseModel):
    USED_MISSION_ID: int
    ACCOUNT_ID: int
    MISSION_ID: int
    COUNT: int
    MAX_COUNT: int
    MISSION_RATE: float
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 미션 상세 응답 모델 (미션 정보 포함)
class UsedMissionDetailResponse(UsedMissionResponse):
    mission: MissionResponse
    
    class Config:
        orm_mode = True
        from_attributes = True

# 미션 요약 정보 응답 모델
class MissionSummaryResponse(BaseModel):
    total_missions: int
    completed_missions: int
    completion_rate: float
    total_rate: float

# 미션 상태 업데이트 요청 모델
class MissionStatusUpdate(BaseModel):
    MISSION_ID: int
    increment: bool = True  # True: 증가, False: 감소

# 일회성 미션 완료 요청 모델
class CompleteMissionRequest(BaseModel):
    MISSION_ID: int
    ACCOUNT_ID: int

# 이자율 응답 모델
class InterestRateResponse(BaseModel):
    ACCOUNT_ID: int
    BASE_INTEREST_RATE: float
    MISSION_INTEREST_RATE: float
    TOTAL_INTEREST_RATE: float