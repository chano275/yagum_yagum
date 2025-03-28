import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 (`DB/` 폴더)에 있으므로, 상위 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# models 및 database 모듈 가져오기
import models
from database import engine

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

record_type = [
    {
        "name":"승리",
    },
    {
        "name":"패배",
    },
    {
        "name":"무승부",
    },
    {
        "name":"안타",
    },
    {
        "name":"홈런",
    },
    {
        "name":"득점",
    },
    {
        "name":"스윕",
    },
    {
        "name":"삼진",
    },
    {
        "name":"볼넷/몸맞공",
    },
    {
        "name":"자책",
    },
    {
        "name":"병살타",
    },
    {
        "name":"실책",
    },
    {
        "name":"도루",
    }
]

# 초기 데이터 생성
initial_record_type = [
    models.RecordType(RECORD_TYPE_ID=i + 1, RECORD_NAME = type["name"])
    for i, type in enumerate(record_type)
]

# 데이터 삽입
session.add_all(initial_record_type)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
