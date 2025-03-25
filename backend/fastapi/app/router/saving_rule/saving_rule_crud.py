from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import models
from router.saving_rule.saving_rule_schema import (
    SavingRuleTypeCreate, SavingRuleListCreate, SavingRuleDetailCreate,
    UserSavingRuleCreate, DailySavingCreate, SavingRuleTypeUpdate,
    SavingRuleListUpdate, SavingRuleDetailUpdate, UserSavingRuleUpdate
)

def get_saving_rule_type_by_id(db: Session, saving_rule_type_id: int):
    """적금 규칙 타입 ID로 조회"""
    return db.query(models.SavingRuleType).filter(
        models.SavingRuleType.SAVING_RULE_TYPE_ID == saving_rule_type_id
    ).first()

def get_saving_rule_type_by_name(db: Session, saving_rule_type_name: str):
    """적금 규칙 타입 이름으로 조회"""
    return db.query(models.SavingRuleType).filter(
        models.SavingRuleType.SAVING_RULE_TYPE_NAME == saving_rule_type_name
    ).first()

def get_all_saving_rule_types(db: Session, skip: int = 0, limit: int = 100):
    """모든 적금 규칙 타입 조회"""
    return db.query(models.SavingRuleType).offset(skip).limit(limit).all()

def create_saving_rule_type(db: Session, saving_rule_type: SavingRuleTypeCreate):
    """적금 규칙 타입 생성"""
    db_saving_rule_type = models.SavingRuleType(
        SAVING_RULE_TYPE_NAME=saving_rule_type.SAVING_RULE_TYPE_NAME
    )
    db.add(db_saving_rule_type)
    db.commit()
    db.refresh(db_saving_rule_type)
    return db_saving_rule_type

def update_saving_rule_type(db: Session, saving_rule_type_id: int, saving_rule_type: SavingRuleTypeUpdate):
    """적금 규칙 타입 업데이트"""
    db_saving_rule_type = get_saving_rule_type_by_id(db, saving_rule_type_id)
    if not db_saving_rule_type:
        return None
    
    db_saving_rule_type.SAVING_RULE_TYPE_NAME = saving_rule_type.SAVING_RULE_TYPE_NAME
    db.commit()
    db.refresh(db_saving_rule_type)
    return db_saving_rule_type

def delete_saving_rule_type(db: Session, saving_rule_type_id: int):
    """적금 규칙 타입 삭제"""
    db_saving_rule_type = get_saving_rule_type_by_id(db, saving_rule_type_id)
    if not db_saving_rule_type:
        return False
    
    # 관련 데이터 확인
    has_related_data = (
        db.query(models.SavingRuleList).filter(
            models.SavingRuleList.SAVING_RULE_TYPE_ID == saving_rule_type_id
        ).count() > 0 or
        db.query(models.SavingRuleDetail).filter(
            models.SavingRuleDetail.SAVING_RULE_TYPE_ID == saving_rule_type_id
        ).count() > 0 or
        db.query(models.UserSavingRule).filter(
            models.UserSavingRule.SAVING_RULE_TYPE_ID == saving_rule_type_id
        ).count() > 0 or
        db.query(models.DailySaving).filter(
            models.DailySaving.SAVING_RULED_TYPE_ID == saving_rule_type_id
        ).count() > 0
    )
    
    if has_related_data:
        return False  # 관련 데이터가 있으면 삭제 불가
    
    db.delete(db_saving_rule_type)
    db.commit()
    return True

def get_record_type_by_id(db: Session, record_type_id: int):
    """기록 타입 ID로 조회"""
    return db.query(models.RecordType).filter(
        models.RecordType.RECORD_TYPE_ID == record_type_id
    ).first()

def get_all_record_types(db: Session, skip: int = 0, limit: int = 100):
    """모든 기록 타입 조회"""
    return db.query(models.RecordType).offset(skip).limit(limit).all()

def get_saving_rule_by_id(db: Session, saving_rule_id: int):
    """적금 규칙 ID로 조회"""
    return db.query(models.SavingRuleList).filter(
        models.SavingRuleList.SAVING_RULE_ID == saving_rule_id
    ).first()

def get_saving_rules_by_type(db: Session, saving_rule_type_id: int, skip: int = 0, limit: int = 100):
    """특정 타입의 적금 규칙 조회"""
    return db.query(models.SavingRuleList).filter(
        models.SavingRuleList.SAVING_RULE_TYPE_ID == saving_rule_type_id
    ).offset(skip).limit(limit).all()

def get_saving_rules_by_record_type(db: Session, record_type_id: int, skip: int = 0, limit: int = 100):
    """특정 기록 타입의 적금 규칙 조회"""
    return db.query(models.SavingRuleList).filter(
        models.SavingRuleList.RECORD_TYPE_ID == record_type_id
    ).offset(skip).limit(limit).all()

def get_all_saving_rules(db: Session, skip: int = 0, limit: int = 100):
    """모든 적금 규칙 조회"""
    return db.query(models.SavingRuleList).offset(skip).limit(limit).all()

def create_saving_rule(db: Session, saving_rule: SavingRuleListCreate):
    """적금 규칙 생성"""
    db_saving_rule = models.SavingRuleList(
        SAVING_RULE_TYPE_ID=saving_rule.SAVING_RULE_TYPE_ID,
        RECORD_TYPE_ID=saving_rule.RECORD_TYPE_ID
    )
    db.add(db_saving_rule)
    db.commit()
    db.refresh(db_saving_rule)
    return db_saving_rule

def update_saving_rule(db: Session, saving_rule_id: int, saving_rule: SavingRuleListUpdate):
    """적금 규칙 업데이트"""
    db_saving_rule = get_saving_rule_by_id(db, saving_rule_id)
    if not db_saving_rule:
        return None
    
    update_data = saving_rule.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_saving_rule, key, value)
    
    db.commit()
    db.refresh(db_saving_rule)
    return db_saving_rule

def delete_saving_rule(db: Session, saving_rule_id: int):
    """적금 규칙 삭제"""
    db_saving_rule = get_saving_rule_by_id(db, saving_rule_id)
    if not db_saving_rule:
        return False
    
    # 관련 데이터 확인
    has_related_data = (
        db.query(models.SavingRuleDetail).filter(
            models.SavingRuleDetail.SAVING_RULE_ID == saving_rule_id
        ).count() > 0
    )
    
    if has_related_data:
        return False  # 관련 데이터가 있으면 삭제 불가
    
    db.delete(db_saving_rule)
    db.commit()
    return True

def get_saving_rule_detail_by_id(db: Session, saving_rule_detail_id: int):
    """적금 규칙 상세 ID로 조회"""
    return db.query(models.SavingRuleDetail).filter(
        models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == saving_rule_detail_id
    ).first()

def get_saving_rule_details_by_type(db: Session, saving_rule_type_id: int, skip: int = 0, limit: int = 100):
    """특정 타입의 적금 규칙 상세 조회"""
    return db.query(models.SavingRuleDetail).filter(
        models.SavingRuleDetail.SAVING_RULE_TYPE_ID == saving_rule_type_id
    ).offset(skip).limit(limit).all()

def get_saving_rule_details_by_player_type(db: Session, player_type_id: int, skip: int = 0, limit: int = 100):
    """특정 선수 타입의 적금 규칙 상세 조회"""
    return db.query(models.SavingRuleDetail).filter(
        models.SavingRuleDetail.PLAYER_TYPE_ID == player_type_id
    ).offset(skip).limit(limit).all()

def get_saving_rule_details_by_rule(db: Session, saving_rule_id: int, skip: int = 0, limit: int = 100):
    """특정 규칙의 적금 규칙 상세 조회"""
    return db.query(models.SavingRuleDetail).filter(
        models.SavingRuleDetail.SAVING_RULE_ID == saving_rule_id
    ).offset(skip).limit(limit).all()

def get_all_saving_rule_details(db: Session, skip: int = 0, limit: int = 100):
    """모든 적금 규칙 상세 조회"""
    return db.query(models.SavingRuleDetail).offset(skip).limit(limit).all()

def create_saving_rule_detail(db: Session, saving_rule_detail: SavingRuleDetailCreate):
    """적금 규칙 상세 생성"""
    db_saving_rule_detail = models.SavingRuleDetail(
        SAVING_RULE_TYPE_ID=saving_rule_detail.SAVING_RULE_TYPE_ID,
        PLAYER_TYPE_ID=saving_rule_detail.PLAYER_TYPE_ID,
        SAVING_RULE_ID=saving_rule_detail.SAVING_RULE_ID
    )
    db.add(db_saving_rule_detail)
    db.commit()
    db.refresh(db_saving_rule_detail)
    return db_saving_rule_detail

def update_saving_rule_detail(db: Session, saving_rule_detail_id: int, saving_rule_detail: SavingRuleDetailUpdate):
    """적금 규칙 상세 업데이트"""
    db_saving_rule_detail = get_saving_rule_detail_by_id(db, saving_rule_detail_id)
    if not db_saving_rule_detail:
        return None
    
    update_data = saving_rule_detail.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_saving_rule_detail, key, value)
    
    db.commit()
    db.refresh(db_saving_rule_detail)
    return db_saving_rule_detail

def delete_saving_rule_detail(db: Session, saving_rule_detail_id: int):
    """적금 규칙 상세 삭제"""
    db_saving_rule_detail = get_saving_rule_detail_by_id(db, saving_rule_detail_id)
    if not db_saving_rule_detail:
        return False
    
    # 관련 데이터 확인
    has_related_data = (
        db.query(models.UserSavingRule).filter(
            models.UserSavingRule.SAVING_RULE_DETAIL_ID == saving_rule_detail_id
        ).count() > 0 or
        db.query(models.DailySaving).filter(
            models.DailySaving.SAVING_RULED_DETAIL_ID == saving_rule_detail_id
        ).count() > 0
    )
    
    if has_related_data:
        return False  # 관련 데이터가 있으면 삭제 불가
    
    db.delete(db_saving_rule_detail)
    db.commit()
    return True

def get_user_saving_rule_by_id(db: Session, user_saving_rule_id: int):
    """사용자 적금 규칙 ID로 조회"""
    return db.query(models.UserSavingRule).filter(
        models.UserSavingRule.USER_SAVING_RULED_ID == user_saving_rule_id
    ).first()

def get_user_saving_rules_by_account(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    """계정별 사용자 적금 규칙 조회"""
    return db.query(models.UserSavingRule).filter(
        models.UserSavingRule.ACCOUNT_ID == account_id
    ).offset(skip).limit(limit).all()

def get_user_saving_rules_by_player(db: Session, player_id: int, skip: int = 0, limit: int = 100):
    """선수별 사용자 적금 규칙 조회"""
    return db.query(models.UserSavingRule).filter(
        models.UserSavingRule.PLAYER_ID == player_id
    ).offset(skip).limit(limit).all()

def get_user_saving_rule_by_account_and_detail(db: Session, account_id: int, saving_rule_detail_id: int):
    """계정과 적금 규칙 상세로 사용자 적금 규칙 조회"""
    return db.query(models.UserSavingRule).filter(
        models.UserSavingRule.ACCOUNT_ID == account_id,
        models.UserSavingRule.SAVING_RULE_DETAIL_ID == saving_rule_detail_id
    ).first()

def create_user_saving_rule(db: Session, user_saving_rule: UserSavingRuleCreate):
    """사용자 적금 규칙 생성"""
    db_user_saving_rule = models.UserSavingRule(
        ACCOUNT_ID=user_saving_rule.ACCOUNT_ID,
        SAVING_RULE_TYPE_ID=user_saving_rule.SAVING_RULE_TYPE_ID,
        SAVING_RULE_DETAIL_ID=user_saving_rule.SAVING_RULE_DETAIL_ID,
        PLAYER_TYPE_ID=user_saving_rule.PLAYER_TYPE_ID,
        USER_SAVING_RULED_AMOUNT=user_saving_rule.USER_SAVING_RULED_AMOUNT,
        PLAYER_ID=user_saving_rule.PLAYER_ID
    )
    db.add(db_user_saving_rule)
    db.commit()
    db.refresh(db_user_saving_rule)
    return db_user_saving_rule

def update_user_saving_rule(db: Session, user_saving_rule_id: int, user_saving_rule: UserSavingRuleUpdate):
    """사용자 적금 규칙 업데이트"""
    db_user_saving_rule = get_user_saving_rule_by_id(db, user_saving_rule_id)
    if not db_user_saving_rule:
        return None
    
    update_data = user_saving_rule.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_user_saving_rule, key, value)
    
    db.commit()
    db.refresh(db_user_saving_rule)
    return db_user_saving_rule

def delete_user_saving_rule(db: Session, user_saving_rule_id: int):
    """사용자 적금 규칙 삭제"""
    db_user_saving_rule = get_user_saving_rule_by_id(db, user_saving_rule_id)
    if not db_user_saving_rule:
        return False
    
    db.delete(db_user_saving_rule)
    db.commit()
    return True

def get_daily_saving_by_id(db: Session, daily_saving_id: int):
    """일일 적금 ID로 조회"""
    return db.query(models.DailySaving).filter(
        models.DailySaving.DAILY_SAVING_ID == daily_saving_id
    ).first()

def get_daily_savings_by_account(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    """계정별 일일 적금 조회"""
    return db.query(models.DailySaving).filter(
        models.DailySaving.ACCOUNT_ID == account_id
    ).order_by(models.DailySaving.DATE.desc()).offset(skip).limit(limit).all()

def get_daily_savings_by_date(db: Session, saving_date: date, skip: int = 0, limit: int = 100):
    """날짜별 일일 적금 조회"""
    return db.query(models.DailySaving).filter(
        models.DailySaving.DATE == saving_date
    ).offset(skip).limit(limit).all()

def get_daily_savings_by_account_and_date(db: Session, account_id: int, saving_date: date):
    """계정과 날짜로 일일 적금 조회"""
    return db.query(models.DailySaving).filter(
        models.DailySaving.ACCOUNT_ID == account_id,
        models.DailySaving.DATE == saving_date
    ).all()

def get_daily_savings_by_account_and_date_range(db: Session, account_id: int, start_date: date, end_date: date):
    """계정과 날짜 범위로 일일 적금 조회"""
    return db.query(models.DailySaving).filter(
        models.DailySaving.ACCOUNT_ID == account_id,
        models.DailySaving.DATE >= start_date,
        models.DailySaving.DATE <= end_date
    ).order_by(models.DailySaving.DATE).all()

def create_daily_saving(db: Session, daily_saving: DailySavingCreate):
    """일일 적금 생성"""
    db_daily_saving = models.DailySaving(
        ACCOUNT_ID=daily_saving.ACCOUNT_ID,
        DATE=daily_saving.DATE,
        SAVING_RULED_DETAIL_ID=daily_saving.SAVING_RULED_DETAIL_ID,
        SAVING_RULED_TYPE_ID=daily_saving.SAVING_RULED_TYPE_ID,
        COUNT=daily_saving.COUNT,
        DAILY_SAVING_AMOUNT=daily_saving.DAILY_SAVING_AMOUNT,
        created_at=datetime.now()
    )
    db.add(db_daily_saving)
    db.commit()
    db.refresh(db_daily_saving)
    
    # 계정 잔액 업데이트
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == daily_saving.ACCOUNT_ID).first()
    if account:
        account.TOTAL_AMOUNT += daily_saving.DAILY_SAVING_AMOUNT
        db.commit()
    
    return db_daily_saving

def delete_daily_saving(db: Session, daily_saving_id: int):
    """일일 적금 삭제"""
    db_daily_saving = get_daily_saving_by_id(db, daily_saving_id)
    if not db_daily_saving:
        return False
    
    # 계정 잔액 업데이트 (차감)
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == db_daily_saving.ACCOUNT_ID).first()
    if account:
        account.TOTAL_AMOUNT -= db_daily_saving.DAILY_SAVING_AMOUNT
        # 음수가 되지 않도록 확인
        if account.TOTAL_AMOUNT < 0:
            account.TOTAL_AMOUNT = 0
    
    db.delete(db_daily_saving)
    db.commit()
    return True

def calculate_daily_saving(db: Session, account_id: int, player_record: Dict):
    """선수 기록을 바탕으로 일일 적금액 계산"""
    # 필요한 데이터 추출
    player_id = player_record.get("PLAYER_ID")
    record_type_id = player_record.get("RECORD_TYPE_ID")
    count = player_record.get("COUNT", 0)
    record_date = player_record.get("DATE")
    
    if not record_type_id or not record_date:
        return None
    
    # 계정 정보 조회
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return None
    
    # 적금 규칙 찾기
    saving_rules = db.query(models.SavingRuleList).filter(
        models.SavingRuleList.RECORD_TYPE_ID == record_type_id
    ).all()
    
    if not saving_rules:
        return None
    
    total_saving = 0
    created_savings = []
    
    for rule in saving_rules:
        # 규칙 타입 확인
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
        is_team_rule = rule_type and rule_type.SAVING_RULE_TYPE_NAME in ["기본 규칙", "상대팀"]
        
        # 해당 규칙의 상세 규칙 찾기
        if is_team_rule:
            # 팀 규칙은 선수 타입 관계없이 처리
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_ID == rule.SAVING_RULE_ID
            ).first()
        else:
            # 선수 규칙은 선수 타입 고려
            if not player_id:
                continue
                
            # 선수 정보 조회
            player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
            if not player:
                continue
                
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_ID == rule.SAVING_RULE_ID,
                models.SavingRuleDetail.PLAYER_TYPE_ID == player.PLAYER_TYPE_ID
            ).first()
        
        if not rule_detail:
            continue
        
        # 사용자 적금 규칙 확인
        if is_team_rule:
            # 팀 규칙은 PLAYER_ID가 NULL인 규칙 찾기
            user_rule = db.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account_id,
                models.UserSavingRule.SAVING_RULE_DETAIL_ID == rule_detail.SAVING_RULE_DETAIL_ID,
                models.UserSavingRule.PLAYER_ID == None
            ).first()
        else:
            # 선수 규칙은 특정 선수 ID를 가진 규칙 찾기
            user_rule = db.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account_id,
                models.UserSavingRule.SAVING_RULE_DETAIL_ID == rule_detail.SAVING_RULE_DETAIL_ID,
                models.UserSavingRule.PLAYER_ID == player_id
            ).first()
        
        if not user_rule:
            continue
        
        # 적금액 계산
        saving_amount = user_rule.USER_SAVING_RULED_AMOUNT * count
        
        # 같은 날짜, 같은 규칙, 같은 계정의 적금 내역이 있는지 확인
        existing_saving = db.query(models.DailySaving).filter(
            models.DailySaving.ACCOUNT_ID == account_id,
            models.DailySaving.DATE == record_date,
            models.DailySaving.SAVING_RULED_DETAIL_ID == rule_detail.SAVING_RULE_DETAIL_ID
        ).first()
        
        if existing_saving:
            # 기존 적금 내역이 있으면 업데이트
            # 계정 잔액 조정 (기존 금액 차감)
            account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
            if account:
                account.TOTAL_AMOUNT -= existing_saving.DAILY_SAVING_AMOUNT
            
            existing_saving.COUNT = count
            existing_saving.DAILY_SAVING_AMOUNT = saving_amount
            db.commit()
            db.refresh(existing_saving)
            
            # 계정 잔액 조정 (새 금액 추가)
            if account:
                account.TOTAL_AMOUNT += saving_amount
                db.commit()
            
            created_savings.append(existing_saving)
        else:
            # 새로운 적금 내역 생성
            daily_saving_data = DailySavingCreate(
                ACCOUNT_ID=account_id,
                DATE=record_date,
                SAVING_RULED_DETAIL_ID=rule_detail.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_TYPE_ID=rule_detail.SAVING_RULE_TYPE_ID,
                COUNT=count,
                DAILY_SAVING_AMOUNT=saving_amount
            )
            
            new_saving = create_daily_saving(db, daily_saving_data)
            created_savings.append(new_saving)
        
        total_saving += saving_amount
    
    return {
        "total_saving": total_saving,
        "created_savings": created_savings
    }

def get_saving_rule_combinations(db: Session):
    """적금 규칙 조합 목록 조회 (타입별, 선수 포지션별, 기록 유형별)"""
    # SavingRuleDetail 조회 - 조인하여 필요한 정보 모두 가져오기
    rule_details = db.query(
        models.SavingRuleDetail,
        models.SavingRuleType.SAVING_RULE_TYPE_NAME,
        models.PlayerType.PLAYER_TYPE_NAME,
        models.SavingRuleList.RECORD_TYPE_ID,
        models.RecordType.RECORD_NAME
    ).join(
        models.SavingRuleType,
        models.SavingRuleDetail.SAVING_RULE_TYPE_ID == models.SavingRuleType.SAVING_RULE_TYPE_ID
    ).join(
        models.PlayerType,
        models.SavingRuleDetail.PLAYER_TYPE_ID == models.PlayerType.PLAYER_TYPE_ID
    ).join(
        models.SavingRuleList,
        models.SavingRuleDetail.SAVING_RULE_ID == models.SavingRuleList.SAVING_RULE_ID
    ).join(
        models.RecordType,
        models.SavingRuleList.RECORD_TYPE_ID == models.RecordType.RECORD_TYPE_ID
    ).all()
    
    result = []
    for detail, rule_type_name, player_type_name, record_type_id, record_name in rule_details:
        result.append({
            "SAVING_RULE_DETAIL_ID": detail.SAVING_RULE_DETAIL_ID,
            "SAVING_RULE_TYPE_ID": detail.SAVING_RULE_TYPE_ID,
            "SAVING_RULE_TYPE_NAME": rule_type_name,
            "PLAYER_TYPE_ID": detail.PLAYER_TYPE_ID,
            "PLAYER_TYPE_NAME": player_type_name,
            "SAVING_RULE_ID": detail.SAVING_RULE_ID,
            "RECORD_TYPE_ID": record_type_id,
            "RECORD_NAME": record_name
        })
    
    return result

def get_account_saving_summary(db: Session, account_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """계정의 적금 요약 정보"""
    # 기본 날짜 범위 설정 (일주일일)
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=7)
    
    # 계정 확인
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return None
    
    # 기간 내 일일 적금 내역 조회
    daily_savings = get_daily_savings_by_account_and_date_range(db, account_id, start_date, end_date)
    
    # 통계 계산
    total_saving = sum(saving.DAILY_SAVING_AMOUNT for saving in daily_savings)
    daily_avg = total_saving / (end_date - start_date).days if (end_date - start_date).days > 0 else 0
    
    # 규칙 타입별 적립 금액
    rule_type_stats = {}
    for saving in daily_savings:
        rule_type = db.query(models.SavingRuleType).filter(
            models.SavingRuleType.SAVING_RULE_TYPE_ID == saving.SAVING_RULED_TYPE_ID
        ).first()
        ### 수정 필요 rule_type_name이 투수가 아닌 퀄스 이런 식으로
        if rule_type:
            rule_type_name = rule_type.SAVING_RULE_TYPE_NAME
            if rule_type_name not in rule_type_stats:
                rule_type_stats[rule_type_name] = 0
            rule_type_stats[rule_type_name] += saving.DAILY_SAVING_AMOUNT
    
    # 일별 적립 추이
    daily_trend = {}
    for saving in daily_savings:
        date_str = saving.DATE.isoformat()
        if date_str not in daily_trend:
            daily_trend[date_str] = 0
        daily_trend[date_str] += saving.DAILY_SAVING_AMOUNT
    
    # 결과 구성
    result = {
        "account_id": account_id,
        "account_num": account.ACCOUNT_NUM,
        "total_amount": account.TOTAL_AMOUNT,
        "period_saving": total_saving,
        "daily_avg_saving": daily_avg,
        "rule_type_stats": rule_type_stats,
        "daily_trend": daily_trend,
        "start_date": start_date,
        "end_date": end_date
    }
    
    return result

def get_available_saving_rules_for_account(db: Session, account_id: int):
    """계정에 등록 가능한 적금 규칙 목록"""
    # 계정 확인
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return []
    
    # 계정이 속한 팀 확인
    team_id = account.TEAM_ID
    if not team_id:
        return []
    
    # 팀 소속 선수 조회
    team_players = db.query(models.Player).filter(models.Player.TEAM_ID == team_id).all()
    if not team_players:
        return []
    
    # 이미 등록된 규칙의 detail_id 목록
    existing_rules = db.query(models.UserSavingRule.SAVING_RULE_DETAIL_ID).filter(
        models.UserSavingRule.ACCOUNT_ID == account_id
    ).all()
    existing_detail_ids = [rule[0] for rule in existing_rules]
    
    # 가능한 규칙 조합 목록
    all_combinations = get_saving_rule_combinations(db)
    
    # 이미 등록되지 않은 규칙만 필터링
    available_rules = [
        rule for rule in all_combinations
        if rule["SAVING_RULE_DETAIL_ID"] not in existing_detail_ids
    ]
    
    # 각 규칙에 대해 선수 목록 추가
    result = []
    for rule in available_rules:
        # 해당 포지션의 선수들 찾기
        position_players = [
            player for player in team_players
            if player.PLAYER_TYPE_ID == rule["PLAYER_TYPE_ID"]
        ]
        
        # 선수 정보 추가
        rule_with_players = rule.copy()
        rule_with_players["players"] = [
            {
                "PLAYER_ID": player.PLAYER_ID, 
                "PLAYER_NAME": player.PLAYER_NAME,
                "PLAYER_NUM": player.PLAYER_NUM,
                "PLAYER_IMAGE_URL": player.PLAYER_IMAGE_URL
            }
            for player in position_players
        ]
        
        result.append(rule_with_players)
    
    return result

def check_daily_limit(db: Session, account_id: int, amount: int):
    """계정의 일일 적립 한도 확인"""
    # 계정 정보 조회
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return False
    
    # 오늘 날짜의 적립 금액 합계 계산
    today = datetime.now().date()
    today_savings = get_daily_savings_by_account_and_date(db, account_id, today)
    today_total = sum(saving.DAILY_SAVING_AMOUNT for saving in today_savings)
    
    # 적립 한도 체크
    return (today_total + amount) <= account.DAILY_LIMIT

def check_monthly_limit(db: Session, account_id: int, amount: int):
    """계정의 월간 적립 한도 확인"""
    # 계정 정보 조회
    account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
    if not account:
        return False
    
    # 이번 달 시작일과 오늘 날짜
    today = datetime.now().date()
    month_start = date(today.year, today.month, 1)
    
    # 이번 달 적립 금액 합계 계산
    month_savings = get_daily_savings_by_account_and_date_range(db, account_id, month_start, today)
    month_total = sum(saving.DAILY_SAVING_AMOUNT for saving in month_savings)
    
    # 적립 한도 체크
    return (month_total + amount) <= account.MONTH_LIMIT

def get_player_saving_rules(db: Session, player_id: int):
    """선수에 등록된 모든 적금 규칙 조회"""
    player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
    if not player:
        return []
    
    # 선수에 등록된 규칙 조회
    user_rules = db.query(models.UserSavingRule).filter(
        models.UserSavingRule.PLAYER_ID == player_id
    ).all()
    
    result = []
    for rule in user_rules:
        # 적금 규칙 상세 정보 조회
        detail = db.query(models.SavingRuleDetail).filter(
            models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
        ).first()
        
        if not detail:
            continue
        
        # 적금 규칙 유형 조회
        rule_type = db.query(models.SavingRuleType).filter(
            models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
        ).first()
        
        # 선수 타입 조회
        player_type = db.query(models.PlayerType).filter(
            models.PlayerType.PLAYER_TYPE_ID == rule.PLAYER_TYPE_ID
        ).first()
        
        # 적금 규칙 조회
        saving_rule = db.query(models.SavingRuleList).filter(
            models.SavingRuleList.SAVING_RULE_ID == detail.SAVING_RULE_ID
        ).first()
        
        if not saving_rule:
            continue
        
        # 기록 유형 조회
        record_type = db.query(models.RecordType).filter(
            models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
        ).first()
        
        # 계정 정보 조회
        account = db.query(models.Account).filter(
            models.Account.ACCOUNT_ID == rule.ACCOUNT_ID
        ).first()
        
        # 결과 구성
        result.append({
            "USER_SAVING_RULED_ID": rule.USER_SAVING_RULED_ID,
            "ACCOUNT_ID": rule.ACCOUNT_ID,
            "ACCOUNT_NUM": account.ACCOUNT_NUM if account else None,
            "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
            "SAVING_RULE_TYPE_NAME": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
            "SAVING_RULE_DETAIL_ID": rule.SAVING_RULE_DETAIL_ID,
            "PLAYER_TYPE_ID": rule.PLAYER_TYPE_ID,
            "PLAYER_TYPE_NAME": player_type.PLAYER_TYPE_NAME if player_type else None,
            "USER_SAVING_RULED_AMOUNT": rule.USER_SAVING_RULED_AMOUNT,
            "PLAYER_ID": rule.PLAYER_ID,
            "PLAYER_NAME": player.PLAYER_NAME,
            "RECORD_TYPE_ID": saving_rule.RECORD_TYPE_ID if saving_rule else None,
            "RECORD_NAME": record_type.RECORD_NAME if record_type else None
        })
    
    return result

def get_player_daily_savings(db: Session, player_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """선수의 일일 적립 내역 조회"""
    player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
    if not player:
        return []
    
    # 기본 날짜 범위 설정
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # 선수의 규칙들 조회
    user_rules = db.query(models.UserSavingRule).filter(
        models.UserSavingRule.PLAYER_ID == player_id
    ).all()
    
    rule_detail_ids = [rule.SAVING_RULE_DETAIL_ID for rule in user_rules]
    
    # 날짜 범위의 일일 적금 내역 중 선수의 규칙에 해당하는 것들만 조회
    daily_savings = db.query(models.DailySaving).filter(
        models.DailySaving.SAVING_RULED_DETAIL_ID.in_(rule_detail_ids),
        models.DailySaving.DATE >= start_date,
        models.DailySaving.DATE <= end_date
    ).order_by(models.DailySaving.DATE.desc()).all()
    
    result = []
    for saving in daily_savings:
        # 계정 정보 조회
        account = db.query(models.Account).filter(
            models.Account.ACCOUNT_ID == saving.ACCOUNT_ID
        ).first()
        
        # 적금 규칙 상세 정보 조회
        detail = db.query(models.SavingRuleDetail).filter(
            models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
        ).first()
        
        if not detail:
            continue
        
        # 적금 규칙 유형 조회
        rule_type = db.query(models.SavingRuleType).filter(
            models.SavingRuleType.SAVING_RULE_TYPE_ID == saving.SAVING_RULED_TYPE_ID
        ).first()
        
        # 적금 규칙 조회
        saving_rule = db.query(models.SavingRuleList).filter(
            models.SavingRuleList.SAVING_RULE_ID == detail.SAVING_RULE_ID
        ).first()
        
        if not saving_rule:
            continue
        
        # 기록 유형 조회
        record_type = db.query(models.RecordType).filter(
            models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
        ).first()
        
        # 결과 구성
        result.append({
            "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
            "ACCOUNT_ID": saving.ACCOUNT_ID,
            "ACCOUNT_NUM": account.ACCOUNT_NUM if account else None,
            "DATE": saving.DATE,
            "SAVING_RULED_DETAIL_ID": saving.SAVING_RULED_DETAIL_ID,
            "SAVING_RULED_TYPE_ID": saving.SAVING_RULED_TYPE_ID,
            "SAVING_RULE_TYPE_NAME": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
            "COUNT": saving.COUNT,
            "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
            "RECORD_TYPE_ID": saving_rule.RECORD_TYPE_ID if saving_rule else None,
            "RECORD_NAME": record_type.RECORD_NAME if record_type else None,
            "PLAYER_ID": player_id,
            "PLAYER_NAME": player.PLAYER_NAME
        })
    
    return result

def get_player_saving_stats(db: Session, player_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """선수의 적립 통계 조회"""
    # 선수의 일일 적립 내역 조회
    daily_savings = get_player_daily_savings(db, player_id, start_date, end_date)
    
    if not daily_savings:
        return {
            "player_id": player_id,
            "total_saving": 0,
            "account_count": 0,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "daily_trend": {},
            "account_stats": {},
            "record_type_stats": {}
        }
    
    # 계정별 통계
    account_stats = {}
    # 기록 유형별 통계
    record_type_stats = {}
    # 일별 추이
    daily_trend = {}
    
    # 데이터 집계
    for saving in daily_savings:
        # 계정별 통계
        account_id = saving["ACCOUNT_ID"]
        account_num = saving["ACCOUNT_NUM"]
        if account_id not in account_stats:
            account_stats[account_id] = {
                "account_num": account_num,
                "total": 0
            }
        account_stats[account_id]["total"] += saving["DAILY_SAVING_AMOUNT"]
        
        # 기록 유형별 통계
        record_name = saving["RECORD_NAME"]
        if record_name not in record_type_stats:
            record_type_stats[record_name] = 0
        record_type_stats[record_name] += saving["DAILY_SAVING_AMOUNT"]
        
        # 일별 추이
        date_str = saving["DATE"].isoformat()
        if date_str not in daily_trend:
            daily_trend[date_str] = 0
        daily_trend[date_str] += saving["DAILY_SAVING_AMOUNT"]
    
    # 총 적립액 및 계정 수
    total_saving = sum(stat["total"] for stat in account_stats.values())
    account_count = len(account_stats)
    
    # 결과 구성
    result = {
        "player_id": player_id,
        "player_name": daily_savings[0]["PLAYER_NAME"] if daily_savings else None,
        "total_saving": total_saving,
        "account_count": account_count,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "daily_trend": daily_trend,
        "account_stats": account_stats,
        "record_type_stats": record_type_stats
    }
    
    return result