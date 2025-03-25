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

saving_rule_type = [
    "기본 규칙",
    "투수",
    "타자",
    "상대팀",
]

# 초기 데이터 생성
initial_saving_rule_type = [
    models.SavingRuleType(SAVING_RULE_TYPE_ID=i + 1, SAVING_RULE_TYPE_NAME = name)
    for i, name in enumerate(saving_rule_type)
]

# 데이터 삽입
session.add_all(initial_saving_rule_type)
session.commit()

print("초기 데이터 삽입 완료")
session.close()
