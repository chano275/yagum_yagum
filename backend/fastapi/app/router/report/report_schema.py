from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# 일일 보고서 기본 모델
class DailyReportBase(BaseModel):
    TEAM_ID: int
    DATE: date
    LLM_CONTEXT: str
    TEAM_AVG_AMOUNT: Optional[int] = None

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
    
# 배치 처리를 위한 스키마 정의
class WeeklyPersonalReportRequest(BaseModel):
    account_id: int
    date: str  # "YYYY-MM-DD" 형식으로 받음
    weekly_text: str

class BatchWeeklyPersonalReportRequest(BaseModel):
    reports: List[WeeklyPersonalReportRequest]

# 부분 성공 결과를 위한 응답 스키마
class BatchReportResult(BaseModel):
    success: List[WeeklyReportPersonalResponse]
    errors: List[Dict[str, Any]]


# 팀별 일일 송금 정보 응답 모델
class TeamDailySavingResponse(BaseModel):
    team_id: int # 팀 id
    team: str  # 우리 팀
    opponent: str  # 상대 팀
    game_record: str  # 경기 기록 (승리, 패배, 무승부)
    total_daily_saving: int  # 우리 팀 전체 송금액
    opponent_total_daily_saving: int  # 상대 팀 전체 송금액

# 여러 팀의 일일 송금 정보를 포함하는 응답 모델
class AllTeamsDailySavingResponse(BaseModel):
    date: str  # 데이터 기준 날짜
    teams_data: List[TeamDailySavingResponse]  # 팀별 데이터 목록

# 단일 일일 팀 보고서 요청 모델
class DailyTeamReportRequest(BaseModel):
    team_id: int
    date: str  # YYYY-MM-DD 형식
    llm_context: str

# 배치 일일 팀 보고서 요청 모델
class BatchDailyTeamReportRequest(BaseModel):
    reports: List[DailyTeamReportRequest]

# 에러 응답 항목 모델
class ErrorReport(BaseModel):
    index: int
    team_id: int
    detail: str
    code: str

# 배치 처리 결과 응답 모델
class DailyBatchReportResult(BaseModel):
    success: List[DailyReportResponse]
    errors: List[ErrorReport]


# report_schema.py에 추가해야 할 코드

# 팀 승패 기록 모델
class TeamRecordInfo(BaseModel):
    WIN: int
    LOSE: int
    DRAW: int

# 적금액 비교 모델
# class SavingsComparisonInfo(BaseModel):
#     previous_week: int
#     change_percentage: float

# 확장된 주간 개인 보고서 응답 모델
class WeeklyReportPersonalResponseExtended(BaseModel):
    DATE: date
    WEEKLY_AMOUNT: int
    LLM_CONTEXT: str
    TEAM_RECORD: TeamRecordInfo
    # savings_comparison: SavingsComparisonInfo
    PREVIOUS_WEEK: int
    CHANGE_PERCENTAGE: float
    DAILY_SAVINGS: Dict[str, int]  # 날짜(ISO 형식) -> 적금액 
    NEWS_SUMMATION: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class WeeklyReportPersonalResponseExtendedTest(WeeklyReportPersonalResponseExtended):
    WEEK_INFO: str
    
    class Config:
        orm_mode = True
        from_attributes = True