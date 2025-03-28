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
rule_combinations = [
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 1},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 2},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 3},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 4},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 5},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 6},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 11},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 12},
    {"SAVING_RULE_TYPE_ID": 1, "RECORD_TYPE_ID": 7},
    {"SAVING_RULE_TYPE_ID": 2, "RECORD_TYPE_ID": 8},
    {"SAVING_RULE_TYPE_ID": 2, "RECORD_TYPE_ID": 9},
    {"SAVING_RULE_TYPE_ID": 2, "RECORD_TYPE_ID": 10},
    {"SAVING_RULE_TYPE_ID": 3, "RECORD_TYPE_ID": 4},
    {"SAVING_RULE_TYPE_ID": 3, "RECORD_TYPE_ID": 5},
    {"SAVING_RULE_TYPE_ID": 3, "RECORD_TYPE_ID": 13},
    {"SAVING_RULE_TYPE_ID": 4, "RECORD_TYPE_ID": 4},
    {"SAVING_RULE_TYPE_ID": 4, "RECORD_TYPE_ID": 5},
    {"SAVING_RULE_TYPE_ID": 4, "RECORD_TYPE_ID": 11},
    {"SAVING_RULE_TYPE_ID": 4, "RECORD_TYPE_ID": 12},
    

]

# 데이터 삽입
for combo in rule_combinations:
    rule = models.SavingRuleList(**combo)
    session.add(rule)

session.commit()
session.close()