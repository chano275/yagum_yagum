from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from database import get_db
import models
from router.report import report_schema, report_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 팀 일일 보고서 목록 조회
@router.get("/daily/team/{team_id}", response_model=List[report_schema.DailyReportResponse])
async def read_daily_reports_by_team(
    team_id: int,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 일일 보고서 목록 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        reports = report_crud.get_daily_reports_by_team(db, team_id, skip, limit)
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 일일 보고서 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 일일 보고서 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 팀과 날짜의 일일 보고서 조회
@router.get("/daily/team/{team_id}/date/{date}", response_model=report_schema.DailyReportResponse)
async def read_daily_report_by_team_and_date(
    team_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀과 날짜로 일일 보고서 조회: 팀 ID {team_id}, 날짜 {date}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        report = report_crud.get_daily_report_by_team_and_date(db, team_id, date)
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: 팀 ID {team_id}, 날짜 {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 보고서를 찾을 수 없습니다"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀과 날짜로 일일 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 보고서 조회 중 오류 발생: {str(e)}"
        )

# # 일일 보고서 생성/업데이트
# @router.post("/daily", response_model=report_schema.DailyReportResponse)
# async def create_daily_report(
#     report: report_schema.DailyReportCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"일일 보고서 생성/업데이트 요청: 팀 ID {report.TEAM_ID}, 날짜 {report.DATE}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 팀 존재 여부 확인
#         team = db.query(models.Team).filter(models.Team.TEAM_ID == report.TEAM_ID).first()
#         if not team:
#             logger.warning(f"존재하지 않는 팀: {report.TEAM_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 팀입니다"
#             )
            
#         # 보고서 생성/업데이트
#         created_report = report_crud.create_daily_report(db, report)
        
#         logger.info(f"일일 보고서 생성/업데이트 완료: 팀 ID {report.TEAM_ID}, 날짜 {report.DATE}")
#         return created_report
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"일일 보고서 생성/업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"일일 보고서 생성/업데이트 중 오류 발생: {str(e)}"
#         )

# # 일일 보고서 삭제
# @router.delete("/daily/{daily_report_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_daily_report(
#     daily_report_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"일일 보고서 삭제 요청: 보고서 ID {daily_report_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 보고서 존재 여부 확인
#         report = report_crud.get_daily_report_by_id(db, daily_report_id)
#         if not report:
#             logger.warning(f"존재하지 않는 보고서: {daily_report_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 보고서입니다"
#             )
            
#         # 보고서 삭제
#         success = report_crud.delete_daily_report(db, daily_report_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="보고서 삭제 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"일일 보고서 삭제 완료: 보고서 ID {daily_report_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"일일 보고서 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"일일 보고서 삭제 중 오류 발생: {str(e)}"
#         )

# 주간 팀 보고서 목록 조회
@router.get("/weekly/team/{team_id}", response_model=List[report_schema.WeeklyReportTeamResponse])
async def read_weekly_team_reports(
    team_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"주간 팀 보고서 목록 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        reports = report_crud.get_weekly_team_reports_by_team(db, team_id, skip, limit)
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주간 팀 보고서 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주간 팀 보고서 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 팀과 날짜의 주간 팀 보고서 조회
@router.get("/weekly/team/{team_id}/date/{date}", response_model=report_schema.WeeklyReportTeamResponse)
async def read_weekly_team_report_by_date(
    team_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀과 날짜로 주간 팀 보고서 조회: 팀 ID {team_id}, 날짜 {date}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        report = report_crud.get_weekly_team_report_by_team_and_date(db, team_id, date)
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: 팀 ID {team_id}, 날짜 {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 보고서를 찾을 수 없습니다"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀과 날짜로 주간 팀 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주간 팀 보고서 조회 중 오류 발생: {str(e)}"
        )

# # 주간 팀 보고서 생성/업데이트
# @router.post("/weekly/team", response_model=report_schema.WeeklyReportTeamResponse)
# async def create_weekly_team_report(
#     report: report_schema.WeeklyReportTeamCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"주간 팀 보고서 생성/업데이트 요청: 팀 ID {report.TEAM_ID}, 날짜 {report.DATE}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 팀 존재 여부 확인
#         team = db.query(models.Team).filter(models.Team.TEAM_ID == report.TEAM_ID).first()
#         if not team:
#             logger.warning(f"존재하지 않는 팀: {report.TEAM_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 팀입니다"
#             )
            
#         # 보고서 생성/업데이트
#         created_report = report_crud.create_weekly_team_report(db, report)
        
#         logger.info(f"주간 팀 보고서 생성/업데이트 완료: 팀 ID {report.TEAM_ID}, 날짜 {report.DATE}")
#         return created_report
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"주간 팀 보고서 생성/업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"주간 팀 보고서 생성/업데이트 중 오류 발생: {str(e)}"
#         )

# # 주간 팀 보고서 삭제
# @router.delete("/weekly/team/{weekly_team_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_weekly_team_report(
#     weekly_team_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"주간 팀 보고서 삭제 요청: 보고서 ID {weekly_team_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 보고서 존재 여부 확인
#         report = report_crud.get_weekly_team_report_by_id(db, weekly_team_id)
#         if not report:
#             logger.warning(f"존재하지 않는 보고서: {weekly_team_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 보고서입니다"
#             )
            
#         # 보고서 삭제
#         success = report_crud.delete_weekly_team_report(db, weekly_team_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="보고서 삭제 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"주간 팀 보고서 삭제 완료: 보고서 ID {weekly_team_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"주간 팀 보고서 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"주간 팀 보고서 삭제 중 오류 발생: {str(e)}"
#         )

# 주간 개인 보고서 목록 조회
@router.get("/weekly/account/{account_id}", response_model=List[report_schema.WeeklyReportPersonalResponse])
async def read_weekly_personal_reports(
    account_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"주간 개인 보고서 목록 조회: 계정 ID {account_id}")
        
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
                detail="이 계정의 보고서를 조회할 권한이 없습니다"
            )
            
        reports = report_crud.get_weekly_personal_reports_by_account(db, account_id, skip, limit)
        return reports
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주간 개인 보고서 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주간 개인 보고서 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 계정과 날짜의 주간 개인 보고서 조회
@router.get("/weekly/account/{account_id}/date/{date}", response_model=report_schema.WeeklyReportPersonalResponse)
async def read_weekly_personal_report_by_date(
    account_id: int,
    date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정과 날짜로 주간 개인 보고서 조회: 계정 ID {account_id}, 날짜 {date}")
        
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
                detail="이 계정의 보고서를 조회할 권한이 없습니다"
            )
            
        report = report_crud.get_weekly_personal_report_by_account_and_date(db, account_id, date)
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: 계정 ID {account_id}, 날짜 {date}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 날짜의 보고서를 찾을 수 없습니다"
            )
            
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정과 날짜로 주간 개인 보고서 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주간 개인 보고서 조회 중 오류 발생: {str(e)}"
        )

# # 주간 개인 보고서 생성/업데이트
# @router.post("/weekly/account", response_model=report_schema.WeeklyReportPersonalResponse)
# async def create_weekly_personal_report(
#     report: report_schema.WeeklyReportPersonalCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"주간 개인 보고서 생성/업데이트 요청: 계정 ID {report.ACCOUNT_ID}, 날짜 {report.DATE}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 계정 존재 여부 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == report.ACCOUNT_ID).first()
#         if not account:
#             logger.warning(f"존재하지 않는 계정: {report.ACCOUNT_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 계정입니다"
#             )
            
#         # 보고서 생성/업데이트
#         created_report = report_crud.create_weekly_personal_report(db, report)
        
#         logger.info(f"주간 개인 보고서 생성/업데이트 완료: 계정 ID {report.ACCOUNT_ID}, 날짜 {report.DATE}")
#         return created_report
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"주간 개인 보고서 생성/업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"주간 개인 보고서 생성/업데이트 중 오류 발생: {str(e)}"
#         )

# # 주간 개인 보고서 삭제
# @router.delete("/weekly/account/{weekly_personal_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_weekly_personal_report(
#     weekly_personal_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"주간 개인 보고서 삭제 요청: 보고서 ID {weekly_personal_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 보고서 존재 여부 확인
#         report = report_crud.get_weekly_personal_report_by_id(db, weekly_personal_id)
#         if not report:
#             logger.warning(f"존재하지 않는 보고서: {weekly_personal_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 보고서입니다"
#             )
            
#         # 계정 소유권 확인
#         account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == report.ACCOUNT_ID).first()
#         if account and account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="이 보고서를 삭제할 권한이 없습니다"
#             )
            
#         # 보고서 삭제
#         success = report_crud.delete_weekly_personal_report(db, weekly_personal_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="보고서 삭제 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"주간 개인 보고서 삭제 완료: 보고서 ID {weekly_personal_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"주간 개인 보고서 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"주간 개인 보고서 삭제 중 오류 발생: {str(e)}"
#         )

# 팀 뉴스 목록 조회
@router.get("/news/team/{team_id}", response_model=List[report_schema.NewsResponse])
async def read_team_news(
    team_id: int,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 뉴스 목록 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        news = report_crud.get_news_by_team(db, team_id, skip, limit)
        return news
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 뉴스 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 뉴스 목록 조회 중 오류 발생: {str(e)}"
        )

# 특정 날짜 범위의 뉴스 조회
@router.get("/news/range", response_model=List[report_schema.NewsResponse])
async def read_news_by_date_range(
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"날짜 범위로 뉴스 조회: {start_date} ~ {end_date}")
        
        # 날짜 유효성 검사
        if end_date < start_date:
            logger.warning(f"유효하지 않은 날짜 범위: {start_date} ~ {end_date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="종료 날짜는 시작 날짜보다 이후여야 합니다"
            )
            
        news = report_crud.get_news_by_date_range(db, start_date, end_date, skip, limit)
        return news
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"날짜 범위로 뉴스 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"뉴스 조회 중 오류 발생: {str(e)}"
        )

# 최신 뉴스 조회
@router.get("/news/latest", response_model=List[report_schema.NewsResponse])
async def read_latest_news(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"최신 뉴스 조회: limit={limit}")
        news = report_crud.get_latest_news(db, limit)
        return news
    except Exception as e:
        logger.error(f"최신 뉴스 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최신 뉴스 조회 중 오류 발생: {str(e)}"
        )

# # 뉴스 생성
# @router.post("/news", response_model=report_schema.NewsResponse)
# async def create_news(
#     news: report_schema.NewsCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"뉴스 생성 요청: 팀 ID {news.TEAM_ID}, 제목 '{news.NEWS_TITLE}'")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 팀 존재 여부 확인
#         team = db.query(models.Team).filter(models.Team.TEAM_ID == news.TEAM_ID).first()
#         if not team:
#             logger.warning(f"존재하지 않는 팀: {news.TEAM_ID}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 팀입니다"
#             )
            
#         # 뉴스 생성
#         created_news = report_crud.create_news(db, news)
        
#         logger.info(f"뉴스 생성 완료: 뉴스 ID {created_news.NEWS_ID}")
#         return created_news
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"뉴스 생성 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"뉴스 생성 중 오류 발생: {str(e)}"
#         )

# # 뉴스 삭제
# @router.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_news(
#     news_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"뉴스 삭제 요청: 뉴스 ID {news_id}")
        
#         # TODO: 관리자 권한 확인 필요
        
#         # 뉴스 존재 여부 확인
#         news = report_crud.get_news_by_id(db, news_id)
#         if not news:
#             logger.warning(f"존재하지 않는 뉴스: {news_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="존재하지 않는 뉴스입니다"
#             )
            
#         # 뉴스 삭제
#         success = report_crud.delete_news(db, news_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="뉴스 삭제 중 오류가 발생했습니다"
#             )
            
#         logger.info(f"뉴스 삭제 완료: 뉴스 ID {news_id}")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"뉴스 삭제 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"뉴스 삭제 중 오류 발생: {str(e)}"
#         )

# 팀 순위 조회
@router.get("/ranking", response_model=List[report_schema.TeamRankingResponse])
async def get_team_ranking(
    ranking_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 순위 조회: 날짜 {ranking_date or '오늘'}")
        
        # 날짜가 없으면 현재 날짜 사용
        if ranking_date is None:
            ranking_date = datetime.now().date()
            
        ranking = report_crud.get_team_ranking(db, ranking_date)
        return ranking
    except Exception as e:
        logger.error(f"팀 순위 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 순위 조회 중 오류 발생: {str(e)}"
        )

# 계정 보고서 요약 정보 조회
@router.get("/summary/account/{account_id}", response_model=report_schema.AccountReportSummaryResponse)
async def get_account_report_summary(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 보고서 요약 정보 조회: 계정 ID {account_id}")
        
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
                detail="이 계정의 요약 정보를 조회할 권한이 없습니다"
            )
            
        summary = report_crud.get_account_report_summary(db, account_id)
        if not summary:
            logger.warning(f"요약 정보를 생성할 수 없음: 계정 ID {account_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="계정 요약 정보를 생성할 수 없습니다"
            )
            
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 보고서 요약 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 보고서 요약 정보 조회 중 오류 발생: {str(e)}"
        )

# 팀 보고서 요약 정보 조회
@router.get("/summary/team/{team_id}", response_model=report_schema.TeamReportSummaryResponse)
async def get_team_report_summary(
    team_id: int,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"팀 보고서 요약 정보 조회: 팀 ID {team_id}")
        
        # 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == team_id).first()
        if not team:
            logger.warning(f"존재하지 않는 팀: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 팀입니다"
            )
            
        summary = report_crud.get_team_report_summary(db, team_id)
        if not summary:
            logger.warning(f"요약 정보를 생성할 수 없음: 팀 ID {team_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="팀 요약 정보를 생성할 수 없습니다"
            )
            
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 보고서 요약 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"팀 보고서 요약 정보 조회 중 오류 발생: {str(e)}"
        )

# 계정 일일 잔액 내역 조회
@router.get("/account/{account_id}/balances", response_model=List[report_schema.DailyBalancesResponse])
async def get_account_daily_balances(
    account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 일일 잔액 내역 조회: 계정 ID {account_id}")
        
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
                detail="이 계정의 잔액 내역을 조회할 권한이 없습니다"
            )
            
        balances = report_crud.get_daily_balances_by_account(db, account_id, start_date, end_date)
        return balances
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 일일 잔액 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 일일 잔액 내역 조회 중 오류 발생: {str(e)}"
        )

# 계정 이자 통계 조회
@router.get("/account/{account_id}/interest-stats", response_model=report_schema.InterestStatsResponse)
async def get_account_interest_stats(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 이자 통계 조회: 계정 ID {account_id}")
        
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
                detail="이 계정의 이자 통계를 조회할 권한이 없습니다"
            )
            
        stats = report_crud.calculate_interest_stats(db, account_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 이자 통계 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 이자 통계 조회 중 오류 발생: {str(e)}"
        )