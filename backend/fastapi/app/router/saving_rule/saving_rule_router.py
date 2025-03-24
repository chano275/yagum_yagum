from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from database import get_db
import models
from router.saving_rule import saving_rule_schema, saving_rule_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 모든 적금 규칙 타입 조회
@router.get("/types", response_model=List[saving_rule_schema.SavingRuleTypeResponse])
async def read_saving_rule_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"적금 규칙 타입 목록 조회: skip={skip}, limit={limit}")
        rule_types = saving_rule_crud.get_all_saving_rule_types(db, skip, limit)
        return rule_types
    except Exception as e:
        logger.error(f"적금 규칙 타입 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 타입 목록 조회 중 오류 발생: {str(e)}"
        )

# 모든 기록 타입 조회
@router.get("/record-types", response_model=List[saving_rule_schema.RecordTypeResponse])
async def read_record_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"기록 타입 목록 조회: skip={skip}, limit={limit}")
        record_types = saving_rule_crud.get_all_record_types(db, skip, limit)
        return record_types
    except Exception as e:
        logger.error(f"기록 타입 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 타입 목록 조회 중 오류 발생: {str(e)}"
        )

# 모든 적금 규칙 조회
@router.get("/rules", response_model=List[saving_rule_schema.SavingRuleListDetailResponse])
async def read_saving_rules(
    saving_rule_type_id: Optional[int] = None,
    record_type_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"적금 규칙 목록 조회: 타입={saving_rule_type_id}, 기록 타입={record_type_id}")
        
        # 필터에 따라 조회
        if saving_rule_type_id:
            rules = saving_rule_crud.get_saving_rules_by_type(db, saving_rule_type_id, skip, limit)
        elif record_type_id:
            rules = saving_rule_crud.get_saving_rules_by_record_type(db, record_type_id, skip, limit)
        else:
            rules = saving_rule_crud.get_all_saving_rules(db, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for rule in rules:
            # 적금 규칙 타입 정보 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
            
            # 기록 타입 정보 조회
            record_type = saving_rule_crud.get_record_type_by_id(db, rule.RECORD_TYPE_ID)
            
            # 결과 구성
            result.append({
                "SAVING_RULE_ID": rule.SAVING_RULE_ID,
                "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
                "RECORD_TYPE_ID": rule.RECORD_TYPE_ID,
                "saving_rule_type": rule_type,
                "record_type": record_type
            })
        
        return result
    except Exception as e:
        logger.error(f"적금 규칙 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 목록 조회 중 오류 발생: {str(e)}"
        )

# # 특정 적금 규칙 조회
# @router.get("/rules/{saving_rule_id}", response_model=saving_rule_schema.SavingRuleListDetailResponse)
# async def read_saving_rule(
#     saving_rule_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         logger.info(f"적금 규칙 조회: ID {saving_rule_id}")
        
#         # 적금 규칙 조회
#         rule = saving_rule_crud.get_saving_rule_by_id(db, saving_rule_id)
#         if not rule:
#             logger.warning(f"존재하지 않는 적금 규칙: {saving_rule_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙입니다"
#             )
            
#         # 적금 규칙 타입 정보 조회
#         rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
        
#         # 기록 타입 정보 조회
#         record_type = saving_rule_crud.get_record_type_by_id(db, rule.RECORD_TYPE_ID)
        
#         # 결과 구성
#         result = {
#             "SAVING_RULE_ID": rule.SAVING_RULE_ID,
#             "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
#             "RECORD_TYPE_ID": rule.RECORD_TYPE_ID,
#             "saving_rule_type": rule_type,
#             "record_type": record_type
#         }
        
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 조회 중 오류 발생: {str(e)}"
#         )

# 계정별 사용자 적금 규칙 조회
@router.get("/user-rules/account/{account_id}", response_model=List[saving_rule_schema.UserSavingRuleDetailResponse])
async def read_user_saving_rules_by_account(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정별 사용자 적금 규칙 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 권한 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"존재하지 않는 계정: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 계정입니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 적금 규칙을 조회할 권한이 없습니다"
            )
            
        # 사용자 적금 규칙 조회
        user_rules = saving_rule_crud.get_user_saving_rules_by_account(db, account_id, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for rule in user_rules:
            # 적금 규칙 타입 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
            
            # 선수 타입 조회
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == rule.PLAYER_TYPE_ID).first()
            
            # 선수 조회
            player = db.query(models.Player).filter(models.Player.PLAYER_ID == rule.PLAYER_ID).first()
            
            # 적금 규칙 상세 조회
            rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, rule.SAVING_RULE_DETAIL_ID)
            
            # 적금 규칙 조회
            if rule_detail:
                saving_rule = saving_rule_crud.get_saving_rule_by_id(db, rule_detail.SAVING_RULE_ID)
            else:
                saving_rule = None
            
            # 기록 타입 조회
            if saving_rule:
                record_type = saving_rule_crud.get_record_type_by_id(db, saving_rule.RECORD_TYPE_ID)
                record_name = record_type.RECORD_NAME if record_type else None
            else:
                record_name = None
            
            # 결과 구성
            result.append({
                "USER_SAVING_RULED_ID": rule.USER_SAVING_RULED_ID,
                "ACCOUNT_ID": rule.ACCOUNT_ID,
                "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
                "SAVING_RULE_DETAIL_ID": rule.SAVING_RULE_DETAIL_ID,
                "PLAYER_TYPE_ID": rule.PLAYER_TYPE_ID,
                "USER_SAVING_RULED_AMOUNT": rule.USER_SAVING_RULED_AMOUNT,
                "PLAYER_ID": rule.PLAYER_ID,
                "account_num": account.ACCOUNT_NUM,
                "saving_rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "player_type_name": player_type.PLAYER_TYPE_NAME if player_type else None,
                "player_name": player.PLAYER_NAME if player else None,
                "record_name": record_name
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정별 사용자 적금 규칙 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정별 사용자 적금 규칙 조회 중 오류 발생: {str(e)}"
        )

# # 사용자 적금 규칙 생성
# @router.post("/user-rules", response_model=saving_rule_schema.UserSavingRuleResponse)
# async def create_user_saving_rule(
#     user_rule: saving_rule_schema.UserSavingRuleCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"사용자 적금 규칙 생성 시도: 계정 ID {user_rule.ACCOUNT_ID}, 규칙 상세 ID {user_rule.SAVING_RULE_DETAIL_ID}")
        
#         # 계정 존재 여부 및 권한 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == user_rule.ACCOUNT_ID).first()
#         if not account:
#             logger.warning(f"존재하지 않는 계정: {user_rule.ACCOUNT_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 계정입니다"
#             )
            
#         if account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="이 계정에 적금 규칙을 생성할 권한이 없습니다"
#             )
            
#         # 적금 규칙 타입 존재 여부 확인
#         rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, user_rule.SAVING_RULE_TYPE_ID)
#         if not rule_type:
#             logger.warning(f"존재하지 않는 적금 규칙 타입: {user_rule.SAVING_RULE_TYPE_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 타입입니다"
#             )
            
#         # 적금 규칙 상세 존재 여부 확인
#         rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, user_rule.SAVING_RULE_DETAIL_ID)
#         if not rule_detail:
#             logger.warning(f"존재하지 않는 적금 규칙 상세: {user_rule.SAVING_RULE_DETAIL_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 상세입니다"
#             )
            
#         # 선수 관련 필드 체크 (팀 규칙이 아닌 경우에만)
#         is_team_rule = rule_type.SAVING_RULE_TYPE_NAME in ["기본 규칙", "상대팀"]
        
#         if not is_team_rule:
#             # 선수 타입 존재 여부 확인
#             if user_rule.PLAYER_TYPE_ID is None:
#                 logger.warning("선수 타입이 필요합니다")
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="선수 규칙에는 선수 타입이 필요합니다"
#                 )
                
#             player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == user_rule.PLAYER_TYPE_ID).first()
#             if not player_type:
#                 logger.warning(f"존재하지 않는 선수 타입: {user_rule.PLAYER_TYPE_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 선수 타입입니다"
#                 )
                
#             # 선수 존재 여부 확인
#             if user_rule.PLAYER_ID is None:
#                 logger.warning("선수 ID가 필요합니다")
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="선수 규칙에는 선수 ID가 필요합니다"
#                 )
                
#             player = db.query(models.Player).filter(models.Player.PLAYER_ID == user_rule.PLAYER_ID).first()
#             if not player:
#                 logger.warning(f"존재하지 않는 선수: {user_rule.PLAYER_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 선수입니다"
#                 )
                
#             # 선수와 선수 타입 일치 확인
#             if player.PLAYER_TYPE_ID != user_rule.PLAYER_TYPE_ID:
#                 logger.warning(f"선수 타입 불일치: 선수 {user_rule.PLAYER_ID}의 타입은 {player.PLAYER_TYPE_ID}이지만, 요청된 타입은 {user_rule.PLAYER_TYPE_ID}입니다")
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="선수와 선수 타입이 일치하지 않습니다"
#                 )
            
#         # 금액 유효성 검사
#         if user_rule.USER_SAVING_RULED_AMOUNT <= 0:
#             logger.warning(f"유효하지 않은 적립 금액: {user_rule.USER_SAVING_RULED_AMOUNT}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="적립 금액은 양수여야 합니다"
#             )
            
#         # 사용자 적금 규칙 생성
#         new_user_rule = saving_rule_crud.create_user_saving_rule(db, user_rule)
#         logger.info(f"사용자 적금 규칙 생성 완료: ID {new_user_rule.USER_SAVING_RULED_ID}")
        
#         return new_user_rule
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"사용자 적금 규칙 생성 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 적금 규칙 생성 중 오류 발생: {str(e)}"
#         )

# 간소화된 적금 규칙 생성
@router.post("/user-rules", response_model=saving_rule_schema.UserSavingRuleResponse)
async def create_user_saving_rule_simplified(
    user_rule: saving_rule_schema.UserSavingRuleCreateSimplified,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"간소화된 적금 규칙 생성 시도: 계정 ID {user_rule.ACCOUNT_ID}")
        
        # 계정 존재 여부 및 권한 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == user_rule.ACCOUNT_ID).first()
        if not account:
            logger.warning(f"존재하지 않는 계정: {user_rule.ACCOUNT_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 계정입니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정에 적금 규칙을 생성할 권한이 없습니다"
            )
            
        # 적금 규칙 타입 확인
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, user_rule.SAVING_RULE_TYPE_ID)
        if not rule_type:
            logger.warning(f"존재하지 않는 적금 규칙 타입: {user_rule.SAVING_RULE_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 타입입니다"
            )
            
        # 기록 타입 확인
        record_type = saving_rule_crud.get_record_type_by_id(db, user_rule.RECORD_TYPE_ID)
        if not record_type:
            logger.warning(f"존재하지 않는 기록 타입: {user_rule.RECORD_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 기록 타입입니다"
            )
        
        # 해당 규칙 타입과 기록 타입에 맞는 적금 규칙 찾기
        saving_rule = db.query(models.SavingRuleList).filter(
            models.SavingRuleList.SAVING_RULE_TYPE_ID == user_rule.SAVING_RULE_TYPE_ID,
            models.SavingRuleList.RECORD_TYPE_ID == user_rule.RECORD_TYPE_ID
        ).first()
        
        if not saving_rule:
            logger.warning(f"해당 조합의 적금 규칙이 존재하지 않음: 타입 {user_rule.SAVING_RULE_TYPE_ID}, 기록 {user_rule.RECORD_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 조합의 적금 규칙이 존재하지 않습니다"
            )
        
        # 규칙 타입이 팀 규칙인지 확인
        is_team_rule = rule_type.SAVING_RULE_TYPE_NAME in ["기본 규칙", "상대팀"]
        
        # 선수 규칙인 경우 선수 및 선수 타입 확인
        player_type_id = None
        if not is_team_rule:
            if not user_rule.PLAYER_ID:
                logger.warning("선수 규칙에는 선수 ID가 필요합니다")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="선수 규칙에는 선수 ID가 필요합니다"
                )
            
            player = db.query(models.Player).filter(models.Player.PLAYER_ID == user_rule.PLAYER_ID).first()
            if not player:
                logger.warning(f"존재하지 않는 선수: {user_rule.PLAYER_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 선수입니다"
                )
            
            player_type_id = player.PLAYER_TYPE_ID
        
        # 적금 규칙 상세 조회
        query = db.query(models.SavingRuleDetail).filter(
            models.SavingRuleDetail.SAVING_RULE_ID == saving_rule.SAVING_RULE_ID
        )
        
        if not is_team_rule and player_type_id is not None:
            query = query.filter(models.SavingRuleDetail.PLAYER_TYPE_ID == player_type_id)
        
        rule_detail = query.first()
        
        if not rule_detail:
            logger.warning(f"적합한 적금 규칙 상세를 찾을 수 없음: 규칙 ID {saving_rule.SAVING_RULE_ID}, 선수 타입 ID {player_type_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="적합한 적금 규칙 상세를 찾을 수 없습니다"
            )
        
        # 중복 확인
        existing_query = db.query(models.UserSavingRule).filter(
            models.UserSavingRule.ACCOUNT_ID == user_rule.ACCOUNT_ID,
            models.UserSavingRule.SAVING_RULE_DETAIL_ID == rule_detail.SAVING_RULE_DETAIL_ID
        )
        
        if is_team_rule:
            existing_query = existing_query.filter(models.UserSavingRule.PLAYER_ID.is_(None))
        else:
            existing_query = existing_query.filter(models.UserSavingRule.PLAYER_ID == user_rule.PLAYER_ID)
        
        existing_rule = existing_query.first()
        
        if existing_rule:
            logger.warning(f"이미 등록된 적금 규칙: 계정 ID {user_rule.ACCOUNT_ID}, 규칙 상세 ID {rule_detail.SAVING_RULE_DETAIL_ID}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 적금 규칙입니다"
            )
        
        # 금액 유효성 검사
        if user_rule.USER_SAVING_RULED_AMOUNT <= 0:
            logger.warning(f"유효하지 않은 적립 금액: {user_rule.USER_SAVING_RULED_AMOUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적립 금액은 양수여야 합니다"
            )
        
        # 완성된 사용자 적금 규칙 생성 객체
        complete_user_rule = {
            "ACCOUNT_ID": user_rule.ACCOUNT_ID,
            "SAVING_RULE_TYPE_ID": user_rule.SAVING_RULE_TYPE_ID,
            "SAVING_RULE_DETAIL_ID": rule_detail.SAVING_RULE_DETAIL_ID,
            "USER_SAVING_RULED_AMOUNT": user_rule.USER_SAVING_RULED_AMOUNT,
        }
        
        # 팀 규칙이 아닌 경우에만 선수 관련 정보 추가
        if not is_team_rule:
            complete_user_rule["PLAYER_TYPE_ID"] = player_type_id
            complete_user_rule["PLAYER_ID"] = user_rule.PLAYER_ID
        else:
            # 팀 규칙은 선수 타입과 선수 ID를 NULL로 설정
            complete_user_rule["PLAYER_TYPE_ID"] = None
            complete_user_rule["PLAYER_ID"] = None
        
        # 사용자 적금 규칙 생성
        create_rule_obj = saving_rule_schema.UserSavingRuleCreate(**complete_user_rule)
        new_user_rule = saving_rule_crud.create_user_saving_rule(db, create_rule_obj)
        
        logger.info(f"적금 규칙 생성 완료: ID {new_user_rule.USER_SAVING_RULED_ID}")
        return new_user_rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 생성 중 오류 발생: {str(e)}"
        )

# 사용자 적금 규칙 업데이트
@router.put("/user-rules/{user_saving_rule_id}", response_model=saving_rule_schema.UserSavingRuleResponse)
async def update_user_saving_rule(
    user_saving_rule_id: int,
    user_rule: saving_rule_schema.UserSavingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 적금 규칙 업데이트 요청: ID {user_saving_rule_id}")
        
        # 사용자 적금 규칙 존재 여부 확인
        db_user_rule = saving_rule_crud.get_user_saving_rule_by_id(db, user_saving_rule_id)
        if not db_user_rule:
            logger.warning(f"존재하지 않는 사용자 적금 규칙: {user_saving_rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 사용자 적금 규칙입니다"
            )
            
        # 계정 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == db_user_rule.ACCOUNT_ID).first()
        if account and account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 사용자 적금 규칙을 업데이트할 권한이 없습니다"
            )
            
        # 적금 규칙 타입 ID가 변경된 경우, 존재 여부 확인
        if user_rule.SAVING_RULE_TYPE_ID is not None:
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, user_rule.SAVING_RULE_TYPE_ID)
            if not rule_type:
                logger.warning(f"존재하지 않는 적금 규칙 타입: {user_rule.SAVING_RULE_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 적금 규칙 타입입니다"
                )
                
        # 적금 규칙 상세 ID가 변경된 경우, 존재 여부 및 중복 확인
        if user_rule.SAVING_RULE_DETAIL_ID is not None and user_rule.SAVING_RULE_DETAIL_ID != db_user_rule.SAVING_RULE_DETAIL_ID:
            rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, user_rule.SAVING_RULE_DETAIL_ID)
            if not rule_detail:
                logger.warning(f"존재하지 않는 적금 규칙 상세: {user_rule.SAVING_RULE_DETAIL_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 적금 규칙 상세입니다"
                )
                
            # 중복 등록 확인
            existing_rule = saving_rule_crud.get_user_saving_rule_by_account_and_detail(db, db_user_rule.ACCOUNT_ID, user_rule.SAVING_RULE_DETAIL_ID)
            if existing_rule and existing_rule.USER_SAVING_RULED_ID != user_saving_rule_id:
                logger.warning(f"이미 등록된 적금 규칙: 계정 ID {db_user_rule.ACCOUNT_ID}, 규칙 상세 ID {user_rule.SAVING_RULE_DETAIL_ID}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 등록된 적금 규칙입니다"
                )
                
        # 선수 타입 ID가 변경된 경우, 존재 여부 확인
        if user_rule.PLAYER_TYPE_ID is not None:
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == user_rule.PLAYER_TYPE_ID).first()
            if not player_type:
                logger.warning(f"존재하지 않는 선수 타입: {user_rule.PLAYER_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 선수 타입입니다"
                )
                
        # 선수 ID가 변경된 경우, 존재 여부 및 선수 타입 일치 확인
        if user_rule.PLAYER_ID is not None:
            player = db.query(models.Player).filter(models.Player.PLAYER_ID == user_rule.PLAYER_ID).first()
            if not player:
                logger.warning(f"존재하지 않는 선수: {user_rule.PLAYER_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 선수입니다"
                )
                
            # 선수와 선수 타입 일치 확인
            check_player_type_id = user_rule.PLAYER_TYPE_ID if user_rule.PLAYER_TYPE_ID is not None else db_user_rule.PLAYER_TYPE_ID
            if player.PLAYER_TYPE_ID != check_player_type_id:
                logger.warning(f"선수 타입 불일치: 선수 {user_rule.PLAYER_ID}의 타입은 {player.PLAYER_TYPE_ID}이지만, 요청된 타입은 {check_player_type_id}입니다")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="선수와 선수 타입이 일치하지 않습니다"
                )
                
        # 적립 금액이 변경된 경우, 유효성 검사
        if user_rule.USER_SAVING_RULED_AMOUNT is not None and user_rule.USER_SAVING_RULED_AMOUNT <= 0:
            logger.warning(f"유효하지 않은 적립 금액: {user_rule.USER_SAVING_RULED_AMOUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적립 금액은 양수여야 합니다"
            )
            
        # 사용자 적금 규칙 업데이트
        updated_user_rule = saving_rule_crud.update_user_saving_rule(db, user_saving_rule_id, user_rule)
        if not updated_user_rule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 적금 규칙 업데이트 중 오류가 발생했습니다"
            )
            
        logger.info(f"사용자 적금 규칙 업데이트 완료: ID {user_saving_rule_id}")
        return updated_user_rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 적금 규칙 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 적금 규칙 업데이트 중 오류 발생: {str(e)}"
        )

# 사용자 적금 규칙 삭제
@router.delete("/user-rules/{user_saving_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_saving_rule(
    user_saving_rule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 적금 규칙 삭제 요청: ID {user_saving_rule_id}")
        
        # 사용자 적금 규칙 존재 여부 확인
        db_user_rule = saving_rule_crud.get_user_saving_rule_by_id(db, user_saving_rule_id)
        if not db_user_rule:
            logger.warning(f"존재하지 않는 사용자 적금 규칙: {user_saving_rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 사용자 적금 규칙입니다"
            )
            
        # 계정 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == db_user_rule.ACCOUNT_ID).first()
        if account and account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 사용자 적금 규칙을 삭제할 권한이 없습니다"
            )
            
        # 사용자 적금 규칙 삭제
        success = saving_rule_crud.delete_user_saving_rule(db, user_saving_rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 적금 규칙 삭제 중 오류가 발생했습니다"
            )
            
        logger.info(f"사용자 적금 규칙 삭제 완료: ID {user_saving_rule_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 적금 규칙 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 적금 규칙 삭제 중 오류 발생: {str(e)}"
        )

# 계정별 일일 적금 내역 조회
@router.get("/daily-savings/account/{account_id}", response_model=List[saving_rule_schema.DailySavingDetailResponse])
async def read_daily_savings_by_account(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정별 일일 적금 내역 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 권한 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"존재하지 않는 계정: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 계정입니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 적금 내역을 조회할 권한이 없습니다"
            )
            
        # 일일 적금 내역 조회
        daily_savings = saving_rule_crud.get_daily_savings_by_account(db, account_id, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for saving in daily_savings:
            # 적금 규칙 타입 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, saving.SAVING_RULED_TYPE_ID)
            
            # 적금 규칙 상세 조회
            rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, saving.SAVING_RULED_DETAIL_ID)
            
            # 적금 규칙 조회
            if rule_detail:
                saving_rule = saving_rule_crud.get_saving_rule_by_id(db, rule_detail.SAVING_RULE_ID)
            else:
                saving_rule = None
            
            # 기록 타입 조회
            if saving_rule:
                record_type = saving_rule_crud.get_record_type_by_id(db, saving_rule.RECORD_TYPE_ID)
                record_name = record_type.RECORD_NAME if record_type else None
            else:
                record_name = None
            
            # 결과 구성
            result.append({
                "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
                "ACCOUNT_ID": saving.ACCOUNT_ID,
                "DATE": saving.DATE,
                "SAVING_RULED_DETAIL_ID": saving.SAVING_RULED_DETAIL_ID,
                "SAVING_RULED_TYPE_ID": saving.SAVING_RULED_TYPE_ID,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                # "created_at": saving.created_at,
                # "account_num": account.ACCOUNT_NUM,
                "saving_rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "record_name": record_name,
                "player_name": None  # 필요한 경우 선수 정보 조회 추가
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정별 일일 적금 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정별 일일 적금 내역 조회 중 오류 발생: {str(e)}"
        )

# 날짜별 일일 적금 내역 조회
@router.get("/daily-savings/date/{date}", response_model=List[saving_rule_schema.DailySavingDetailResponse])
async def read_daily_savings_by_date(
    date: date,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"날짜별 일일 적금 내역 조회: 날짜 {date}")
        
        # 일일 적금 내역 조회
        daily_savings = saving_rule_crud.get_daily_savings_by_date(db, date, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for saving in daily_savings:
            # 계정 조회
            account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == saving.ACCOUNT_ID).first()
            
            # 계정 소유자 확인 (관리자가 아닌 경우)
            if account and account.USER_ID != current_user.USER_ID:
                continue  # 다른 사용자의 적금 내역은 건너뜀
            
            # 적금 규칙 타입 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, saving.SAVING_RULED_TYPE_ID)
            
            # 적금 규칙 상세 조회
            rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, saving.SAVING_RULED_DETAIL_ID)
            
            # 적금 규칙 조회
            if rule_detail:
                saving_rule = saving_rule_crud.get_saving_rule_by_id(db, rule_detail.SAVING_RULE_ID)
            else:
                saving_rule = None
            
            # 기록 타입 조회
            if saving_rule:
                record_type = saving_rule_crud.get_record_type_by_id(db, saving_rule.RECORD_TYPE_ID)
                record_name = record_type.RECORD_NAME if record_type else None
            else:
                record_name = None
            
            # 결과 구성
            result.append({
                "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
                "ACCOUNT_ID": saving.ACCOUNT_ID,
                "DATE": saving.DATE,
                "SAVING_RULED_DETAIL_ID": saving.SAVING_RULED_DETAIL_ID,
                "SAVING_RULED_TYPE_ID": saving.SAVING_RULED_TYPE_ID,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                "created_at": saving.created_at,
                "account_num": account.ACCOUNT_NUM if account else None,
                "saving_rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "record_name": record_name,
                "player_name": None  # 필요한 경우 선수 정보 조회 추가
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"날짜별 일일 적금 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"날짜별 일일 적금 내역 조회 중 오류 발생: {str(e)}"
        )

# 계정 적금 요약 정보 조회
@router.get("/summary/{account_id}", response_model=saving_rule_schema.AccountSavingSummaryResponse)
async def get_account_saving_summary(
    account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 적금 요약 정보 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 권한 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"존재하지 않는 계정: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 계정입니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 적금 요약 정보를 조회할 권한이 없습니다"
            )
            
        # 적금 요약 정보 조회
        summary = saving_rule_crud.get_account_saving_summary(db, account_id, start_date, end_date)
        if not summary:
            logger.warning(f"적금 요약 정보를 조회할 수 없음: 계정 ID {account_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="적금 요약 정보를 조회할 수 없습니다"
            )
            
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 적금 요약 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 적금 요약 정보 조회 중 오류 발생: {str(e)}"
        )
