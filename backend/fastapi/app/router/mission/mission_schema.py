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

# 팀 순위 예측 관련 스키마
class TeamRankPredictionCreate(BaseModel):
    TEAM_ID: int
    PREDICTED_RANK: int
    SEASON_YEAR: int = datetime.now().year  # 기본값은 현재 연도

class TeamRankPredictionResponse(BaseModel):
    PREDICTION_ID: int
    ACCOUNT_ID: int
    TEAM_ID: int
    PREDICTED_RANK: int
    SEASON_YEAR: int
    IS_CORRECT: int
    # created_at: datetime
    team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True
    
class OCRResponse(BaseModel):
    success:bool
    text:str
    confidence: Optional[float] = None
    error: Optional[str] = None