from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional,Dict, Any
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
    
# 뉴스 요약 정보를 받아 주간 보고서 업데이트
@router.post("/news-summary", response_model=report_schema.NewsSummaryResponse)
async def update_news_summary(
    data: report_schema.NewsSummaryRequest,
    db: Session = Depends(get_db)
):
    """
    GCP에서 크롤링한 뉴스 요약 정보를 받아 주간 보고서에 저장합니다.
    
    요청 본문 예시:
    {
        "header": {"date": "2025-04-01"},
        "body": [
            {"team": "KIA", "news_summation": "KIA 타이거즈 뉴스 요약..."},
            {"team": "삼성", "news_summation": "삼성 라이온즈 뉴스 요약..."}
        ]
    }
    """
    try:
        logger.info(f"뉴스 요약 정보 업데이트 요청 수신")
        
        # 날짜 처리 (제공되지 않은 경우 현재 날짜 사용)
        report_date = None
        if data.header.date:
            try:
                report_date = datetime.strptime(data.header.date, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"잘못된 날짜 형식: {data.header.date}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식이어야 합니다."
                )
        else:
            # 날짜가 제공되지 않은 경우 현재 날짜 사용
            report_date = datetime.now().date()
        
        results = []
        for news_item in data.body:
            team_name = news_item.team
            summary = news_item.news_summation
            
            # 팀 이름으로 팀 ID 찾기
            team = db.query(models.Team).filter(
                models.Team.TEAM_NAME.like(f"%{team_name}%")
            ).first()
            
            if not team:
                logger.warning(f"존재하지 않는 팀 이름: {team_name}")
                results.append(report_schema.NewsSummaryResultItem(
                    team=team_name,
                    status="error",
                    message=f"팀 '{team_name}'을 찾을 수 없습니다"
                ))
                continue
            
            team_id = team.TEAM_ID
            
            # 해당 팀의 주간 보고서 조회 (없으면 생성)
            weekly_report = db.query(models.WeeklyReportTeam).filter(
                models.WeeklyReportTeam.TEAM_ID == team_id,
                models.WeeklyReportTeam.DATE == report_date
            ).first()
            
            if weekly_report:
                # 기존 보고서 업데이트
                weekly_report.NEWS_SUMMATION = summary
                logger.info(f"기존 주간 보고서 업데이트: 팀 ID {team_id}, 팀 {team_name}, 날짜 {report_date}")
            else:
                # 새 보고서 생성
                # 승/패/무 등의 기본 데이터 설정
                total_win = team.TOTAL_WIN
                total_lose = team.TOTAL_LOSE
                total_draw = team.TOTAL_DRAW
                
                # 팀 계정들의 총액 계산
                team_amount = 0
                accounts = db.query(models.Account).filter(models.Account.TEAM_ID == team_id).all()
                if accounts:
                    team_amount = sum(account.TOTAL_AMOUNT for account in accounts)
                
                weekly_report = models.WeeklyReportTeam(
                    TEAM_ID=team_id,
                    DATE=report_date,
                    NEWS_SUMMATION=summary,
                    TEAM_AMOUNT=team_amount,
                    TEAM_WIN=total_win,
                    TEAM_DRAW=total_draw,
                    TEAM_LOSE=total_lose
                )
                db.add(weekly_report)
                logger.info(f"새 주간 보고서 생성: 팀 ID {team_id}, 팀 {team_name}, 날짜 {report_date}")
            
            # 결과에 추가
            results.append(report_schema.NewsSummaryResultItem(
                team=team_name,
                team_id=team_id,
                status="success",
                message="뉴스 요약 정보가 성공적으로 저장되었습니다"
            ))
        
        db.commit()
        
        # 응답 구성
        response = report_schema.NewsSummaryResponse(
            status="success",
            message=f"{len(results)}개 팀의 뉴스 요약 정보가 처리되었습니다",
            date=report_date.isoformat(),
            results=results
        )
        
        return response
        
    except HTTPException:
        # 이미 정의된 HTTP 예외는 그대로 발생
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        logger.error(f"뉴스 요약 정보 업데이트 중 오류 발생: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"뉴스 요약 정보 처리 중 오류가 발생했습니다: {str(e)}"
        )
    
@router.get("/all-accounts-summary", response_model=Dict[str, Any])
async def get_all_system_accounts_summary(
    game_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    시스템의 모든 계정에 대한 일일 요약 정보를 제공합니다.
    
    - 모든 계정 정보가 account_id로 구분되어 제공됩니다
    - 각 계정마다 우리팀, 상대팀, 최애선수, 적금규칙, 경기결과, 입금금액 정보 포함
    
    Args:
        game_date: 경기 날짜 (기본값: 어제)
    
    Returns:
        Dict: 계정 ID를 키로 하는 일일 요약 정보
    """
    try:
        # 날짜 설정 (기본값: 어제)
        if game_date is None:
            game_date = datetime.now().date() - timedelta(days=1)
        
        logger.info(f"시스템의 모든 계정에 대한 {game_date} 일일 요약 정보 조회 시작")
        
        # 1. 시스템의 모든 계정 조회
        accounts = db.query(models.Account).all()
        
        if not accounts:
            logger.warning("시스템에 계정이 없습니다.")
            return {"accounts": {}, "message": "시스템에 등록된 계정이 없습니다."}
        
        # 2. 각 계정별 정보 구성
        result = {"accounts": {}}
        
        # 금융 API 유틸리티 import
        from router.user.user_ssafy_api_utils import get_account_balance

        for account in accounts:
            account_id = account.ACCOUNT_ID
            
            # 팀 정보 조회
            our_team = db.query(models.Team).filter(models.Team.TEAM_ID == account.TEAM_ID).first()
            if not our_team:
                logger.warning(f"팀 ID {account.TEAM_ID}를 찾을 수 없습니다.")
                continue
            
            # 경기 일정 조회 (우리 팀이 참여한 경기)
            game_schedule = db.query(models.GameSchedule).filter(
                models.GameSchedule.DATE == game_date,
                ((models.GameSchedule.HOME_TEAM_ID == account.TEAM_ID) | 
                 (models.GameSchedule.AWAY_TEAM_ID == account.TEAM_ID))
            ).first()
            
            # 경기가 없는 경우 처리
            if not game_schedule:
                result["accounts"][str(account_id)] = {
                    "our_team": our_team.TEAM_NAME,
                    "opposing_team": None,
                    "favorite_player": None,
                    "savings_rules": {},
                    "game_results": {},
                    "original_outcome": 0,
                    "real_outcome": 0,
                    "message": f"{game_date} 날짜에 경기 일정이 없습니다."
                }
                continue
            
            # 상대팀 정보 조회
            opposing_team_id = game_schedule.AWAY_TEAM_ID if game_schedule.HOME_TEAM_ID == account.TEAM_ID else game_schedule.HOME_TEAM_ID
            opposing_team = db.query(models.Team).filter(models.Team.TEAM_ID == opposing_team_id).first()
            
            # 최애 선수 정보 조회
            favorite_player = None
            if account.FAVORITE_PLAYER_ID:
                favorite_player = db.query(models.Player).filter(models.Player.PLAYER_ID == account.FAVORITE_PLAYER_ID).first()
            
            # 적금 규칙 조회
            user_saving_rules = db.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account_id
            ).all()
            
            # 적금 규칙 정보 구성 및 game_results 기본값 설정
            savings_rules = {}
            expected_records = {}  # 예상되는 기록 키 저장
            
            for rule in user_saving_rules:
                # 규칙 유형 조회
                rule_type = db.query(models.SavingRuleType).filter(
                    models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
                ).first()
                
                # 규칙 상세 조회
                rule_detail = db.query(models.SavingRuleDetail).filter(
                    models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
                ).first()
                
                if not rule_detail or not rule_type:
                    continue
                
                # 기록 유형 조회
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if not saving_rule:
                    continue
                    
                record_type = db.query(models.RecordType).filter(
                    models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                ).first()
                
                if not record_type:
                    continue
                
                # 규칙 이름 생성
                rule_name = ""
                if rule_type.SAVING_RULE_TYPE_NAME == "기본 규칙":
                    rule_name = f"우리팀_{record_type.RECORD_NAME}"
                    expected_records[rule_name] = 0  # 기본값 0으로 설정
                elif rule_type.SAVING_RULE_TYPE_NAME == "상대팀":
                    rule_name = f"상대팀_{record_type.RECORD_NAME}"
                    expected_records[rule_name] = 0  # 기본값 0으로 설정
                elif rule.PLAYER_ID:
                    # 선수 정보 조회
                    player = db.query(models.Player).filter(models.Player.PLAYER_ID == rule.PLAYER_ID).first()
                    if player and (favorite_player and player.PLAYER_ID == favorite_player.PLAYER_ID):
                        rule_name = f"선수_{record_type.RECORD_NAME}"
                        expected_records[rule_name] = 0  # 기본값 0으로 설정
                
                # 의미 있는 규칙만 추가
                if rule_name:
                    savings_rules[rule_name] = rule.USER_SAVING_RULED_AMOUNT
            
            # 경기 결과 조회 (기본값은 이미 0으로 설정됨)
            game_results = expected_records.copy()
            
            # 우리 팀 기록 조회
            our_team_logs = db.query(models.GameLog).filter(
                models.GameLog.DATE == game_date,
                models.GameLog.TEAM_ID == account.TEAM_ID
            ).all()
            
            # 상대 팀 기록 조회
            opposing_team_logs = db.query(models.GameLog).filter(
                models.GameLog.DATE == game_date,
                models.GameLog.TEAM_ID == opposing_team_id
            ).all()
            
            # 최애 선수 기록 조회
            favorite_player_records = []
            if favorite_player:
                favorite_player_records = db.query(models.PlayerRecord).filter(
                    models.PlayerRecord.DATE == game_date,
                    models.PlayerRecord.PLAYER_ID == favorite_player.PLAYER_ID
                ).all()
            
            # 경기 결과 업데이트 (우리팀)
            for log in our_team_logs:
                record_type = db.query(models.RecordType).filter(
                    models.RecordType.RECORD_TYPE_ID == log.RECORD_TYPE_ID
                ).first()
                
                if record_type:
                    key = f"우리팀_{record_type.RECORD_NAME}"
                    if key in game_results:  # savings_rules에 있는 경우만 업데이트
                        game_results[key] = log.COUNT
            
            # 경기 결과 업데이트 (상대팀)
            for log in opposing_team_logs:
                record_type = db.query(models.RecordType).filter(
                    models.RecordType.RECORD_TYPE_ID == log.RECORD_TYPE_ID
                ).first()
                
                if record_type:
                    key = f"상대팀_{record_type.RECORD_NAME}"
                    if key in game_results:  # savings_rules에 있는 경우만 업데이트
                        game_results[key] = log.COUNT
            
            # 경기 결과 업데이트 (최애선수)
            if favorite_player:
                for record in favorite_player_records:
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == record.RECORD_TYPE_ID
                    ).first()
                    
                    if record_type:
                        key = f"선수_{record_type.RECORD_NAME}"
                        if key in game_results:  # savings_rules에 있는 경우만 업데이트
                            game_results[key] = record.COUNT
            
            # 실제 입금 금액 계산 (일일 적금 내역 조회)
            daily_savings = db.query(models.DailySaving).filter(
                models.DailySaving.ACCOUNT_ID == account_id,
                models.DailySaving.DATE == game_date
            ).all()
            
            # 원래 계산된 적립 금액
            original_total = sum(saving.DAILY_SAVING_AMOUNT for saving in daily_savings)
            
            # 실제 이체될 금액 계산
            real_outcome = original_total
            
            # 해당 날짜에 이미 이체된 금액 확인 (실제 구현 시에는 이체 이력 테이블에서 조회)
            already_transferred_today = 0
            
            # 해당 월에 이미 이체된 금액 확인 (실제 구현 시에는 이체 이력 테이블에서 조회)
            month_start = game_date.replace(day=1)
            already_transferred_this_month = 0
            
            # 일일 한도 확인
            if already_transferred_today + original_total > account.DAILY_LIMIT:
                # 일일 한도 초과 시 한도 내로 조정
                real_outcome = max(0, account.DAILY_LIMIT - already_transferred_today)
            
            # 월간 한도 확인
            if already_transferred_this_month + real_outcome > account.MONTH_LIMIT:
                # 월간 한도 초과 시 한도 내로 조정
                real_outcome = max(0, account.MONTH_LIMIT - already_transferred_this_month)
            
            # 출금 계좌 잔액 조회 (추가된 부분)
            try:
                source_account_balance = await get_account_balance(
                    user_key=account.user.USER_KEY, 
                    account_num=account.SOURCE_ACCOUNT
                )
            except Exception as e:
                logger.warning(f"계정 {account.ACCOUNT_ID}의 출금 계좌 잔액 조회 실패: {str(e)}")
                source_account_balance = 0  # 기본값 설정
            
            # 실제 이체될 금액 계산 (수정된 부분)
            # 잔액 부족 확인 로직 추가
            if source_account_balance < original_total:
                real_outcome = "잔액부족"
            else:
                real_outcome = min(
                    original_total,  # 원래 계산된 적립 금액
                    source_account_balance,  # 출금 계좌 실제 잔액
                    account.DAILY_LIMIT - already_transferred_today,  # 일일 한도
                    account.MONTH_LIMIT - already_transferred_this_month  # 월간 한도
                )

            # 계정별 정보 저장
            result["accounts"][str(account_id)] = {
                "our_team": our_team.TEAM_NAME,
                "opposing_team": opposing_team.TEAM_NAME if opposing_team else None,
                "favorite_player": favorite_player.PLAYER_NAME if favorite_player else None,
                "savings_rules": savings_rules,
                "game_results": game_results,
                "original_outcome": original_total,  # 원래 계산된 적립 금액
                "real_outcome": real_outcome         # 실제 이체될 금액
            }
        
        # 추가 정보 설정
        result["date"] = game_date.isoformat()
        result["total_accounts"] = len(accounts)
        result["accounts_with_games"] = sum(1 for acc_info in result["accounts"].values() if "message" not in acc_info)
        
        logger.info(f"시스템의 모든 계정에 대한 일일 요약 정보 조회 완료: {len(result['accounts'])}개의 계정 처리됨")
        return result
        
    except Exception as e:
        logger.error(f"모든 계정 일일 요약 정보 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모든 계정 일일 요약 정보 조회 중 오류 발생: {str(e)}"
        )