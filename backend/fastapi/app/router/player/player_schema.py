from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# 선수 기본 모델
class PlayerBase(BaseModel):
    TEAM_ID: int
    PLAYER_NUM: int
    PLAYER_TYPE_ID: int
    PLAYER_NAME: str
    PLAYER_IMAGE_URL: Optional[str] = None

# 선수 생성 모델 (요청)
class PlayerCreate(PlayerBase):
    pass

# 선수 업데이트 모델 (요청)
class PlayerUpdate(BaseModel):
    TEAM_ID: Optional[int] = None
    PLAYER_NUM: Optional[int] = None
    PLAYER_TYPE_ID: Optional[int] = None
    PLAYER_NAME: Optional[str] = None
    PLAYER_IMAGE_URL: Optional[str] = None

# 선수 응답 모델
class PlayerResponse(PlayerBase):
    PLAYER_ID: int
    LIKE_COUNT: int
    created_at: datetime
    
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

# 선수 상세 응답 모델 (포지션 정보 포함)
class PlayerDetailResponse(PlayerResponse):
    player_type: PlayerTypeResponse
    team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 기록 기본 모델
class PlayerRecordBase(BaseModel):
    DATE: date
    PLAYER_ID: int
    TEAM_ID: int
    RECORD_TYPE_ID: int
    COUNT: int

# 선수 기록 생성 모델 (요청)
class PlayerRecordCreate(PlayerRecordBase):
    pass

# 선수 기록 응답 모델
class PlayerRecordResponse(PlayerRecordBase):
    PLAYER_RECORD_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 기록 상세 응답 모델 (선수, 팀, 기록 유형 정보 포함)
class PlayerRecordDetailResponse(PlayerRecordResponse):
    player_name: str
    team_name: str
    record_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 통계 응답 모델
class PlayerStatsResponse(BaseModel):
    player: PlayerResponse
    stats: dict

# 선수 보고서 기본 모델
class PlayerReportBase(BaseModel):
    DATE: date
    PLAYER_ID: int
    LLM_CONTEXT: str

# 선수 일일 보고서 생성 모델 (요청)
class DailyReportCreate(PlayerReportBase):
    pass

# 선수 주간 보고서 생성 모델 (요청)
class WeeklyReportCreate(PlayerReportBase):
    pass

# 선수 일일 보고서 응답 모델
class DailyReportResponse(PlayerReportBase):
    DAILY_REPORT_PLAYER_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 주간 보고서 응답 모델
class WeeklyReportResponse(PlayerReportBase):
    WEEKLY_REPORT_PLAYER_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 상위 선수 응답 모델
class TopPlayerResponse(BaseModel):
    player: PlayerResponse
    total: int
    record_name: str

# 선수 출전 기록 응답 모델
class PlayerRunResponse(BaseModel):
    RUN_PLAYER_ID: int
    DATE: date
    PLAYER_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 선수 좋아요 응답 모델
class PlayerLikeResponse(BaseModel):
    PLAYER_ID: int
    PLAYER_NAME: str
    LIKE_COUNT: int