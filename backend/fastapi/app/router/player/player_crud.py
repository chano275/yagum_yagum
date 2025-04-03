from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import models
from router.player.player_schema import PlayerCreate, PlayerUpdate, PlayerRecordCreate, DailyReportCreate

def get_player_by_id(db: Session, player_id: int):
    """선수 ID로 선수 정보 조회"""
    return db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()

def get_player_by_name_and_team(db: Session, player_name: str, team_id: int):
    """선수 이름과 팀 ID로 선수 정보 조회"""
    return db.query(models.Player).filter(
        models.Player.PLAYER_NAME == player_name,
        models.Player.TEAM_ID == team_id
    ).first()

def get_players_by_team(db: Session, team_id: int, skip: int = 0, limit: int = 100):
    """특정 팀의 모든 선수 조회"""
    return db.query(models.Player).filter(models.Player.TEAM_ID == team_id).offset(skip).limit(limit).all()

def get_players_by_type(db: Session, player_type_id: int, skip: int = 0, limit: int = 100):
    """특정 포지션의 모든 선수 조회"""
    return db.query(models.Player).filter(models.Player.PLAYER_TYPE_ID == player_type_id).offset(skip).limit(limit).all()

def get_all_players(db: Session, skip: int = 0, limit: int = 100):
    """모든 선수 조회"""
    return db.query(models.Player).offset(skip).limit(limit).all()

def create_player(db: Session, player: PlayerCreate):
    """새로운 선수 생성"""
    db_player = models.Player(
        TEAM_ID=player.TEAM_ID,
        PLAYER_NUM=player.PLAYER_NUM,
        PLAYER_TYPE_ID=player.PLAYER_TYPE_ID,
        PLAYER_NAME=player.PLAYER_NAME,
        PLAYER_IMAGE_URL=player.PLAYER_IMAGE_URL,
        LIKE_COUNT=0,
        created_at=datetime.now()
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: int, player: PlayerUpdate):
    """선수 정보 업데이트"""
    db_player = get_player_by_id(db, player_id)
    if not db_player:
        return None
    
    update_data = player.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_player, key, value)
    
    db.commit()
    db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: int):
    """선수 삭제"""
    db_player = get_player_by_id(db, player_id)
    if not db_player:
        return False
    
    db.delete(db_player)
    db.commit()
    return True

def increase_player_like(db: Session, player_id: int):
    """선수 좋아요 증가"""
    db_player = get_player_by_id(db, player_id)
    if not db_player:
        return None
    
    db_player.LIKE_COUNT += 1
    db.commit()
    db.refresh(db_player)
    return db_player

def get_player_types(db: Session):
    """모든 선수 포지션 타입 조회"""
    return db.query(models.PlayerType).all()

def get_player_type_by_id(db: Session, player_type_id: int):
    """포지션 ID로 포지션 정보 조회"""
    return db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == player_type_id).first()

def get_player_records(db: Session, player_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """선수의 기록 조회"""
    query = db.query(models.PlayerRecord).filter(models.PlayerRecord.PLAYER_ID == player_id)
    
    if start_date:
        query = query.filter(models.PlayerRecord.DATE >= start_date)
    if end_date:
        query = query.filter(models.PlayerRecord.DATE <= end_date)
    
    return query.order_by(models.PlayerRecord.DATE.desc()).all()

def get_player_records_by_team(db: Session, team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """팀 선수들의 기록 조회"""
    query = db.query(models.PlayerRecord).filter(models.PlayerRecord.TEAM_ID == team_id)
    
    if start_date:
        query = query.filter(models.PlayerRecord.DATE >= start_date)
    if end_date:
        query = query.filter(models.PlayerRecord.DATE <= end_date)
    
    return query.order_by(models.PlayerRecord.DATE.desc(), models.PlayerRecord.PLAYER_ID).all()

def get_player_records_by_type(db: Session, record_type_id: int, skip: int = 0, limit: int = 100):
    """특정 기록 유형의 선수 기록 조회"""
    return db.query(models.PlayerRecord).filter(
        models.PlayerRecord.RECORD_TYPE_ID == record_type_id
    ).order_by(
        models.PlayerRecord.DATE.desc(), 
        models.PlayerRecord.COUNT.desc()
    ).offset(skip).limit(limit).all()

def create_player_record(db: Session, record: PlayerRecordCreate):
    """선수 기록 생성"""
    # 동일한 날짜, 선수, 팀, 기록 타입의 레코드 확인
    existing_record = db.query(models.PlayerRecord).filter(
        models.PlayerRecord.DATE == record.DATE,
        models.PlayerRecord.PLAYER_ID == record.PLAYER_ID,
        models.PlayerRecord.TEAM_ID == record.TEAM_ID,
        models.PlayerRecord.RECORD_TYPE_ID == record.RECORD_TYPE_ID
    ).first()
    
    if existing_record:
        # 이미 존재하면 카운트 업데이트
        existing_record.COUNT = record.COUNT
        db.commit()
        db.refresh(existing_record)
        return existing_record
    else:
        # 새로 생성
        db_record = models.PlayerRecord(
            DATE=record.DATE,
            PLAYER_ID=record.PLAYER_ID,
            TEAM_ID=record.TEAM_ID,
            RECORD_TYPE_ID=record.RECORD_TYPE_ID,
            COUNT=record.COUNT
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

def get_player_monthly_stats(db: Session, player_id: int, year: int, month: int):
    """선수의 월간 기록 통계"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    records = db.query(
        models.PlayerRecord.RECORD_TYPE_ID,
        func.sum(models.PlayerRecord.COUNT).label("total")
    ).filter(
        models.PlayerRecord.PLAYER_ID == player_id,
        models.PlayerRecord.DATE >= start_date,
        models.PlayerRecord.DATE <= end_date
    ).group_by(
        models.PlayerRecord.RECORD_TYPE_ID
    ).all()
    
    result = {}
    for record in records:
        record_type = db.query(models.RecordType).filter(
            models.RecordType.RECORD_TYPE_ID == record.RECORD_TYPE_ID
        ).first()
        
        if record_type:
            result[record_type.RECORD_NAME] = record.total
    
    return result

def get_player_daily_reports(db: Session, player_id: int, skip: int = 0, limit: int = 10):
    """선수의 일일 보고서 조회"""
    return db.query(models.DailyReportPlayer).filter(
        models.DailyReportPlayer.PLAYER_ID == player_id
    ).order_by(
        models.DailyReportPlayer.DATE.desc()
    ).offset(skip).limit(limit).all()

def get_player_weekly_reports(db: Session, player_id: int, skip: int = 0, limit: int = 10):
    """선수의 주간 보고서 조회"""
    return db.query(models.WeeklyReportPlayer).filter(
        models.WeeklyReportPlayer.PLAYER_ID == player_id
    ).order_by(
        models.WeeklyReportPlayer.DATE.desc()
    ).offset(skip).limit(limit).all()

def create_player_daily_report(db: Session, report: DailyReportCreate):
    """선수 일일 보고서 생성"""
    # 같은 날짜, 같은 선수의 보고서가 있는지 확인
    existing_report = db.query(models.DailyReportPlayer).filter(
        models.DailyReportPlayer.DATE == report.DATE,
        models.DailyReportPlayer.PLAYER_ID == report.PLAYER_ID
    ).first()
    
    if existing_report:
        # 이미 존재하면 내용 업데이트
        existing_report.LLM_CONTEXT = report.LLM_CONTEXT
        db.commit()
        db.refresh(existing_report)
        return existing_report
    else:
        # 새로 생성
        db_report = models.DailyReportPlayer(
            DATE=report.DATE,
            PLAYER_ID=report.PLAYER_ID,
            LLM_CONTEXT=report.LLM_CONTEXT
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

def get_top_players_by_record(db: Session, record_type_id: int, limit: int = 10):
    """특정 기록 유형별 상위 선수 조회"""
    # 최근 30일간의 데이터만 고려
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    player_records = db.query(
        models.PlayerRecord.PLAYER_ID,
        func.sum(models.PlayerRecord.COUNT).label("total")
    ).filter(
        models.PlayerRecord.RECORD_TYPE_ID == record_type_id,
        models.PlayerRecord.DATE >= thirty_days_ago
    ).group_by(
        models.PlayerRecord.PLAYER_ID
    ).order_by(
        desc("total")
    ).limit(limit).all()
    
    result = []
    for record in player_records:
        player = get_player_by_id(db, record.PLAYER_ID)
        if player:
            result.append({
                "player": player,
                "total": record.total
            })
    
    return result

def get_player_run_history(db: Session, player_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """선수의 출전 기록 조회"""
    query = db.query(models.RunPlayer).filter(models.RunPlayer.PLAYER_ID == player_id)
    
    if start_date:
        query = query.filter(models.RunPlayer.DATE >= start_date)
    if end_date:
        query = query.filter(models.RunPlayer.DATE <= end_date)
    
    return query.order_by(models.RunPlayer.DATE.desc()).all()

def record_player_run(db: Session, player_id: int, run_date: date):
    """선수 출전 기록 생성"""
    # 같은 날짜, 같은 선수의 출전 기록이 있는지 확인
    existing_run = db.query(models.RunPlayer).filter(
        models.RunPlayer.DATE == run_date,
        models.RunPlayer.PLAYER_ID == player_id
    ).first()
    
    if existing_run:
        # 이미 존재하면 기존 것 반환
        return existing_run
    else:
        # 새로 생성
        db_run = models.RunPlayer(
            DATE=run_date,
            PLAYER_ID=player_id
        )
        db.add(db_run)
        db.commit()
        db.refresh(db_run)
        return db_run