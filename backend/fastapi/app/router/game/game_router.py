from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from database import get_db
import models
from router.game import game_schema, game_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 게임 일정 생성
@router.post("/schedule", response_model=game_schema.GameScheduleResponse)
async def create_game_schedule(
    game_schedule: game_schema.GameScheduleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"게임 일정 생성 시도: {game_schedule.DATE} - 홈팀 {game_schedule.HOME_TEAM_ID} vs 원정팀 {game_schedule.AWAY_TEAM_ID}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 팀 존재 여부 확인
        home_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_schedule.HOME_TEAM_ID).first()
        away_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_schedule.AWAY_TEAM_ID).first()
        
        if not home_team or not away_team:
            logger.warning(f"존재하지 않는 팀: 홈팀 {game_schedule.HOME_TEAM_ID} 또는 원정팀 {game_schedule.AWAY_TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
        
        # 중복 일정 확인
        existing_schedule = db.query(models.GameSchedule).filter(
            models.GameSchedule.DATE == game_schedule.DATE,
            models.GameSchedule.HOME_TEAM_ID == game_schedule.HOME_TEAM_ID,
            models.GameSchedule.AWAY_TEAM_ID == game_schedule.AWAY_TEAM_ID
        ).first()
        
        if existing_schedule:
            logger.warning(f"중복 일정: {game_schedule.DATE} - 홈팀 {game_schedule.HOME_TEAM_ID} vs 원정팀 {game_schedule.AWAY_TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 일정입니다"
            )
        
        # 일정 생성
        new_schedule = game_crud.create_game_schedule(db, game_schedule)
        logger.info(f"게임 일정 생성 완료: ID {new_schedule.GAME_SCHEDULE_KEY}")
        
        return new_schedule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게임 일정 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 일정 생성 중 오류 발생: {str(e)}"
        )

# 모든 게임 일정 조회
@router.get("/schedule", response_model=List[game_schema.GameScheduleDetailResponse])
async def read_game_schedules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 게임 일정 조회: skip={skip}, limit={limit}")
        
        schedules = game_crud.get_game_schedules(db, skip, limit)
        
        # 팀 이름 추가
        result = []
        for schedule in schedules:
            home_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.HOME_TEAM_ID).first()
            away_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.AWAY_TEAM_ID).first()
            
            schedule_dict = {
                "GAME_SCHEDULE_KEY": schedule.GAME_SCHEDULE_KEY,
                "DATE": schedule.DATE,
                "HOME_TEAM_ID": schedule.HOME_TEAM_ID,
                "AWAY_TEAM_ID": schedule.AWAY_TEAM_ID,
                "home_team_name": home_team.TEAM_NAME if home_team else None,
                "away_team_name": away_team.TEAM_NAME if away_team else None
            }
            
            result.append(schedule_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"게임 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 일정 조회 중 오류 발생: {str(e)}"
        )

# 특정 날짜 게임 일정 조회
@router.get("/schedule/date/{date}", response_model=List[game_schema.GameScheduleDetailResponse])
async def read_game_schedules_by_date(
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 날짜 게임 일정 조회: {date}")
        
        schedules = game_crud.get_game_schedules_by_date(db, date)
        
        # 팀 이름 추가
        result = []
        for schedule in schedules:
            home_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.HOME_TEAM_ID).first()
            away_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.AWAY_TEAM_ID).first()
            
            schedule_dict = {
                "GAME_SCHEDULE_KEY": schedule.GAME_SCHEDULE_KEY,
                "DATE": schedule.DATE,
                "HOME_TEAM_ID": schedule.HOME_TEAM_ID,
                "AWAY_TEAM_ID": schedule.AWAY_TEAM_ID,
                "home_team_name": home_team.TEAM_NAME if home_team else None,
                "away_team_name": away_team.TEAM_NAME if away_team else None
            }
            
            result.append(schedule_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"특정 날짜 게임 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 일정 조회 중 오류 발생: {str(e)}"
        )

# 날짜 범위 게임 일정 조회
@router.get("/schedule/range", response_model=List[game_schema.GameScheduleDetailResponse])
async def read_game_schedules_by_date_range(
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"날짜 범위 게임 일정 조회: {start_date} ~ {end_date}")
        
        # 날짜 유효성 검사
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="종료 날짜는 시작 날짜보다 이후여야 합니다"
            )
        
        schedules = game_crud.get_game_schedules_by_date_range(db, start_date, end_date)
        
        # 팀 이름 추가
        result = []
        for schedule in schedules:
            home_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.HOME_TEAM_ID).first()
            away_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.AWAY_TEAM_ID).first()
            
            schedule_dict = {
                "GAME_SCHEDULE_KEY": schedule.GAME_SCHEDULE_KEY,
                "DATE": schedule.DATE,
                "HOME_TEAM_ID": schedule.HOME_TEAM_ID,
                "AWAY_TEAM_ID": schedule.AWAY_TEAM_ID,
                "home_team_name": home_team.TEAM_NAME if home_team else None,
                "away_team_name": away_team.TEAM_NAME if away_team else None
            }
            
            result.append(schedule_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"날짜 범위 게임 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 일정 조회 중 오류 발생: {str(e)}"
        )

# 특정 팀 게임 일정 조회
@router.get("/schedule/team/{team_id}", response_model=List[game_schema.GameScheduleDetailResponse])
async def read_game_schedules_by_team(
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 팀 게임 일정 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
        
        schedules = game_crud.get_game_schedules_by_team(db, team_id, skip, limit)
        
        # 팀 이름 추가
        result = []
        for schedule in schedules:
            home_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.HOME_TEAM_ID).first()
            away_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.AWAY_TEAM_ID).first()
            
            schedule_dict = {
                "GAME_SCHEDULE_KEY": schedule.GAME_SCHEDULE_KEY,
                "DATE": schedule.DATE,
                "HOME_TEAM_ID": schedule.HOME_TEAM_ID,
                "AWAY_TEAM_ID": schedule.AWAY_TEAM_ID,
                "home_team_name": home_team.TEAM_NAME if home_team else None,
                "away_team_name": away_team.TEAM_NAME if away_team else None
            }
            
            result.append(schedule_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"특정 팀 게임 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 일정 조회 중 오류 발생: {str(e)}"
        )

# # 특정 게임 일정 조회
# @router.get("/schedule/{game_schedule_key}", response_model=game_schema.GameScheduleDetailResponse)
# async def read_game_schedule(
#     game_schedule_key: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         logger.info(f"특정 게임 일정 조회: 일정 ID {game_schedule_key}")
        
#         schedule = game_crud.get_game_schedule_by_id(db, game_schedule_key)
#         if not schedule:
#             logger.warning(f"존재하지 않는 게임 일정: {game_schedule_key}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 게임 일정입니다"
#             )
        
#         # 팀 이름 추가
#         home_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.HOME_TEAM_ID).first()
#         away_team = db.query(models.Team).filter(models.Team.TEAM_ID == schedule.AWAY_TEAM_ID).first()
        
#         schedule_dict = {
#             "GAME_SCHEDULE_KEY": schedule.GAME_SCHEDULE_KEY,
#             "DATE": schedule.DATE,
#             "HOME_TEAM_ID": schedule.HOME_TEAM_ID,
#             "AWAY_TEAM_ID": schedule.AWAY_TEAM_ID,
#             "home_team_name": home_team.TEAM_NAME if home_team else None,
#             "away_team_name": away_team.TEAM_NAME if away_team else None
#         }
        
#         return schedule_dict
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"특정 게임 일정 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"게임 일정 조회 중 오류 발생: {str(e)}"
#         )

# # 게임 일정 업데이트
# @router.put("/schedule/{game_schedule_key}", response_model=game_schema.GameScheduleResponse)
# async def update_game_schedule(
#     game_schedule_key: int,
#     game_schedule: game_schema.GameScheduleUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"게임 일정 업데이트 요청: 일정 ID {game_schedule_key}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 일정 존재 여부 확인
#         db_game_schedule = game_crud.get_game_schedule_by_id(db, game_schedule_key)
#         if not db_game_schedule:
#             logger.warning(f"존재하지 않는 게임 일정: {game_schedule_key}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 게임 일정입니다"
#             )
        
#         # 팀 ID가 변경된 경우 팀 존재 여부 확인
#         if game_schedule.HOME_TEAM_ID is not None:
#             home_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_schedule.HOME_TEAM_ID).first()
#             if not home_team:
#                 logger.warning(f"존재하지 않는 홈팀: {game_schedule.HOME_TEAM_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 홈팀입니다"
#                 )
        
#         if game_schedule.AWAY_TEAM_ID is not None:
#             away_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_schedule.AWAY_TEAM_ID).first()
#             if not away_team:
#                 logger.warning(f"존재하지 않는 원정팀: {game_schedule.AWAY_TEAM_ID}")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="존재하지 않는 원정팀입니다"
#                 )
        
#         # 일정 업데이트
#         updated_schedule = game_crud.update_game_schedule(db, game_schedule_key, game_schedule)
#         if not updated_schedule:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="일정 업데이트 중 오류가 발생했습니다"
#             )
        
#         logger.info(f"게임 일정 업데이트 완료: 일정 ID {game_schedule_key}")
#         return updated_schedule
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"게임 일정 업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"게임 일정 업데이트 중 오류 발생: {str(e)}"
#         )

# # 게임 일정 삭제
# @router.delete("/schedule/{game_schedule_key}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_game_schedule(
#     game_schedule_key: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"게임 일정 삭제 요청: 일정 ID {game_schedule_key}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 일정 존재 여부 확인
#         db_game_schedule = game_crud.get_game_schedule_by_id(db, game_schedule_key)
#         if not db_game_schedule:
#             logger.warning(f"존재하지 않는 게임 일정: {game_schedule_key}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 게임 일정입니다"
#             )
        
#         # 일정 삭제
#         success = game_crud.delete_game_schedule(db, game_schedule_key)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="일정 삭제 중 오류가 발생했습니다"
#             )
        
#         logger.info(f"게임 일정 삭제 완료: 일정 ID {game_schedule_key}")
#         return None
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"게임 일정 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"게임 일정 삭제 중 오류 발생: {str(e)}"
#         )

# # 게임 로그 생성
# @router.post("/log", response_model=game_schema.GameLogResponse)
# async def create_game_log(
#     game_log: game_schema.GameLogCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"게임 로그 생성 시도: {game_log.DATE} - 팀 {game_log.TEAM_ID}, 기록 유형 {game_log.RECORD_TYPE_ID}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 팀 존재 여부 확인
#         team = db.query(models.Team).filter(models.Team.TEAM_ID == game_log.TEAM_ID).first()
#         if not team:
#             logger.warning(f"존재하지 않는 팀: {game_log.TEAM_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 팀입니다"
#             )
        
#         # 기록 유형 존재 여부 확인
#         record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == game_log.RECORD_TYPE_ID).first()
#         if not record_type:
#             logger.warning(f"존재하지 않는 기록 유형: {game_log.RECORD_TYPE_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 기록 유형입니다"
#             )
        
#         # 게임 로그 생성
#         new_log = game_crud.create_game_log(db, game_log)
#         logger.info(f"게임 로그 생성 완료: ID {new_log.GAME_LOG_ID}")
        
#         return new_log
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"게임 로그 생성 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"게임 로그 생성 중 오류 발생: {str(e)}"
#         )

# 모든 게임 로그 조회
@router.get("/log", response_model=List[game_schema.GameLogDetailResponse])
async def read_game_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 게임 로그 조회: skip={skip}, limit={limit}")
        
        logs = game_crud.get_game_logs(db, skip, limit)
        
        # 팀 이름 및 기록 유형 이름 추가
        result = []
        for log in logs:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == log.TEAM_ID).first()
            record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == log.RECORD_TYPE_ID).first()
            
            log_dict = {
                "GAME_LOG_ID": log.GAME_LOG_ID,
                "DATE": log.DATE,
                "TEAM_ID": log.TEAM_ID,
                "RECORD_TYPE_ID": log.RECORD_TYPE_ID,
                "COUNT": log.COUNT,
                "team_name": team.TEAM_NAME if team else None,
                "record_name": record_type.RECORD_NAME if record_type else None
            }
            
            result.append(log_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"게임 로그 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 로그 조회 중 오류 발생: {str(e)}"
        )

# 특정 날짜 게임 로그 조회
@router.get("/log/date/{date}", response_model=List[game_schema.GameLogDetailResponse])
async def read_game_logs_by_date(
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 날짜 게임 로그 조회: {date}")
        
        logs = game_crud.get_game_logs_by_date(db, date)
        
        # 팀 이름 및 기록 유형 이름 추가
        result = []
        for log in logs:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == log.TEAM_ID).first()
            record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == log.RECORD_TYPE_ID).first()
            
            log_dict = {
                "GAME_LOG_ID": log.GAME_LOG_ID,
                "DATE": log.DATE,
                "TEAM_ID": log.TEAM_ID,
                "RECORD_TYPE_ID": log.RECORD_TYPE_ID,
                "COUNT": log.COUNT,
                "team_name": team.TEAM_NAME if team else None,
                "record_name": record_type.RECORD_NAME if record_type else None
            }
            
            result.append(log_dict)
        
        return result
        
    except Exception as e:
        logger.error(f"특정 날짜 게임 로그 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 로그 조회 중 오류 발생: {str(e)}"
        )

# 특정 팀 게임 로그 조회
@router.get("/log/team/{team_id}", response_model=List[game_schema.GameLogDetailResponse])
async def read_game_logs_by_team(
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 팀 게임 로그 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
        
        logs = game_crud.get_game_logs_by_team(db, team_id, skip, limit)
        
        # 기록 유형 이름 추가
        result = []
        for log in logs:
            record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == log.RECORD_TYPE_ID).first()
            
            log_dict = {
                "GAME_LOG_ID": log.GAME_LOG_ID,
                "DATE": log.DATE,
                "TEAM_ID": log.TEAM_ID,
                "RECORD_TYPE_ID": log.RECORD_TYPE_ID,
                "COUNT": log.COUNT,
                "team_name": team.TEAM_NAME,
                "record_name": record_type.RECORD_NAME if record_type else None
            }
            
            result.append(log_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"특정 팀 게임 로그 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 로그 조회 중 오류 발생: {str(e)}"
        )

# # 게임 결과 기록
# @router.post("/result", response_model=game_schema.GameResultResponse)
# async def record_game_result(
#     game_result: game_schema.GameResultCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"게임 결과 기록 시도: {game_result.DATE} - 홈팀 {game_result.HOME_TEAM_ID} vs 원정팀 {game_result.AWAY_TEAM_ID}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 팀 존재 여부 확인
#         home_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_result.HOME_TEAM_ID).first()
#         away_team = db.query(models.Team).filter(models.Team.TEAM_ID == game_result.AWAY_TEAM_ID).first()
        
#         if not home_team or not away_team:
#             logger.warning(f"존재하지 않는 팀: 홈팀 {game_result.HOME_TEAM_ID} 또는 원정팀 {game_result.AWAY_TEAM_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 팀입니다"
#             )
        
#         # 결과 유효성 검사
#         valid_results = ["HOME_WIN", "AWAY_WIN", "DRAW"]
#         if game_result.RESULT not in valid_results:
#             logger.warning(f"유효하지 않은 게임 결과: {game_result.RESULT}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="유효하지 않은 게임 결과입니다. 'HOME_WIN', 'AWAY_WIN', 'DRAW' 중 하나여야 합니다."
#             )
        
#         # 점수와 결과 일치 여부 검사
#         if game_result.RESULT == "HOME_WIN" and game_result.HOME_SCORE <= game_result.AWAY_SCORE:
#             logger.warning(f"점수와 결과 불일치: 홈팀 승리인데 홈팀 점수 {game_result.HOME_SCORE} <= 원정팀 점수 {game_result.AWAY_SCORE}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="점수와 결과가 일치하지 않습니다"
#             )
        
#         if game_result.RESULT == "AWAY_WIN" and game_result.HOME_SCORE >= game_result.AWAY_SCORE:
#             logger.warning(f"점수와 결과 불일치: 원정팀 승리인데 홈팀 점수 {game_result.HOME_SCORE} >= 원정팀 점수 {game_result.AWAY_SCORE}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="점수와 결과가 일치하지 않습니다"
#             )
        
#         if game_result.RESULT == "DRAW" and game_result.HOME_SCORE != game_result.AWAY_SCORE:
#             logger.warning(f"점수와 결과 불일치: 무승부인데 홈팀 점수 {game_result.HOME_SCORE} != 원정팀 점수 {game_result.AWAY_SCORE}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="점수와 결과가 일치하지 않습니다"
#             )
        
#         # 게임 결과 기록
#         result = game_crud.record_game_result(db, game_result)
#         if not result:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="게임 결과 기록 중 오류가 발생했습니다"
#             )
        
#         logger.info(f"게임 결과 기록 완료: {game_result.DATE} - 홈팀 {game_result.HOME_TEAM_ID} vs 원정팀 {game_result.AWAY_TEAM_ID}")
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"게임 결과 기록 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"게임 결과 기록 중 오류 발생: {str(e)}"
#         )

# 팀 전적 조회
@router.get("/team/{team_id}/record", response_model=game_schema.TeamRecordResponse)
async def get_team_record(
    team_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 전적 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
        
        record = game_crud.get_team_record(db, team_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="팀 전적 조회 중 오류가 발생했습니다"
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 전적 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 전적 조회 중 오류 발생: {str(e)}"
        )

# 모든 팀 전적 조회 (순위표)
@router.get("/team/ranking", response_model=List[game_schema.TeamRecordResponse])
async def get_team_rankings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 팀 전적 조회 (순위표): skip={skip}, limit={limit}")
        
        rankings = game_crud.get_all_team_records(db, skip, limit)
        
        return rankings
        
    except Exception as e:
        logger.error(f"팀 순위표 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 순위표 조회 중 오류 발생: {str(e)}"
        )

# 게임 로그 업데이트
@router.put("/log/{game_log_id}", response_model=game_schema.GameLogResponse)
async def update_game_log(
    game_log_id: int,
    game_log: game_schema.GameLogUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"게임 로그 업데이트 요청: 로그 ID {game_log_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 게임 로그 존재 여부 확인
        db_game_log = game_crud.get_game_log_by_id(db, game_log_id)
        if not db_game_log:
            logger.warning(f"존재하지 않는 게임 로그: {game_log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 게임 로그입니다"
            )
        
        # 팀 ID가 변경된 경우 팀 존재 여부 확인
        if game_log.TEAM_ID is not None:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == game_log.TEAM_ID).first()
            if not team:
                logger.warning(f"존재하지 않는 팀: {game_log.TEAM_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 팀입니다"
                )
        
        # 기록 유형 ID가 변경된 경우 기록 유형 존재 여부 확인
        if game_log.RECORD_TYPE_ID is not None:
            record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == game_log.RECORD_TYPE_ID).first()
            if not record_type:
                logger.warning(f"존재하지 않는 기록 유형: {game_log.RECORD_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 기록 유형입니다"
                )
        
        # 게임 로그 업데이트
        updated_log = game_crud.update_game_log(db, game_log_id, game_log)
        if not updated_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게임 로그 업데이트 중 오류가 발생했습니다"
            )
        
        logger.info(f"게임 로그 업데이트 완료: 로그 ID {game_log_id}")
        return updated_log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게임 로그 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 로그 업데이트 중 오류 발생: {str(e)}"
        )

# 게임 로그 삭제
@router.delete("/log/{game_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_log(
    game_log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"게임 로그 삭제 요청: 로그 ID {game_log_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 게임 로그 존재 여부 확인
        db_game_log = game_crud.get_game_log_by_id(db, game_log_id)
        if not db_game_log:
            logger.warning(f"존재하지 않는 게임 로그: {game_log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 게임 로그입니다"
            )
        
        # 게임 로그 삭제
        success = game_crud.delete_game_log(db, game_log_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="게임 로그 삭제 중 오류가 발생했습니다"
            )
        
        logger.info(f"게임 로그 삭제 완료: 로그 ID {game_log_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게임 로그 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 로그 삭제 중 오류 발생: {str(e)}"
        )