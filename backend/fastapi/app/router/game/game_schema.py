from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# 게임 일정 기본 모델
class GameScheduleBase(BaseModel):
    DATE: date
    HOME_TEAM_ID: int
    AWAY_TEAM_ID: int

# 게임 일정 생성 모델 (요청)
class GameScheduleCreate(GameScheduleBase):
    pass

# 게임 일정 업데이트 모델 (요청)
class GameScheduleUpdate(BaseModel):
    DATE: Optional[date] = None
    HOME_TEAM_ID: Optional[int] = None
    AWAY_TEAM_ID: Optional[int] = None

# 게임 일정 응답 모델
class GameScheduleResponse(GameScheduleBase):
    GAME_SCHEDULE_KEY: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 확장된 게임 일정 응답 모델 (팀 정보 포함)
class GameScheduleDetailResponse(GameScheduleResponse):
    home_team_name: str
    away_team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 게임 로그 기본 모델
class GameLogBase(BaseModel):
    DATE: date
    TEAM_ID: int
    RECORD_TYPE_ID: int
    COUNT: int

# 게임 로그 생성 모델 (요청)
class GameLogCreate(GameLogBase):
    pass

# 게임 로그 업데이트 모델 (요청)
class GameLogUpdate(BaseModel):
    DATE: Optional[date] = None
    TEAM_ID: Optional[int] = None
    RECORD_TYPE_ID: Optional[int] = None
    COUNT: Optional[int] = None

# 게임 로그 응답 모델
class GameLogResponse(GameLogBase):
    GAME_LOG_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 확장된 게임 로그 응답 모델 (팀 및 기록 유형 정보 포함)
class GameLogDetailResponse(GameLogResponse):
    team_name: str
    record_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 게임 결과 기본 모델
class GameResultBase(BaseModel):
    DATE: date
    HOME_TEAM_ID: int
    AWAY_TEAM_ID: int
    HOME_SCORE: int
    AWAY_SCORE: int
    RESULT: str  # "HOME_WIN", "AWAY_WIN", "DRAW"

# 게임 결과 생성 모델 (요청)
class GameResultCreate(GameResultBase):
    pass

# 게임 결과 응답 모델
class GameResultResponse(GameResultBase):
    GAME_SCHEDULE_KEY: int
    home_team_name: str
    away_team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 성적 응답 모델
class TeamRecordResponse(BaseModel):
    RANK: int
    TEAM_ID: int
    TEAM_NAME: str
    TOTAL_WIN: int
    TOTAL_LOSE: int
    TOTAL_DRAW: int
    WIN_RATE: float
    
    class Config:
        orm_mode = True
        from_attributes = True

class UserTeamGameScheduleResponse(BaseModel):
    GAME_SCHEDULE_KEY: int
    DATE: date
    HOME_TEAM_ID: int
    AWAY_TEAM_ID: int
    home_team_name: str
    away_team_name: str
    is_home: bool
    
    class Config:
        orm_mode = True
        from_attributes = True

class GameResultResponse(BaseModel):
    game_date: date
    result: str  # "승리", "패배", "무승부"
    opponent_team_name: str
    score: Optional[str] = None  # 예: "3-2"
    is_home: bool  # 홈 경기 여부
    
    class Config:
        orm_mode = True
        from_attributes = True