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

players = [
    {
        "team":6,
        "number":29,
        "type":1,
        "name":"김광현",
        "url":"",
        "like":0
    },
]

# 초기 데이터 생성
initial_player = [
    models.Player(
        PLAYER_ID=i + 1, 
        TEAM_ID = player["team"],
        PLAYER_NUM = player["number"],
        PLAYER_TYPE_ID = player["type"],
        PLAYER_NAME = player["name"],
        PLAYER_IMAGE_URL = player["url"],
        LIKE_COUNT = player["like"]
        )
    for i, player in enumerate(players)
]

# 데이터 삽입
session.add_all(initial_player)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
