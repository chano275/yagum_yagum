from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import models
from router.game.game_schema import GameScheduleCreate, GameScheduleUpdate, GameLogCreate, GameLogUpdate, GameResultCreate

def get_game_schedule_by_id(db: Session, game_schedule_key: int):
    """게임 일정 ID로 조회"""
    return db.query(models.GameSchedule).filter(models.GameSchedule.GAME_SCHEDULE_KEY == game_schedule_key).first()

def get_game_schedules(db: Session, skip: int = 0, limit: int = 100):
    """모든 게임 일정 조회"""
    return db.query(models.GameSchedule).offset(skip).limit(limit).all()

def get_game_schedules_by_date(db: Session, game_date: date):
    """특정 날짜의 게임 일정 조회"""
    return db.query(models.GameSchedule).filter(models.GameSchedule.DATE == game_date).all()

def get_game_schedules_by_date_range(db: Session, start_date: date, end_date: date):
    """날짜 범위 내의 게임 일정 조회"""
    return db.query(models.GameSchedule).filter(
        models.GameSchedule.DATE >= start_date,
        models.GameSchedule.DATE <= end_date
    ).order_by(models.GameSchedule.DATE).all()

def get_game_schedules_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """특정 팀의 게임 일정 조회"""
    return db.query(models.GameSchedule).filter(
        or_(
            models.GameSchedule.HOME_TEAM_ID == team_id,
            models.GameSchedule.AWAY_TEAM_ID == team_id
        )
    ).offset(skip).limit(limit).all()

def create_game_schedule(db: Session, game_schedule: GameScheduleCreate):
    """게임 일정 생성"""
    db_game_schedule = models.GameSchedule(
        DATE=game_schedule.DATE,
        HOME_TEAM_ID=game_schedule.HOME_TEAM_ID,
        AWAY_TEAM_ID=game_schedule.AWAY_TEAM_ID
    )
    db.add(db_game_schedule)
    db.commit()
    db.refresh(db_game_schedule)
    return db_game_schedule

def update_game_schedule(db: Session, game_schedule_key: int, game_schedule: GameScheduleUpdate):
    """게임 일정 업데이트"""
    db_game_schedule = get_game_schedule_by_id(db, game_schedule_key)
    if not db_game_schedule:
        return None
    
    update_data = game_schedule.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_game_schedule, key, value)
    
    db.commit()
    db.refresh(db_game_schedule)
    return db_game_schedule

def delete_game_schedule(db: Session, game_schedule_key: int):
    """게임 일정 삭제"""
    db_game_schedule = get_game_schedule_by_id(db, game_schedule_key)
    if not db_game_schedule:
        return False
    
    db.delete(db_game_schedule)
    db.commit()
    return True

def get_game_log_by_id(db: Session, game_log_id: int):
    """게임 로그 ID로 조회"""
    return db.query(models.GameLog).filter(models.GameLog.GAME_LOG_ID == game_log_id).first()

def get_game_logs(db: Session, skip: int = 0, limit: int = 100):
    """모든 게임 로그 조회"""
    return db.query(models.GameLog).offset(skip).limit(limit).all()

def get_game_logs_by_date(db: Session, log_date: date):
    """특정 날짜의 게임 로그 조회"""
    return db.query(models.GameLog).filter(models.GameLog.DATE == log_date).all()

def get_game_logs_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """특정 팀의 게임 로그 조회"""
    return db.query(models.GameLog).filter(models.GameLog.TEAM_ID == team_id).offset(skip).limit(limit).all()

def get_game_logs_by_record_type(db: Session, record_type_id: int, skip: int = 0, limit: int = 100):
    """특정 기록 유형의 게임 로그 조회"""
    return db.query(models.GameLog).filter(models.GameLog.RECORD_TYPE_ID == record_type_id).offset(skip).limit(limit).all()

def get_game_logs_by_date_and_team(db: Session, log_date: date, team_id: int):
    """특정 날짜와 팀의 게임 로그 조회"""
    return db.query(models.GameLog).filter(
        models.GameLog.DATE == log_date,
        models.GameLog.TEAM_ID == team_id
    ).all()

def create_game_log(db: Session, game_log: GameLogCreate):
    """게임 로그 생성"""
    db_game_log = models.GameLog(
        DATE=game_log.DATE,
        TEAM_ID=game_log.TEAM_ID,
        RECORD_TYPE_ID=game_log.RECORD_TYPE_ID,
        COUNT=game_log.COUNT
    )
    db.add(db_game_log)
    db.commit()
    db.refresh(db_game_log)
    return db_game_log

def update_game_log(db: Session, game_log_id: int, game_log: GameLogUpdate):
    """게임 로그 업데이트"""
    db_game_log = get_game_log_by_id(db, game_log_id)
    if not db_game_log:
        return None
    
    update_data = game_log.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_game_log, key, value)
    
    db.commit()
    db.refresh(db_game_log)
    return db_game_log

def delete_game_log(db: Session, game_log_id: int):
    """게임 로그 삭제"""
    db_game_log = get_game_log_by_id(db, game_log_id)
    if not db_game_log:
        return False
    
    db.delete(db_game_log)
    db.commit()
    return True

def record_game_result(db: Session, game_result: GameResultCreate):
    """게임 결과 기록"""
    # 게임 일정 확인 및 가져오기
    game_schedule = db.query(models.GameSchedule).filter(
        models.GameSchedule.DATE == game_result.DATE,
        models.GameSchedule.HOME_TEAM_ID == game_result.HOME_TEAM_ID,
        models.GameSchedule.AWAY_TEAM_ID == game_result.AWAY_TEAM_ID
    ).first()
    
    if not game_schedule:
        # 일정이 없다면 새로 생성
        game_schedule = models.GameSchedule(
            DATE=game_result.DATE,
            HOME_TEAM_ID=game_result.HOME_TEAM_ID,
            AWAY_TEAM_ID=game_result.AWAY_TEAM_ID
        )
        db.add(game_schedule)
        db.flush()
    
    # 홈팀과 원정팀 정보 가져오기
    home_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_result.HOME_TEAM_ID).first()
    away_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_result.AWAY_TEAM_ID).first()
    
    if not home_team or not away_team:
        return None
    
    # 게임 결과에 따라 팀 성적 업데이트
    if game_result.RESULT == "HOME_WIN":
        home_team.TOTAL_WIN += 1
        away_team.TOTAL_LOSE += 1
    elif game_result.RESULT == "AWAY_WIN":
        home_team.TOTAL_LOSE += 1
        away_team.TOTAL_WIN += 1
    elif game_result.RESULT == "DRAW":
        home_team.TOTAL_DRAW += 1
        away_team.TOTAL_DRAW += 1
    
    db.commit()
    db.refresh(home_team)
    db.refresh(away_team)
    
    # 응답 형식에 맞게 데이터 구성
    result = {
        "GAME_SCHEDULE_KEY": game_schedule.GAME_SCHEDULE_KEY,
        "DATE": game_result.DATE,
        "HOME_TEAM_ID": game_result.HOME_TEAM_ID,
        "AWAY_TEAM_ID": game_result.AWAY_TEAM_ID,
        "HOME_SCORE": game_result.HOME_SCORE,
        "AWAY_SCORE": game_result.AWAY_SCORE,
        "RESULT": game_result.RESULT,
        "home_team_name": home_team.TEAM_NAME,
        "away_team_name": away_team.TEAM_NAME
    }
    
    return result

def get_team_record(db: Session, team_id: int):
    """팀 성적 조회"""
    team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
    if not team:
        return None
    
    total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
    win_rate = team.TOTAL_WIN / total_games * 100 if total_games > 0 else 0
    
    result = {
        "TEAM_ID": team.TEAM_ID,
        "TEAM_NAME": team.TEAM_NAME,
        "TOTAL_WIN": team.TOTAL_WIN,
        "TOTAL_LOSE": team.TOTAL_LOSE,
        "TOTAL_DRAW": team.TOTAL_DRAW,
        "WIN_RATE": round(win_rate, 2)
    }
    
    return result

def get_all_team_records(db: Session, skip: int = 0, limit: int = 100):
    """모든 팀 성적 조회"""
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    
    results = []
    for team in teams:
        total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
        win_rate = team.TOTAL_WIN / total_games * 100 if total_games > 0 else 0
        
        results.append({
            "TEAM_ID": team.TEAM_ID,
            "TEAM_NAME": team.TEAM_NAME,
            "TOTAL_WIN": team.TOTAL_WIN,
            "TOTAL_LOSE": team.TOTAL_LOSE,
            "TOTAL_DRAW": team.TOTAL_DRAW,
            "WIN_RATE": round(win_rate, 2)
        })
    
    # 승률 기준으로 정렬
    results.sort(key=lambda x: x["WIN_RATE"], reverse=True)
    
    return results