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

# 특정 팀의 선수 조회
@router.get("/team/{team_id}", response_model=List[player_schema.PlayerResponse])
async def read_players_by_team(
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 선수 조회: 팀 ID {team_id}")
        
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
        logger.error(f"팀 선수 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 선수 조회 중 오류 발생: {str(e)}"
        )

# 특정 포지션의 선수 조회
@router.get("/type/{player_type_id}", response_model=List[player_schema.PlayerResponse])
async def read_players_by_type(
    player_type_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"포지션 선수 조회: 포지션 ID {player_type_id}")
        
        # 포지션 타입 존재 여부 확인
        player_type = player_crud.get_player_type_by_id(db, player_type_id)
        if not player_type:
            logger.warning(f"존재하지 않는 포지션: {player_type_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 포지션입니다"
            )
            
        players = player_crud.get_players_by_type(db, player_type_id, skip, limit)
        return players
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"포지션 선수 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"포지션 선수 조회 중 오류 발생: {str(e)}"
        )

# 특정 선수 조회
@router.get("/{player_id}", response_model=player_schema.PlayerDetailResponse)
async def read_player(
    player_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 조회: 선수 ID {player_id}")
        
        player = player_crud.get_player_by_id(db, player_id)
        if not player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수 타입 정보 가져오기
        player_type = player_crud.get_player_type_by_id(db, player.PLAYER_TYPE_ID)
        
        # 팀 정보 가져오기
        team = db.query(models.Team).filter(models.Team.TEAM_ID == player.TEAM_ID).first()
        
        # 응답 데이터 구성
        result = {
            "PLAYER_ID": player.PLAYER_ID,
            "TEAM_ID": player.TEAM_ID,
            "PLAYER_NUM": player.PLAYER_NUM,
            "PLAYER_TYPE_ID": player.PLAYER_TYPE_ID,
            "PLAYER_NAME": player.PLAYER_NAME,
            "PLAYER_IMAGE_URL": player.PLAYER_IMAGE_URL,
            "LIKE_COUNT": player.LIKE_COUNT,
            "created_at": player.created_at,
            "player_type": player_type,
            "team_name": team.TEAM_NAME if team else None
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 조회 중 오류 발생: {str(e)}"
        )

# 선수 생성
@router.post("/", response_model=player_schema.PlayerResponse)
async def create_player(
    player: player_schema.PlayerCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 생성 시도: {player.PLAYER_NAME}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == player.TEAM_ID).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {player.TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 포지션 타입 존재 여부 확인
        player_type = player_crud.get_player_type_by_id(db, player.PLAYER_TYPE_ID)
        if not player_type:
            logger.warning(f"존재하지 않는 포지션: {player.PLAYER_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 포지션입니다"
            )
            
        # 같은 팀에 동일한 이름의 선수가 있는지 확인
        existing_player = player_crud.get_player_by_name_and_team(db, player.PLAYER_NAME, player.TEAM_ID)
        if existing_player:
            logger.warning(f"이미 존재하는 선수: {player.PLAYER_NAME}, 팀 ID {player.TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 팀에 이미 존재하는 선수 이름입니다"
            )
            
        # 선수 생성
        new_player = player_crud.create_player(db, player)
        logger.info(f"선수 생성 완료: ID {new_player.PLAYER_ID}")
        
        return new_player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 생성 중 오류 발생: {str(e)}"
        )

# 선수 정보 업데이트
@router.put("/{player_id}", response_model=player_schema.PlayerResponse)
async def update_player(
    player_id: int,
    player: player_schema.PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 업데이트 요청: 선수 ID {player_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 팀 ID 변경 시 팀 존재 여부 확인
        if player.TEAM_ID is not None:
            team = db.query(models.Team).filter(models.Team.TEAM_ID == player.TEAM_ID).first()
            if not team:
                logger.warning(f"존재하지 않는 팀: {player.TEAM_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 팀입니다"
                )
                
        # 포지션 타입 ID 변경 시 포지션 존재 여부 확인
        if player.PLAYER_TYPE_ID is not None:
            player_type = player_crud.get_player_type_by_id(db, player.PLAYER_TYPE_ID)
            if not player_type:
                logger.warning(f"존재하지 않는 포지션: {player.PLAYER_TYPE_ID}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="존재하지 않는 포지션입니다"
                )
                
        # 이름 변경 시 중복 확인
        if player.PLAYER_NAME is not None and player.PLAYER_NAME != db_player.PLAYER_NAME:
            team_id = player.TEAM_ID if player.TEAM_ID is not None else db_player.TEAM_ID
            existing_player = player_crud.get_player_by_name_and_team(db, player.PLAYER_NAME, team_id)
            if existing_player:
                logger.warning(f"이미 존재하는 선수: {player.PLAYER_NAME}, 팀 ID {team_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="해당 팀에 이미 존재하는 선수 이름입니다"
                )
                
        # 선수 업데이트
        updated_player = player_crud.update_player(db, player_id, player)
        if not updated_player:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="선수 업데이트 중 오류가 발생했습니다"
            )
            
        logger.info(f"선수 업데이트 완료: 선수 ID {player_id}")
        return updated_player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 업데이트 중 오류 발생: {str(e)}"
        )

# 선수 삭제
@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 삭제 요청: 선수 ID {player_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수 삭제
        success = player_crud.delete_player(db, player_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="선수 삭제 중 오류가 발생했습니다"
            )
            
        logger.info(f"선수 삭제 완료: 선수 ID {player_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 삭제 중 오류 발생: {str(e)}"
        )

# 선수 좋아요 증가
@router.post("/{player_id}/like", response_model=player_schema.PlayerLikeResponse)
async def like_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 좋아요 요청: 선수 ID {player_id}")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 좋아요 증가
        updated_player = player_crud.increase_player_like(db, player_id)
        if not updated_player:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="좋아요 업데이트 중 오류가 발생했습니다"
            )
            
        # 응답 데이터
        result = {
            "PLAYER_ID": updated_player.PLAYER_ID,
            "PLAYER_NAME": updated_player.PLAYER_NAME,
            "LIKE_COUNT": updated_player.LIKE_COUNT
        }
        
        logger.info(f"선수 좋아요 업데이트 완료: 선수 ID {player_id}, 좋아요 수 {updated_player.LIKE_COUNT}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 좋아요 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 좋아요 중 오류 발생: {str(e)}"
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

# 선수 기록 생성/업데이트
@router.post("/{player_id}/records", response_model=player_schema.PlayerRecordResponse)
async def create_player_record(
    player_id: int,
    record: player_schema.PlayerRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 기록 생성/업데이트 요청: 선수 ID {player_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == record.TEAM_ID).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {record.TEAM_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 기록 유형 존재 여부 확인
        record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == record.RECORD_TYPE_ID).first()
        if not record_type:
            logger.warning(f"존재하지 않는 기록 유형: {record.RECORD_TYPE_ID}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 기록 유형입니다"
            )
            
        # 선수 ID 일치 여부 확인
        if record.PLAYER_ID != player_id:
            logger.warning(f"URL의 선수 ID와 요청 데이터의 선수 ID 불일치: URL {player_id}, 데이터 {record.PLAYER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL의 선수 ID와 요청 데이터의 선수 ID가 일치하지 않습니다"
            )
            
        # 기록 생성/업데이트
        player_record = player_crud.create_player_record(db, record)
        
        logger.info(f"선수 기록 생성/업데이트 완료: 선수 ID {player_id}")
        return player_record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 기록 생성/업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 기록 생성/업데이트 중 오류 발생: {str(e)}"
        )

# 선수 월간 통계 조회
@router.get("/{player_id}/stats/{year}/{month}", response_model=player_schema.PlayerStatsResponse)
async def get_player_monthly_stats(
    player_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"선수 월간 통계 조회: 선수 ID {player_id}, {year}년 {month}월")
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 날짜 유효성 검사
        if month < 1 or month > 12:
            logger.warning(f"유효하지 않은 월: {month}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월은 1부터 12 사이의 값이어야 합니다"
            )
            
        # 월간 통계 조회
        stats = player_crud.get_player_monthly_stats(db, player_id, year, month)
        
        # 응답 데이터
        result = {
            "player": db_player,
            "stats": stats
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 월간 통계 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 월간 통계 조회 중 오류 발생: {str(e)}"
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

# 선수 일일 보고서 생성/업데이트
@router.post("/{player_id}/daily-reports", response_model=player_schema.DailyReportResponse)
async def create_player_daily_report(
    player_id: int,
    report: player_schema.DailyReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"선수 일일 보고서 생성/업데이트 요청: 선수 ID {player_id}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 선수 ID 일치 여부 확인
        if report.PLAYER_ID != player_id:
            logger.warning(f"URL의 선수 ID와 요청 데이터의 선수 ID 불일치: URL {player_id}, 데이터 {report.PLAYER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL의 선수 ID와 요청 데이터의 선수 ID가 일치하지 않습니다"
            )
            
        # 보고서 생성/업데이트
        daily_report = player_crud.create_player_daily_report(db, report)
        
        logger.info(f"선수 일일 보고서 생성/업데이트 완료: 선수 ID {player_id}")
        return daily_report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 일일 보고서 생성/업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 일일 보고서 생성/업데이트 중 오류 발생: {str(e)}"
        )

# 특정 기록 유형별 상위 선수 조회
@router.get("/top/{record_type_id}", response_model=List[player_schema.TopPlayerResponse])
async def get_top_players_by_record(
    record_type_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"기록 유형별 상위 선수 조회: 기록 유형 ID {record_type_id}, limit={limit}")
        
        # 기록 유형 존재 여부 확인
        record_type = db.query(models.RecordType).filter(models.RecordType.RECORD_TYPE_ID == record_type_id).first()
        if not record_type:
            logger.warning(f"존재하지 않는 기록 유형: {record_type_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 기록 유형입니다"
            )
            
        top_players = player_crud.get_top_players_by_record(db, record_type_id, limit)
        
        # 응답 데이터 구성
        result = []
        for item in top_players:
            result.append({
                "player": item["player"],
                "total": item["total"],
                "record_name": record_type.RECORD_NAME
            })
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"기록 유형별 상위 선수 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기록 유형별 상위 선수 조회 중 오류 발생: {str(e)}"
        )

# 선수 포지션 타입 목록 조회
@router.get("/types", response_model=List[player_schema.PlayerTypeResponse])
async def get_player_types(db: Session = Depends(get_db)):
    try:
        logger.info("선수 포지션 타입 목록 조회")
        types = player_crud.get_player_types(db)
        return types
    except Exception as e:
        logger.error(f"선수 포지션 타입 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 포지션 타입 목록 조회 중 오류 발생: {str(e)}"
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

# 선수 출전 기록 생성
@router.post("/{player_id}/runs", response_model=player_schema.PlayerRunResponse)
async def record_player_run(
    player_id: int,
    run_date: date = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 날짜가 없으면 오늘 날짜 사용
        if run_date is None:
            run_date = datetime.now().date()
            
        logger.info(f"선수 출전 기록 생성 요청: 선수 ID {player_id}, 날짜 {run_date}")
        
        # TODO: 관리자 권한 확인 필요
        
        # 선수 존재 여부 확인
        db_player = player_crud.get_player_by_id(db, player_id)
        if not db_player:
            logger.warning(f"존재하지 않는 선수: {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 선수입니다"
            )
            
        # 출전 기록 생성
        run = player_crud.record_player_run(db, player_id, run_date)
        
        logger.info(f"선수 출전 기록 생성 완료: 선수 ID {player_id}, 날짜 {run_date}")
        return run
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"선수 출전 기록 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"선수 출전 기록 생성 중 오류 발생: {str(e)}"
        )