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

# # 특정 적금 규칙 타입 조회
# @router.get("/types/{saving_rule_type_id}", response_model=saving_rule_schema.SavingRuleTypeResponse)
# async def read_saving_rule_type(
#     saving_rule_type_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         logger.info(f"적금 규칙 타입 조회: ID {saving_rule_type_id}")
        
#         rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, saving_rule_type_id)
#         if not rule_type:
#             logger.warning(f"존재하지 않는 적금 규칙 타입: {saving_rule_type_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 타입입니다"
#             )
            
#         return rule_type
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 타입 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 타입 조회 중 오류 발생: {str(e)}"
#         )

# # 적금 규칙 타입 생성
# @router.post("/types", response_model=saving_rule_schema.SavingRuleTypeResponse)
# async def create_saving_rule_type(
#     rule_type: saving_rule_schema.SavingRuleTypeCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 타입 생성 시도: {rule_type.SAVING_RULE_TYPE_NAME}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 중복 이름 확인
#         existing_type = saving_rule_crud.get_saving_rule_type_by_name(db, rule_type.SAVING_RULE_TYPE_NAME)
#         if existing_type:
#             logger.warning(f"이미 존재하는 적금 규칙 타입 이름: {rule_type.SAVING_RULE_TYPE_NAME}")
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="이미 존재하는 적금 규칙 타입 이름입니다"
#             )
            
#         # 적금 규칙 타입 생성
#         new_rule_type = saving_rule_crud.create_saving_rule_type(db, rule_type)
#         logger.info(f"적금 규칙 타입 생성 완료: ID {new_rule_type.SAVING_RULE_TYPE_ID}")
        
#         return new_rule_type
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 타입 생성 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 타입 생성 중 오류 발생: {str(e)}"
#         )

# # 적금 규칙 타입 업데이트
# @router.put("/types/{saving_rule_type_id}", response_model=saving_rule_schema.SavingRuleTypeResponse)
# async def update_saving_rule_type(
#     saving_rule_type_id: int,
#     rule_type: saving_rule_schema.SavingRuleTypeUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 타입 업데이트 요청: ID {saving_rule_type_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 타입 존재 여부 확인
#         db_rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, saving_rule_type_id)
#         if not db_rule_type:
#             logger.warning(f"존재하지 않는 적금 규칙 타입: {saving_rule_type_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 타입입니다"
#             )
            
#         # 중복 이름 확인 (이름이 변경된 경우)
#         if rule_type.SAVING_RULE_TYPE_NAME != db_rule_type.SAVING_RULE_TYPE_NAME:
#             existing_type = saving_rule_crud.get_saving_rule_type_by_name(db, rule_type.SAVING_RULE_TYPE_NAME)
#             if existing_type:
#                 logger.warning(f"이미 존재하는 적금 규칙 타입 이름: {rule_type.SAVING_RULE_TYPE_NAME}")
#                 raise HTTPException(
#                     status_code=status.HTTP_409_CONFLICT,
#                     detail="이미 존재하는 적금 규칙 타입 이름입니다"
#                 )
                
#         # 적금 규칙 타입 업데이트
#         updated_rule_type = saving_rule_crud.update_saving_rule_type(db, saving_rule_type_id, rule_type)
#         if not updated_rule_type:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="적금 규칙 타입 업데이트 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"적금 규칙 타입 업데이트 완료: ID {saving_rule_type_id}")
#         return updated_rule_type
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 타입 업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 타입 업데이트 중 오류 발생: {str(e)}"
#         )

# # 적금 규칙 타입 삭제
# @router.delete("/types/{saving_rule_type_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_saving_rule_type(
#     saving_rule_type_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 타입 삭제 요청: ID {saving_rule_type_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 타입 존재 여부 확인
#         db_rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, saving_rule_type_id)
#         if not db_rule_type:
#             logger.warning(f"존재하지 않는 적금 규칙 타입: {saving_rule_type_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 타입입니다"
#             )
            
#         # 적금 규칙 타입 삭제
#         success = saving_rule_crud.delete_saving_rule_type(db, saving_rule_type_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="이 적금 규칙 타입을 참조하는 다른 데이터가 있어 삭제할 수 없습니다"
#             )
            
#         logger.info(f"적금 규칙 타입 삭제 완료: ID {saving_rule_type_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 타입 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 타입 삭제 중 오류 발생: {str(e)}"
#         )

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

# 특정 적금 규칙 조회
@router.get("/rules/{saving_rule_id}", response_model=saving_rule_schema.SavingRuleListDetailResponse)
async def read_saving_rule(
    saving_rule_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"적금 규칙 조회: ID {saving_rule_id}")
        
        # 적금 규칙 조회
        rule = saving_rule_crud.get_saving_rule_by_id(db, saving_rule_id)
        if not rule:
            logger.warning(f"존재하지 않는 적금 규칙: {saving_rule_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙입니다"
            )
            
        # 적금 규칙 타입 정보 조회
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
        
        # 기록 타입 정보 조회
        record_type = saving_rule_crud.get_record_type_by_id(db, rule.RECORD_TYPE_ID)
        
        # 결과 구성
        result = {
            "SAVING_RULE_ID": rule.SAVING_RULE_ID,
            "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
            "RECORD_TYPE_ID": rule.RECORD_TYPE_ID,
            "saving_rule_type": rule_type,
            "record_type": record_type
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 조회 중 오류 발생: {str(e)}"
        )

# # 적금 규칙 생성
# @router.post("/rules", response_model=saving_rule_schema.SavingRuleListResponse)
# async def create_saving_rule(
#     rule: saving_rule_schema.SavingRuleListCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 생성 시도: 타입 ID {rule.SAVING_RULE_TYPE_ID}, 기록 타입 ID {rule.RECORD_TYPE_ID}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 적금 규칙 타입 존재 여부 확인
#         rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
#         if not rule_type:
#             logger.warning(f"존재하지 않는 적금 규칙 타입: {rule.SAVING_RULE_TYPE_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙 타입입니다"
#             )
            
#         # 기록 타입 존재 여부 확인
#         record_type = saving_rule_crud.get_record_type_by_id(db, rule.RECORD_TYPE_ID)
#         if not record_type:
#             logger.warning(f"존재하지 않는 기록 타입: {rule.RECORD_TYPE_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 기록 타입입니다"
#             )
            
#         # 적금 규칙 생성
#         new_rule = saving_rule_crud.create_saving_rule(db, rule)
#         logger.info(f"적금 규칙 생성 완료: ID {new_rule.SAVING_RULE_ID}")
        
#         return new_rule
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 생성 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 생성 중 오류 발생: {str(e)}"
#         )

# # 적금 규칙 업데이트
# @router.put("/rules/{saving_rule_id}", response_model=saving_rule_schema.SavingRuleListResponse)
# async def update_saving_rule(
#     saving_rule_id: int,
#     rule: saving_rule_schema.SavingRuleListUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 업데이트 요청: ID {saving_rule_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 적금 규칙 존재 여부 확인
#         db_rule = saving_rule_crud.get_saving_rule_by_id(db, saving_rule_id)
#         if not db_rule:
#             logger.warning(f"존재하지 않는 적금 규칙: {saving_rule_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙입니다"
#             )
            
#         # 적금 규칙 타입 ID가 변경된 경우, 존재 여부 확인
#         if rule.SAVING_RULE_TYPE_ID is not None:
#             rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
#             if not rule_type:
#                 logger.warning(f"존재하지 않는 적금 규칙 타입: {rule.SAVING_RULE_TYPE_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 적금 규칙 타입입니다"
#                 )
                
#         # 기록 타입 ID가 변경된 경우, 존재 여부 확인
#         if rule.RECORD_TYPE_ID is not None:
#             record_type = saving_rule_crud.get_record_type_by_id(db, rule.RECORD_TYPE_ID)
#             if not record_type:
#                 logger.warning(f"존재하지 않는 기록 타입: {rule.RECORD_TYPE_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 기록 타입입니다"
#                 )
                
#         # 적금 규칙 업데이트
#         updated_rule = saving_rule_crud.update_saving_rule(db, saving_rule_id, rule)
#         if not updated_rule:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="적금 규칙 업데이트 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"적금 규칙 업데이트 완료: ID {saving_rule_id}")
#         return updated_rule
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 업데이트 중 오류 발생: {str(e)}"
#         )

# # 적금 규칙 삭제
# @router.delete("/rules/{saving_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_saving_rule(
#     saving_rule_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적금 규칙 삭제 요청: ID {saving_rule_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 적금 규칙 존재 여부 확인
#         db_rule = saving_rule_crud.get_saving_rule_by_id(db, saving_rule_id)
#         if not db_rule:
#             logger.warning(f"존재하지 않는 적금 규칙: {saving_rule_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 적금 규칙입니다"
#             )
            
#         # 적금 규칙 삭제
#         success = saving_rule_crud.delete_saving_rule(db, saving_rule_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="이 적금 규칙을 참조하는 다른 데이터가 있어 삭제할 수 없습니다"
#             )
            
#         logger.info(f"적금 규칙 삭제 완료: ID {saving_rule_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적금 규칙 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적금 규칙 삭제 중 오류 발생: {str(e)}"
#         )

# 모든 적금 규칙 상세 조회
@router.get("/rule-details", response_model=List[saving_rule_schema.SavingRuleDetailExtendedResponse])
async def read_saving_rule_details(
    saving_rule_type_id: Optional[int] = None,
    player_type_id: Optional[int] = None,
    saving_rule_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"적금 규칙 상세 목록 조회: 타입={saving_rule_type_id}, 선수 타입={player_type_id}, 규칙={saving_rule_id}")
        
        # 필터에 따라 조회
        if saving_rule_type_id:
            details = saving_rule_crud.get_saving_rule_details_by_type(db, saving_rule_type_id, skip, limit)
        elif player_type_id:
            details = saving_rule_crud.get_saving_rule_details_by_player_type(db, player_type_id, skip, limit)
        elif saving_rule_id:
            details = saving_rule_crud.get_saving_rule_details_by_rule(db, saving_rule_id, skip, limit)
        else:
            details = saving_rule_crud.get_all_saving_rule_details(db, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for detail in details:
            # 적금 규칙 타입 정보 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, detail.SAVING_RULE_TYPE_ID)
            
            # 선수 타입 정보 조회
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == detail.PLAYER_TYPE_ID).first()
            
            # 적금 규칙 정보 조회
            saving_rule = saving_rule_crud.get_saving_rule_by_id(db, detail.SAVING_RULE_ID)
            
            # 결과 구성
            result.append({
                "SAVING_RULE_DETAIL_ID": detail.SAVING_RULE_DETAIL_ID,
                "SAVING_RULE_TYPE_ID": detail.SAVING_RULE_TYPE_ID,
                "PLAYER_TYPE_ID": detail.PLAYER_TYPE_ID,
                "SAVING_RULE_ID": detail.SAVING_RULE_ID,
                "saving_rule_type": rule_type,
                "player_type": player_type,
                "saving_rule": saving_rule
            })
        
        return result
    except Exception as e:
        logger.error(f"적금 규칙 상세 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 상세 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 적금 규칙 상세 조회
@router.get("/rule-details/{saving_rule_detail_id}", response_model=saving_rule_schema.SavingRuleDetailExtendedResponse)
async def read_saving_rule_detail(
    saving_rule_detail_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"적금 규칙 상세 조회: ID {saving_rule_detail_id}")
        
        # 적금 규칙 상세 조회
        detail = saving_rule_crud.get_saving_rule_detail_by_id(db, saving_rule_detail_id)
        if not detail:
            logger.warning(f"존재하지 않는 적금 규칙 상세: {saving_rule_detail_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 상세입니다"
            )
            
        # 적금 규칙 타입 정보 조회
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, detail.SAVING_RULE_TYPE_ID)
        
        # 선수 타입 정보 조회
        player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == detail.PLAYER_TYPE_ID).first()
        
        # 적금 규칙 정보 조회
        saving_rule = saving_rule_crud.get_saving_rule_by_id(db, detail.SAVING_RULE_ID)
        
        # 결과 구성
        result = {
            "SAVING_RULE_DETAIL_ID": detail.SAVING_RULE_DETAIL_ID,
            "SAVING_RULE_TYPE_ID": detail.SAVING_RULE_TYPE_ID,
            "PLAYER_TYPE_ID": detail.PLAYER_TYPE_ID,
            "SAVING_RULE_ID": detail.SAVING_RULE_ID,
            "saving_rule_type": rule_type,
            "player_type": player_type,
            "saving_rule": saving_rule
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 상세 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 상세 조회 중 오류 발생: {str(e)}"
        )

# 적금 규칙 상세 생성
@router.post("/rule-details", response_model=saving_rule_schema.SavingRuleDetailResponse)
async def create_saving_rule_detail(
    detail: saving_rule_schema.SavingRuleDetailCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"적금 규칙 상세 생성 시도: 타입 ID {detail.SAVING_RULE_TYPE_ID}, 선수 타입 ID {detail.PLAYER_TYPE_ID}, 규칙 ID {detail.SAVING_RULE_ID}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 적금 규칙 타입 존재 여부 확인
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, detail.SAVING_RULE_TYPE_ID)
        if not rule_type:
            logger.warning(f"존재하지 않는 적금 규칙 타입: {detail.SAVING_RULE_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 타입입니다"
            )
            
        # 선수 타입 존재 여부 확인
        player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == detail.PLAYER_TYPE_ID).first()
        if not player_type:
            logger.warning(f"존재하지 않는 선수 타입: {detail.PLAYER_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수 타입입니다"
            )
            
        # 적금 규칙 존재 여부 확인
        saving_rule = saving_rule_crud.get_saving_rule_by_id(db, detail.SAVING_RULE_ID)
        if not saving_rule:
            logger.warning(f"존재하지 않는 적금 규칙: {detail.SAVING_RULE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙입니다"
            )
            
        # 적금 규칙 상세 생성
        new_detail = saving_rule_crud.create_saving_rule_detail(db, detail)
        logger.info(f"적금 규칙 상세 생성 완료: ID {new_detail.SAVING_RULE_DETAIL_ID}")
        
        return new_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 상세 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 상세 생성 중 오류 발생: {str(e)}"
        )

# 적금 규칙 상세 업데이트
@router.put("/rule-details/{saving_rule_detail_id}", response_model=saving_rule_schema.SavingRuleDetailResponse)
async def update_saving_rule_detail(
    saving_rule_detail_id: int,
    detail: saving_rule_schema.SavingRuleDetailUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"적금 규칙 상세 업데이트 요청: ID {saving_rule_detail_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 적금 규칙 상세 존재 여부 확인
        db_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, saving_rule_detail_id)
        if not db_detail:
            logger.warning(f"존재하지 않는 적금 규칙 상세: {saving_rule_detail_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 상세입니다"
            )
            
        # 적금 규칙 타입 ID가 변경된 경우, 존재 여부 확인
        if detail.SAVING_RULE_TYPE_ID is not None:
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, detail.SAVING_RULE_TYPE_ID)
            if not rule_type:
                logger.warning(f"존재하지 않는 적금 규칙 타입: {detail.SAVING_RULE_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 적금 규칙 타입입니다"
                )
                
        # 선수 타입 ID가 변경된 경우, 존재 여부 확인
        if detail.PLAYER_TYPE_ID is not None:
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == detail.PLAYER_TYPE_ID).first()
            if not player_type:
                logger.warning(f"존재하지 않는 선수 타입: {detail.PLAYER_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 선수 타입입니다"
                )
                
        # 적금 규칙 ID가 변경된 경우, 존재 여부 확인
        if detail.SAVING_RULE_ID is not None:
            saving_rule = saving_rule_crud.get_saving_rule_by_id(db, detail.SAVING_RULE_ID)
            if not saving_rule:
                logger.warning(f"존재하지 않는 적금 규칙: {detail.SAVING_RULE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 적금 규칙입니다"
                )
                
        # 적금 규칙 상세 업데이트
        updated_detail = saving_rule_crud.update_saving_rule_detail(db, saving_rule_detail_id, detail)
        if not updated_detail:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="적금 규칙 상세 업데이트 중 오류가 발생했습니다"
            )
            
        logger.info(f"적금 규칙 상세 업데이트 완료: ID {saving_rule_detail_id}")
        return updated_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 상세 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 상세 업데이트 중 오류 발생: {str(e)}"
        )

# 적금 규칙 상세 삭제
@router.delete("/rule-details/{saving_rule_detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saving_rule_detail(
    saving_rule_detail_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"적금 규칙 상세 삭제 요청: ID {saving_rule_detail_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 적금 규칙 상세 존재 여부 확인
        db_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, saving_rule_detail_id)
        if not db_detail:
            logger.warning(f"존재하지 않는 적금 규칙 상세: {saving_rule_detail_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 상세입니다"
            )
            
        # 적금 규칙 상세 삭제
        success = saving_rule_crud.delete_saving_rule_detail(db, saving_rule_detail_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 적금 규칙 상세를 참조하는 다른 데이터가 있어 삭제할 수 없습니다"
            )
            
        logger.info(f"적금 규칙 상세 삭제 완료: ID {saving_rule_detail_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 상세 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 상세 삭제 중 오류 발생: {str(e)}"
        )

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

# 선수별 사용자 적금 규칙 조회
@router.get("/user-rules/player/{player_id}", response_model=List[saving_rule_schema.UserSavingRuleDetailResponse])
async def read_user_saving_rules_by_player(
    player_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수별 사용자 적금 규칙 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 사용자 적금 규칙 조회
        user_rules = saving_rule_crud.get_user_saving_rules_by_player(db, player_id, skip, limit)
        
        # 응답 형식에 맞게 변환
        result = []
        for rule in user_rules:
            # 계정 조회
            account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == rule.ACCOUNT_ID).first()
            
            # 적금 규칙 타입 조회
            rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, rule.SAVING_RULE_TYPE_ID)
            
            # 선수 타입 조회
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == rule.PLAYER_TYPE_ID).first()
            
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
                "account_num": account.ACCOUNT_NUM if account else None,
                "saving_rule_type_name": rule_type.SAVING_RULE_TYPE_NAME if rule_type else None,
                "player_type_name": player_type.PLAYER_TYPE_NAME if player_type else None,
                "player_name": player.PLAYER_NAME,
                "record_name": record_name
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수별 사용자 적금 규칙 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수별 사용자 적금 규칙 조회 중 오류 발생: {str(e)}"
        )

# 사용자 적금 규칙 생성
@router.post("/user-rules", response_model=saving_rule_schema.UserSavingRuleResponse)
async def create_user_saving_rule(
    user_rule: saving_rule_schema.UserSavingRuleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 적금 규칙 생성 시도: 계정 ID {user_rule.ACCOUNT_ID}, 규칙 상세 ID {user_rule.SAVING_RULE_DETAIL_ID}")
        
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
            
        # 적금 규칙 타입 존재 여부 확인
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, user_rule.SAVING_RULE_TYPE_ID)
        if not rule_type:
            logger.warning(f"존재하지 않는 적금 규칙 타입: {user_rule.SAVING_RULE_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 타입입니다"
            )
            
        # 적금 규칙 상세 존재 여부 확인
        rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, user_rule.SAVING_RULE_DETAIL_ID)
        if not rule_detail:
            logger.warning(f"존재하지 않는 적금 규칙 상세: {user_rule.SAVING_RULE_DETAIL_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 상세입니다"
            )
            
        # 선수 타입 존재 여부 확인
        player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == user_rule.PLAYER_TYPE_ID).first()
        if not player_type:
            logger.warning(f"존재하지 않는 선수 타입: {user_rule.PLAYER_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수 타입입니다"
            )
            
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == user_rule.PLAYER_ID).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {user_rule.PLAYER_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수와 선수 타입 일치 확인
        if player.PLAYER_TYPE_ID != user_rule.PLAYER_TYPE_ID:
            logger.warning(f"선수 타입 불일치: 선수 {user_rule.PLAYER_ID}의 타입은 {player.PLAYER_TYPE_ID}이지만, 요청된 타입은 {user_rule.PLAYER_TYPE_ID}입니다")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="선수와 선수 타입이 일치하지 않습니다"
            )
            
        # 중복 등록 확인
        existing_rule = saving_rule_crud.get_user_saving_rule_by_account_and_detail(db, user_rule.ACCOUNT_ID, user_rule.SAVING_RULE_DETAIL_ID)
        if existing_rule:
            logger.warning(f"이미 등록된 적금 규칙: 계정 ID {user_rule.ACCOUNT_ID}, 규칙 상세 ID {user_rule.SAVING_RULE_DETAIL_ID}")
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
            
        # 사용자 적금 규칙 생성
        new_user_rule = saving_rule_crud.create_user_saving_rule(db, user_rule)
        logger.info(f"사용자 적금 규칙 생성 완료: ID {new_user_rule.USER_SAVING_RULED_ID}")
        
        return new_user_rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 적금 규칙 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 적금 규칙 생성 중 오류 발생: {str(e)}"
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
                "created_at": saving.created_at,
                "account_num": account.ACCOUNT_NUM,
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
        
        # TODO: 관리자 권한 확인 필요
        
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

# 일일 적금 생성
@router.post("/daily-savings", response_model=saving_rule_schema.DailySavingResponse)
async def create_daily_saving(
    daily_saving: saving_rule_schema.DailySavingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"일일 적금 생성 시도: 계정 ID {daily_saving.ACCOUNT_ID}, 날짜 {daily_saving.DATE}")
        
        # 계정 존재 여부 및 권한 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == daily_saving.ACCOUNT_ID).first()
        if not account:
            logger.warning(f"존재하지 않는 계정: {daily_saving.ACCOUNT_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 계정입니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정에 일일 적금을 생성할 권한이 없습니다"
            )
            
        # 적금 규칙 타입 존재 여부 확인
        rule_type = saving_rule_crud.get_saving_rule_type_by_id(db, daily_saving.SAVING_RULED_TYPE_ID)
        if not rule_type:
            logger.warning(f"존재하지 않는 적금 규칙 타입: {daily_saving.SAVING_RULED_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 타입입니다"
            )
            
        # 적금 규칙 상세 존재 여부 확인
        rule_detail = saving_rule_crud.get_saving_rule_detail_by_id(db, daily_saving.SAVING_RULED_DETAIL_ID)
        if not rule_detail:
            logger.warning(f"존재하지 않는 적금 규칙 상세: {daily_saving.SAVING_RULED_DETAIL_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 적금 규칙 상세입니다"
            )
            
        # 카운트 및 금액 유효성 검사
        if daily_saving.COUNT < 0:
            logger.warning(f"유효하지 않은 카운트: {daily_saving.COUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="카운트는 음수가 될 수 없습니다"
            )
            
        if daily_saving.DAILY_SAVING_AMOUNT <= 0:
            logger.warning(f"유효하지 않은 적립 금액: {daily_saving.DAILY_SAVING_AMOUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적립 금액은 양수여야 합니다"
            )
            
        # 일일 적립 한도 확인
        if not saving_rule_crud.check_daily_limit(db, daily_saving.ACCOUNT_ID, daily_saving.DAILY_SAVING_AMOUNT):
            logger.warning(f"일일 적립 한도 초과: 계정 ID {daily_saving.ACCOUNT_ID}, 금액 {daily_saving.DAILY_SAVING_AMOUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="일일 적립 한도를 초과했습니다"
            )
            
        # 월간 적립 한도 확인
        if not saving_rule_crud.check_monthly_limit(db, daily_saving.ACCOUNT_ID, daily_saving.DAILY_SAVING_AMOUNT):
            logger.warning(f"월간 적립 한도 초과: 계정 ID {daily_saving.ACCOUNT_ID}, 금액 {daily_saving.DAILY_SAVING_AMOUNT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월간 적립 한도를 초과했습니다"
            )
            
        # 일일 적금 생성
        new_daily_saving = saving_rule_crud.create_daily_saving(db, daily_saving)
        logger.info(f"일일 적금 생성 완료: ID {new_daily_saving.DAILY_SAVING_ID}")
        
        return new_daily_saving
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일일 적금 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 적금 생성 중 오류 발생: {str(e)}"
        )

# 일일 적금 삭제
@router.delete("/daily-savings/{daily_saving_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_saving(
    daily_saving_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"일일 적금 삭제 요청: ID {daily_saving_id}")
        
        # 일일 적금 존재 여부 확인
        db_daily_saving = saving_rule_crud.get_daily_saving_by_id(db, daily_saving_id)
        if not db_daily_saving:
            logger.warning(f"존재하지 않는 일일 적금: {daily_saving_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 일일 적금입니다"
            )
            
        # 계정 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == db_daily_saving.ACCOUNT_ID).first()
        if account and account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 일일 적금을 삭제할 권한이 없습니다"
            )
            
        # 일일 적금 삭제
        success = saving_rule_crud.delete_daily_saving(db, daily_saving_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="일일 적금 삭제 중 오류가 발생했습니다"
            )
            
        logger.info(f"일일 적금 삭제 완료: ID {daily_saving_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일일 적금 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 적금 삭제 중 오류 발생: {str(e)}"
        )

# 선수 기록을 통한 일일 적금 계산
@router.post("/calculate", response_model=dict)
async def calculate_daily_saving_from_record(
    player_record: saving_rule_schema.PlayerRecordModel,
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 기록을 통한 일일 적금 계산 요청: 계정 ID {account_id}, 선수 ID {player_record.PLAYER_ID}")
        
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
                detail="이 계정에 일일 적금을 계산할 권한이 없습니다"
            )
            
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_record.PLAYER_ID).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_record.PLAYER_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 기록 유형 존재 여부 확인
        record_type = saving_rule_crud.get_record_type_by_id(db, player_record.RECORD_TYPE_ID)
        if not record_type:
            logger.warning(f"존재하지 않는 기록 유형: {player_record.RECORD_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 기록 유형입니다"
            )
            
        # 선수 기록을 딕셔너리로 변환
        record_dict = {
            "PLAYER_ID": player_record.PLAYER_ID,
            "RECORD_TYPE_ID": player_record.RECORD_TYPE_ID,
            "COUNT": player_record.COUNT,
            "DATE": player_record.DATE
        }
        
        # 일일 적금 계산
        result = saving_rule_crud.calculate_daily_saving(db, account_id, record_dict)
        if not result:
            logger.warning(f"적용할 수 있는 적금 규칙이 없거나 계산 중 오류 발생")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적용할 수 있는 적금 규칙이 없거나 계산 중 오류가 발생했습니다"
            )
            
        logger.info(f"일일 적금 계산 완료: 계정 ID {account_id}, 총 금액 {result['total_saving']}")
        
        # 응답 데이터 구성
        response = {
            "account_id": account_id,
            "player_id": player_record.PLAYER_ID,
            "player_name": player.PLAYER_NAME,
            "record_type_id": player_record.RECORD_TYPE_ID,
            "record_name": record_type.RECORD_NAME,
            "count": player_record.COUNT,
            "date": player_record.DATE.isoformat(),
            "total_saving": result["total_saving"],
            "created_savings_count": len(result["created_savings"])
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일일 적금 계산 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 적금 계산 중 오류 발생: {str(e)}"
        )

# 적금 규칙 조합 목록 조회
@router.get("/combinations", response_model=List[saving_rule_schema.SavingRuleCombinationResponse])
async def read_saving_rule_combinations(db: Session = Depends(get_db)):
    try:
        logger.info("적금 규칙 조합 목록 조회")
        combinations = saving_rule_crud.get_saving_rule_combinations(db)
        return combinations
    except Exception as e:
        logger.error(f"적금 규칙 조합 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 조합 목록 조회 중 오류 발생: {str(e)}"
        )

# 계정에 등록 가능한 적금 규칙 목록 조회
@router.get("/available/{account_id}", response_model=List[saving_rule_schema.SavingRuleCombinationResponse])
async def read_available_saving_rules(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정에 등록 가능한 적금 규칙 목록 조회: 계정 ID {account_id}")
        
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
            
        # 등록 가능한 적금 규칙 목록 조회
        available_rules = saving_rule_crud.get_available_saving_rules_for_account(db, account_id)
        return available_rules
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"등록 가능한 적금 규칙 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"등록 가능한 적금 규칙 목록 조회 중 오류 발생: {str(e)}"
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

# 선수별 적립 내역 조회
@router.get("/player/{player_id}/savings", response_model=List[dict])
async def get_player_daily_savings(
    player_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수별 적립 내역 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수별 적립 내역 조회
        savings = saving_rule_crud.get_player_daily_savings(db, player_id, start_date, end_date)
        return savings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수별 적립 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수별 적립 내역 조회 중 오류 발생: {str(e)}"
        )

# 선수별 적립 통계 조회
@router.get("/player/{player_id}/stats", response_model=saving_rule_schema.PlayerSavingStatsResponse)
async def get_player_saving_stats(
    player_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수별 적립 통계 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수별 적립 통계 조회
        stats = saving_rule_crud.get_player_saving_stats(db, player_id, start_date, end_date)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수별 적립 통계 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수별 적립 통계 조회 중 오류 발생: {str(e)}"
        )

# 선수별 적금 규칙 조회
@router.get("/player/{player_id}/rules", response_model=List[dict])
async def get_player_saving_rules(
    player_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수별 적금 규칙 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수별 적금 규칙 조회
        rules = saving_rule_crud.get_player_saving_rules(db, player_id)
        return rules
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수별 적금 규칙 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수별 적금 규칙 조회 중 오류 발생: {str(e)}"
        )

# # 적립 한도 검사
# @router.post("/check-limit", response_model=saving_rule_schema.SavingLimitCheckResponse)
# async def check_saving_limit(
#     request: saving_rule_schema.SavingLimitCheckRequest,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"적립 한도 검사 요청: 계정 ID {request.ACCOUNT_ID}, 금액 {request.AMOUNT}")
        
#         # 계정 존재 여부 및 권한 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == request.ACCOUNT_ID).first()
#         if not account:
#             logger.warning(f"존재하지 않는 계정: {request.ACCOUNT_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 계정입니다"
#             )
            
#         if account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="이 계정의 적립 한도를 검사할 권한이 없습니다"
#             )
            
#         # 금액 유효성 검사
#         if request.AMOUNT <= 0:
#             logger.warning(f"유효하지 않은 금액: {request.AMOUNT}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="금액은 양수여야 합니다"
#             )
            
#         # 오늘 날짜의 적립 금액 합계 계산
#         today = datetime.now().date()
#         today_savings = saving_rule_crud.get_daily_savings_by_account_and_date(db, request.ACCOUNT_ID, today)
#         today_total = sum(saving.DAILY_SAVING_AMOUNT for saving in today_savings)
        
#         # 이번 달 시작일과 오늘 날짜
#         month_start = date(today.year, today.month, 1)
        
#         # 이번 달 적립 금액 합계 계산
#         month_savings = saving_rule_crud.get_daily_savings_by_account_and_date_range(db, request.ACCOUNT_ID, month_start, today)
#         month_total = sum(saving.DAILY_SAVING_AMOUNT for saving in month_savings)
        
#         # 한도 계산
#         is_within_daily_limit = (today_total + request.AMOUNT) <= account.DAILY_LIMIT
#         is_within_monthly_limit = (month_total + request.AMOUNT) <= account.MONTH_LIMIT
#         remaining_daily_limit = max(0, account.DAILY_LIMIT - today_total)
#         remaining_monthly_limit = max(0, account.MONTH_LIMIT - month_total)
        
#         # 응답 데이터 구성
#         response = {
#             "account_id": request.ACCOUNT_ID,
#             "amount": request.AMOUNT,
#             "daily_limit": account.DAILY_LIMIT,
#             "monthly_limit": account.MONTH_LIMIT,
#             "is_within_daily_limit": is_within_daily_limit,
#             "is_within_monthly_limit": is_within_monthly_limit,
#             "remaining_daily_limit": remaining_daily_limit,
#             "remaining_monthly_limit": remaining_monthly_limit
#         }
        
#         return response
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"적립 한도 검사 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"적립 한도 검사 중 오류 발생: {str(e)}"
#         )
    