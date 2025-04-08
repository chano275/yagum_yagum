from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
import os
import importlib
import logging
import traceback
from datetime import datetime, time, timedelta
from pytz import timezone
from sqlalchemy.orm import sessionmaker
# APScheduler 추가
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

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
from utils.process_saving import process_savings_for_date

# 데이터베이스 초기화
from database import engine
import models
models.Base.metadata.create_all(bind=engine)

# Job 실행 결과를 처리하는 리스너
def job_listener(event):
    if event.exception:
        logger.error(f"작업 {event.job_id} 실행 중 오류 발생: {event.exception}")
        logger.error(traceback.format_exc())
    else:
        logger.info(f"작업 {event.job_id} 성공적으로 완료됨")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # 애플리케이션 시작 시 실행
        scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        scheduler.start()
        logger.info("스케줄러 시작됨")
        
        # 현재 등록된 모든 작업 출력
        for job in scheduler.get_jobs():
            logger.info(f"등록된 작업: {job.name}, 다음 실행 시간: {job.next_run_time}")
        
        yield  # 애플리케이션 실행 중
    except Exception as e:
        logger.critical(f"애플리케이션 시작 중 심각한 오류 발생: {str(e)}")
        logger.critical(traceback.format_exc())
    finally:
        # 애플리케이션 종료 시 실행
        try:
            scheduler.shutdown()
            logger.info("스케줄러 정상 종료됨")
        except Exception as e:
            logger.error(f"스케줄러 종료 중 오류 발생: {str(e)}")

app = FastAPI(
    title="야금야금 서비스 API",
    description="야구 기반 적금 서비스를 위한 백엔드 API",
    version="1.0.0",
    lifespan=lifespan
)

# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"전역 예외 발생: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "서버 내부 오류가 발생했습니다."}
    )

# 검증 예외 핸들러
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"요청 검증 오류: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "요청 데이터 검증에 실패했습니다.", "detail": exc.errors()}
    )

# HTTP 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP 예외: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
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

# 공통 유틸리티 함수
def change_directory(target_dir):
    """
    작업 디렉토리를 변경하고 원래 디렉토리를 반환
    """
    original_dir = os.getcwd()
    logger.info(f"현재 작업 디렉토리: {original_dir}")
    
    try:
        os.chdir(target_dir)
        logger.info(f"작업 디렉토리 변경됨: {os.getcwd()}")
        return original_dir
    except Exception as e:
        logger.error(f"디렉토리 변경 중 오류: {str(e)}")
        raise

def run_function_with_directory_change(directory, function, *args, **kwargs):
    """
    디렉토리를 변경하고 함수를 실행한 후 원래 디렉토리로 돌아가는 유틸리티 함수
    """
    original_dir = None
    try:
        if directory:
            original_dir = change_directory(directory)
        return function(*args, **kwargs)
    except Exception as e:
        raise
    finally:
        if original_dir:
            try:
                os.chdir(original_dir)
                logger.info(f"작업 디렉토리 복원됨: {original_dir}")
            except Exception as e:
                logger.error(f"작업 디렉토리 복원 중 오류: {str(e)}")

# 스케줄러 작업 함수들
def run_crawler():
    """경기 기록 크롤링 작업 실행"""
    try:
        logger.info("경기 기록 크롤링 작업 시작")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 경로가 존재하는지 확인
        if not os.path.exists(baseball_data_dir):
            logger.error(f"baseball_data 디렉토리가 존재하지 않습니다: {baseball_data_dir}")
            return False
        
        # 모듈 임포트 확인
        try:
            from baseball_data.def_crawl_gamelog import crawl_gamelog
        except ImportError as e:
            logger.error(f"crawl_gamelog 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행
        result = run_function_with_directory_change(baseball_data_dir, crawl_gamelog)
        
        if result:
            logger.info("경기 기록 크롤링 작업 성공")
            return True
        else:
            logger.error("경기 기록 크롤링 작업 실패")
            return False
            
    except Exception as e:
        logger.error(f"경기 기록 크롤링 작업 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_preprocessing():
    """데이터 전처리 작업 실행"""
    try:
        logger.info("데이터 전처리 작업 시작")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 경로가 존재하는지 확인
        if not os.path.exists(baseball_data_dir):
            logger.error(f"baseball_data 디렉토리가 존재하지 않습니다: {baseball_data_dir}")
            return False
        
        # 모듈 임포트 확인
        try:
            from baseball_data.def_game_preprocessing import main
        except ImportError as e:
            logger.error(f"game_preprocessing 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행
        run_function_with_directory_change(baseball_data_dir, main)
        
        logger.info("데이터 전처리 작업 완료")
        return True
    except Exception as e:
        logger.error(f"데이터 전처리 작업 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_json_conversion():
    """CSV를 JSON으로 변환하는 작업 실행"""
    try:
        logger.info("CSV to JSON 변환 작업 시작")
        
        # baseball_data 디렉토리 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data')
        logger.info(f"baseball_data 디렉토리 경로: {baseball_data_dir}")
        
        # 경로가 존재하는지 확인
        if not os.path.exists(baseball_data_dir):
            logger.error(f"baseball_data 디렉토리가 존재하지 않습니다: {baseball_data_dir}")
            return False
        
        # 모듈 임포트 확인
        try:
            from baseball_data.def_change_json import csv_to_json_with_specific_date
        except ImportError as e:
            logger.error(f"change_json 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행
        result = run_function_with_directory_change(baseball_data_dir, csv_to_json_with_specific_date)
        
        if result:
            logger.info("CSV to JSON 변환 작업 성공")
            return True
        else:
            logger.error("CSV to JSON 변환 작업 실패")
            return False
            
    except Exception as e:
        logger.error(f"CSV to JSON 변환 작업 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_update_game_log():
    """경기 로그를 저장하는 작업 실행"""
    try:
        logger.info("경기 로그 저장 파이프라인 실행")
        
        # 모듈 임포트 확인
        try:
            from utils.update_game_log import process_json_game_logs
        except ImportError as e:
            logger.error(f"update_game_log 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행
        process_json_game_logs()
        
        logger.info("경기 로그 저장 작업 성공")
        return True
        
    except Exception as e:
        logger.error(f"경기 로그 저장 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_save_player_record():
    """선수 기록을 저장하는 작업 실행"""
    try:
        logger.info("선수 기록 저장 파이프라인 실행")
        
        # 모듈 임포트 확인
        try:
            from utils.save_player_record import process_game_data_folder
        except ImportError as e:
            logger.error(f"save_player_record 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행
        process_game_data_folder()
        
        logger.info("선수 기록 저장 작업 성공")
        return True
        
    except Exception as e:
        logger.error(f"선수 기록 저장 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_update_daily_rank():
    """팀 순위를 저장하는 작업 실행"""
    try:
        logger.info("팀 순위 저장 파이프라인 실행")
        
        # 모듈 임포트 확인
        try:
            from utils.update_daily_rank import process_daily_rank_file, find_rank_file
        except ImportError as e:
            logger.error(f"update_daily_rank 모듈 임포트 실패: {str(e)}")
            return False
        
        # 경로 확인
        baseball_data_dir = os.path.join(os.path.dirname(__file__), 'baseball_data','daily_rank')
        logger.info(baseball_data_dir)
        if not os.path.exists(baseball_data_dir):
            logger.error(f"baseball_data 디렉토리가 존재하지 않습니다: {baseball_data_dir}")
            return False
            
        # 타겟 날짜 설정 및 파일 찾기
        target_date = datetime.now().date() - timedelta(days=1)
        
        try:
            rank_file = find_rank_file(baseball_data_dir, target_date)
            if not rank_file:
                logger.warning(f"{target_date} 날짜에 해당하는 순위 파일을 찾을 수 없습니다.")
                return False
                
            result = process_daily_rank_file(rank_file)
            
            if result:
                logger.info("팀 순위 저장 작업 성공")
                return True
            else:
                logger.error("팀 순위 저장 작업 실패")
                return False
        except Exception as e:
            logger.error(f"순위 파일 처리 중 오류: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"팀 순위 저장 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_saving():
    """유저별 일일 적금 금액 저장하는 작업 실행"""
    try:
        logger.info("유저별 일일 적금 금액 저장 파이프라인 실행")
        
        # 모듈 임포트 확인
        try:
            from utils.process_saving import process_savings_for_date
        except ImportError as e:
            logger.error(f"process_saving 모듈 임포트 실패: {str(e)}")
            return False
        
        # 함수 실행 (예외 처리 추가)
        try:
            result = process_savings_for_date(None)
            logger.info(f"처리 결과: {result}")
            return True
        except Exception as e:
            logger.error(f"process_savings_for_date 실행 중 오류: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"유저별 일일 적금 금액 저장 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def run_transfer():
    """
        유저별 적금액 이체
    """
    try:
        logger.info("유저별 일일 적금 이체")

        try:
            from utils.process_transfer import process_actual_transfers
        except ImportError as e:
            logger.error(f"process_actual_transfers 모듈 임포트 실패: {str(e)}")
            return False

        # 함수 실행 (예외 처리 추가) TODO
        try:
            # 데이터베이스 연결
            Session = sessionmaker(bind=engine)
            db = Session()

            result = await process_actual_transfers(db)
            logger.info(f"처리 결과: {result}")
            return True
        except Exception as e:
            logger.error(f"process_savings_for_date 실행 중 오류: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"유저별 적금액 이체 작업 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def sync_run_trsnfer():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_transfer())
    finally:
        loop.close()

def run_game_data_pipeline(**kwargs):
    """전체 게임 데이터 파이프라인 실행
    
    kwargs: 스케줄러에서 전달되는 추가 매개변수(retries 등)
    """
    pipeline_success = True
    
    try:
        # 재시도 횟수 로깅 (있는 경우)
        if 'retries' in kwargs and kwargs['retries'] > 0:
            logger.info(f"게임 데이터 파이프라인 재시도 #{kwargs['retries']} 시작")
        else:
            logger.info("게임 데이터 파이프라인 시작")
        
        # 크롤링 실행
        if not run_crawler():
            logger.error("크롤링 단계 실패, 다음 단계 진행")
            pipeline_success = False
        
        # 전처리 실행 (크롤링이 실패해도 이전 데이터로 진행)
        if not run_preprocessing():
            logger.error("전처리 단계 실패, 다음 단계 진행")
            pipeline_success = False
        
        # JSON 변환 실행 (이전 단계가 실패해도 진행)
        if not run_json_conversion():
            logger.error("JSON 변환 단계 실패")
            pipeline_success = False
        
        if pipeline_success:
            logger.info("게임 데이터 파이프라인 성공적으로 완료")
        else:
            logger.warning("게임 데이터 파이프라인 일부 단계 실패, 가능한 데이터까지 처리됨")
            
        return pipeline_success
        
    except Exception as e:
        logger.error(f"게임 데이터 파이프라인 중 예기치 않은 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_user_saving_pipeline(**kwargs):
    """경기기록 저장 및 사용자별 적금 금액 파이프라인 실행
    
    kwargs: 스케줄러에서 전달되는 추가 매개변수(retries 등)
    """
    pipeline_success = True
    
    try:
        # 재시도 횟수 로깅 (있는 경우)
        if 'retries' in kwargs and kwargs['retries'] > 0:
            logger.info(f"경기 기록 저장 및 사용자별 적금 금액 파이프라인 재시도 #{kwargs['retries']} 시작")
        else:
            logger.info("경기 기록 저장 및 사용자별 적금 금액 파이프라인 시작")
        
        # 경기 로그 업데이트
        if not run_update_game_log():
            logger.error("경기 로그 업데이트 단계 실패, 다음 단계 진행")
            pipeline_success = False
        
        # 선수 기록 저장
        if not run_save_player_record():
            logger.error("선수 기록 저장 단계 실패, 다음 단계 진행")
            pipeline_success = False
        
        # 일일 순위 업데이트
        if not run_update_daily_rank():
            logger.error("일일 순위 업데이트 단계 실패, 다음 단계 진행")
            pipeline_success = False
        
        # 적금 처리
        if not run_saving():
            logger.error("적금 처리 단계 실패")
            pipeline_success = False
        
        if pipeline_success:
            logger.info("경기 기록 저장 및 사용자별 적금 금액 파이프라인 성공적으로 완료")
        else:
            logger.warning("경기 기록 저장 및 사용자별 적금 금액 파이프라인 일부 단계 실패, 가능한 데이터까지 처리됨")
            
        return pipeline_success
        
    except Exception as e:
        logger.error(f"경기기록 저장 및 사용자별 적금 금액 파이프라인 중 예기치 않은 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        return False


# 스케줄러 설정 및 시작
scheduler = BackgroundScheduler(timezone=timezone('Asia/Seoul'))

# 서울 시간대 설정
seoul_timezone = timezone('Asia/Seoul')

# 스케줄러 복구 시도
def retry_job(job_id, max_retries=3, retry_delay=300):
    """실패한 작업을 재시도하는 함수"""
    job = scheduler.get_job(job_id)
    if job is None:
        logger.error(f"재시도할 작업을 찾을 수 없음: {job_id}")
        return
        
    # 작업의 현재 재시도 횟수 확인 - 기본값 0
    retries = job.kwargs.get('retries', 0) + 1
    
    if retries <= max_retries:
        logger.info(f"작업 {job_id} 재시도 중 ({retries}/{max_retries}), {retry_delay}초 후 실행")
        
        # 현재 시간 + 지연 시간으로 한 번만 실행되는 작업 추가
        run_date = datetime.now(seoul_timezone) + timedelta(seconds=retry_delay)
        
        # 원래 작업의 함수 참조
        func = job.func
        
        # 함수의 인자 검사
        try:
            import inspect
            sig = inspect.signature(func)
            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            
            # kwargs를 받는 함수인 경우에만 retries 전달
            if has_kwargs:
                scheduler.add_job(
                    func,
                    'date',
                    run_date=run_date,
                    id=f"{job_id}_retry_{retries}",
                    kwargs={'retries': retries},
                    name=f"{job.name} (재시도 {retries})"
                )
            else:
                # kwargs를 받지 않는 함수는 retries 없이 실행
                logger.info(f"함수 {func.__name__}는 가변 키워드 인자를 받지 않으므로 retries 인자 없이 실행합니다")
                scheduler.add_job(
                    func,
                    'date',
                    run_date=run_date,
                    id=f"{job_id}_retry_{retries}",
                    name=f"{job.name} (재시도 {retries})"
                )
        except Exception as e:
            logger.error(f"재시도 작업 추가 중 오류 발생: {str(e)}")
            # 최소한의 방식으로 재시도 시도
            try:
                scheduler.add_job(
                    func,
                    'date',
                    run_date=run_date,
                    id=f"{job_id}_retry_{retries}",
                    name=f"{job.name} (재시도 {retries})"
                )
            except Exception as e2:
                logger.error(f"재시도 작업 추가 2차 시도 중 오류 발생: {str(e2)}")
    else:
        logger.error(f"작업 {job_id}의 최대 재시도 횟수 ({max_retries})를 초과했습니다.")

# 작업 오류 리스너
def error_listener(event):
    if event.exception:
        logger.error(f"작업 {event.job_id} 실행 중 오류 발생: {event.exception}")
        retry_job(event.job_id)

# 오류 리스너 등록
scheduler.add_listener(error_listener, EVENT_JOB_ERROR)

# 매일 ??시에 게임 데이터 파이프라인 실행 (전날 경기 데이터)
try:
    scheduler.add_job(
        run_game_data_pipeline,
        trigger=CronTrigger(hour=15, minute=30, timezone=seoul_timezone),
        id='game_data_pipeline',
        name='게임 데이터 파이프라인',
        replace_existing=True,
        misfire_grace_time=3600  # 1시간의 미스파이어 허용 시간
    )
    logger.info("게임 데이터 파이프라인 작업이 스케줄러에 추가되었습니다.")
except Exception as e:
    logger.error(f"게임 데이터 파이프라인 작업 추가 중 오류 발생: {str(e)}")

try:
    scheduler.add_job(
        run_user_saving_pipeline,
        trigger=CronTrigger(hour=15, minute=35, timezone=seoul_timezone),
        id='user_saving_pipeline',
        name="경기 기록 및 사용자별 적금 금액 파이프라인",
        replace_existing=True,
        misfire_grace_time=3600  # 1시간의 미스파이어 허용 시간
    )
    logger.info("경기 기록 및 사용자별 적금 금액 파이프라인 작업이 스케줄러에 추가되었습니다.")
except Exception as e:
    logger.error(f"경기 기록 및 사용자별 적금 금액 파이프라인 작업 추가 중 오류 발생: {str(e)}")

# # 적금 이체 스케줄러 필요시 주석처리리
# try:
#     scheduler.add_job(
#         sync_run_trsnfer,
#         trigger = CronTrigger(hour=20, minute=45, timezone=seoul_timezone),
#         id='transfer',
#         name="적금 이체",
#         replace_existing=True,
#         misfire_grace_time=3600
#     )
#     logger.info("적금 이체 작업이 스케줄러에 추가되었습니다.")
# except Exception as e:
#     logger.error

@app.get("/")
async def root():
    return {"message": "야금야금 서비스 API에 오신 것을 환영합니다"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)