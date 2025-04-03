from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from database import get_db
import models
from router.team import team_schema, team_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 모든 팀 조회
@router.get("/", response_model=List[team_schema.TeamResponse])
async def read_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"모든 팀 목록 조회: skip={skip}, limit={limit}")
        teams = team_crud.get_all_teams(db, skip, limit)
        return teams
    except Exception as e:
        logger.error(f"팀 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 팀 조회
@router.get("/{team_id}", response_model=team_schema.TeamDetailResponse)
async def read_team(
    team_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 조회: 팀 ID {team_id}")
        
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 팀 상세 정보 구성
        total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
        win_rate = (team.TOTAL_WIN / total_games * 100) if total_games > 0 else 0
        
        result = {
            "TEAM_ID": team.TEAM_ID,
            "TEAM_NAME": team.TEAM_NAME,
            "TOTAL_WIN": team.TOTAL_WIN,
            "TOTAL_LOSE": team.TOTAL_LOSE,
            "TOTAL_DRAW": team.TOTAL_DRAW,
            "created_at": team.created_at,
            "win_rate": round(win_rate, 2),
            "total_games": total_games
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 조회 중 오류 발생: {str(e)}"
        )

# 팀 상세 정보 조회 (선수, 계정, 게임 일정 포함)
@router.get("/{team_id}/details", response_model=team_schema.TeamFullDetailResponse)
async def read_team_full_details(
    team_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 상세 정보 조회: 팀 ID {team_id}")
        
        # 팀 기본 정보 조회
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 팀 선수 목록 조회
        players = team_crud.get_team_players(db, team_id)
        player_info = []
        for player in players:
            player_type = db.query(models.PlayerType).filter(models.PlayerType.PLAYER_TYPE_ID == player.PLAYER_TYPE_ID).first()
            player_info.append({
                "PLAYER_ID": player.PLAYER_ID,
                "PLAYER_NAME": player.PLAYER_NAME,
                "PLAYER_NUM": player.PLAYER_NUM,
                "PLAYER_TYPE_ID": player.PLAYER_TYPE_ID,
                "player_type_name": player_type.PLAYER_TYPE_NAME if player_type else None,
                "PLAYER_IMAGE_URL": player.PLAYER_IMAGE_URL
            })
            
        # 팀 계정 목록 조회
        accounts = team_crud.get_team_accounts(db, team_id)
        account_info = []
        for account in accounts:
            progress = (account.TOTAL_AMOUNT / account.SAVING_GOAL * 100) if account.SAVING_GOAL > 0 else 0
            account_info.append({
                "ACCOUNT_ID": account.ACCOUNT_ID,
                "ACCOUNT_NUM": account.ACCOUNT_NUM,
                "TOTAL_AMOUNT": account.TOTAL_AMOUNT,
                "SAVING_GOAL": account.SAVING_GOAL,
                "progress_percentage": round(progress, 2)
            })
            
        # 팀 향후 경기 일정 조회
        today = datetime.now().date()
        games = team_crud.get_team_games(db, team_id)
        upcoming_games = []
        
        for game in games:
            if game.DATE >= today:
                home_team = team_crud.get_team_by_id(db, game.HOME_TEAM_ID)
                away_team = team_crud.get_team_by_id(db, game.AWAY_TEAM_ID)
                
                upcoming_games.append({
                    "GAME_SCHEDULE_KEY": game.GAME_SCHEDULE_KEY,
                    "DATE": game.DATE,
                    "HOME_TEAM_ID": game.HOME_TEAM_ID,
                    "AWAY_TEAM_ID": game.AWAY_TEAM_ID,
                    "home_team_name": home_team.TEAM_NAME if home_team else None,
                    "away_team_name": away_team.TEAM_NAME if away_team else None,
                    "is_home": game.HOME_TEAM_ID == team_id
                })
                
        # 상위 10개만 선택
        upcoming_games = sorted(upcoming_games, key=lambda x: x["DATE"])[:10]
        
        # 팀 상세 정보 구성
        total_games = team.TOTAL_WIN + team.TOTAL_LOSE + team.TOTAL_DRAW
        win_rate = (team.TOTAL_WIN / total_games * 100) if total_games > 0 else 0
        
        result = {
            "TEAM_ID": team.TEAM_ID,
            "TEAM_NAME": team.TEAM_NAME,
            "TOTAL_WIN": team.TOTAL_WIN,
            "TOTAL_LOSE": team.TOTAL_LOSE,
            "TOTAL_DRAW": team.TOTAL_DRAW,
            "created_at": team.created_at,
            "win_rate": round(win_rate, 2),
            "total_games": total_games,
            "players": player_info,
            "accounts": account_info,
            "upcoming_games": upcoming_games
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 상세 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 상세 정보 조회 중 오류 발생: {str(e)}"
        )

# 팀 일일 보고서 조회
@router.get("/{team_id}/daily-reports", response_model=List[team_schema.DailyReportResponse])
async def read_team_daily_reports(
    team_id: int,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 일일 보고서 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 일일 보고서 조회
        reports = team_crud.get_daily_reports_by_team(db, team_id, skip, limit)
        
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 일일 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 일일 보고서 조회 중 오류 발생: {str(e)}"
        )

# 특정 날짜의 팀 일일 보고서 조회
@router.get("/{team_id}/daily-reports/{date}", response_model=team_schema.DailyReportResponse)
async def read_team_daily_report_by_date(
    team_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 날짜 팀 일일 보고서 조회: 팀 ID {team_id}, 날짜 {date}")
        
        # 팀 존재 여부 확인
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 일일 보고서 조회
        report = team_crud.get_daily_report_by_team_and_date(db, team_id, date)
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: 팀 ID {team_id}, 날짜 {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 팀 일일 보고서를 찾을 수 없습니다"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"특정 날짜 팀 일일 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"특정 날짜 팀 일일 보고서 조회 중 오류 발생: {str(e)}"
        )

# 팀 주간 보고서 조회
@router.get("/{team_id}/weekly-reports", response_model=List[team_schema.WeeklyReportResponse])
async def read_team_weekly_reports(
    team_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 주간 보고서 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 주간 보고서 조회
        reports = team_crud.get_weekly_reports_by_team(db, team_id, skip, limit)
        
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 주간 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 주간 보고서 조회 중 오류 발생: {str(e)}"
        )

# 특정 날짜의 팀 주간 보고서 조회
@router.get("/{team_id}/weekly-reports/{date}", response_model=team_schema.WeeklyReportResponse)
async def read_team_weekly_report_by_date(
    team_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"특정 날짜 팀 주간 보고서 조회: 팀 ID {team_id}, 날짜 {date}")
        
        # 팀 존재 여부 확인
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 주간 보고서 조회
        report = team_crud.get_weekly_report_by_team_and_date(db, team_id, date)
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: 팀 ID {team_id}, 날짜 {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 팀 주간 보고서를 찾을 수 없습니다"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"특정 날짜 팀 주간 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"특정 날짜 팀 주간 보고서 조회 중 오류 발생: {str(e)}"
        )


# 팀 계정 목록 조회
@router.get("/{team_id}/accounts", response_model=List[team_schema.TeamAccountBasicInfo])
async def read_team_accounts(
    team_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 계정 목록 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = team_crud.get_team_by_id(db, team_id)
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        # 팀 계정 목록 조회
        accounts = team_crud.get_team_accounts(db, team_id)
        
        # 계정 정보 변환
        result = []
        for account in accounts:
            progress = (account.TOTAL_AMOUNT / account.SAVING_GOAL * 100) if account.SAVING_GOAL > 0 else 0
            result.append({
                "ACCOUNT_ID": account.ACCOUNT_ID,
                "ACCOUNT_NUM": account.ACCOUNT_NUM,
                "TOTAL_AMOUNT": account.TOTAL_AMOUNT,
                "SAVING_GOAL": account.SAVING_GOAL,
                "progress_percentage": round(progress, 2)
            })
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 계정 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 계정 목록 조회 중 오류 발생: {str(e)}"
        )

