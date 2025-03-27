import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 (`DB/` 폴더)에 있으므로, 상위 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# models 및 database 모듈 가져오기
import models
from database import engine

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

record_type = [
    {
        "name":"승리",
        "comment":"팀이 승리할 경우"
    },
    {
        "name":"안타",
        "comment":"팀이 안타를 칠 경우"
    },
        {
        "name":"홈런",
        "comment":"팀이 홈런을 칠 경우"
    },
        {
        "name":"3연승",
        "comment":"3연승을 달성할 경우"
    },
        {
        "name":"퀄리티 스타트",
        "comment":"6이닝 이상 3자책점 이하로 던질 경우"
    },
        {
        "name":"삼진",
        "comment":"삼진을 잡을 경우"
    },
        {
        "name":"볼넷",
        "comment":"볼넷을 내줄 경우"
    },
        {
        "name":"타점",
        "comment":"타점을 기록할 경우"
    },
        {
        "name":"볼넷/몸맞공",
        "comment":"볼넷이나 몸에 맞는 공으로 출루할 경우"
    },
        {
        "name":"삼진",
        "comment":"삼진으로 아웃될 경우"
    },
        {
        "name":"병살타",
        "comment":"병살타를 칠 경우"
    },
        {
        "name":"안타",
        "comment":"상대팀이 안타를 칠 경우"
    },
        {
        "name":"홈런",
        "comment":"상대팀이 홈런을 칠 경우"
    },
        {
        "name":"실책",
        "comment":"상대팀이 실책을 할 경우"
    },
]

# 초기 데이터 생성
initial_record_type = [
    models.RecordType(RECORD_TYPE_ID=i + 1, RECORD_NAME = type["name"],RECORD_COMMENT=type["comment"])
    for i, type in enumerate(record_type)
]

# 데이터 삽입
session.add_all(initial_record_type)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
