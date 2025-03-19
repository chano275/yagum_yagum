import sys
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 (`DB/` 폴더)에 있으므로, 상위 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from database import engine

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE user MODIFY COLUMN PASSWORD VARCHAR(100)"))
    connection.commit()
    print("칼럼 변경 성공")