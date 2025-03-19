from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# DATABASE_URL 설정
DATABASE_URL = f'{os.getenv("DATABASE_TYPE")}://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_IP")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_DB")}?charset=utf8mb4'

# 환경 변수 디버깅을 위해 DATABASE_URL 출력
logger.info(f"Using DATABASE_URL: {DATABASE_URL}")

# 엔진 생성 시 MariaDB 특화 옵션 설정
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,  # MariaDB 연결 timeout 방지
    pool_pre_ping=True,  # 연결이 유효한지 확인
    connect_args={"connect_timeout": 60}  # 연결 타임아웃 설정
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    DB 세션을 제공하는 의존성 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

