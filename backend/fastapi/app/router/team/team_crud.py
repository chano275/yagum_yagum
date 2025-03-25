from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import models
from router.team.team_schema import TeamCreate, TeamUpdate, TeamRatingCreate, NewsCreate, DailyReportCreate

def get_team_by_id(db: Session, team_id: int):
    """팀 ID로 팀 정보 조회"""
    return db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()

def get_team_by_name(db: Session, team_name: str):
    """팀 이름으로 팀 정보 조회"""
    return db.query(models.Team).filter(models.Team.TEAM_NAME == team_name).first()

def get_all_teams(db: Session, skip: int = 0, limit: int = 100):
    """모든 팀 조회"""
    return db.query(models.Team).offset(skip).limit(limit).all()

def create_team(db: Session, team: TeamCreate):
    """새로운 팀 생성"""
    db_team = models.Team(
        TEAM_NAME=team.TEAM_NAME,
        TOTAL_WIN=team.TOTAL_WIN,
        TOTAL_LOSE=team.TOTAL_LOSE,
        TOTAL_DRAW=team.TOTAL_DRAW,
        created_at=datetime.now()
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def update_team(db: Session, team_id: int, team: TeamUpdate):
    """팀 정보 업데이트"""
    db_team = get_team_by_id(db, team_id)
    if not db_team:
        return None
    
    update_data = team.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_team, key, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int):
    """팀 삭제"""
    db_team = get_team_by_id(db, team_id)
    if not db_team:
        return False
    
    # 관련 데이터 확인
    has_accounts = db.query(models.Account).filter(models.Account.TEAM_ID == team_id).count() > 0
    has_players = db.query(models.Player).filter(models.Player.TEAM_ID == team_id).count() > 0
    
    if has_accounts or has_players:
        return False  # 관련 데이터가 있으면 삭제 불가
    
    db.delete(db_team)
    db.commit()
    return True

def get_team_rating_by_id(db: Session, team_rating_id: int):
    """팀 순위 ID로 조회"""
    return db.query(models.TeamRating).filter(
        models.TeamRating.TEAM_RATING_ID == team_rating_id
    ).first()

def get_team_ratings_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """특정 팀의 순위 정보 조회"""
    return db.query(models.TeamRating).filter(
        models.TeamRating.TEAM_ID == team_id
    ).order_by(models.TeamRating.DATE.desc()).offset(skip).limit(limit).all()

def get_team_ratings_by_date(db: Session, rating_date: date):
    """특정 날짜의 모든 팀 순위 정보 조회"""
    return db.query(models.TeamRating).filter(
        models.TeamRating.DATE == rating_date
    ).order_by(models.TeamRating.DAILY_RANKING).all()

def get_team_rating(db: Session, team_id: int, rating_date: date):
    """특정 팀, 특정 날짜의 순위 정보 조회"""
    return db.query(models.TeamRating).filter(
        models.TeamRating.TEAM_ID == team_id,
        models.TeamRating.DATE == rating_date
    ).first()

def create_team_rating(db: Session, team_rating: TeamRatingCreate):
    """팀 순위 정보 생성"""
    # 같은 날짜, 같은 팀의 순위 정보가 있는지 확인
    existing_rating = get_team_rating(db, team_rating.TEAM_ID, team_rating.DATE)
    if existing_rating:
        # 이미 존재하면 업데이트
        existing_rating.DAILY_RANKING = team_rating.DAILY_RANKING
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    # 새로 생성
    db_team_rating = models.TeamRating(
        TEAM_ID=team_rating.TEAM_ID,
        DAILY_RANKING=team_rating.DAILY_RANKING,
        DATE=team_rating.DATE
    )
    db.add(db_team_rating)
    db.commit()
    db.refresh(db_team_rating)
    return db_team_rating

def delete_team_rating(db: Session, team_rating_id: int):
    """팀 순위 정보 삭제"""
    db_team_rating = get_team_rating_by_id(db, team_rating_id)
    if not db_team_rating:
        return False
    
    db.delete(db_team_rating)
    db.commit()
    return True

def get_news_by_id(db: Session, news_id: int):
    """뉴스 ID로 조회"""
    return db.query(models.News).filter(models.News.NEWS_ID == news_id).first()

def get_news_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 30):
    """특정 팀의 뉴스 조회"""
    return db.query(models.News).filter(
        models.News.TEAM_ID == team_id
    ).order_by(models.News.PUBLISHED_DATE.desc()).offset(skip).limit(limit).all()

def get_news_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100):
    """날짜 범위로 뉴스 조회"""
    return db.query(models.News).filter(
        models.News.PUBLISHED_DATE >= start_date,
        models.News.PUBLISHED_DATE <= end_date
    ).order_by(models.News.PUBLISHED_DATE.desc()).offset(skip).limit(limit).all()

def get_latest_news(db: Session, limit: int = 10):
    """최신 뉴스 조회"""
    return db.query(models.News).order_by(models.News.PUBLISHED_DATE.desc()).limit(limit).all()

def create_news(db: Session, news: NewsCreate):
    """뉴스 생성"""
    db_news = models.News(
        TEAM_ID=news.TEAM_ID,
        NEWS_CONTENT=news.NEWS_CONTENT,
        NEWS_TITLE=news.NEWS_TITLE,
        PUBLISHED_DATE=news.PUBLISHED_DATE
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

def update_news(db: Session, news_id: int, news_data: Dict):
    """뉴스 업데이트"""
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        return None
    
    for key, value in news_data.items():
        if key in ["TEAM_ID", "NEWS_TITLE", "NEWS_CONTENT", "PUBLISHED_DATE"]:
            setattr(db_news, key, value)
    
    db.commit()
    db.refresh(db_news)
    return db_news

def delete_news(db: Session, news_id: int):
    """뉴스 삭제"""
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        return False
    
    db.delete(db_news)
    db.commit()
    return True

def get_daily_report_by_id(db: Session, daily_report_id: int):
    """일일 보고서 ID로 조회"""
    return db.query(models.DailyReport).filter(
        models.DailyReport.DAILY_REPORT_ID == daily_report_id
    ).first()

def get_daily_reports_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 30):
    """특정 팀의 일일 보고서 조회"""
    return db.query(models.DailyReport).filter(
        models.DailyReport.TEAM_ID == team_id
    ).order_by(models.DailyReport.DATE.desc()).offset(skip).limit(limit).all()

def get_daily_report_by_team_and_date(db: Session, team_id: int, report_date: date):
    """특정 팀, 특정 날짜의 일일 보고서 조회"""
    return db.query(models.DailyReport).filter(
        models.DailyReport.TEAM_ID == team_id,
        models.DailyReport.DATE == report_date
    ).first()

def create_daily_report(db: Session, daily_report: DailyReportCreate):
    """일일 보고서 생성"""
    # 같은 날짜, 같은 팀의 보고서가 있는지 확인
    existing_report = get_daily_report_by_team_and_date(db, daily_report.TEAM_ID, daily_report.DATE)
    if existing_report:
        # 이미 존재하면 업데이트
        existing_report.LLM_CONTEXT = daily_report.LLM_CONTEXT
        existing_report.TEAM_AVG_AMOUNT = daily_report.TEAM_AVG_AMOUNT
        db.commit()
        db.refresh(existing_report)
        return existing_report
    
    # 새로 생성
    db_daily_report = models.DailyReport(
        TEAM_ID=daily_report.TEAM_ID,
        DATE=daily_report.DATE,
        LLM_CONTEXT=daily_report.LLM_CONTEXT,
        TEAM_AVG_AMOUNT=daily_report.TEAM_AVG_AMOUNT
    )
    db.add(db_daily_report)
    db.commit()
    db.refresh(db_daily_report)
    return db_daily_report

def update_daily_report(db: Session, daily_report_id: int, report_data: Dict):
    """일일 보고서 업데이트"""
    db_daily_report = get_daily_report_by_id(db, daily_report_id)
    if not db_daily_report:
        return None
    
    for key, value in report_data.items():
        if key in ["TEAM_ID", "DATE", "LLM_CONTEXT", "TEAM_AVG_AMOUNT"]:
            setattr(db_daily_report, key, value)
    
    db.commit()
    db.refresh(db_daily_report)
    return db_daily_report

def delete_daily_report(db: Session, daily_report_id: int):
    """일일 보고서 삭제"""
    db_daily_report = get_daily_report_by_id(db, daily_report_id)
    if not db_daily_report:
        return False
    
    db.delete(db_daily_report)
    db.commit()
    return True

def get_weekly_report_by_id(db: Session, weekly_report_id: int):
    """주간 팀 보고서 ID로 조회"""
    return db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.WEEKLY_TEAM_ID == weekly_report_id
    ).first()

def get_weekly_reports_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 10):
    """특정 팀의 주간 보고서 조회"""
    return db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.TEAM_ID == team_id
    ).order_by(models.WeeklyReportTeam.DATE.desc()).offset(skip).limit(limit).all()

def get_weekly_report_by_team_and_date(db: Session, team_id: int, report_date: date):
    """특정 팀, 특정 날짜의 주간 보고서 조회"""
    return db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.TEAM_ID == team_id,
        models.WeeklyReportTeam.DATE == report_date
    ).first()

def create_weekly_report(db: Session, weekly_report_data: Dict):
    """주간 팀 보고서 생성"""
    # 같은 날짜, 같은 팀의 보고서가 있는지 확인
    existing_report = get_weekly_report_by_team_and_date(db, weekly_report_data["TEAM_ID"], weekly_report_data["DATE"])
    if existing_report:
        # 이미 존재하면 업데이트
        for key, value in weekly_report_data.items():
            if key in ["TEAM_ID", "DATE", "NEWS_SUMMATION", "TEAM_AMOUNT", "TEAM_WIN", "TEAM_DRAW", "TEAM_LOSE"]:
                setattr(existing_report, key, value)
        db.commit()
        db.refresh(existing_report)
        return existing_report
    
    # 새로 생성
    db_weekly_report = models.WeeklyReportTeam(**weekly_report_data)
    db.add(db_weekly_report)
    db.commit()
    db.refresh(db_weekly_report)
    return db_weekly_report

def update_weekly_report(db: Session, weekly_report_id: int, report_data: Dict):
    """주간 팀 보고서 업데이트"""
    db_weekly_report = get_weekly_report_by_id(db, weekly_report_id)
    if not db_weekly_report:
        return None
    
    for key, value in report_data.items():
        if key in ["TEAM_ID", "DATE", "NEWS_SUMMATION", "TEAM_AMOUNT", "TEAM_WIN", "TEAM_DRAW", "TEAM_LOSE"]:
            setattr(db_weekly_report, key, value)
    
    db.commit()
    db.refresh(db_weekly_report)
    return db_weekly_report

def delete_weekly_report(db: Session, weekly_report_id: int):
    """주간 팀 보고서 삭제"""
    db_weekly_report = get_weekly_report_by_id(db, weekly_report_id)
    if not db_weekly_report:
        return False
    
    db.delete(db_weekly_report)
    db.commit()
    return True

def get_team_accounts(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """팀의 모든 계정 조회"""
    return db.query(models.Account).filter(
        models.Account.TEAM_ID == team_id
    ).offset(skip).limit(limit).all()

def get_team_players(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """팀의 모든 선수 조회"""
    return db.query(models.Player).filter(
        models.Player.TEAM_ID == team_id
    ).offset(skip).limit(limit).all()

def get_team_games(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """팀의 모든 경기 일정 조회"""
    return db.query(models.GameSchedule).filter(
        or_(
            models.GameSchedule.HOME_TEAM_ID == team_id,
            models.GameSchedule.AWAY_TEAM_ID == team_id
        )
    ).order_by(models.GameSchedule.DATE.desc()).offset(skip).limit(limit).all()

def get_team_player_records(db: Session, team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """팀 선수들의 기록 조회"""
    query = db.query(models.PlayerRecord).filter(models.PlayerRecord.TEAM_ID == team_id)
    
    if start_date:
        query = query.filter(models.PlayerRecord.DATE >= start_date)
    if end_date:
        query = query.filter(models.PlayerRecord.DATE <= end_date)
    
    return query.order_by(models.PlayerRecord.DATE.desc()).all()

def get_team_summary(db: Session, team_id: int):
    """팀 요약 정보"""
    team = get_team_by_id(db, team_id)
    if not team:
        return None
    
    # 계정 수 및 총 적금액
    accounts = get_team_accounts(db, team_id)
    account_count = len(accounts)
    total_amount = sum(account.TOTAL_AMOUNT for account in accounts)
    
    # 선수 수
    players = get_team_players(db, team_id)
    player_count = len(players)
    
    # 승률 계산
    total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
    win_rate = (team.TOTAL_WIN / total_games * 100) if total_games > 0 else 0
    
    # 최근 순위
    today = datetime.now().date()
    recent_rating = db.query(models.TeamRating).filter(
        models.TeamRating.TEAM_ID == team_id,
        models.TeamRating.DATE <= today
    ).order_by(models.TeamRating.DATE.desc()).first()
    
    current_ranking = recent_rating.DAILY_RANKING if recent_rating else None
    
    # 결과 구성
    result = {
        "team_id": team_id,
        "team_name": team.TEAM_NAME,
        "account_count": account_count,
        "total_amount": total_amount,
        "player_count": player_count,
        "total_games": total_games,
        "win_count": team.TOTAL_WIN,
        "lose_count": team.TOTAL_LOSE,
        "draw_count": team.TOTAL_DRAW,
        "win_rate": round(win_rate, 2),
        "current_ranking": current_ranking
    }
    
    return result

def get_team_monthly_stats(db: Session, team_id: int, year: int, month: int):
    """팀의 월간 통계"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # 해당 월의 경기 결과
    team_games = db.query(models.GameSchedule).filter(
        or_(
            models.GameSchedule.HOME_TEAM_ID == team_id,
            models.GameSchedule.AWAY_TEAM_ID == team_id
        ),
        models.GameSchedule.DATE >= start_date,
        models.GameSchedule.DATE <= end_date
    ).all()
    
    win_count = 0
    lose_count = 0
    draw_count = 0
    
    # 경기 결과 계산은 실제 구현에 따라 달라질 수 있음
    # 여기서는 간단한 로직만 제시
    
    # 선수 기록
    player_records = get_team_player_records(db, team_id, start_date, end_date)
    
    # 기록 유형별 집계
    record_stats = {}
    for record in player_records:
        record_type = db.query(models.RecordType).filter(
            models.RecordType.RECORD_TYPE_ID == record.RECORD_TYPE_ID
        ).first()
        
        if record_type:
            record_name = record_type.RECORD_NAME
            if record_name not in record_stats:
                record_stats[record_name] = 0
            record_stats[record_name] += record.COUNT
    
    # 계정 적금 통계
    accounts = get_team_accounts(db, team_id)
    account_count = len(accounts)
    
    month_savings = []
    for account in accounts:
        account_savings = db.query(models.DailySaving).filter(
            models.DailySaving.ACCOUNT_ID == account.ACCOUNT_ID,
            models.DailySaving.DATE >= start_date,
            models.DailySaving.DATE <= end_date
        ).all()
        
        month_savings.extend(account_savings)
    
    total_saving = sum(saving.DAILY_SAVING_AMOUNT for saving in month_savings)
    avg_daily_saving = total_saving / (end_date - start_date).days if (end_date - start_date).days > 0 else 0
    
    # 결과 구성
    result = {
        "team_id": team_id,
        "year": year,
        "month": month,
        "win_count": win_count,
        "lose_count": lose_count,
        "draw_count": draw_count,
        "total_games": win_count + lose_count + draw_count,
        "record_stats": record_stats,
        "account_count": account_count,
        "total_saving": total_saving,
        "avg_daily_saving": avg_daily_saving
    }
    
    return result