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

# 적금 규칙 타입과 기록 유형 조합 생성
saving_rules = [
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":1},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":2},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":3},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":4},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":5},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":6},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":7},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":8},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":9},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":10},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":11},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":11},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":11},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":11},
]

# 데이터 삽입
for combo in saving_rules:
    rule = models.SavingRuleDetail(**combo)
    session.add(rule)

session.commit()
session.close()

print("DB에 추가 성공")