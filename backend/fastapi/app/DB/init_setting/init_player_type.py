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

player_types = [
    "투수",
    "타자"
]

# 초기 데이터 생성
initial_player_type = [
    models.PlayerType(PLAYER_TYPE_ID=i + 1, PLAYER_TYPE_NAME = name)
    for i, name in enumerate(player_types)
]

# 데이터 삽입
session.add_all(initial_player_type)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
