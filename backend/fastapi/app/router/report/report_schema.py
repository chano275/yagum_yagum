from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# 일일 보고서 기본 모델
class DailyReportBase(BaseModel):
    TEAM_ID: int
    DATE: date
    LLM_CONTEXT: str
    TEAM_AVG_AMOUNT: int

# 일일 보고서 생성 모델 (요청)
class DailyReportCreate(DailyReportBase):
    pass

# 일일 보고서 응답 모델
class DailyReportResponse(DailyReportBase):
    DAILY_REPORT_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 주간 팀 보고서 기본 모델
class WeeklyReportTeamBase(BaseModel):
    TEAM_ID: int
    DATE: date
    NEWS_SUMMATION: str
    TEAM_AMOUNT: int
    TEAM_WIN: int
    TEAM_DRAW: int
    TEAM_LOSE: int

# 주간 팀 보고서 생성 모델 (요청)
class WeeklyReportTeamCreate(WeeklyReportTeamBase):
    pass

# 주간 팀 보고서 응답 모델
class WeeklyReportTeamResponse(WeeklyReportTeamBase):
    WEEKLY_TEAM_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 주간 개인 보고서 기본 모델
class WeeklyReportPersonalBase(BaseModel):
    ACCOUNT_ID: int
    DATE: date
    WEEKLY_AMOUNT: int
    LLM_CONTEXT: str

# 주간 개인 보고서 생성 모델 (요청)
class WeeklyReportPersonalCreate(WeeklyReportPersonalBase):
    pass

# 주간 개인 보고서 응답 모델
class WeeklyReportPersonalResponse(WeeklyReportPersonalBase):
    WEEKLY_PERSONAL_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 뉴스 기본 모델
class NewsBase(BaseModel):
    TEAM_ID: int
    NEWS_CONTENT: str
    NEWS_TITLE: str
    PUBLISHED_DATE: date

# 뉴스 생성 모델 (요청)
class NewsCreate(NewsBase):
    pass

# 뉴스 응답 모델
class NewsResponse(NewsBase):
    NEWS_ID: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 팀 순위 응답 모델
class TeamRankingResponse(BaseModel):
    ranking: int
    team_id: int
    team_name: str
    win: int
    lose: int
    draw: int
    date: date

# 계정 보고서 요약 응답 모델
class AccountReportSummaryResponse(BaseModel):
    account_id: int
    account_num: str
    total_amount: int
    saving_goal: int
    progress_percentage: float
    team_name: Optional[str] = None
    recent_reports_count: int
    recent_total_weekly_amount: int
    average_weekly_amount: float

# 팀 보고서 요약 응답 모델
class TeamReportSummaryResponse(BaseModel):
    team_id: int
    team_name: str
    account_count: int
    total_amount: int
    win_count: int
    lose_count: int
    draw_count: int
    win_rate: float
    recent_reports_count: int
    recent_total_team_amount: int
    average_weekly_team_amount: float

# 일일 잔액 응답 모델
class DailyBalancesResponse(BaseModel):
    DAILY_BALANCES_ID: int
    ACCOUNT_ID: int
    DATE: date
    CLOSING_BALANCE: int
    DAILY_INTEREST: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# 이자 통계 응답 모델
class InterestStatsResponse(BaseModel):
    total_interest: int
    avg_daily_interest: float
    max_daily_interest: int
    min_daily_interest: int
    days_count: int

# 보고서 조회 필터 모델
class ReportFilterParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 10

# 뉴스 검색 필터 모델
class NewsFilterParams(BaseModel):
    team_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = 0
    limit: int = 30

# 팀 순위 검색 필터 모델
class RankingFilterParams(BaseModel):
    ranking_date: Optional[date] = None

class NewsItem(BaseModel):
    team: str
    news_summation: str

class NewsHeader(BaseModel):
    date: Optional[str] = None

class NewsSummaryRequest(BaseModel):
    header: NewsHeader
    body: List[NewsItem]

class NewsSummaryResultItem(BaseModel):
    team: str
    team_id: Optional[int] = None
    status: str
    message: str

class NewsSummaryResponse(BaseModel):
    status: str
    message: str
    date: str
    results: List[NewsSummaryResultItem]

class WeeklyRecord(BaseModel):
    win: int
    lose: int
    draw: int

class AccountWeeklyReport(BaseModel):
    account_id: int
    user_name: str
    team_name: str
    weekly_saving: int
    before_weekly_saving: int
    weekly_record: WeeklyRecord
    before_weekly_record: WeeklyRecord
    current_savings: int
    target_amount: int

class WeeklyReportDataResponse(BaseModel):
    accounts_data: List[AccountWeeklyReport]
    total_accounts: int
    report_date: str