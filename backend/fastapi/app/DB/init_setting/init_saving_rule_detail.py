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

# 적금 규칙 타입과 기록 유형 조합 생성
saving_rules = [
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":1,"RULE_DESCRIPTION":"팀이 승리하는 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":4,"RULE_DESCRIPTION":"팀이 안타를 친 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":5,"RULE_DESCRIPTION":"팀이 홈런을 친 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":6,"RULE_DESCRIPTION":"팀이 득점하는 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":7,"RULE_DESCRIPTION":"팀이 병살타하는 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":8,"RULE_DESCRIPTION":"팀이 실책하는 경우"},
    {"SAVING_RULE_TYPE_ID": 1, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":9,"RULE_DESCRIPTION":"팀이 스윕하는 경우"},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":10,"RULE_DESCRIPTION":"이(가) 삼진을 잡는 경우"},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":11,"RULE_DESCRIPTION":"이(가) 볼넷을 던진 경우"},
    {"SAVING_RULE_TYPE_ID": 2, "PLAYER_TYPE_ID": 1,"SAVING_RULE_ID":12,"RULE_DESCRIPTION":"이(가) 자책하는 경우"},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":13,"RULE_DESCRIPTION":"이(가) 안타를 친 경우"},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":14,"RULE_DESCRIPTION":"이(가) 홈런을 친 경우"},
    {"SAVING_RULE_TYPE_ID": 3, "PLAYER_TYPE_ID": 2,"SAVING_RULE_ID":15,"RULE_DESCRIPTION":"이(가) 도루하는 경우"},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":16,"RULE_DESCRIPTION":"상대팀이 안타를 친 경우"},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":17,"RULE_DESCRIPTION":"상대팀이 홈런을 친 경우"},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":18,"RULE_DESCRIPTION":"상대팀이 병살타하는 경우"},
    {"SAVING_RULE_TYPE_ID": 4, "PLAYER_TYPE_ID": None,"SAVING_RULE_ID":19,"RULE_DESCRIPTION":"상대팀이 실책하는 경우"},

]

# 데이터 삽입
for combo in saving_rules:
    rule = models.SavingRuleDetail(**combo)
    session.add(rule)

session.commit()
session.close()

print("DB에 추가 성공")