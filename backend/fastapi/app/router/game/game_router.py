from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
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

# 로그인한 사용자의 팀 전체 경기 일정 조회
@router.get("/user-team-schedule/all", response_model=List[game_schema.UserTeamGameScheduleResponse])
async def read_user_team_all_schedule(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"로그인 사용자 팀 전체 경기 일정 조회: 사용자 ID {current_user.USER_ID}")
        
        # 1. 사용자의 계정에서 팀 ID 조회
        # 현재 사용자의 계정 목록 조회
        accounts = db.query(models.Account).filter(models.Account.USER_ID == current_user.USER_ID).all()
        
        if not accounts:
            logger.warning(f"사용자 ID {current_user.USER_ID}에 연결된 계정이 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 계정이 없습니다"
            )
        
        # 첫 번째 계정의 팀 ID 사용 (여러 계정이 있을 경우)
        team_id = accounts[0].TEAM_ID
        
        if not team_id:
            logger.warning(f"사용자 계정에 연결된 팀 ID가 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 팀 정보가 없습니다"
            )
        
        # 2. 팀 존재 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"팀 ID {team_id}를 찾을 수 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="팀 정보를 찾을 수 없습니다"
            )
        
        # 3. 팀 경기 일정 조회 (전체)
        schedules = db.query(models.GameSchedule).filter(
            or_(
                models.GameSchedule.HOME_TEAM_ID == team_id,
                models.GameSchedule.AWAY_TEAM_ID == team_id
            )
        ).order_by(models.GameSchedule.DATE).all()
        
        # 4. 응답 데이터 구성
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
                "away_team_name": away_team.TEAM_NAME if away_team else None,
                "is_home": schedule.HOME_TEAM_ID == team_id  # 응원 팀이 홈 팀인지 여부
            }
            
            result.append(schedule_dict)
        
        logger.info(f"조회된 전체 경기 일정 수: {len(result)}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 전체 경기 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 전체 경기 일정 조회 중 오류 발생: {str(e)}"
        )

# 로그인한 사용자의 팀 월별 경기 일정 조회
@router.get("/user-team-schedule/month/{month}", response_model=List[game_schema.UserTeamGameScheduleResponse])
async def read_user_team_monthly_schedule(
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"로그인 사용자 팀 월별 경기 일정 조회: 사용자 ID {current_user.USER_ID}, 월 {month}")
        
        # 월 범위 확인
        if month < 1 or month > 12:
            logger.warning(f"유효하지 않은 월: {month}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월은 1부터 12 사이의 값이어야 합니다"
            )
        
        # 1. 사용자의 계정에서 팀 ID 조회
        # 현재 사용자의 계정 목록 조회
        accounts = db.query(models.Account).filter(models.Account.USER_ID == current_user.USER_ID).all()
        
        if not accounts:
            logger.warning(f"사용자 ID {current_user.USER_ID}에 연결된 계정이 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 계정이 없습니다"
            )
        
        # 첫 번째 계정의 팀 ID 사용 (여러 계정이 있을 경우)
        team_id = accounts[0].TEAM_ID
        
        if not team_id:
            logger.warning(f"사용자 계정에 연결된 팀 ID가 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연결된 팀 정보가 없습니다"
            )
        
        # 2. 팀 존재 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"팀 ID {team_id}를 찾을 수 없습니다")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="팀 정보를 찾을 수 없습니다"
            )
            
        # 3. 현재 연도 가져오기
        current_year = datetime.now().year
        
        # 4. 해당 월의 시작일과 종료일 계산
        start_date = date(current_year, month, 1)
        
        # 월에 따라 종료일 계산
        if month == 12:
            end_date = date(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(current_year, month + 1, 1) - timedelta(days=1)
        
        # 5. 팀 경기 일정 조회 (월별)
        schedules = db.query(models.GameSchedule).filter(
            or_(
                models.GameSchedule.HOME_TEAM_ID == team_id,
                models.GameSchedule.AWAY_TEAM_ID == team_id
            ),
            models.GameSchedule.DATE >= start_date,
            models.GameSchedule.DATE <= end_date
        ).order_by(models.GameSchedule.DATE).all()
        
        # 6. 응답 데이터 구성
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
                "away_team_name": away_team.TEAM_NAME if away_team else None,
                "is_home": schedule.HOME_TEAM_ID == team_id  # 응원 팀이 홈 팀인지 여부
            }
            
            result.append(schedule_dict)
        
        logger.info(f"조회된 {month}월 경기 일정 수: {len(result)}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 월별 경기 일정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 월별 경기 일정 조회 중 오류 발생: {str(e)}"
        )
    
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