from fastapi import APIRouter, Depends, HTTPException, status,FastAPI,File,UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db
import models
import os
import io
import tempfile
from PIL import Image
import utils.ticket_certificate as ticket_ocr
from router.mission import mission_schema, mission_crud
from router.user.user_router import get_current_user
from datetime import datetime

# OCR 모듈 import
from utils.ticket_certificate import decode_qr_and_barcodes, clova_ocr

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
    
# OCR 엔드포인트 추가
@router.post("/ocr", response_model=mission_schema.OCRResponse)
async def check_ocr(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    이미지 파일을 받아 OCR 처리하여 티켓을 검증하고 미션 완료 처리
    """
    try:
        logger.info(f"OCR 요청: 사용자 ID {current_user.USER_ID}")
        
        # 파일 확장자 검증
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"지원하지 않는 파일 형식: {file_ext}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}", "text": ""}
            )
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            contents = await file.read()
            temp_file.write(contents)
        
        try:
            # OCR 모듈을 이용해 티켓 번호 읽기
            # 먼저 QR 코드/바코드 검사 시도
            ticket_number = decode_qr_and_barcodes(temp_file_path)
            
            # QR/바코드 인식 실패 시 Clova OCR 시도
            if not ticket_number:
                ticket_number = clova_ocr(temp_file_path)
            
            # 티켓 번호를 찾지 못한 경우
            if not ticket_number:
                logger.warning("티켓 번호를 인식할 수 없음")
                return mission_schema.OCRResponse(
                    success=False,
                    text="",
                    error="티켓 번호를 인식할 수 없습니다."
                )
            
            # DB에 있는 티켓인지 검증
            ticket = db.query(models.TicketNumber).filter(
                models.TicketNumber.TICKET_NUMBER == ticket_number
            ).first()
            
            if not ticket:
                logger.warning(f"유효하지 않은 티켓 번호: {ticket_number}")
                return mission_schema.OCRResponse(
                    success=False,
                    text=ticket_number,
                    error="유효하지 않은 티켓 번호입니다."
                )
            
            # 이미 사용된 티켓인지 확인 (ACCOUNT_ID가 NULL이 아닌 경우)
            if ticket.ACCOUNT_ID is not None:
                logger.warning(f"이미 사용된 티켓: {ticket_number}")
                return mission_schema.OCRResponse(
                    success=False,
                    text=ticket_number,
                    error="이미 사용된 티켓입니다."
                )
            
            # 사용자의 계정 정보 조회
            account = db.query(models.Account).filter(
                models.Account.USER_ID == current_user.USER_ID
            ).first()
            
            if not account:
                logger.warning(f"사용자에게 연결된 계정이 없음: 사용자 ID {current_user.USER_ID}")
                return mission_schema.OCRResponse(
                    success=False,
                    text=ticket_number,
                    error="계정 정보를 찾을 수 없습니다."
                )
            
            # 티켓에 계정 연결
            ticket.ACCOUNT_ID = account.ACCOUNT_ID
            ticket.VERIFIED_STATUS = True
            
            # 입장권 인증 미션 찾기 (미션 이름 "직관 인증시 우대금리")
            mission = db.query(models.Mission).filter(
                models.Mission.MISSION_NAME == "직관 인증시 우대금리"
            ).first()
            
            if not mission:
                logger.warning("직관 인증 미션 정보를 찾을 수 없음")
                db.commit()  # 티켓 상태는 업데이트
                return mission_schema.OCRResponse(
                    success=True,
                    text=ticket_number,
                    error="티켓은 인증되었으나, 해당 미션을 찾을 수 없습니다."
                )
            
            # 이미 등록된 미션인지 확인
            used_mission = mission_crud.get_used_mission(db, account.ACCOUNT_ID, mission.MISSION_ID)
            
            if not used_mission:
                # 미션이 등록되어 있지 않으면 자동 등록
                used_mission_data = mission_schema.UsedMissionCreate(
                    ACCOUNT_ID=account.ACCOUNT_ID,
                    MISSION_ID=mission.MISSION_ID,
                    COUNT=0
                )
                used_mission = mission_crud.create_used_mission(db, used_mission_data)
                if not used_mission:
                    logger.error("미션 등록 중 오류 발생")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="미션 등록 중 오류가 발생했습니다"
                    )
            
            # 카운트가 최대치에 도달했는지 확인
            if used_mission.COUNT >= used_mission.MAX_COUNT:
                # 티켓 상태는 업데이트하지만 미션 카운트는 증가시키지 않음
                db.commit()
                logger.warning(f"미션 최대 횟수({used_mission.MAX_COUNT}) 도달: 계정 ID {account.ACCOUNT_ID}")
                return mission_schema.OCRResponse(
                    success=True,
                    text=ticket_number,
                    error=f"티켓은 인증되었으나, 미션 최대 적용 횟수({used_mission.MAX_COUNT}회)에 도달하여 금리가 추가 적용되지 않았습니다."
                )
            
            # 미션 카운트 증가
            used_mission.COUNT += 1
            
            # 변경사항 커밋
            db.commit()
            
            # 이전에 호출하던 이자율 업데이트 함수 대신, 이자 재계산 함수 호출
            from utils.interest_utils import recalculate_interest_history
            await recalculate_interest_history(db,account.ACCOUNT_ID)
            
            # 성공 응답
            logger.info(f"티켓 인증 및 미션 적용 성공: 계정 ID {account.ACCOUNT_ID}, 티켓 번호 {ticket_number}")
            return mission_schema.OCRResponse(
                success=True,
                text=ticket_number,
                error=None
            )
                
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"OCR 처리 중 오류 발생: {str(e)}")
        return mission_schema.OCRResponse(
            success=False,
            text="",
            error=f"OCR 처리 중 오류 발생: {str(e)}"
        )