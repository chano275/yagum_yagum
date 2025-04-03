from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from database import get_db
import models
from router.player import player_schema, player_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 모든 선수 조회
@router.get("/", response_model=List[player_schema.PlayerResponse])
async def read_players(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 선수 조회: skip={skip}, limit={limit}")
        players = player_crud.get_all_players(db, skip, limit)
        return players
    except Exception as e:
        logger.error(f"선수 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 조회 중 오류 발생: {str(e)}"
        )

# 선수 기록 조회
@router.get("/{player_id}/records", response_model=List[player_schema.PlayerRecordDetailResponse])
async def read_player_records(
    player_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 기록 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        records = player_crud.get_player_records(db, player_id, start_date, end_date)
        
        # 선수 이름, 팀 이름, 기록 유형 이름 추가
        result = []
        for record in records:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == record.TEAM_ID).first()
            record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == record.RECORD_TYPE_ID).first()
            
            record_dict = {
                "PLAYER_RECORD_ID": record.PLAYER_RECORD_ID,
                "DATE": record.DATE,
                "PLAYER_ID": record.PLAYER_ID,
                "TEAM_ID": record.TEAM_ID,
                "RECORD_TYPE_ID": record.RECORD_TYPE_ID,
                "COUNT": record.COUNT,
                "player_name": db_player.PLAYER_NAME,
                "team_name": team.TEAM_NAME if team else None,
                "record_name": record_type.RECORD_NAME if record_type else None
            }
            
            result.append(record_dict)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 기록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 기록 조회 중 오류 발생: {str(e)}"
        )

# 선수 일일 보고서 조회
@router.get("/{player_id}/daily-reports", response_model=List[player_schema.DailyReportResponse])
async def get_player_daily_reports(
    player_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 일일 보고서 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        reports = player_crud.get_player_daily_reports(db, player_id, skip, limit)
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 일일 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 일일 보고서 조회 중 오류 발생: {str(e)}"
        )

# 선수 주간 보고서 조회
@router.get("/{player_id}/weekly-reports", response_model=List[player_schema.WeeklyReportResponse])
async def get_player_weekly_reports(
    player_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 주간 보고서 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        reports = player_crud.get_player_weekly_reports(db, player_id, skip, limit)
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 주간 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 주간 보고서 조회 중 오류 발생: {str(e)}"
        )

# 선수 출전 기록 조회
@router.get("/{player_id}/runs", response_model=List[player_schema.PlayerRunResponse])
async def get_player_run_history(
    player_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 출전 기록 조회: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        runs = player_crud.get_player_run_history(db, player_id, start_date, end_date)
        return runs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 출전 기록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 출전 기록 조회 중 오류 발생: {str(e)}"
        )

@router.get("/{team_id}", response_model=List[player_schema.PlayerResponse])
async def read_players_by_team(
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 ID {team_id}에 속한 선수 목록 조회: skip={skip}, limit={limit}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        players = player_crud.get_players_by_team(db, team_id, skip, limit)
        return players
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀별 선수 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀별 선수 목록 조회 중 오류 발생: {str(e)}"
        )