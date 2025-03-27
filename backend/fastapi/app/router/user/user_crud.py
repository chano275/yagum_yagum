from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional

import models
from router.user.user_schema import UserCreate, UserUpdate

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key-here"  # 실제 애플리케이션에서는 환경 변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.USER_EMAIL == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.USER_ID == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.PASSWORD):
        return False
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, user_key: str = None, source_account: str = None):
    """사용자 생성 함수"""
    hashed_password = get_password_hash(user.PASSWORD)
    db_user = models.User(
        NAME=user.NAME,
        USER_EMAIL=user.USER_EMAIL,
        PASSWORD=hashed_password,
        USER_KEY=user_key,
        SOURCE_ACCOUNT=source_account,  # 생성된 입출금 계좌번호 저장
        created_at=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# def update_user(db: Session, user_id: int, user: UserUpdate):
#     db_user = get_user_by_id(db, user_id)
    
#     update_data = user.dict(exclude_unset=True)
    
#     # 비밀번호가 포함되어 있으면 해싱
#     if "PASSWORD" in update_data and update_data["PASSWORD"]:
#         update_data["PASSWORD"] = get_password_hash(update_data["PASSWORD"])
    
#     for key, value in update_data.items():
#         setattr(db_user, key, value)
    
#     db.commit()
#     db.refresh(db_user)
#     return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()
    return True