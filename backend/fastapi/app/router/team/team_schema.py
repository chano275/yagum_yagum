from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime

# 팀 기본 모델
class TeamBase(BaseModel):
    TEAM_NAME: str
    TOTAL_WIN: int = 0
    TOTAL_LOSE: int = 0
    TOTAL_DRAW: int = 0

# 팀 생성 모델 (요청)
class TeamCreate(TeamBase):
    pass

# 팀 업데이트 모델 (요청)
class TeamUpdate(BaseModel):
    TEAM_NAME: Optional[str] = None
    TOTAL_WIN: Optional[int] = None
    TOTAL_LOSE: Optional[int] = None
    TOTAL_DRAW: Optional[int] = None

# 팀 응답 모델
class TeamResponse(TeamBase):
    TEAM_ID: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 상세 응답 모델
class TeamDetailResponse(TeamResponse):
    win_rate: float
    total_games: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 순위 기본 모델
class TeamRatingBase(BaseModel):
    TEAM_ID: int
    DAILY_RANKING: int
    DATE: date

# 팀 순위 생성 모델 (요청)
class TeamRatingCreate(TeamRatingBase):
    pass

# 팀 순위 응답 모델
class TeamRatingResponse(TeamRatingBase):
    TEAM_RATING_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 순위 상세 응답 모델
class TeamRatingDetailResponse(TeamRatingResponse):
    team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 뉴스 기본 모델
class NewsBase(BaseModel):
    TEAM_ID: int
    NEWS_TITLE: str
    NEWS_CONTENT: str
    PUBLISHED_DATE: date

# 뉴스 생성 모델 (요청)
class NewsCreate(NewsBase):
    pass

# 뉴스 업데이트 모델 (요청)
class NewsUpdate(BaseModel):
    NEWS_TITLE: Optional[str] = None
    NEWS_CONTENT: Optional[str] = None
    PUBLISHED_DATE: Optional[date] = None

# 뉴스 응답 모델
class NewsResponse(NewsBase):
    NEWS_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 뉴스 상세 응답 모델
class NewsDetailResponse(NewsResponse):
    team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 일일 보고서 기본 모델
class DailyReportBase(BaseModel):
    TEAM_ID: int
    DATE: date
    LLM_CONTEXT: str
    TEAM_AVG_AMOUNT: int

# 일일 보고서 생성 모델 (요청)
class DailyReportCreate(DailyReportBase):
    pass

# 일일 보고서 업데이트 모델 (요청)
class DailyReportUpdate(BaseModel):
    LLM_CONTEXT: Optional[str] = None
    TEAM_AVG_AMOUNT: Optional[int] = None

# 일일 보고서 응답 모델
class DailyReportResponse(DailyReportBase):
    DAILY_REPORT_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 일일 보고서 상세 응답 모델
class DailyReportDetailResponse(DailyReportResponse):
    team_name: str
    
    class Config:
        orm_mode = True
        from_attributes = True

# 주간 팀 보고서 기본 모델
class WeeklyReportBase(BaseModel):
    TEAM_ID: int
    DATE: date
    NEWS_SUMMATION: str
    TEAM_AMOUNT: int
    TEAM_WIN: int
    TEAM_DRAW: int
    TEAM_LOSE: int

# 주간 팀 보고서 생성 모델 (요청)
class WeeklyReportCreate(WeeklyReportBase):
    pass

# 주간 팀 보고서 업데이트 모델 (요청)
class WeeklyReportUpdate(BaseModel):
    NEWS_SUMMATION: Optional[str] = None
    TEAM_AMOUNT: Optional[int] = None
    TEAM_WIN: Optional[int] = None
    TEAM_DRAW: Optional[int] = None
    TEAM_LOSE: Optional[int] = None

# 주간 팀 보고서 응답 모델
class WeeklyReportResponse(WeeklyReportBase):
    WEEKLY_TEAM_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 주간 팀 보고서 상세 응답 모델
class WeeklyReportDetailResponse(WeeklyReportResponse):
    team_name: str
    win_rate: float
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 요약 정보 응답 모델
class TeamSummaryResponse(BaseModel):
    team_id: int
    team_name: str
    account_count: int
    total_amount: int
    player_count: int
    total_games: int
    win_count: int
    lose_count: int
    draw_count: int
    win_rate: float
    current_ranking: Optional[int] = None

# 팀 월간 통계 응답 모델
class TeamMonthlyStatsResponse(BaseModel):
    team_id: int
    year: int
    month: int
    win_count: int
    lose_count: int
    draw_count: int
    total_games: int
    record_stats: Dict[str, int]
    account_count: int
    total_saving: int
    avg_daily_saving: float

# 팀 선수 정보 응답 모델
class TeamPlayerBasicInfo(BaseModel):
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_NUM: int
    PLAYER_TYPE_ID: int
    player_type_name: str
    PLAYER_IMAGE_URL: Optional[str] = None

# 팀 계정 정보 응답 모델
class TeamAccountBasicInfo(BaseModel):
    ACCOUNT_ID: int
    ACCOUNT_NUM: str
    TOTAL_AMOUNT: int
    SAVING_GOAL: int
    progress_percentage: float

# 팀 게임 일정 응답 모델
class TeamGameScheduleInfo(BaseModel):
    GAME_SCHEDULE_KEY: int
    DATE: date
    HOME_TEAM_ID: int
    AWAY_TEAM_ID: int
    home_team_name: str
    away_team_name: str
    is_home: bool

# 팀 상세 정보 응답 모델 (선수, 계정, 게임 일정 포함)
class TeamFullDetailResponse(TeamDetailResponse):
    players: List[TeamPlayerBasicInfo]
    accounts: List[TeamAccountBasicInfo]
    upcoming_games: List[TeamGameScheduleInfo]
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 검색 필터 모델
class TeamFilterParams(BaseModel):
    name: Optional[str] = None
    skip: int = 0
    limit: int = 100

# 뉴스 검색 필터 모델
class NewsFilterParams(BaseModel):
    team_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 30

# 보고서 검색 필터 모델
class ReportFilterParams(BaseModel):
    team_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 10