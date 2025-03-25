from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db
import models
from router.mission import mission_schema, mission_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 모든 미션 조회
@router.get("/", response_model=List[mission_schema.MissionResponse])
async def read_missions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 미션 조회: skip={skip}, limit={limit}")
        missions = mission_crud.get_all_missions(db, skip, limit)
        return missions
    except Exception as e:
        logger.error(f"미션 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"미션 조회 중 오류 발생: {str(e)}"
        )

# 특정 미션 조회
@router.get("/{mission_id}", response_model=mission_schema.MissionResponse)
async def read_mission(
    mission_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"미션 조회 요청: 미션 ID {mission_id}")
        
        mission = mission_crud.get_mission_by_id(db, mission_id)
        if not mission:
            logger.warning(f"미션을 찾을 수 없음: {mission_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="미션을 찾을 수 없습니다"
            )
            
        return mission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"미션 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"미션 조회 중 오류 발생: {str(e)}"
        )

# 계정 미션 목록 조회
@router.get("/account/{account_id}", response_model=List[mission_schema.UsedMissionDetailResponse])
async def read_account_missions(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 미션 목록 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 미션 정보를 조회할 권한이 없습니다"
            )
            
        # 미션 목록 조회
        used_missions = mission_crud.get_used_missions_by_account(db, account_id)
        
        # 응답 형식에 맞게 변환
        result = []
        for used_mission in used_missions:
            mission = mission_crud.get_mission_by_id(db, used_mission.MISSION_ID)
            result.append({
                "USED_MISSION_ID": used_mission.USED_MISSION_ID,
                "ACCOUNT_ID": used_mission.ACCOUNT_ID,
                "MISSION_ID": used_mission.MISSION_ID,
                "COUNT": used_mission.COUNT,
                "MAX_COUNT": used_mission.MAX_COUNT,
                "MISSION_RATE": used_mission.MISSION_RATE,
                "created_at": used_mission.created_at,
                "mission": mission
            })
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 미션 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 미션 목록 조회 중 오류 발생: {str(e)}"
        )

# 계정 미션 요약 정보 조회
@router.get("/account/{account_id}/summary", response_model=mission_schema.MissionSummaryResponse)
async def read_account_mission_summary(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 미션 요약 정보 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 미션 정보를 조회할 권한이 없습니다"
            )
            
        # 미션 요약 정보 조회
        summary = mission_crud.get_account_mission_summary(db, account_id)
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 미션 요약 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 미션 요약 정보 조회 중 오류 발생: {str(e)}"
        )

# 계정에 미션 등록
@router.post("/account/{account_id}", response_model=mission_schema.UsedMissionResponse)
async def add_mission_to_account(
    account_id: int,
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정에 미션 등록 요청: 계정 ID {account_id}, 미션 ID {mission_id}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정에 미션을 등록할 권한이 없습니다"
            )
            
        # 미션 존재 여부 확인
        mission = mission_crud.get_mission_by_id(db, mission_id)
        if not mission:
            logger.warning(f"미션을 찾을 수 없음: {mission_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="미션을 찾을 수 없습니다"
            )
            
        # 이미 등록된 미션인지 확인
        existing_used_mission = mission_crud.get_used_mission(db, account_id, mission_id)
        if existing_used_mission:
            logger.warning(f"이미 등록된 미션: 계정 ID {account_id}, 미션 ID {mission_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 미션입니다"
            )
            
        # 미션 등록
        used_mission_data = mission_schema.UsedMissionCreate(
            ACCOUNT_ID=account_id,
            MISSION_ID=mission_id,
            COUNT=0
        )
        
        new_used_mission = mission_crud.create_used_mission(db, used_mission_data)
        if not new_used_mission:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="미션 등록 중 오류가 발생했습니다"
            )
            
        logger.info(f"계정에 미션 등록 완료: 계정 ID {account_id}, 미션 ID {mission_id}")
        return new_used_mission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정에 미션 등록 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정에 미션 등록 중 오류 발생: {str(e)}"
        )

# 미션 카운트 업데이트
@router.put("/account/{account_id}/mission/{mission_id}", response_model=mission_schema.UsedMissionResponse)
async def update_mission_status(
    account_id: int,
    mission_id: int,
    status_update: mission_schema.MissionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"미션 카운트 업데이트 요청: 계정 ID {account_id}, 미션 ID {mission_id}, 증가={status_update.increment}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 미션 상태를 업데이트할 권한이 없습니다"
            )
            
        # 미션 등록 여부 확인
        used_mission = mission_crud.get_used_mission(db, account_id, mission_id)
        if not used_mission:
            logger.warning(f"등록되지 않은 미션: 계정 ID {account_id}, 미션 ID {mission_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이 계정에 등록되지 않은 미션입니다"
            )
            
        # 카운트 업데이트
        if status_update.increment:
            # 카운트 증가
            if used_mission.COUNT >= used_mission.MAX_COUNT:
                return used_mission  # 이미 최대치
                
            update_data = mission_schema.UsedMissionUpdate(COUNT=used_mission.COUNT + 1)
        else:
            # 카운트 감소
            if used_mission.COUNT <= 0:
                return used_mission  # 이미 최소치
                
            update_data = mission_schema.UsedMissionUpdate(COUNT=used_mission.COUNT - 1)
            
        updated_mission = mission_crud.update_used_mission(db, used_mission.USED_MISSION_ID, update_data)
        if not updated_mission:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="미션 상태 업데이트 중 오류가 발생했습니다"
            )
            
        # 이자율 업데이트 (미션 완료 시)
        if updated_mission.COUNT >= updated_mission.MAX_COUNT:
            mission_crud.update_account_interest_rate(db, account_id)
            
        logger.info(f"미션 카운트 업데이트 완료: 계정 ID {account_id}, 미션 ID {mission_id}, 현재 카운트={updated_mission.COUNT}")
        return updated_mission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"미션 카운트 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"미션 카운트 업데이트 중 오류 발생: {str(e)}"
        )

# 일회성 미션 완료
@router.post("/complete", response_model=mission_schema.UsedMissionResponse)
async def complete_mission(
    request: mission_schema.CompleteMissionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"일회성 미션 완료 요청: 계정 ID {request.ACCOUNT_ID}, 미션 ID {request.MISSION_ID}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == request.ACCOUNT_ID).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {request.ACCOUNT_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 미션을 완료할 권한이 없습니다"
            )
            
        # 미션 존재 여부 확인
        mission = mission_crud.get_mission_by_id(db, request.MISSION_ID)
        if not mission:
            logger.warning(f"미션을 찾을 수 없음: {request.MISSION_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="미션을 찾을 수 없습니다"
            )
            
        # 미션 등록 여부 확인
        used_mission = mission_crud.get_used_mission(db, request.ACCOUNT_ID, request.MISSION_ID)
        if not used_mission:
            # 미션이 등록되어 있지 않으면 자동 등록
            used_mission_data = mission_schema.UsedMissionCreate(
                ACCOUNT_ID=request.ACCOUNT_ID,
                MISSION_ID=request.MISSION_ID,
                COUNT=0
            )
            used_mission = mission_crud.create_used_mission(db, used_mission_data)
            if not used_mission:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="미션 등록 중 오류가 발생했습니다"
                )
                
        # 이미 완료된 미션인지 확인
        if used_mission.COUNT >= used_mission.MAX_COUNT:
            logger.warning(f"이미 완료된 미션: 계정 ID {request.ACCOUNT_ID}, 미션 ID {request.MISSION_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 완료된 미션입니다"
            )
            
        # 미션 완료 처리 (MAX_COUNT로 설정)
        update_data = mission_schema.UsedMissionUpdate(COUNT=used_mission.MAX_COUNT)
        completed_mission = mission_crud.update_used_mission(db, used_mission.USED_MISSION_ID, update_data)
        if not completed_mission:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="미션 완료 처리 중 오류가 발생했습니다"
            )
            
        # 이자율 업데이트
        mission_crud.update_account_interest_rate(db, request.ACCOUNT_ID)
            
        logger.info(f"일회성 미션 완료 처리: 계정 ID {request.ACCOUNT_ID}, 미션 ID {request.MISSION_ID}")
        return completed_mission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일회성 미션 완료 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일회성 미션 완료 중 오류 발생: {str(e)}"
        )

# 계정 이자율 조회
@router.get("/account/{account_id}/interest", response_model=mission_schema.InterestRateResponse)
async def get_account_interest_rate(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 이자율 조회 요청: 계정 ID {account_id}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 이자율을 조회할 권한이 없습니다"
            )
            
        # 미션 이자율 계산
        mission_summary = mission_crud.get_account_mission_summary(db, account_id)
        
        # 응답 데이터 구성
        response = {
            "ACCOUNT_ID": account_id,
            "BASE_INTEREST_RATE": account.INTEREST_RATE - mission_summary["total_rate"],
            "MISSION_INTEREST_RATE": mission_summary["total_rate"],
            "TOTAL_INTEREST_RATE": account.INTEREST_RATE
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 이자율 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 이자율 조회 중 오류 발생: {str(e)}"
        )

# 계정의 미션 삭제 (미션 등록 취소)
@router.delete("/account/{account_id}/mission/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_mission_from_account(
    account_id: int,
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정의 미션 삭제 요청: 계정 ID {account_id}, 미션 ID {mission_id}")
        
        # 계정 존재 여부 및 소유권 확인
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
            
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 계정의 미션을 삭제할 권한이 없습니다"
            )
            
        # 미션 등록 여부 확인
        used_mission = mission_crud.get_used_mission(db, account_id, mission_id)
        if not used_mission:
            logger.warning(f"등록되지 않은 미션: 계정 ID {account_id}, 미션 ID {mission_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이 계정에 등록되지 않은 미션입니다"
            )
            
        # 완료된 미션인 경우 (이자율에 영향을 미치는 경우)
        was_completed = used_mission.COUNT >= used_mission.MAX_COUNT
        
        # 미션 삭제
        success = mission_crud.delete_used_mission(db, used_mission.USED_MISSION_ID)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="미션 삭제 중 오류가 발생했습니다"
            )
            
        # 이자율 업데이트 (이전에 완료된 미션이었다면)
        if was_completed:
            mission_crud.update_account_interest_rate(db, account_id)
            
        logger.info(f"계정의 미션 삭제 완료: 계정 ID {account_id}, 미션 ID {mission_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정의 미션 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정의 미션 삭제 중 오류 발생: {str(e)}"
        )

