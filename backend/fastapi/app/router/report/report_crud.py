from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import models
from router.report.report_schema import (
    DailyReportCreate, WeeklyReportTeamCreate, 
    WeeklyReportPersonalCreate, NewsCreate
)

def get_daily_report_by_id(db: Session, daily_report_id: int):
    """일일 보고서 ID로 조회"""
    return db.query(models.DailyReport).filter(models.DailyReport.DAILY_REPORT_ID == daily_report_id).first()

# def get_daily_reports_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 30):
#     """팀 ID로 일일 보고서 조회"""
#     return db.query(models.DailyReport).filter(
#         models.DailyReport.TEAM_ID == team_id
#     ).order_by(
#         models.DailyReport.DATE.desc()
#     ).offset(skip).limit(limit).all()

def get_daily_reports_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 30):
    """팀 ID로 일일 보고서 조회"""
    return db.query(models.DailyReport).filter(
        models.DailyReport.TEAM_ID == team_id
    ).order_by(
        models.DailyReport.DATE.desc()
    ).offset(skip).limit(limit).first()

def get_daily_report_by_team_and_date(db: Session, team_id: int, report_date: date):
    """팀 ID와 날짜로 일일 보고서 조회"""
    return db.query(models.DailyReport).filter(
        models.DailyReport.TEAM_ID == team_id,
        models.DailyReport.DATE == report_date
    ).first()

def create_daily_report(db: Session, report: DailyReportCreate):
    """일일 보고서 생성"""
    # 같은 날짜, 같은 팀의 보고서가 있는지 확인
    existing_report = get_daily_report_by_team_and_date(db, report.TEAM_ID, report.DATE)
    
    if existing_report:
        # 이미 존재하면 내용 업데이트
        existing_report.LLM_CONTEXT = report.LLM_CONTEXT
        existing_report.TEAM_AVG_AMOUNT = report.TEAM_AVG_AMOUNT
        db.commit()
        db.refresh(existing_report)
        return existing_report
    
    # 새로 생성
    db_report = models.DailyReport(
        TEAM_ID=report.TEAM_ID,
        DATE=report.DATE,
        LLM_CONTEXT=report.LLM_CONTEXT,
        TEAM_AVG_AMOUNT=report.TEAM_AVG_AMOUNT
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def delete_daily_report(db: Session, daily_report_id: int):
    """일일 보고서 삭제"""
    db_report = get_daily_report_by_id(db, daily_report_id)
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True

def get_weekly_team_report_by_id(db: Session, weekly_team_id: int):
    """주간 팀 보고서 ID로 조회"""
    return db.query(models.WeeklyReportTeam).filter(models.WeeklyReportTeam.WEEKLY_TEAM_ID == weekly_team_id).first()

def get_weekly_team_reports_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 10):
    """팀 ID로 주간 팀 보고서 조회"""
    return db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.TEAM_ID == team_id
    ).order_by(
        models.WeeklyReportTeam.DATE.desc()
    ).offset(skip).limit(limit).all()

def get_weekly_team_report_by_team_and_date(db: Session, team_id: int, report_date: date):
    """팀 ID와 날짜로 주간 팀 보고서 조회"""
    return db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.TEAM_ID == team_id,
        models.WeeklyReportTeam.DATE == report_date
    ).first()

def create_weekly_team_report(db: Session, report: WeeklyReportTeamCreate):
    """주간 팀 보고서 생성"""
    # 같은 날짜, 같은 팀의 보고서가 있는지 확인
    existing_report = get_weekly_team_report_by_team_and_date(db, report.TEAM_ID, report.DATE)
    
    if existing_report:
        # 이미 존재하면 내용 업데이트
        for key, value in report.dict().items():
            setattr(existing_report, key, value)
        db.commit()
        db.refresh(existing_report)
        return existing_report
    
    # 새로 생성
    db_report = models.WeeklyReportTeam(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def delete_weekly_team_report(db: Session, weekly_team_id: int):
    """주간 팀 보고서 삭제"""
    db_report = get_weekly_team_report_by_id(db, weekly_team_id)
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True

def get_weekly_personal_report_by_id(db: Session, weekly_personal_id: int):
    """주간 개인 보고서 ID로 조회"""
    return db.query(models.WeeklyReportPersonal).filter(models.WeeklyReportPersonal.WEEKLY_PERSONAL_ID == weekly_personal_id).first()

def get_weekly_personal_reports_by_account(db: Session, account_id: int, skip: int = 0, limit: int = 10):
    """계정 ID로 주간 개인 보고서 조회"""
    return db.query(models.WeeklyReportPersonal).filter(
        models.WeeklyReportPersonal.ACCOUNT_ID == account_id
    ).order_by(
        models.WeeklyReportPersonal.DATE.desc()
    ).offset(skip).limit(limit).all()

def get_weekly_personal_report_by_account_and_date(db: Session, account_id: int, report_date: date):
    """계정 ID와 날짜로 주간 개인 보고서 조회"""
    return db.query(models.WeeklyReportPersonal).filter(
        models.WeeklyReportPersonal.ACCOUNT_ID == account_id,
        models.WeeklyReportPersonal.DATE == report_date
    ).first()

def create_weekly_personal_report(db: Session, report: WeeklyReportPersonalCreate):
    """주간 개인 보고서 생성"""
    # 같은 날짜, 같은 계정의 보고서가 있는지 확인
    existing_report = get_weekly_personal_report_by_account_and_date(db, report.ACCOUNT_ID, report.DATE)
    
    if existing_report:
        # 이미 존재하면 내용 업데이트
        existing_report.LLM_CONTEXT = report.LLM_CONTEXT
        existing_report.WEEKLY_AMOUNT = report.WEEKLY_AMOUNT
        db.commit()
        db.refresh(existing_report)
        return existing_report
    
    # 새로 생성
    db_report = models.WeeklyReportPersonal(
        ACCOUNT_ID=report.ACCOUNT_ID,
        DATE=report.DATE,
        WEEKLY_AMOUNT=report.WEEKLY_AMOUNT,
        LLM_CONTEXT=report.LLM_CONTEXT
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def delete_weekly_personal_report(db: Session, weekly_personal_id: int):
    """주간 개인 보고서 삭제"""
    db_report = get_weekly_personal_report_by_id(db, weekly_personal_id)
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True

def get_news_by_id(db: Session, news_id: int):
    """뉴스 ID로 조회"""
    return db.query(models.News).filter(models.News.NEWS_ID == news_id).first()

def get_news_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 30):
    """팀 ID로 뉴스 조회"""
    return db.query(models.News).filter(
        models.News.TEAM_ID == team_id
    ).order_by(
        models.News.PUBLISHED_DATE.desc()
    ).offset(skip).limit(limit).all()

def get_news_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100):
    """날짜 범위로 뉴스 조회"""
    return db.query(models.News).filter(
        models.News.PUBLISHED_DATE >= start_date,
        models.News.PUBLISHED_DATE <= end_date
    ).order_by(
        models.News.PUBLISHED_DATE.desc()
    ).offset(skip).limit(limit).all()

def get_latest_news(db: Session, limit: int = 10):
    """최신 뉴스 조회"""
    return db.query(models.News).order_by(
        models.News.PUBLISHED_DATE.desc()
    ).limit(limit).all()

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

def delete_news(db: Session, news_id: int):
    """뉴스 삭제"""
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        return False
    
    db.delete(db_news)
    db.commit()
    return True

def get_team_ranking(db: Session, ranking_date: date = None):
    """팀 순위 조회"""
    if ranking_date is None:
        ranking_date = datetime.now().date()
    
    # 특정 날짜의 팀 순위
    team_ratings = db.query(models.TeamRating).filter(
        models.TeamRating.DATE == ranking_date
    ).order_by(
        models.TeamRating.DAILY_RANKING
    ).all()
    
    # 순위 정보가 없으면 팀 정보만 반환
    if not team_ratings:
        teams = db.query(models.Team).all()
        result = []
        
        for idx, team in enumerate(teams):
            result.append({
                "ranking": idx + 1,
                "team_id": team.TEAM_ID,
                "team_name": team.TEAM_NAME,
                "win": team.TOTAL_WIN,
                "lose": team.TOTAL_LOSE,
                "draw": team.TOTAL_DRAW,
                "date": ranking_date
            })
            
        return result
    
    # 순위 정보가 있으면 상세 정보 추가
    result = []
    for rating in team_ratings:
        team = db.query(models.Team).filter(models.Team.TEAM_ID == rating.TEAM_ID).first()
        if team:
            result.append({
                "ranking": rating.DAILY_RANKING,
                "team_id": team.TEAM_ID,
                "team_name": team.TEAM_NAME,
                "win": team.TOTAL_WIN,
                "lose": team.TOTAL_LOSE,
                "draw": team.TOTAL_DRAW,
                "date": rating.DATE
            })
    
    return result

def get_account_report_summary(db: Session, account_id: int):
    """계정의 보고서 요약 정보"""
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return None
    
    # 최근 4주간 주간 보고서 조회
    four_weeks_ago = datetime.now().date() - timedelta(days=28)
    weekly_reports = db.query(models.WeeklyReportPersonal).filter(
        models.WeeklyReportPersonal.ACCOUNT_ID == account_id,
        models.WeeklyReportPersonal.DATE >= four_weeks_ago
    ).order_by(
        models.WeeklyReportPersonal.DATE.desc()
    ).all()
    
    # 계정에 연결된 팀 정보
    team = None
    if account.TEAM_ID:
        team = db.query(models.Team).filter(models.Team.TEAM_ID == account.TEAM_ID).first()
    
    # 응답 데이터 구성
    total_weekly_amount = sum(report.WEEKLY_AMOUNT for report in weekly_reports)
    
    result = {
        "account_id": account_id,
        "account_num": account.ACCOUNT_NUM,
        "total_amount": account.TOTAL_AMOUNT,
        "saving_goal": account.SAVING_GOAL,
        "progress_percentage": (account.TOTAL_AMOUNT / account.SAVING_GOAL * 100) if account.SAVING_GOAL > 0 else 0,
        "team_name": team.TEAM_NAME if team else None,
        "recent_reports_count": len(weekly_reports),
        "recent_total_weekly_amount": total_weekly_amount,
        "average_weekly_amount": total_weekly_amount / len(weekly_reports) if weekly_reports else 0
    }
    
    return result

def get_team_report_summary(db: Session, team_id: int):
    """팀의 보고서 요약 정보"""
    team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
    if not team:
        return None
    
    # 최근 4주간 주간 보고서 조회
    four_weeks_ago = datetime.now().date() - timedelta(days=28)
    weekly_reports = db.query(models.WeeklyReportTeam).filter(
        models.WeeklyReportTeam.TEAM_ID == team_id,
        models.WeeklyReportTeam.DATE >= four_weeks_ago
    ).order_by(
        models.WeeklyReportTeam.DATE.desc()
    ).all()
    
    # 팀 소속 계정 수
    account_count = db.query(func.count(models.Account.ACCOUNT_ID)).filter(
        models.Account.TEAM_ID == team_id
    ).scalar()
    
    # 팀 소속 계정 총 금액
    total_amount = db.query(func.sum(models.Account.TOTAL_AMOUNT)).filter(
        models.Account.TEAM_ID == team_id
    ).scalar() or 0
    
    # 팀 승률 계산
    total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
    win_rate = (team.TOTAL_WIN / total_games * 100) if total_games > 0 else 0
    
    # 최근 4주간 총 적립 금액
    recent_total_team_amount = sum(report.TEAM_AMOUNT for report in weekly_reports)
    
    # 응답 데이터 구성
    result = {
        "team_id": team_id,
        "team_name": team.TEAM_NAME,
        "account_count": account_count,
        "total_amount": total_amount,
        "win_count": team.TOTAL_WIN,
        "lose_count": team.TOTAL_LOSE,
        "draw_count": team.TOTAL_DRAW,
        "win_rate": win_rate,
        "recent_reports_count": len(weekly_reports),
        "recent_total_team_amount": recent_total_team_amount,
        "average_weekly_team_amount": recent_total_team_amount / len(weekly_reports) if weekly_reports else 0
    }
    
    return result

def get_daily_balances_by_account(db: Session, account_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """계정의 일일 잔액 내역 조회"""
    query = db.query(models.DailyBalances).filter(models.DailyBalances.ACCOUNT_ID == account_id)
    
    if start_date:
        query = query.filter(models.DailyBalances.DATE >= start_date)
    if end_date:
        query = query.filter(models.DailyBalances.DATE <= end_date)
    
    return query.order_by(models.DailyBalances.DATE).all()

def calculate_interest_stats(db: Session, account_id: int):
    """계정의 이자 통계 계산"""
    # 일일 잔액 내역 조회
    daily_balances = get_daily_balances_by_account(db, account_id)
    
    if not daily_balances:
        return {
            "total_interest": 0,
            "avg_daily_interest": 0,
            "max_daily_interest": 0,
            "min_daily_interest": 0,
            "days_count": 0
        }
    
    total_interest = sum(balance.DAILY_INTEREST for balance in daily_balances)
    days_count = len(daily_balances)
    max_interest = max(balance.DAILY_INTEREST for balance in daily_balances)
    min_interest = min(balance.DAILY_INTEREST for balance in daily_balances)
    
    return {
        "total_interest": total_interest,
        "avg_daily_interest": total_interest / days_count if days_count > 0 else 0,
        "max_daily_interest": max_interest,
        "min_daily_interest": min_interest,
        "days_count": days_count
    }

def get_all_teams_daily_saving(db: Session, target_date: date = None):
    """
    모든 팀의 일일 송금 정보를 조회합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        target_date (date, optional): 조회할 날짜. 기본값은 어제.
    
    Returns:
        list: 팀별 일일 송금 정보 목록
    """
    # 날짜 설정 (기본값: 어제)
    if target_date is None:
        target_date = datetime.now().date() - timedelta(days=1)
    
    # 결과 저장 리스트
    teams_data = []
    
    # 1. 모든 팀 조회
    teams = db.query(models.Team).all()
    
    # 2. 각 팀에 대해 정보 수집
    for team in teams:
        # 해당 날짜의 경기 스케줄 조회 (팀이 참여한 경기)
        game = db.query(models.GameSchedule).filter(
            models.GameSchedule.DATE == target_date,
            or_(
                models.GameSchedule.HOME_TEAM_ID == team.TEAM_ID,
                models.GameSchedule.AWAY_TEAM_ID == team.TEAM_ID
            )
        ).first()
        
        # 경기가 없으면 건너뜀
        if not game:
            continue
        
        # 3. 상대팀 정보 조회
        if game.HOME_TEAM_ID == team.TEAM_ID:
            opponent_id = game.AWAY_TEAM_ID
            is_home = True
        else:
            opponent_id = game.HOME_TEAM_ID
            is_home = False
            
        opponent = db.query(models.Team).filter(models.Team.TEAM_ID == opponent_id).first()
        
        # 4. 경기 결과 조회 (승/패/무)
        game_record = "무승부"  # 기본값
        
        # 승리 기록 확인
        win_log = db.query(models.GameLog).filter(
            models.GameLog.DATE == target_date,
            models.GameLog.TEAM_ID == team.TEAM_ID,
            models.GameLog.RECORD_TYPE_ID == 1  # 승리
        ).first()
        
        if win_log:
            game_record = "승리"
        else:
            # 패배 기록 확인
            lose_log = db.query(models.GameLog).filter(
                models.GameLog.DATE == target_date,
                models.GameLog.TEAM_ID == team.TEAM_ID,
                models.GameLog.RECORD_TYPE_ID == 2  # 패배
            ).first()
            
            if lose_log:
                game_record = "패배"
        
        # 5. 우리 팀 일일 송금액 조회
        our_team_accounts = db.query(models.Account).filter(models.Account.TEAM_ID == team.TEAM_ID).all()
        total_daily_saving = 0
        
        for account in our_team_accounts:
            # DailyTransfer 테이블에서 해당 날짜의 송금액 조회
            transfers = db.query(func.sum(models.DailyTransfer.AMOUNT)).filter(
                models.DailyTransfer.ACCOUNT_ID == account.ACCOUNT_ID,
                models.DailyTransfer.DATE == target_date
            ).scalar() or 0
            
            total_daily_saving += transfers
        
        # 6. 상대 팀 일일 송금액 조회
        opponent_accounts = db.query(models.Account).filter(models.Account.TEAM_ID == opponent_id).all()
        opponent_total_daily_saving = 0
        
        for account in opponent_accounts:
            # DailyTransfer 테이블에서 해당 날짜의 송금액 조회
            transfers = db.query(func.sum(models.DailyTransfer.AMOUNT)).filter(
                models.DailyTransfer.ACCOUNT_ID == account.ACCOUNT_ID,
                models.DailyTransfer.DATE == target_date
            ).scalar() or 0
            
            opponent_total_daily_saving += transfers
        
        # 7. 결과 데이터 추가
        teams_data.append({
            "team_id" : team.TEAM_ID,
            "team": team.TEAM_NAME,
            "opponent": opponent.TEAM_NAME if opponent else "Unknown",
            "game_record": game_record,
            "total_daily_saving": total_daily_saving,
            "opponent_total_daily_saving": opponent_total_daily_saving
        })
    
    return teams_data