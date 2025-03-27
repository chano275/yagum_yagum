from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Date, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# 사용자 및 인증 테이블
class User(Base):
    __tablename__ = "user"

    USER_ID = Column(Integer, primary_key=True)
    NAME = Column(String(30))
    USER_EMAIL = Column(String(100))
    PASSWORD = Column(String(100))
    USER_KEY = Column(String(60))
    created_at = Column(DateTime, server_default=func.now())
    SOURCE_ACCOUNT = Column(String(16))
    
    # 관계 정의
    accounts = relationship("Account", back_populates="user")

# 계정 테이블
class Account(Base):
    __tablename__ = "account"

    ACCOUNT_ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey("user.USER_ID"), nullable=False)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    ACCOUNT_NUM = Column(String(16), nullable=False)
    INTEREST_RATE = Column(Float)
    SAVING_GOAL = Column(Integer)
    DAILY_LIMIT = Column(Integer)
    MONTH_LIMIT = Column(Integer)
    SOURCE_ACCOUNT = Column(String(16), nullable=False)
    TOTAL_AMOUNT = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    user = relationship("User", back_populates="accounts")
    team = relationship("Team", back_populates="accounts")
    used_missions = relationship("UsedMission", back_populates="account")
    user_saving_rules = relationship("UserSavingRule", back_populates="account")
    daily_savings = relationship("DailySaving", back_populates="account")
    ticket_numbers = relationship("TicketNumber", back_populates="account")
    daily_balances = relationship("DailyBalances", back_populates="account")
    weekly_reports = relationship("WeeklyReportPersonal", back_populates="account")

# 팀 테이블
class Team(Base):
    __tablename__ = "team"

    TEAM_ID = Column(Integer, primary_key=True)
    TEAM_NAME = Column(String(20))
    TOTAL_WIN = Column(Integer)
    TOTAL_LOSE = Column(Integer)
    TOTAL_DRAW = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    accounts = relationship("Account", back_populates="team")
    players = relationship("Player", back_populates="team")
    team_ratings = relationship("TeamRating", back_populates="team")
    daily_reports = relationship("DailyReport", back_populates="team")
    weekly_reports = relationship("WeeklyReportTeam", back_populates="team")
    news = relationship("News", back_populates="team")
    player_records = relationship("PlayerRecord", back_populates="team")
    home_games = relationship("GameSchedule", foreign_keys="GameSchedule.HOME_TEAM_ID", back_populates="home_team")
    away_games = relationship("GameSchedule", foreign_keys="GameSchedule.AWAY_TEAM_ID", back_populates="away_team")
    game_logs = relationship("GameLog", back_populates="team")

# 플레이어 테이블
class Player(Base):
    __tablename__ = "player"

    PLAYER_ID = Column(Integer, primary_key=True)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    PLAYER_NUM = Column(Integer)
    PLAYER_TYPE_ID = Column(Integer, ForeignKey("player_type.PLAYER_TYPE_ID"), nullable=False)
    PLAYER_NAME = Column(String(20))
    PLAYER_IMAGE_URL = Column(String(255))
    LIKE_COUNT = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    team = relationship("Team", back_populates="players")
    player_type = relationship("PlayerType", back_populates="players")
    weekly_reports = relationship("WeeklyReportPlayer", back_populates="player")
    daily_reports = relationship("DailyReportPlayer", back_populates="player")
    run_records = relationship("RunPlayer", back_populates="player")
    records = relationship("PlayerRecord", back_populates="player")
    user_saving_rules = relationship("UserSavingRule", back_populates="player")

# 플레이어 타입 테이블
class PlayerType(Base):
    __tablename__ = "player_type"

    PLAYER_TYPE_ID = Column(Integer, primary_key=True)
    PLAYER_TYPE_NAME = Column(String(10))
    
    # 관계 정의
    players = relationship("Player", back_populates="player_type")
    saving_rule_details = relationship("SavingRuleDetail", back_populates="player_type")
    user_saving_rules = relationship("UserSavingRule", back_populates="player_type")

# 미션 테이블
class Mission(Base):
    __tablename__ = "mission"

    MISSION_ID = Column(Integer, primary_key=True)
    MISSION_NAME = Column(String(20))
    MISSION_MAX_COUNT = Column(Integer)
    MISSION_RATE = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    used_missions = relationship("UsedMission", back_populates="mission")

# 사용된 미션 테이블
class UsedMission(Base):
    __tablename__ = "used_mission"

    USED_MISSION_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    MISSION_ID = Column(Integer, ForeignKey("mission.MISSION_ID"), nullable=False)
    COUNT = Column(Integer)
    MAX_COUNT = Column(Integer)
    MISSION_RATE = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    account = relationship("Account", back_populates="used_missions")
    mission = relationship("Mission", back_populates="used_missions")

# 적금 규칙 유형 테이블
class SavingRuleType(Base):
    __tablename__ = "saving_rule_type"

    SAVING_RULE_TYPE_ID = Column(Integer, primary_key=True)
    SAVING_RULE_TYPE_NAME = Column(String(10))
    
    # 관계 정의
    saving_rule_lists = relationship("SavingRuleList", back_populates="saving_rule_type")
    saving_rule_details = relationship("SavingRuleDetail", back_populates="saving_rule_type")
    user_saving_rules = relationship("UserSavingRule", back_populates="saving_rule_type")
    daily_savings = relationship("DailySaving", back_populates="saving_rule_type")

# 기록 유형 테이블
class RecordType(Base):
    __tablename__ = "record_type"

    RECORD_TYPE_ID = Column(Integer, primary_key=True)
    RECORD_NAME = Column(String(20))
    RECORD_COMMENT = Column(String(50))
    
    # 관계 정의
    saving_rule_lists = relationship("SavingRuleList", back_populates="record_type")
    player_records = relationship("PlayerRecord", back_populates="record_type")
    game_logs = relationship("GameLog", back_populates="record_type")

# 적금 규칙 목록 테이블
class SavingRuleList(Base):
    __tablename__ = "saving_rule_list"

    SAVING_RULE_ID = Column(Integer, primary_key=True)
    SAVING_RULE_TYPE_ID = Column(Integer, ForeignKey("saving_rule_type.SAVING_RULE_TYPE_ID"), nullable=False)
    RECORD_TYPE_ID = Column(Integer, ForeignKey("record_type.RECORD_TYPE_ID"), nullable=False)
    
    # 관계 정의
    saving_rule_type = relationship("SavingRuleType", back_populates="saving_rule_lists")
    record_type = relationship("RecordType", back_populates="saving_rule_lists")
    saving_rule_details = relationship("SavingRuleDetail", back_populates="saving_rule")

# 적금 규칙 세부 테이블
class SavingRuleDetail(Base):
    __tablename__ = "saving_rule_detail"

    SAVING_RULE_DETAIL_ID = Column(Integer, primary_key=True)
    SAVING_RULE_TYPE_ID = Column(Integer, ForeignKey("saving_rule_type.SAVING_RULE_TYPE_ID"), nullable=False)
    PLAYER_TYPE_ID = Column(Integer, ForeignKey("player_type.PLAYER_TYPE_ID"), nullable=True)
    SAVING_RULE_ID = Column(Integer, ForeignKey("saving_rule_list.SAVING_RULE_ID"), nullable=False)
    
    # 관계 정의
    saving_rule_type = relationship("SavingRuleType", back_populates="saving_rule_details")
    player_type = relationship("PlayerType", back_populates="saving_rule_details")
    saving_rule = relationship("SavingRuleList", back_populates="saving_rule_details")
    user_saving_rules = relationship("UserSavingRule", back_populates="saving_rule_detail")
    daily_savings = relationship("DailySaving", back_populates="saving_rule_detail")

# 사용자 적금 규칙 테이블
class UserSavingRule(Base):
    __tablename__ = "user_saving_rule"

    USER_SAVING_RULED_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    SAVING_RULE_TYPE_ID = Column(Integer, ForeignKey("saving_rule_type.SAVING_RULE_TYPE_ID"), nullable=False)
    SAVING_RULE_DETAIL_ID = Column(Integer, ForeignKey("saving_rule_detail.SAVING_RULE_DETAIL_ID"), nullable=False)
    PLAYER_TYPE_ID = Column(Integer, ForeignKey("player_type.PLAYER_TYPE_ID"), nullable=True)  # NULL 허용으로 변경
    USER_SAVING_RULED_AMOUNT = Column(Integer, nullable=False)
    PLAYER_ID = Column(Integer, ForeignKey("player.PLAYER_ID"), nullable=True)  # NULL 허용으로 변경
    
    # 관계 정의
    account = relationship("Account", back_populates="user_saving_rules")
    saving_rule_type = relationship("SavingRuleType", back_populates="user_saving_rules")
    saving_rule_detail = relationship("SavingRuleDetail", back_populates="user_saving_rules")
    player_type = relationship("PlayerType", back_populates="user_saving_rules")
    player = relationship("Player", back_populates="user_saving_rules")

# 일일 적금 테이블
class DailySaving(Base):
    __tablename__ = "daily_saving"

    DAILY_SAVING_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    DATE = Column(Date)
    SAVING_RULED_DETAIL_ID = Column(Integer, ForeignKey("saving_rule_detail.SAVING_RULE_DETAIL_ID"), nullable=False)
    SAVING_RULED_TYPE_ID = Column(Integer, ForeignKey("saving_rule_type.SAVING_RULE_TYPE_ID"), nullable=False)
    COUNT = Column(Integer)
    DAILY_SAVING_AMOUNT = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계 정의
    account = relationship("Account", back_populates="daily_savings")
    saving_rule_detail = relationship("SavingRuleDetail", back_populates="daily_savings")
    saving_rule_type = relationship("SavingRuleType", back_populates="daily_savings")

# 티켓 번호 테이블
class TicketNumber(Base):
    __tablename__ = "ticket_number"

    TICKET_NUMBER_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    TICKET_NUMBER = Column(String(20))
    TICKET_TYPE = Column(String(10))
    VERIFIED_STATUS = Column(Boolean)
    
    # 관계 정의
    account = relationship("Account", back_populates="ticket_numbers")

# 일일 잔액 테이블
class DailyBalances(Base):
    __tablename__ = "daily_balances"

    DAILY_BALANCES_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    DATE = Column(Date)
    CLOSING_BALANCE = Column(Integer)
    DAILY_INTEREST = Column(Integer)
    
    # 관계 정의
    account = relationship("Account", back_populates="daily_balances")

# 주간 개인 보고서 테이블
class WeeklyReportPersonal(Base):
    __tablename__ = "weekly_report_personal"

    WEEKLY_PERSONAL_ID = Column(Integer, primary_key=True)
    ACCOUNT_ID = Column(Integer, ForeignKey("account.ACCOUNT_ID"), nullable=False)
    DATE = Column(Date)
    WEEKLY_AMOUNT = Column(Integer)
    LLM_CONTEXT = Column(Text)
    
    # 관계 정의
    account = relationship("Account", back_populates="weekly_reports")

# 주간 팀 보고서 테이블
class WeeklyReportTeam(Base):
    __tablename__ = "weekly_report_team"

    WEEKLY_TEAM_ID = Column(Integer, primary_key=True)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    DATE = Column(Date)
    NEWS_SUMMATION = Column(Text)
    TEAM_AMOUNT = Column(Integer)
    TEAM_WIN = Column(Integer)
    TEAM_DRAW = Column(Integer)
    TEAM_LOSE = Column(Integer)
    
    # 관계 정의
    team = relationship("Team", back_populates="weekly_reports")

# 팀 평가 테이블
class TeamRating(Base):
    __tablename__ = "team_rating"

    TEAM_RATING_ID = Column(Integer, primary_key=True)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    DAILY_RANKING = Column(Integer)
    DATE = Column(Date)
    
    # 관계 정의
    team = relationship("Team", back_populates="team_ratings")

# 일일 보고서 테이블
class DailyReport(Base):
    __tablename__ = "daily_report"

    DAILY_REPORT_ID = Column(Integer, primary_key=True)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    DATE = Column(Date)
    LLM_CONTEXT = Column(Text)
    TEAM_AVG_AMOUNT = Column(Integer)
    
    # 관계 정의
    team = relationship("Team", back_populates="daily_reports")

# 뉴스 테이블
class News(Base):
    __tablename__ = "news"

    NEWS_ID = Column(Integer, primary_key=True)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    NEWS_CONTENT = Column(Text)
    NEWS_TITLE = Column(String(255))
    PUBLISHED_DATE = Column(Date)
    
    # 관계 정의
    team = relationship("Team", back_populates="news")

# 주간 플레이어 보고서 테이블
class WeeklyReportPlayer(Base):
    __tablename__ = "weekly_report_player"

    WEEKLY_REPORT_PLAYER_ID = Column(Integer, primary_key=True)
    DATE = Column(Date)
    PLAYER_ID = Column(Integer, ForeignKey("player.PLAYER_ID"), nullable=False)
    LLM_CONTEXT = Column(Text)
    
    # 관계 정의
    player = relationship("Player", back_populates="weekly_reports")

# 일일 플레이어 보고서 테이블
class DailyReportPlayer(Base):
    __tablename__ = "daily_report_player"

    DAILY_REPORT_PLAYER_ID = Column(Integer, primary_key=True)
    DATE = Column(Date)
    PLAYER_ID = Column(Integer, ForeignKey("player.PLAYER_ID"), nullable=False)
    LLM_CONTEXT = Column(Text)
    
    # 관계 정의
    player = relationship("Player", back_populates="daily_reports")

# 플레이어 달리기 테이블
class RunPlayer(Base):
    __tablename__ = "run_player"

    RUN_PLAYER_ID = Column(Integer, primary_key=True)
    DATE = Column(Date)
    PLAYER_ID = Column(Integer, ForeignKey("player.PLAYER_ID"), nullable=False)
    
    # 관계 정의
    player = relationship("Player", back_populates="run_records")

# 플레이어 기록 테이블
class PlayerRecord(Base):
    __tablename__ = "player_record"

    PLAYER_RECORD_ID = Column(Integer, primary_key=True)
    DATE = Column(Date)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    PLAYER_ID = Column(Integer, ForeignKey("player.PLAYER_ID"), nullable=False)
    RECORD_TYPE_ID = Column(Integer, ForeignKey("record_type.RECORD_TYPE_ID"), nullable=False)
    COUNT = Column(Integer)
    
    # 관계 정의
    team = relationship("Team", back_populates="player_records")
    player = relationship("Player", back_populates="records")
    record_type = relationship("RecordType", back_populates="player_records")

# 게임 일정 테이블
class GameSchedule(Base):
    __tablename__ = "game_schedule"

    GAME_SCHEDULE_KEY = Column(Integer, primary_key=True)
    DATE = Column(Date)
    HOME_TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    AWAY_TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    
    # 관계 정의
    home_team = relationship("Team", foreign_keys=[HOME_TEAM_ID], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[AWAY_TEAM_ID], back_populates="away_games")

# 게임 로그 테이블
class GameLog(Base):
    __tablename__ = "game_log"

    GAME_LOG_ID = Column(Integer, primary_key=True)
    DATE = Column(Date)
    TEAM_ID = Column(Integer, ForeignKey("team.TEAM_ID"), nullable=False)
    RECORD_TYPE_ID = Column(Integer, ForeignKey("record_type.RECORD_TYPE_ID"), nullable=False)
    COUNT = Column(Integer)
    
    # 관계 정의
    team = relationship("Team", back_populates="game_logs")
    record_type = relationship("RecordType", back_populates="game_logs")