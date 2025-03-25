from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

import models
from router.mission.mission_schema import MissionCreate, MissionUpdate, UsedMissionCreate, UsedMissionUpdate

def get_mission_by_id(db: Session, mission_id: int):
    """미션 ID로 미션 정보 조회"""
    return db.query(models.Mission).filter(models.Mission.MISSION_ID == mission_id).first()

def get_mission_by_name(db: Session, mission_name: str):
    """미션 이름으로 미션 정보 조회"""
    return db.query(models.Mission).filter(models.Mission.MISSION_NAME == mission_name).first()

def get_all_missions(db: Session, skip: int = 0, limit: int = 100):
    """모든 미션 조회"""
    return db.query(models.Mission).offset(skip).limit(limit).all()

def create_mission(db: Session, mission: MissionCreate):
    """새로운 미션 생성"""
    db_mission = models.Mission(
        MISSION_NAME=mission.MISSION_NAME,
        MISSION_MAX_COUNT=mission.MISSION_MAX_COUNT,
        MISSION_RATE=mission.MISSION_RATE,
        created_at=datetime.now()
    )
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission

def update_mission(db: Session, mission_id: int, mission: MissionUpdate):
    """미션 정보 업데이트"""
    db_mission = get_mission_by_id(db, mission_id)
    if not db_mission:
        return None
    
    update_data = mission.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_mission, key, value)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

def delete_mission(db: Session, mission_id: int):
    """미션 삭제"""
    db_mission = get_mission_by_id(db, mission_id)
    if not db_mission:
        return False
    
    # 사용된 미션이 있는지 확인
    used_missions = db.query(models.UsedMission).filter(models.UsedMission.MISSION_ID == mission_id).all()
    if used_missions:
        # 이미 사용 중인 미션은 삭제할 수 없음 (참조 무결성)
        return False
    
    db.delete(db_mission)
    db.commit()
    return True

def get_used_mission_by_id(db: Session, used_mission_id: int):
    """사용된 미션 ID로 조회"""
    return db.query(models.UsedMission).filter(models.UsedMission.USED_MISSION_ID == used_mission_id).first()

def get_used_missions_by_account(db: Session, account_id: int):
    """계정별 사용된 미션 조회"""
    return db.query(models.UsedMission).filter(models.UsedMission.ACCOUNT_ID == account_id).all()

def get_used_mission(db: Session, account_id: int, mission_id: int):
    """특정 계정의 특정 미션 사용 정보 조회"""
    return db.query(models.UsedMission).filter(
        models.UsedMission.ACCOUNT_ID == account_id,
        models.UsedMission.MISSION_ID == mission_id
    ).first()

def create_used_mission(db: Session, used_mission: UsedMissionCreate):
    """사용된 미션 정보 생성"""
    # 미션 정보 조회
    mission = get_mission_by_id(db, used_mission.MISSION_ID)
    if not mission:
        return None
    
    # 이미 존재하는지 확인
    existing = get_used_mission(db, used_mission.ACCOUNT_ID, used_mission.MISSION_ID)
    if existing:
        return None  # 이미 해당 계정에 해당 미션이 등록됨
    
    db_used_mission = models.UsedMission(
        ACCOUNT_ID=used_mission.ACCOUNT_ID,
        MISSION_ID=used_mission.MISSION_ID,
        COUNT=used_mission.COUNT if used_mission.COUNT is not None else 0,
        MAX_COUNT=mission.MISSION_MAX_COUNT,
        MISSION_RATE=mission.MISSION_RATE,
        created_at=datetime.now()
    )
    db.add(db_used_mission)
    db.commit()
    db.refresh(db_used_mission)
    return db_used_mission

def update_used_mission(db: Session, used_mission_id: int, used_mission: UsedMissionUpdate):
    """사용된 미션 정보 업데이트"""
    db_used_mission = get_used_mission_by_id(db, used_mission_id)
    if not db_used_mission:
        return None
    
    update_data = used_mission.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_used_mission, key, value)
    
    # 카운트가 최대치를 넘지 않도록 조정
    if db_used_mission.COUNT > db_used_mission.MAX_COUNT:
        db_used_mission.COUNT = db_used_mission.MAX_COUNT
    
    db.commit()
    db.refresh(db_used_mission)
    return db_used_mission

def delete_used_mission(db: Session, used_mission_id: int):
    """사용된 미션 정보 삭제"""
    db_used_mission = get_used_mission_by_id(db, used_mission_id)
    if not db_used_mission:
        return False
    
    db.delete(db_used_mission)
    db.commit()
    return True

def increment_mission_count(db: Session, account_id: int, mission_id: int):
    """미션 카운트 증가"""
    db_used_mission = get_used_mission(db, account_id, mission_id)
    if not db_used_mission:
        # 해당 계정에 미션이 등록되어 있지 않음
        return None
    
    # 카운트가 최대치에 도달했는지 확인
    if db_used_mission.COUNT >= db_used_mission.MAX_COUNT:
        return db_used_mission  # 이미 최대치에 도달
    
    # 카운트 증가
    db_used_mission.COUNT += 1
    db.commit()
    db.refresh(db_used_mission)
    return db_used_mission

def get_account_mission_summary(db: Session, account_id: int):
    """계정의 미션 달성 요약 정보"""
    used_missions = get_used_missions_by_account(db, account_id)
    
    total_missions = len(used_missions)
    completed_missions = sum(1 for m in used_missions if m.COUNT >= m.MAX_COUNT)
    total_rate = sum(m.MISSION_RATE for m in used_missions if m.COUNT >= m.MAX_COUNT)
    
    return {
        "total_missions": total_missions,
        "completed_missions": completed_missions,
        "completion_rate": (completed_missions / total_missions * 100) if total_missions > 0 else 0,
        "total_rate": total_rate
    }

def get_unused_missions(db: Session, account_id: int):
    """계정이 아직 등록하지 않은 미션 목록"""
    # 계정이 이미 사용 중인 미션 ID 목록
    used_mission_ids = db.query(models.UsedMission.MISSION_ID).filter(
        models.UsedMission.ACCOUNT_ID == account_id
    ).all()
    
    used_mission_ids = [m[0] for m in used_mission_ids]
    
    # 사용 중이지 않은 미션 조회
    unused_missions = db.query(models.Mission).filter(
        models.Mission.MISSION_ID.notin_(used_mission_ids)
    ).all()
    
    return unused_missions

def calculate_account_interest_rate(db: Session, account_id: int):
    """계정의 미션 달성에 따른 이자율 계산"""
    # 계정 정보 조회
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return None
    
    # 계정의 미션 달성 정보 조회
    mission_summary = get_account_mission_summary(db, account_id)
    
    # 기본 이자율 + 미션 달성에 따른 추가 이자율
    total_interest_rate = account.INTEREST_RATE + mission_summary["total_rate"]
    
    return total_interest_rate

def update_account_interest_rate(db: Session, account_id: int):
    """계정의 이자율 업데이트"""
    # 계정 정보 조회
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return None
    
    # 미션 달성에 따른 이자율 계산
    new_interest_rate = calculate_account_interest_rate(db, account_id)
    
    # 이자율 업데이트
    account.INTEREST_RATE = new_interest_rate
    db.commit()
    db.refresh(account)
    
    return account