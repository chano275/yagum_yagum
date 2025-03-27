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

# 미션 이름 리스트
missions_name = [
    "응원팀 10승당 우대금리",
    "직관 인증시 우대금리",
    "정규시즌 응원팀의 순위를 맞춰라라"
]


missions_max_count = [5,5,1]
missions_rate = [0.1,0.1,0.3]

# 초기 데이터 생성
initial_missions = [
    models.Mission(MISSION_NAME=missions_name[i], MISSION_MAX_COUNT = missions_max_count[i], MISSION_RATE = missions_rate[i])
    for i in range(len(missions_name))
]

# 데이터 삽입
session.add_all(initial_missions)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
