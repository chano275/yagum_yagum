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
from router.user.user_schema import UserCreate, UserResponse, TokenResponse, TokenData,CheckNum
import router.user.user_crud as user_crud
from router.account import account_schema, account_crud
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
        

        # 2-2. 입출금 계좌 자동 입금 (3000만원)
        from router.user.user_ssafy_api_utils import init_money
        logger.info(f"입출금 계좌 초기 자금 입금: userKey{user_key}")
        money_log = await init_money(user_key,account_no)

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

        # 사용자의 계정 정보 조회
        accounts = db.query(models.Account).filter(models.Account.USER_ID == user.USER_ID).all()
        
        # 팀 정보 추가
        team_info = None
        if accounts:
            for account in accounts:
                if account.TEAM_ID:
                    team = db.query(models.Team).filter(models.Team.TEAM_ID == account.TEAM_ID).first()
                    if team:
                        team_info = {
                            "team_id": team.TEAM_ID,
                            "team_name": team.TEAM_NAME,
                            "account_id": account.ACCOUNT_ID
                        }
                        break

        logger.info(f"로그인 성공: {form_data.username}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위
            "user": {
                "id": user.USER_ID,
                "name": user.NAME,
                "email": user.USER_EMAIL
            },
            "team": team_info  # 팀 정보 추가
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

@router.get("/transaction-history", response_model=List[dict])
async def read_transaction_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: str = "A",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    로그인한 사용자의 계좌 거래 내역을 조회합니다.
    
    Args:
        start_date (str, optional): 조회 시작 날짜 (YYYYMMDD 형식). 지정하지 않으면 1개월 전.
        end_date (str, optional): 조회 종료 날짜 (YYYYMMDD 형식). 지정하지 않으면 오늘.
        transaction_type (str, optional): 거래구분 (A: 전체, M: 입금, D: 출금). 기본값은 A.
        
    Returns:
        List[dict]: 거래 내역 목록
    """
    try:
        logger.info(f"사용자 거래 내역 조회 요청: 사용자 ID {current_user.USER_ID}")
        
        # 사용자 키 확인
        user_key = current_user.USER_KEY
        if not user_key:
            logger.warning(f"사용자 키가 없음: 사용자 ID {current_user.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자 인증 정보가 없습니다"
            )
        
        # 사용자의 출금 계좌 정보 확인 (SOURCE_ACCOUNT)
        source_account = current_user.SOURCE_ACCOUNT
        if not source_account:
            logger.warning(f"출금 계좌 정보가 없음: 사용자 ID {current_user.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="계좌 정보가 없습니다"
            )
        
        # 날짜 설정 (기본값: 1개월)
        if not end_date:
            today = datetime.now()
            end_date = today.strftime("%Y%m%d")
        
        if not start_date:
            # 1개월 전
            one_month_ago = datetime.now() - timedelta(days=30)
            start_date = one_month_ago.strftime("%Y%m%d")
        
        # 날짜 형식 검증
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            logger.warning(f"날짜 형식 오류: {start_date}, {end_date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요."
            )
        
        # 거래 내역 조회
        from router.user.user_ssafy_api_utils import get_transaction_history
        transactions = await get_transaction_history(
            user_key=user_key,
            account_num=source_account,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        transactions = transactions.get("list")
        # 트랜잭션 정보 가공 및 반환
        result = []
        for transaction in transactions:
            result.append({
                "transactionDate": transaction.get("transactionDate"),
                "balance": transaction.get("transactionBalance"),
                "summary" :transaction.get("transactionSummary"),
                "afterBalance" : transaction.get("transactionAfterBalance"),
                "transactionType" : transaction.get("transactionTypeName")
            })
        
        logger.info(f"거래 내역 조회 완료: {len(result)}건")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"거래 내역 조회 중 오류 발생: {str(e)}"
        )

@router.post("/transfer-money")
async def transfer_money(
    deposit_account_no = str,
    balance = int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
        로그인한 사용자의 계좌에서 다른 계좌로 돈을 이체합니다.

        deposit_account_no : 입금 계좌 번호
        balance : 이체 금액
    """
    try:
        logger.info(f"사용자 계좌 이체 요청: 사용자 ID {current_user.USER_ID}")
        
        # 사용자 키 확인
        user_key = current_user.USER_KEY
        if not user_key:
            logger.warning(f"사용자 키가 없음: 사용자 ID {current_user.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자 인증 정보가 없습니다"
            )
        
        # 사용자의 출금 계좌 정보 확인 (SOURCE_ACCOUNT)
        source_account = current_user.SOURCE_ACCOUNT
        if not source_account:
            logger.warning(f"출금 계좌 정보가 없음: 사용자 ID {current_user.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="계좌 정보가 없습니다"
            )
        
        # 계좌 이체 
        from router.user.user_ssafy_api_utils import post_transfer_money
        transfer = await post_transfer_money(
            user_key=user_key,
            deposit_account_no=deposit_account_no,
            transaction_balance=balance,
            withdrawal_account_no=source_account,
            text=current_user.NAME
        )
        # # 트랜잭션 정보 가공 및 반환
        # result = []
        # for transaction in transfer:
        #     result.append({
        #         "transactionDate": transaction.get("transactionDate"),
        #         "balance": transaction.get("transactionBalance"),
        #         "summary" :transaction.get("transactionSummary"),
        #         "afterBalance" : transaction.get("transactionAfterBalance")
        #     })
        
        logger.info(f"계좌 이체 완료")
        return "계좌 이체 완료"

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계좌 이체 요청 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌 이체 요청 중 오류 발생: {str(e)}"
        )


   
@router.get("/accounts", response_model=account_schema.UserAccountsResponse)
async def get_user_accounts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 계좌 정보 조회 요청: 사용자 ID {current_user.USER_ID}")
        
        # 입출금 계좌 정보 가져오기
        source_account = current_user.SOURCE_ACCOUNT
        
        # 금융 API를 통해 입출금 계좌 잔액 조회
        from router.user.user_ssafy_api_utils import get_account_balance
        
        source_account_balance = await get_account_balance(
            user_key=current_user.USER_KEY,
            account_num=source_account
        )
        
        # 사용자의 모든 적금 계좌 조회
        savings_accounts = account_crud.get_accounts_by_user_id(db, current_user.USER_ID)
        
        # 적금 계좌 정보 구성
        savings_info = []
        for account in savings_accounts:
            # 팀 이름 조회
            team = db.query(models.Team).filter(models.Team.TEAM_ID == account.TEAM_ID).first()
            
            # 진행률 계산
            progress_percentage = (account.TOTAL_AMOUNT / account.SAVING_GOAL * 100) if account.SAVING_GOAL > 0 else 0
            
            savings_info.append({
                "account_id": account.ACCOUNT_ID,
                "account_num": account.ACCOUNT_NUM,
                "total_amount": account.TOTAL_AMOUNT,
                "interest_rate": account.INTEREST_RATE,
                "saving_goal": account.SAVING_GOAL,
                "progress_percentage": round(progress_percentage, 2),
                "team_name": team.TEAM_NAME if team else None,
                "created_at": account.created_at
            })
        
        # 결과 구성
        result = {
            "user_id": current_user.USER_ID,
            "user_email": current_user.USER_EMAIL,
            "user_name": current_user.NAME,
            "source_account": {
                "account_num": source_account,
                "total_amount": source_account_balance
            },
            "savings_accounts": savings_info
        }
        
        return result
        
    except Exception as e:
        logger.error(f"사용자 계좌 정보 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 계좌 정보 조회 중 오류 발생: {str(e)}"
        )
    
@router.get("check-account-num", response_model=CheckNum)
async def check_account_num(
    account_num: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 사용자 키 확인
        user_key = current_user.USER_KEY
        if not user_key:
            logger.warning(f"사용자 키가 없음: 사용자 ID {current_user.USER_ID}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자 인증 정보가 없습니다"
            )

        try:
            from router.user.user_ssafy_api_utils import check_account_num
            user_name = await check_account_num(
                user_key=user_key,
                account_no=account_num
            )

            # 성공 응답
            result = {
                "NAME": user_name,
                "ACCOUNT_NUM": account_num,
                "BOOL": True
            }
            return result
            
        except Exception as api_error:
            error_message = str(api_error)
            # 계좌번호 유효성 오류 확인
            if "계좌번호가 유효하지 않습니다" in error_message:
                # 유효하지 않은 계좌번호일 경우도 200 응답, 하지만 BOOL은 False
                result = {
                    "NAME": "",
                    "ACCOUNT_NUM": account_num,
                    "BOOL": False
                }
                return result
            else:
                # 그 외의 API 오류는 다시 예외로 발생시켜 외부 catch로 전달
                raise api_error

    except Exception as e:
        logger.error(f"계좌번호 조회 중 오류: {str(e)}")
        # 다른 모든 오류에 대해서는 500 에러 응답
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌번호 조회 중 오류가 발생했습니다: {str(e)}"
        )

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
 