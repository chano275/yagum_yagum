from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import importlib
import logging
from datetime import datetime, time
from pytz import timezone

# APScheduler 추가
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 라우터 임포트
from router.user.user_router import router as user_router
from router.account.account_router import router as account_router
from router.team.team_router import router as team_router
from router.player.player_router import router as player_router
from router.mission.mission_router import router as mission_router
from router.saving_rule.saving_rule_router import router as saving_rule_router
from router.report.report_router import router as report_router
from router.game.game_router import router as game_router
from baseball_data import def_change_json,def_crawl_gamelog,def_game_preprocessing


# 데이터베이스 초기화
from database import engine
import models
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행
    scheduler.start()
    logger.info("스케줄러 시작됨")
    
    # 현재 등록된 모든 작업 출력
    for job in scheduler.get_jobs():
        logger.info(f"등록된 작업: {job.name}, 다음 실행 시간: {job.next_run_time}")
    
    yield  # 애플리케이션 실행 중
    
    # 애플리케이션 종료 시 실행
    scheduler.shutdown()
    logger.info("스케줄러 종료됨")

app = FastAPI(
    title="야금야금 서비스 API",
    description="야구 기반 적금 서비스를 위한 백엔드 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
# .env 파일에서 CORS_ORIGINS 가져오기
origins_str = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 
app.include_router(user_router, prefix="/api/user", tags=["사용자"])
app.include_router(account_router, prefix="/api/account", tags=["계정"])
app.include_router(team_router, prefix="/api/team", tags=["팀"])
app.include_router(player_router, prefix="/api/player", tags=["선수"])
app.include_router(mission_router, prefix="/api/mission", tags=["우대금리"])
app.include_router(saving_rule_router, prefix="/api/saving_rule", tags=["적금 규칙"])
app.include_router(report_router, prefix="/api/report", tags=["보고서"])
app.include_router(game_router, prefix="/api/game", tags=["경기"])

# 스케줄러 작업 함수들
def run_crawler():
    """경기 기록 크롤링 작업 실행"""
    try:
        logger.info("경기 기록 크롤링 작업 시작")
        
        # 현재 작업 디렉토리 저장
        original_dir = os.getcwd()
        logger.info(f"현재 작업 디렉토리: {original_dir}")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 작업 디렉토리를 baseball_data로 변경
        os.chdir(baseball_data_dir)
        logger.info(f"작업 디렉토리 변경됨: {os.getcwd()}")
        
        # 직접 모듈 로드 및 실행
        from baseball_data.def_crawl_gamelog import crawl_gamelog
        result = crawl_gamelog()
        
        # 작업 디렉토리 복원
        os.chdir(original_dir)
        
        if result:
            logger.info("경기 기록 크롤링 작업 성공")
        else:
            logger.error("경기 기록 크롤링 작업 실패")
            
    except Exception as e:
        logger.error(f"경기 기록 크롤링 작업 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def run_preprocessing():
    """데이터 전처리 작업 실행"""
    try:
        logger.info("데이터 전처리 작업 시작")
        
        # 현재 작업 디렉토리 저장
        original_dir = os.getcwd()
        logger.info(f"현재 작업 디렉토리: {original_dir}")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 작업 디렉토리를 baseball_data로 변경
        os.chdir(baseball_data_dir)
        logger.info(f"작업 디렉토리 변경됨: {os.getcwd()}")
        
        # 직접 모듈 로드 및 실행
        from baseball_data.def_game_preprocessing import main
        main()
        
        # 작업 디렉토리 복원
        os.chdir(original_dir)
        
        logger.info("데이터 전처리 작업 완료")
    except Exception as e:
        logger.error(f"데이터 전처리 작업 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def run_json_conversion():
    """CSV를 JSON으로 변환하는 작업 실행"""
    try:
        logger.info("CSV to JSON 변환 작업 시작")
        
        # 현재 작업 디렉토리 저장
        original_dir = os.getcwd()
        logger.info(f"현재 작업 디렉토리: {original_dir}")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 작업 디렉토리를 baseball_data로 변경
        os.chdir(baseball_data_dir)
        logger.info(f"작업 디렉토리 변경됨: {os.getcwd()}")
        
        # 직접 모듈 로드 및 실행
        from baseball_data.def_change_json import csv_to_json_with_specific_date
        result = csv_to_json_with_specific_date()
        
        # 작업 디렉토리 복원
        os.chdir(original_dir)
        
        if result:
            logger.info("CSV to JSON 변환 작업 성공")
        else:
            logger.error("CSV to JSON 변환 작업 실패")
            
    except Exception as e:
        logger.error(f"CSV to JSON 변환 작업 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def run_game_data_pipeline():
    """전체 게임 데이터 파이프라인 실행"""
    try:
        logger.info("게임 데이터 파이프라인 시작")
        # 크롤링 -> 전처리 -> JSON 변환 순서대로 실행
        run_crawler()
        run_preprocessing()
        run_json_conversion()
        logger.info("게임 데이터 파이프라인 완료")
    except Exception as e:
        logger.error(f"게임 데이터 파이프라인 중 오류 발생: {str(e)}")

# 스케줄러 설정 및 시작
scheduler = BackgroundScheduler()

# 서울 시간대 설정
seoul_timezone = timezone('Asia/Seoul')

# 매일 ??시에 게임 데이터 파이프라인 실행 (전날 경기 데이터)
scheduler.add_job(
    run_game_data_pipeline,
    trigger=CronTrigger(hour=18, minute=00, timezone=seoul_timezone),
    id='game_data_pipeline',
    name='게임 데이터 파이프라인',
    replace_existing=True
)

@app.get("/")
async def root():
    return {"message": "야금야금 서비스 API에 오신 것을 환영합니다"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)