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

# 팀 이름 리스트
team_names = [
    "KIA 타이거즈", "삼성 라이온즈", "LG 트윈스", "두산 베어스",
    "KT 위즈", "SSG 랜더스", "롯데 자이언츠", "한화 이글스",
    "NC 다이노스", "키움 히어로즈"
]

# 초기 데이터 생성
initial_teams = [
    models.Team(TEAM_ID=i + 1, TEAM_NAME=name, TOTAL_WIN=0, TOTAL_LOSE=0, TOTAL_DRAW=0)
    for i, name in enumerate(team_names)
]

# 데이터 삽입
session.add_all(initial_teams)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
