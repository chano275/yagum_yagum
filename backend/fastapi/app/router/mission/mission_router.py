from fastapi import APIRouter, Depends, HTTPException, status,FastAPI,File,UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db
import models
import os
import io
from PIL import Image
from router.mission import mission_schema, mission_crud
from router.user.user_router import get_current_user
from datetime import datetime
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

# # 계정 미션 목록 조회
# @router.get("/account/{account_id}", response_model=List[mission_schema.UsedMissionDetailResponse])
# async def read_account_missions(
#     account_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"계정 미션 목록 조회: 계정 ID {account_id}")
        
#         # 계정 존재 여부 및 소유권 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
#         if not account:
#             logger.warning(f"계정을 찾을 수 없음: {account_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="계정을 찾을 수 없습니다"
#             )
            
#         if account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="이 계정의 미션 정보를 조회할 권한이 없습니다"
#             )
            
#         # 미션 목록 조회
#         used_missions = mission_crud.get_used_missions_by_account(db, account_id)
        
#         # 응답 형식에 맞게 변환
#         result = []
#         for used_mission in used_missions:
#             mission = mission_crud.get_mission_by_id(db, used_mission.MISSION_ID)
#             result.append({
#                 "USED_MISSION_ID": used_mission.USED_MISSION_ID,
#                 "ACCOUNT_ID": used_mission.ACCOUNT_ID,
#                 "MISSION_ID": used_mission.MISSION_ID,
#                 "COUNT": used_mission.COUNT,
#                 "MAX_COUNT": used_mission.MAX_COUNT,
#                 "MISSION_RATE": used_mission.MISSION_RATE,
#                 "created_at": used_mission.created_at,
#                 "mission": mission
#             })
            
#         return result
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"계정 미션 목록 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"계정 미션 목록 조회 중 오류 발생: {str(e)}"
#         )

# # 계정의 미션 삭제 (미션 등록 취소)
# @router.delete("/account/{account_id}/mission/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_mission_from_account(
#     account_id: int,
#     mission_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"계정의 미션 삭제 요청: 계정 ID {account_id}, 미션 ID {mission_id}")
        
#         # 계정 존재 여부 및 소유권 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
#         if not account:
#             logger.warning(f"계정을 찾을 수 없음: {account_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="계정을 찾을 수 없습니다"
#             )
            
#         if account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="이 계정의 미션을 삭제할 권한이 없습니다"
#             )
            
#         # 미션 등록 여부 확인
#         used_mission = mission_crud.get_used_mission(db, account_id, mission_id)
#         if not used_mission:
#             logger.warning(f"등록되지 않은 미션: 계정 ID {account_id}, 미션 ID {mission_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="이 계정에 등록되지 않은 미션입니다"
#             )
            
#         # 완료된 미션인 경우 (이자율에 영향을 미치는 경우)
#         was_completed = used_mission.COUNT >= used_mission.MAX_COUNT
        
#         # 미션 삭제
#         success = mission_crud.delete_used_mission(db, used_mission.USED_MISSION_ID)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="미션 삭제 중 오류가 발생했습니다"
#             )
            
#         # 이자율 업데이트 (이전에 완료된 미션이었다면)
#         if was_completed:
#             mission_crud.update_account_interest_rate(db, account_id)
            
#         logger.info(f"계정의 미션 삭제 완료: 계정 ID {account_id}, 미션 ID {mission_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"계정의 미션 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"계정의 미션 삭제 중 오류 발생: {str(e)}"
#         )

# 순위 예측 생성
@router.post("/rank-predictions", response_model=mission_schema.TeamRankPredictionResponse)
async def create_team_rank_prediction(
    prediction: mission_schema.TeamRankPredictionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"순위 예측 생성 요청: 사용자 ID {current_user.USER_ID}")
        
        # 1. 사용자의 계정 확인 (첫 번째 계정 사용)
        account = db.query(models.Account).filter(
            models.Account.USER_ID == current_user.USER_ID
        ).first()
        
        if not account:
            logger.warning(f"사용자 ID {current_user.USER_ID}에 연결된 계정이 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 계정이 없습니다"
            )
        
        # 2. 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == prediction.TEAM_ID).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {prediction.TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
        
        # 3. 순위 유효성 검사
        if prediction.PREDICTED_RANK < 1 or prediction.PREDICTED_RANK > 10:  # KBO는 10개 팀
            logger.warning(f"유효하지 않은 순위: {prediction.PREDICTED_RANK}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="순위는 1부터 10 사이의 값이어야 합니다"
            )
        
        # 4. 해당 계정에 이미 예측이 있는지 확인 (해당 시즌에)
        existing_prediction = db.query(models.TeamRankPrediction).filter(
            models.TeamRankPrediction.ACCOUNT_ID == account.ACCOUNT_ID,
            models.TeamRankPrediction.SEASON_YEAR == prediction.SEASON_YEAR
        ).first()
        
        if existing_prediction:
            logger.warning(f"이미 해당 시즌에 예측이 있음: 계정 ID {account.ACCOUNT_ID}, 시즌 {prediction.SEASON_YEAR}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 시즌에 이미 예측을 등록했습니다"
            )
        
        # 5. 예측 저장
        new_prediction = models.TeamRankPrediction(
            ACCOUNT_ID=account.ACCOUNT_ID,
            TEAM_ID=prediction.TEAM_ID,
            PREDICTED_RANK=prediction.PREDICTED_RANK,
            SEASON_YEAR=prediction.SEASON_YEAR,
            IS_CORRECT=0,  # 초기값: 미확정
            created_at=datetime.now()
        )
        
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)
        
        # 6. 응답 준비
        response = {
            "PREDICTION_ID": new_prediction.PREDICTION_ID,
            "ACCOUNT_ID": new_prediction.ACCOUNT_ID,
            "TEAM_ID": new_prediction.TEAM_ID,
            "PREDICTED_RANK": new_prediction.PREDICTED_RANK,
            "SEASON_YEAR": new_prediction.SEASON_YEAR,
            "IS_CORRECT": new_prediction.IS_CORRECT,
            "created_at": new_prediction.created_at,
            "team_name": team.TEAM_NAME
        }
        
        logger.info(f"순위 예측 생성 완료: ID {new_prediction.PREDICTION_ID}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"순위 예측 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"순위 예측 생성 중 오류 발생: {str(e)}"
        )

# 사용자의 순위 예측 조회
@router.get("/rank-predictions/check", response_model=List[mission_schema.TeamRankPredictionResponse])
async def get_user_predictions(
    season_year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 순위 예측 조회: 사용자 ID {current_user.USER_ID}")
        
        # 1. 사용자의 계정 확인
        accounts = db.query(models.Account).filter(
            models.Account.USER_ID == current_user.USER_ID
        ).all()
        
        if not accounts:
            logger.warning(f"사용자 ID {current_user.USER_ID}에 연결된 계정이 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 계정이 없습니다"
            )
        
        # 계정 ID 목록
        account_ids = [account.ACCOUNT_ID for account in accounts]
        
        # 2. 순위 예측 조회
        query = db.query(models.TeamRankPrediction).filter(
            models.TeamRankPrediction.ACCOUNT_ID.in_(account_ids)
        )
        
        # 시즌 필터 적용
        if season_year:
            query = query.filter(models.TeamRankPrediction.SEASON_YEAR == season_year)
        
        predictions = query.order_by(models.TeamRankPrediction.created_at.desc()).all()
        
        # 3. 응답 준비
        result = []
        for prediction in predictions:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == prediction.TEAM_ID).first()
            
            prediction_dict = {
                "PREDICTION_ID": prediction.PREDICTION_ID,
                "ACCOUNT_ID": prediction.ACCOUNT_ID,
                "TEAM_ID": prediction.TEAM_ID,
                "PREDICTED_RANK": prediction.PREDICTED_RANK,
                "SEASON_YEAR": prediction.SEASON_YEAR,
                "IS_CORRECT": prediction.IS_CORRECT,
                # "created_at": prediction.created_at,
                "team_name": team.TEAM_NAME if team else "알 수 없음"
            }
            
            result.append(prediction_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 순위 예측 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 순위 예측 조회 중 오류 발생: {str(e)}"
        )
    
@router.post("/ocr", response_model=mission_schema.OCRResponse)
async def check_ocr(file: UploadFile = File(...)):
    """
    이미지 파일을 받아 OCR 처리하는 엔드포인트
    
    Args:
        file: 업로드된 이미지 파일
    
    Returns:
        OCRResponse: OCR 처리 결과
    """
    # 파일 확장자 검증
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}", "text": ""}
        )
    
    try:
        # 이미지 파일 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        ### TODO 
        '''
            OCR 모듈 이용해서 티켓번호 읽기 
            DB에 있는 티켓인지 검증
            티켓 사용한걸로 변경 -> ticket 테이블에 user_id 추가 -> 나중에 사용한 OCR 기록 보려고
            금리 적용 -> used_mission에 추가가
            
        '''
        
        
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"OCR 처리 중 오류 발생: {str(e)}", "text": ""}
        )
