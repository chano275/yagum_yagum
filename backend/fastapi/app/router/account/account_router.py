from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
import logging
import os

from database import get_db
import models
from router.account import account_schema, account_crud
from router.user.user_router import get_current_user
from router.player import player_schema

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 현재 로그인한 사용자의 계정 가져오기 헬퍼 함수
async def get_user_account(db: Session, current_user: models.User):
    """로그인한 사용자의 첫 번째 계정을 반환합니다."""
    accounts = db.query(models.Account).filter(models.Account.USER_ID == current_user.USER_ID).all()
    
    if not accounts:
        logger.warning(f"사용자 ID {current_user.USER_ID}에 연결된 계정이 없습니다")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연결된 계정이 없습니다"
        )
    
    return accounts[0]

@router.post("/create", response_model=account_schema.AccountCreateResponse)
async def create_account(
    request: account_schema.AccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """모든 정보를 한 번에 전송하여 적금 가입"""
    try:
        logger.info(f"적금 가입 요청: 사용자 ID {current_user.USER_ID}")
        
        # 1. 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == request.TEAM_ID).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선택한 팀이 존재하지 않습니다"
            )
        
        # 1.1 최애 선수 ID가 제공된 경우 유효성 검사
        if request.FAVORITE_PLAYER_ID:
            player = db.query(models.Player).filter(models.Player.PLAYER_ID == request.FAVORITE_PLAYER_ID).first()
            if not player:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 선수입니다"
                )
            # 선수가 선택된 팀에 소속되어 있는지 확인
            if player.TEAM_ID != request.TEAM_ID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="선택한 선수는 선택한 팀에 소속되어 있지 않습니다"
                )
        
        # 2. 목표 설정 유효성 검사
        if request.SAVING_GOAL <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="저축 목표액은 0보다 커야 합니다"
            )
        
        if request.DAILY_LIMIT <= 0 or request.MONTH_LIMIT <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="일일 한도와 월 한도는 0보다 커야 합니다"
            )
        
        if request.MONTH_LIMIT < request.DAILY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월 한도는 일일 한도보다 커야 합니다"
            )
        
        # 3. 규칙 유효성 검사
        if not request.saving_rules or len(request.saving_rules) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적어도 하나의 적금 규칙을 설정해야 합니다"
            )
        
        for rule in request.saving_rules:
            # 규칙 상세 존재 여부 확인
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
            ).first()
            
            if not rule_detail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"규칙 상세 ID {rule.SAVING_RULE_DETAIL_ID}가 존재하지 않습니다"
                )
            
            # 규칙 타입 정보 가져오기
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule_detail.SAVING_RULE_TYPE_ID
            ).first()
            
            if not rule_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"규칙 타입을 찾을 수 없습니다: {rule_detail.SAVING_RULE_TYPE_ID}"
                )
            
            # 적립 금액 확인
            if rule.SAVING_RULED_AMOUNT <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="적립 금액은 0보다 커야 합니다"
                )
        
        # 4. 출금 계좌 유효성 확인
        if not request.SOURCE_ACCOUNT or len(request.SOURCE_ACCOUNT.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="출금 계좌번호를 입력해주세요"
            )
        
        # 5. 금융 API를 통해 계좌번호 발급
        from router.user.user_ssafy_api_utils import create_demand_deposit_account
        SAVING_CODE = os.getenv("SAVING_CODE")
        account_num = await create_demand_deposit_account(current_user.USER_KEY, SAVING_CODE)
        
        # 6. 계좌 생성
        db_account = models.Account(
            USER_ID=current_user.USER_ID,
            TEAM_ID=request.TEAM_ID,
            FAVORITE_PLAYER_ID=request.FAVORITE_PLAYER_ID,
            ACCOUNT_NUM=account_num,
            INTEREST_RATE=2.5,  # 기본 이자율
            SAVING_GOAL=request.SAVING_GOAL,
            DAILY_LIMIT=request.DAILY_LIMIT,
            MONTH_LIMIT=request.MONTH_LIMIT,
            SOURCE_ACCOUNT=request.SOURCE_ACCOUNT,
            TOTAL_AMOUNT=0,
            created_at=datetime.now()
        )
        db.add(db_account)
        db.flush()  # 임시 커밋하여 ID 생성
        
        # 7. 적금 규칙 추가
        saved_rules = []
        for rule in request.saving_rules:
            # 규칙 상세 정보 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
            ).first()
            
            # 규칙 타입 정보 가져오기
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule_detail.SAVING_RULE_TYPE_ID
            ).first()
            
            # PLAYER_ID 설정 (투수/타자 규칙인 경우 favorite_player_id 사용)
            player_id = None
            player_type_id = None
            
            if rule_type.SAVING_RULE_TYPE_ID in [2, 3]:  # 투수 또는 타자 규칙
                if request.FAVORITE_PLAYER_ID:
                    player = db.query(models.Player).filter(models.Player.PLAYER_ID == request.FAVORITE_PLAYER_ID).first()
                    if player and player.PLAYER_TYPE_ID == rule_detail.PLAYER_TYPE_ID:
                        player_id = request.FAVORITE_PLAYER_ID
                        player_type_id = player.PLAYER_TYPE_ID
                    else:
                        logger.warning(f"최애 선수 타입이 규칙 타입과 일치하지 않습니다: 선수 타입 {player.PLAYER_TYPE_ID if player else 'Unknown'}, 규칙 타입 {rule_detail.PLAYER_TYPE_ID}")
                        continue
            else:
                # 기본 규칙 또는 상대팀 규칙인 경우 null 사용
                player_id = None
                player_type_id = rule_detail.PLAYER_TYPE_ID
            
            # 적금 규칙 조회
            saving_rule = db.query(models.SavingRuleList).filter(
                models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
            ).first()
            
            if not saving_rule:
                logger.warning(f"적금 규칙 ID {rule_detail.SAVING_RULE_ID}를 찾을 수 없습니다.")
                continue
            
            # 사용자 적금 규칙 생성
            db_user_rule = models.UserSavingRule(
                ACCOUNT_ID=db_account.ACCOUNT_ID,
                SAVING_RULE_TYPE_ID=rule_detail.SAVING_RULE_TYPE_ID,
                SAVING_RULE_DETAIL_ID=rule.SAVING_RULE_DETAIL_ID,
                PLAYER_TYPE_ID=player_type_id,
                USER_SAVING_RULED_AMOUNT=rule.SAVING_RULED_AMOUNT,
                PLAYER_ID=player_id
            )
            db.add(db_user_rule)
            db.flush()
            
            # 기록 타입 정보 가져오기
            record_type = db.query(models.RecordType).filter(
                models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
            ).first()
            
            # 저장된 규칙 정보 구성
            rule_info = {
                "USER_SAVING_RULED_ID": db_user_rule.USER_SAVING_RULED_ID,
                "rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "record_name": record_type.RECORD_NAME if record_type else None,
                "amount": rule.SAVING_RULED_AMOUNT
            }
            
            # 선수 정보 추가
            if player_id:
                player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
                if player:
                    rule_info["player_name"] = player.PLAYER_NAME
            
            saved_rules.append(rule_info)
        
        # 최종 커밋
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"적금 계좌 생성 완료: 계정 ID {db_account.ACCOUNT_ID}, 계좌번호 {account_num}")
        
        # 응답 데이터 구성
        response = {
            "ACCOUNT_ID": db_account.ACCOUNT_ID,
            "ACCOUNT_NUM": db_account.ACCOUNT_NUM,
            "TEAM_ID": db_account.TEAM_ID,
            "FAVORITE_PLAYER_ID": db_account.FAVORITE_PLAYER_ID,
            "SAVING_GOAL": db_account.SAVING_GOAL,
            "DAILY_LIMIT": db_account.DAILY_LIMIT,
            "MONTH_LIMIT": db_account.MONTH_LIMIT,
            "SOURCE_ACCOUNT": db_account.SOURCE_ACCOUNT,
            "TOTAL_AMOUNT": db_account.TOTAL_AMOUNT,
            "INTEREST_RATE": db_account.INTEREST_RATE,
            "created_at": db_account.created_at.isoformat(),
            "saving_rules": saved_rules
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 가입 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 가입 중 오류 발생: {str(e)}"
        )

@router.get("/transfers_log", response_model=List[account_schema.DailyTransferResponse])
async def get_my_transfers(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"로그인 사용자의 송금 내역 조회: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        logger.info(f"사용자의 계정으로 송금 내역 조회: 계정 ID {account_id}")
        
        # 송금 내역 조회
        transfers = account_crud.get_account_transfers(db, account_id, start_date, end_date)
        
        return transfers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"송금 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"송금 내역 조회 중 오류 발생: {str(e)}"
        )

@router.get("/daily-savings-detail", response_model=List[account_schema.DailySavingDetailResponse])
async def get_my_daily_savings_detail(
    date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    로그인한 사용자의 특정 날짜(기본값: 어제) 적금 상세 내역을 조회합니다.
    
    Args:
        date (date, optional): 조회할 날짜. 기본값은 어제.
        
    Returns:
        List[DailySavingDetailResponse]: 적금 상세 내역 목록 (규칙 정보 포함)
    """
    try:
        logger.info(f"로그인 사용자의 적금 상세 내역 조회: 사용자 ID {current_user.USER_ID}")
        
        # 날짜 설정 (기본값: 어제)
        if date is None:
            date = datetime.now().date() - timedelta(days=1)
            
        logger.info(f"조회 날짜: {date}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        logger.info(f"사용자의 계정으로 상세 내역 조회: 계정 ID {account_id}")
        
        # 해당 날짜의 적금 내역 조회
        daily_savings = db.query(models.DailySaving).filter(
            models.DailySaving.ACCOUNT_ID == account_id,
            models.DailySaving.DATE == date
        ).all()
        
        # 결과 목록
        result = []
        
        for saving in daily_savings:
            # 적금 규칙 타입 조회
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == saving.SAVING_RULED_TYPE_ID
            ).first()
            
            # 적금 규칙 상세 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
            ).first()
            
            # 규칙 설명 가져오기
            rule_description = rule_detail.RULE_DESCRIPTION if rule_detail else "알 수 없는 규칙"
            
            # 적금 규칙 조회
            saving_rule = None
            record_type = None
            if rule_detail:
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if saving_rule:
                    # 기록 타입 조회
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                    ).first()
            
            # 사용자 적금 규칙 조회 (적립 금액 단위 확인용)
            user_rule = db.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account_id,
                models.UserSavingRule.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
            ).first()
            
            # 선수 정보 (해당되는 경우)
            player = None
            if user_rule and user_rule.PLAYER_ID:
                player = db.query(models.Player).filter(
                    models.Player.PLAYER_ID == user_rule.PLAYER_ID
                ).first()
                
                # 선수 이름을 규칙 설명에 포함
                if player and "이(가)" in rule_description:
                    rule_description = rule_description.replace("이(가)", f"{player.PLAYER_NAME}이(가)")
            
            # 상세 정보 구성
            detail = {
                "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
                "ACCOUNT_ID": saving.ACCOUNT_ID,
                "DATE": saving.DATE,
                "SAVING_RULED_DETAIL_ID": saving.SAVING_RULED_DETAIL_ID,
                "SAVING_RULED_TYPE_ID": saving.SAVING_RULED_TYPE_ID,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                "rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "rule_description": rule_description,
                "record_name": record_type.RECORD_NAME if record_type else None,
                "player_name": player.PLAYER_NAME if player else None,
                "unit_amount": user_rule.USER_SAVING_RULED_AMOUNT if user_rule else None
            }
            
            result.append(detail)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 상세 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 상세 내역 조회 중 오류 발생: {str(e)}"
        )

@router.get("/detail", response_model=account_schema.AccountDetailResponse)
async def read_account_detail(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 상세 정보 조회 요청: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 이자율 정보 계산
        from router.mission import mission_crud  # 순환 참조 방지를 위해 여기서 import
        interest_details = mission_crud.calculate_account_interest_details(db, account_id)
        
        # 사용자의 미션 조회 (진행 중 또는 완료된 미션)
        used_missions = db.query(models.UsedMission).filter(
            models.UsedMission.ACCOUNT_ID == account_id
        ).all()
        
        # 활성 미션 정보 구성
        active_missions = []
        for used_mission in used_missions:
            mission = used_mission.mission
            active_missions.append({
                "MISSION_ID": mission.MISSION_ID,
                "MISSION_NAME": mission.MISSION_NAME,
                "MISSION_MAX_COUNT": mission.MISSION_MAX_COUNT,
                "MISSION_RATE": mission.MISSION_RATE,
                "COUNT": used_mission.COUNT,
                "CURRENT_COUNT": used_mission.COUNT,
                "MAX_COUNT": used_mission.MAX_COUNT
            })
        
        # 계정 상세 정보 구성
        account_detail = {
            **account.__dict__,  # 기존 계정 정보 포함
            "base_interest_rate": interest_details['base_interest_rate'],  # 기본 이자율
            "mission_interest_rate": interest_details['mission_interest_rate'],  # 미션 이자율
            "total_interest_rate": interest_details['total_interest_rate'],  # 총 이자율
            "active_missions": active_missions,  # 활성 미션 목록
        }
        
        return account_detail
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 상세 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 상세 정보 조회 중 오류 발생: {str(e)}"
        )

@router.get("/interest-details", response_model=account_schema.AccountInterestDetailResponse)
async def get_account_interest_details(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 이자율 상세 정보 조회 요청: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 이자율 정보 계산
        from router.mission import mission_crud  # 순환 참조 방지를 위해 여기서 import
        interest_details = mission_crud.calculate_account_interest_details(db, account_id)
        
        # 필수 필드가 없어서 발생하는 에러 해결을 위해 필드 추가
        if 'total_mission_rate' not in interest_details:
            # total_mission_rate는 mission_interest_rate와 동일하게 처리
            interest_details['total_mission_rate'] = interest_details.get('mission_interest_rate', 0)
        
        if 'mission_details' not in interest_details:
            # 미션 상세 정보 조회
            used_missions = db.query(models.UsedMission).filter(
                models.UsedMission.ACCOUNT_ID == account_id
            ).all()
            
            mission_details = []
            for used_mission in used_missions:
                mission = used_mission.mission
                mission_detail = {
                    "mission_id": mission.MISSION_ID,
                    "mission_name": mission.MISSION_NAME,
                    "mission_rate": mission.MISSION_RATE,
                    "current_count": used_mission.COUNT,
                    "max_count": used_mission.MAX_COUNT,
                    "is_completed": used_mission.COUNT >= used_mission.MAX_COUNT
                }
                mission_details.append(mission_detail)
            
            interest_details['mission_details'] = mission_details
        
        return interest_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 이자율 상세 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 이자율 상세 정보 조회 중 오류 발생: {str(e)}"
        )

@router.put("/setup", response_model=account_schema.AccountResponse)
async def setup_account(
    account_setup: account_schema.AccountSetup,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계좌 설정 요청: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 필수 필드 확인
        if not account_setup.TEAM_ID or not account_setup.SAVING_GOAL or not account_setup.DAILY_LIMIT or not account_setup.MONTH_LIMIT or not account_setup.SOURCE_ACCOUNT:
            logger.warning(f"필수 필드 누락: {account_setup}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="모든 필수 필드를 입력해야 합니다"
            )
            
        # 계정 설정 업데이트
        account.TEAM_ID = account_setup.TEAM_ID
        account.SAVING_GOAL = account_setup.SAVING_GOAL
        account.DAILY_LIMIT = account_setup.DAILY_LIMIT
        account.MONTH_LIMIT = account_setup.MONTH_LIMIT
        account.SOURCE_ACCOUNT = account_setup.SOURCE_ACCOUNT
        
        db.commit()
        db.refresh(account)
        
        logger.info(f"계좌 설정 완료: 계정 ID {account_id}")
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계좌 설정 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌 설정 중 오류 발생: {str(e)}"
        )

@router.get("/daily-balances", response_model=List[dict])
async def get_daily_balances(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 일일 잔액 내역 조회: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 일일 잔액 내역 조회
        balances = account_crud.get_account_daily_balances(db, account_id, start_date, end_date)
        
        # ORM 모델을 딕셔너리로 변환
        result = []
        for balance in balances:
            result.append({
                "DATE": balance.DATE,
                "CLOSING_BALANCE": balance.CLOSING_BALANCE,
                "DAILY_INTEREST": balance.DAILY_INTEREST
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일일 잔액 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 잔액 내역 조회 중 오류 발생: {str(e)}"
        )

@router.get("/saving-rules", response_model=List[dict])
async def get_saving_rules(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 적금 규칙 설정 조회: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 적금 규칙 설정 조회
        rules = account_crud.get_account_saving_rules(db, account_id)
        
        # ORM 모델을 딕셔너리로 변환하면서 관련 정보 포함
        result = []
        for rule in rules:
            # 적금 규칙 타입 이름 조회
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
            ).first()
            rule_type_name = rule_type.SAVING_RULE_TYPE_NAME if rule_type else None
            
            # 적금 규칙 상세 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
            ).first()
            
            # 기록 유형 이름 조회
            record_name = None
            if rule_detail:
                # 적금 규칙 조회
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if saving_rule:
                    # 기록 유형 이름 조회
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                    ).first()
                    record_name = record_type.RECORD_NAME if record_type else None
            
            # 선수 타입 이름 조회
            player_type = None
            if rule.PLAYER_TYPE_ID:
                player_type_obj = db.query(models.PlayerType).filter(
                    models.PlayerType.PLAYER_TYPE_ID == rule.PLAYER_TYPE_ID
                ).first()
                player_type = player_type_obj.PLAYER_TYPE_NAME if player_type_obj else None
            
            # 선수 이름 조회
            player_name = None
            if rule.PLAYER_ID:
                player = db.query(models.Player).filter(
                    models.Player.PLAYER_ID == rule.PLAYER_ID
                ).first()
                player_name = player.PLAYER_NAME if player else None
            
            # 결과 딕셔너리 구성
            rule_dict = {
                "USER_SAVING_RULED_ID": rule.USER_SAVING_RULED_ID,
                "ACCOUNT_ID": rule.ACCOUNT_ID,
                "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
                "SAVING_RULE_TYPE_NAME": rule_type_name,
                "SAVING_RULE_DETAIL_ID": rule.SAVING_RULE_DETAIL_ID,
                "PLAYER_TYPE_ID": rule.PLAYER_TYPE_ID,
                "PLAYER_TYPE_NAME": player_type,
                "USER_SAVING_RULED_AMOUNT": rule.USER_SAVING_RULED_AMOUNT,
                "PLAYER_ID": rule.PLAYER_ID,
                "PLAYER_NAME": player_name,
                "RECORD_NAME": record_name
            }
            
            result.append(rule_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 설정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 설정 조회 중 오류 발생: {str(e)}"
        )
    
@router.get("/favorite-player", response_model=player_schema.PlayerResponse)
async def get_favorite_player(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        
        # 최애 선수 확인
        if not account.FAVORITE_PLAYER_ID:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 최애 선수가 없습니다"
            )
        
        # 선수 정보 조회
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == account.FAVORITE_PLAYER_ID).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선수 정보를 찾을 수 없습니다"
            )
        
        return player
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최애 선수 조회 중 오류 발생: {str(e)}"
        )
    
@router.put("/favorite-player", response_model=account_schema.AccountResponse)
async def update_favorite_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
        
        # 선수가 계정의 팀에 소속되어 있는지 확인
        if player.TEAM_ID != account.TEAM_ID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="선택한 선수는 계정의 팀에 소속되어 있지 않습니다"
            )
        
        # 최애 선수 업데이트
        account.FAVORITE_PLAYER_ID = player_id
        db.commit()
        db.refresh(account)
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최애 선수 업데이트 중 오류 발생: {str(e)}"
        )
    
# 계정의 모든 송금 메시지 조회
@router.get("/transactions", response_model=List[account_schema.TransactionMessageResponse])
async def get_account_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 트랜잭션 메시지 조회: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 트랜잭션 메시지 조회
        transactions = account_crud.get_transaction_messages_by_account(db, account_id, skip, limit)
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"트랜잭션 메시지 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"트랜잭션 메시지 조회 중 오류 발생: {str(e)}"
        )

# 특정 기간의 송금 메시지 조회
@router.get("/transactions/range", response_model=List[account_schema.TransactionMessageResponse])
async def get_account_transactions_by_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"기간별 트랜잭션 메시지 조회: 사용자 ID {current_user.USER_ID}, 기간 {start_date} ~ {end_date}")
        
        # 날짜 유효성 검사
        if end_date < start_date:
            logger.warning(f"유효하지 않은 날짜 범위: {start_date} ~ {end_date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="종료 날짜는 시작 날짜보다 이후여야 합니다"
            )
            
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 기간별 트랜잭션 메시지 조회
        transactions = account_crud.get_transaction_messages_by_date_range(db, account_id, start_date, end_date)
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"기간별 트랜잭션 메시지 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기간별 트랜잭션 메시지 조회 중 오류 발생: {str(e)}"
        )
        
# 송금 메시지 받는 API
@router.post("/transactions", response_model=List[account_schema.TransactionMessageResponse])
async def create_transaction_messages_endpoint(
    transaction_data: List[Dict],  # 송금 메시지 리스트로 받음
    db: Session = Depends(get_db)
):
    """
    여러 트랜잭션 메시지를 한 번에 생성합니다.

    - **transaction_data**: 트랜잭션 메시지 정보 리스트
      - `account_id`: 계정 ID (필수)
      - `date`: 트랜잭션 날짜 (필수)
      - `text`: 트랜잭션 메시지 (필수)
    """
    created_transactions = []
    
    try:
        for transaction in transaction_data:
            # 필수 입력값 확인
            account_id = transaction.get("account_id")
            date = transaction.get("date")
            text = transaction.get("text")
            
            if not account_id or not date or not text:
                logger.warning("필수 입력값 누락")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="account_id, date, text는 모두 필수 입력값입니다"
                )
            
            # 계정 존재 여부 확인
            account = account_crud.get_account_by_id(db, int(account_id))
            if not account:
                logger.warning(f"계정을 찾을 수 없음: {account_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"계정을 찾을 수 없습니다: {account_id}"
                )
            
            # TransactionMessageCreate 객체 생성
            transaction_schema = account_schema.TransactionMessageCreate(
                ACCOUNT_ID=int(account_id),
                TRANSACTION_DATE=date,
                MESSAGE=text
            )
            
            # 트랜잭션 메시지 생성
            created_transaction = account_crud.create_transaction_message(db, transaction_schema)
            created_transactions.append(created_transaction)
        
        return created_transactions
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"입력값 형식 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"입력값 형식 오류: {str(e)}"
        )
    except Exception as e:
        logger.error(f"트랜잭션 메시지 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"트랜잭션 메시지 생성 중 오류 발생: {str(e)}"
        )

@router.get("/savings", response_model=List[dict])
async def get_savings(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 적금 내역 조회: 사용자 ID {current_user.USER_ID}")
        
        # 사용자의 계정 조회
        account = await get_user_account(db, current_user)
        account_id = account.ACCOUNT_ID
        
        # 적금 내역 조회
        savings = account_crud.get_account_savings(db, account_id, start_date, end_date)
        
        # ORM 모델을 딕셔너리로 변환하면서 필요한 정보만 포함
        result = []
        for saving in savings:
            # 적금 규칙 유형 이름 조회
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == saving.SAVING_RULED_TYPE_ID
            ).first()
            rule_type_name = rule_type.SAVING_RULE_TYPE_NAME if rule_type else None
            
            # 기록 유형 이름 조회
            record_type_name = None
            # 적금 규칙 상세 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
            ).first()
            
            if rule_detail:
                # 해당 적금 규칙 조회
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if saving_rule:
                    # 기록 유형 이름 조회
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                    ).first()
                    record_type_name = record_type.RECORD_NAME if record_type else None
            
            # 선수 이름 (해당되는 경우)
            player_name = None
            if rule_type and rule_type.SAVING_RULE_TYPE_NAME not in ["기본 규칙", "상대팀"]:
                # 사용자 적금 규칙 조회
                user_rule = db.query(models.UserSavingRule).filter(
                    models.UserSavingRule.ACCOUNT_ID == account_id,
                    models.UserSavingRule.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
                ).first()
                
                if user_rule and user_rule.PLAYER_ID:
                    player = db.query(models.Player).filter(
                        models.Player.PLAYER_ID == user_rule.PLAYER_ID
                    ).first()
                    
                    if player:
                        player_name = player.PLAYER_NAME
            
            # 결과 딕셔너리 구성 - 간소화된 버전
            saving_dict = {
                "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
                "DATE": saving.DATE,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                "RULE_TYPE_NAME": rule_type_name,
                "RECORD_TYPE_NAME": record_type_name,
                "PLAYER_NAME": player_name
            }
            
            result.append(saving_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 내역 조회 중 오류 발생: {str(e)}"
        )