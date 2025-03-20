from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from fastapi import APIRouter, Depends, HTTPException, status, security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
from router.user.user_schema import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse, TokenData
import router.user.user_crud as user_crud
# 새로 추가된 임포트
from router.user.user_ssafy_api_utils import get_or_create_user_key
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 가져오기 (없으면 기본값 사용)
SECRET_KEY = os.getenv("SECRET_KEY", user_crud.SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", user_crud.ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

router = APIRouter()

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

# JWT 토큰 생성 함수
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# 현재 유저 가져오기
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# 회원가입
@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"회원가입 시도: {user.USER_EMAIL}")
        
        # 기존 사용자 확인
        existing_user = user_crud.get_user_by_email(db, email=user.USER_EMAIL)
        
        if existing_user:
            logger.warning(f"이미 존재하는 이메일: {user.USER_EMAIL}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="이미 가입된 이메일입니다."
            )

        # 1. 금융 API에서 userKey 조회 또는 생성 (기존 로직 유지)
        logger.info(f"금융 API에서 userKey 조회/생성 시작: {user.USER_EMAIL}")
        user_key = await get_or_create_user_key(user.USER_EMAIL, user.NAME)
        
        if not user_key:
            logger.error(f"userKey를 가져오지 못함: {user.USER_EMAIL}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 키를 가져오지 못했습니다"
            )
        
        logger.info(f"금융 API에서 userKey 획득 완료: {user_key}")
        
        # 2. 입출금 계좌 개설 (업데이트된 함수 사용)
        from router.user.user_ssafy_api_utils import create_demand_deposit_account
        logger.info(f"입출금 계좌 개설 시작: userKey {user_key}")
        account_no = await create_demand_deposit_account(user_key)
        logger.info(f"입출금 계좌 개설 완료: 계좌번호 {account_no}")
        
        # 3. 사용자 생성 (SOURCE_ACCOUNT 포함)
        logger.info("새 사용자 생성 시작")
        new_user = user_crud.create_user(
            db=db, 
            user=user, 
            user_key=user_key, 
            source_account=account_no
        )
        logger.info(f"사용자 생성 완료: ID {new_user.USER_ID}, 계좌번호 {account_no}")
        
        return new_user
    
    except HTTPException:
        # HTTP 예외 다시 발생
        raise
    
    except Exception as e:
        # 기타 예외 처리
        logger.error(f"회원가입 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류 발생: {str(e)}"
        )

# 로그인 및 토큰 발급
@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        logger.info(f'로그인 시도: {form_data.username}')
        
        # 회원 존재 여부 및 비밀번호 확인
        user = user_crud.authenticate_user(db, form_data.username, form_data.password)

        if not user:
            logger.warning(f"유효하지 않은 사용자 또는 비밀번호: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다",
                headers={"WWW-Authenticate":"Bearer"},
            )
        
        # 액세스 토큰 생성 (만료 시간 설정)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.USER_EMAIL, "user_id": user.USER_ID},
            expires_delta=access_token_expires
        )

        logger.info(f"로그인 성공: {form_data.username}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위
            "user": {
                "id": user.USER_ID,
                "name": user.NAME,
                "email": user.USER_EMAIL
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        logger.error(f"로그인 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 사용자 목록 조회
@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        logger.info(f"사용자 목록 조회: skip={skip}, limit={limit}")
        users = user_crud.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        logger.error(f"사용자 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 현재 로그인한 사용자 정보 조회
@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: models.User = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )

# # 특정 사용자 정보 조회
# @router.get("/{user_id}", response_model=UserResponse)
# async def get_user(user_id: int, db: Session = Depends(get_db)):
#     try:
#         logger.info(f"사용자 조회 요청: {user_id}")
#         user = user_crud.get_user_by_id(db, user_id=user_id)
        
#         if not user:
#             logger.warning(f"사용자를 찾을 수 없음: {user_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="사용자를 찾을 수 없습니다"
#             )
            
#         return user
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"사용자 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 조회 중 오류가 발생했습니다: {str(e)}"
#         )

# # 사용자 정보 업데이트 - 수정된 부분
# @router.put("/{user_id}", response_model=UserResponse)
# async def update_user_info(user_id: int, user: UserUpdate, db: Session = Depends(get_db), 
#                           current_user: models.User = Depends(get_current_user)):
#     try:
#         logger.info(f"사용자 업데이트 요청: {user_id}")
        
#         # 권한 확인
#         if current_user.USER_ID != user_id:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 대상 ID {user_id}")
#             raise HTTPException(status_code=403, detail="권한이 없습니다")
        
#         # 사용자 존재 여부 확인
#         db_user = user_crud.get_user_by_id(db, user_id=user_id)
#         if not db_user:
#             logger.warning(f"업데이트할 사용자를 찾을 수 없음: {user_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="사용자를 찾을 수 없습니다"
#             )
        
#         # 이메일 변경 시 중복 확인 및 userKey 업데이트
#         if user.USER_EMAIL and user.USER_EMAIL != db_user.USER_EMAIL:
#             email_exists = user_crud.get_user_by_email(db, email=user.USER_EMAIL)
#             if email_exists:
#                 logger.warning(f"이미 존재하는 이메일: {user.USER_EMAIL}")
#                 raise HTTPException(
#                     status_code=status.HTTP_409_CONFLICT,
#                     detail="이미 가입된 이메일입니다"
#                 )
                
#             # 이메일 변경 시 금융 API에서 userKey 다시 조회
#             logger.info(f"이메일 변경으로 금융 API에서 userKey 재조회: {user.USER_EMAIL}")
#             user_key = await get_or_create_user_key(user.USER_EMAIL, db_user.NAME)
            
#             # userKey 설정
#             user_data = user.dict(exclude_unset=True)
#             user_data["USER_KEY"] = user_key
#             user = UserUpdate(**user_data)
        
#         # 사용자 정보 업데이트
#         updated_user = user_crud.update_user(db=db, user_id=user_id, user=user)
#         return updated_user
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"사용자 업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 업데이트 중 오류가 발생했습니다: {str(e)}"
#         )

# 사용자 삭제
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db), 
                     current_user: models.User = Depends(get_current_user)):
    try:
        logger.info(f"사용자 삭제 요청: {user_id}")
        
        # 권한 확인
        if current_user.USER_ID != user_id:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 대상 ID {user_id}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 사용자 존재 여부 확인
        db_user = user_crud.get_user_by_id(db, user_id=user_id)
        if not db_user:
            logger.warning(f"삭제할 사용자를 찾을 수 없음: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 사용자 삭제
        success = user_crud.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 삭제 중 오류가 발생했습니다"
            )
            
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 삭제 중 오류가 발생했습니다: {str(e)}"
        )