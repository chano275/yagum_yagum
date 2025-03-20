from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import logging
import os

from database import get_db
import models
from router.account import account_schema, account_crud
from router.user.user_router import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/init", response_model=account_schema.InitAccountResponse)
async def initialize_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계좌번호 초기 발급 시도: 사용자 ID {current_user.USER_ID}")
        
        # 금융 API를 통해 계좌번호만 발급
        from router.user.user_ssafy_api_utils import create_demand_deposit_account
        SAVING_CODE = os.getenv("SAVING_CODE")
        account_num = await create_demand_deposit_account(current_user.USER_KEY, SAVING_CODE)
        
        # 임시 기본값 설정 (나중에 업데이트할 값들)
        default_team_id = 1  # 임시 팀 ID (가장 첫 번째 팀으로 설정)
        default_saving_goal = 1000000  # 100만원으로 임시 설정
        default_daily_limit = 100000  # 10만원으로 임시 설정
        default_month_limit = 1000000  # 100만원으로 임시 설정
        default_source_account = current_user.SOURCE_ACCOUNT  # 사용자의 입출금 계좌로 설정
        
        # 최소한의 정보로 계정 생성 (필수 필드에는 기본값 설정)
        db_account = models.Account(
            USER_ID=current_user.USER_ID,
            TEAM_ID=default_team_id,  # 임시 팀 ID
            ACCOUNT_NUM=account_num,
            INTEREST_RATE=2.5,  # 기본 이자율
            SAVING_GOAL=default_saving_goal,
            DAILY_LIMIT=default_daily_limit,
            MONTH_LIMIT=default_month_limit,
            SOURCE_ACCOUNT=default_source_account,
            TOTAL_AMOUNT=0,
            created_at=datetime.now()
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"계좌번호 초기 발급 완료: 계정 ID {db_account.ACCOUNT_ID}, 계좌번호 {account_num}")
        
        return {"ACCOUNT_ID": db_account.ACCOUNT_ID, "ACCOUNT_NUM": account_num}
        
    except Exception as e:
        logger.error(f"계좌번호 발급 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌번호 발급 중 오류 발생: {str(e)}"
        )

# 계정 생성
@router.post("/", response_model=account_schema.AccountResponse)
async def create_account(
    account: account_schema.AccountCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 생성 시도: 사용자 ID {current_user.USER_ID}")
        
        # CRUD 함수 호출하여 계정 생성
        new_account = await account_crud.create_account(
            db=db,
            user_id=current_user.USER_ID,
            team_id=account.TEAM_ID,
            saving_goal=account.SAVING_GOAL,
            daily_limit=account.DAILY_LIMIT,
            month_limit=account.MONTH_LIMIT,
            source_account=account.SOURCE_ACCOUNT,
            user_key=current_user.USER_KEY
        )
        
        logger.info(f"계정 생성 완료: 계정 ID {new_account.ACCOUNT_ID}")
        return new_account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 생성 중 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 생성 중 오류 발생: {str(e)}"
        )

# 사용자의 전체 계정 조회
@router.get("/user/{user_id}", response_model=List[account_schema.AccountResponse])
async def read_user_accounts(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"사용자 계정 목록 조회: 사용자 ID {user_id}")
        
        # 권한 확인: 본인 계정만 조회 가능 (관리자 기능은 별도로 구현 필요)
        if current_user.USER_ID != user_id:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 대상 ID {user_id}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        accounts = account_crud.get_accounts_by_user_id(db, user_id, skip, limit)
        return accounts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 계정 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 계정 목록 조회 중 오류 발생: {str(e)}"
        )

# # 팀에 속한 계정 조회
# @router.get("/team/{team_id}", response_model=List[account_schema.AccountSummary])
# async def read_team_accounts(
#     team_id: int,
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db)
# ):
#     try:
#         logger.info(f"팀 계정 목록 조회: 팀 ID {team_id}")
#         accounts = account_crud.get_accounts_by_team_id(db, team_id, skip, limit)
#         return accounts
#     except Exception as e:
#         logger.error(f"팀 계정 목록 조회 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"팀 계정 목록 조회 중 오류 발생: {str(e)}"
#         )

# 특정 계정 조회
@router.get("/{account_id}", response_model=account_schema.AccountResponse)
async def read_account(
    account_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 조회 요청: 계정 ID {account_id}")
        
        # 계정 조회
        account = account_crud.get_account_by_id(db, account_id)
        if not account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 조회 가능
        if account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 조회 중 오류 발생: {str(e)}"
        )

# 계정 정보 업데이트
# @router.put("/{account_id}", response_model=account_schema.AccountResponse)
# async def update_account_info(
#     account_id: int,
#     account_update: account_schema.AccountUpdate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"계정 업데이트 요청: 계정 ID {account_id}")
        
#         # 계정 존재 여부 확인
#         db_account = account_crud.get_account_by_id(db, account_id)
#         if not db_account:
#             logger.warning(f"업데이트할 계정을 찾을 수 없음: {account_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="계정을 찾을 수 없습니다"
#             )
        
#         # 권한 확인: 본인 계정만 업데이트 가능
#         if db_account.USER_ID != current_user.USER_ID:
#             logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
#             raise HTTPException(status_code=403, detail="권한이 없습니다")
        
#         # 계정 업데이트
#         updated_account = account_crud.update_account(db, account_id, account_update)
#         if not updated_account:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="계정 정보 업데이트 중 오류가 발생했습니다"
#             )
        
#         return updated_account
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"계정 업데이트 중 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"계정 업데이트 중 오류 발생: {str(e)}"
#         )
@router.put("/{account_id}/setup", response_model=account_schema.AccountResponse)
async def setup_account(
    account_id: int,
    account_setup: account_schema.AccountSetup,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계좌 설정 요청: 계정 ID {account_id}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"설정할 계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 업데이트 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 필수 필드 확인
        if not account_setup.TEAM_ID or not account_setup.SAVING_GOAL or not account_setup.DAILY_LIMIT or not account_setup.MONTH_LIMIT or not account_setup.SOURCE_ACCOUNT:
            logger.warning(f"필수 필드 누락: {account_setup}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="모든 필수 필드를 입력해야 합니다"
            )
            
        # 계정 설정 업데이트
        db_account.TEAM_ID = account_setup.TEAM_ID
        db_account.SAVING_GOAL = account_setup.SAVING_GOAL
        db_account.DAILY_LIMIT = account_setup.DAILY_LIMIT
        db_account.MONTH_LIMIT = account_setup.MONTH_LIMIT
        db_account.SOURCE_ACCOUNT = account_setup.SOURCE_ACCOUNT
        
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"계좌 설정 완료: 계정 ID {account_id}")
        return db_account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계좌 설정 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌 설정 중 오류 발생: {str(e)}"
        )

# 계정 삭제
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 삭제 요청: 계정 ID {account_id}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"삭제할 계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 삭제 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 계정 삭제
        success = account_crud.delete_account(db, account_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="계정 삭제 중 오류가 발생했습니다"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"계정 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 삭제 중 오류 발생: {str(e)}"
        )

# 계정 잔액 업데이트 (입금/출금)
@router.post("/{account_id}/balance", response_model=account_schema.AccountResponse)
async def update_balance(
    account_id: int,
    balance_update: account_schema.BalanceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 잔액 업데이트 요청: 계정 ID {account_id}, 금액 {balance_update.amount}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 업데이트 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 일별 한도 체크 (입금인 경우)
        if balance_update.amount > 0 and balance_update.amount > db_account.DAILY_LIMIT:
            logger.warning(f"일별 한도 초과: 요청 금액 {balance_update.amount}, 한도 {db_account.DAILY_LIMIT}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"일별 입금 한도({db_account.DAILY_LIMIT:,}원)를 초과했습니다"
            )
        
        # 잔액 업데이트
        updated_account = account_crud.update_account_balance(db, account_id, balance_update)
        
        if updated_account is False:  # 잔액 부족
            logger.warning(f"잔액 부족: 계정 ID {account_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="잔액이 부족합니다"
            )
        
        if not updated_account:  # 기타 오류
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="잔액 업데이트 중 오류가 발생했습니다"
            )
        
        return updated_account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"잔액 업데이트 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"잔액 업데이트 중 오류 발생: {str(e)}"
        )

# 계정 일일 잔액 내역 조회
@router.get("/{account_id}/daily-balances", response_model=List[dict])
async def get_daily_balances(
    account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 일일 잔액 내역 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 조회 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 일일 잔액 내역 조회
        balances = account_crud.get_account_daily_balances(db, account_id, start_date, end_date)
        
        # ORM 모델을 딕셔너리로 변환
        result = []
        for balance in balances:
            result.append({
                "DATE": balance.DATE,
                "CLOSING_BALANCE": balance.CLOSING_BALANCE,
                "DAILY_INTEREST": balance.DAILY_INTEREST
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"일일 잔액 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일일 잔액 내역 조회 중 오류 발생: {str(e)}"
        )

# 계정 적금 내역 조회
@router.get("/{account_id}/savings", response_model=List[dict])
async def get_savings(
    account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 적금 내역 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 조회 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 적금 내역 조회
        savings = account_crud.get_account_savings(db, account_id, start_date, end_date)
        
        # ORM 모델을 딕셔너리로 변환
        result = []
        for saving in savings:
            result.append({
                "DATE": saving.DATE,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                "SAVING_RULED_TYPE_ID": saving.SAVING_RULED_TYPE_ID,
                "SAVING_RULED_DETAIL_ID": saving.SAVING_RULED_DETAIL_ID
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 내역 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 내역 조회 중 오류 발생: {str(e)}"
        )

# 계정 적금 규칙 설정 조회
@router.get("/{account_id}/saving-rules", response_model=List[dict])
async def get_saving_rules(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"계정 적금 규칙 설정 조회: 계정 ID {account_id}")
        
        # 계정 존재 여부 확인
        db_account = account_crud.get_account_by_id(db, account_id)
        if not db_account:
            logger.warning(f"계정을 찾을 수 없음: {account_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="계정을 찾을 수 없습니다"
            )
        
        # 권한 확인: 본인 계정만 조회 가능
        if db_account.USER_ID != current_user.USER_ID:
            logger.warning(f"권한 없음: 요청자 ID {current_user.USER_ID}, 계정 소유자 ID {db_account.USER_ID}")
            raise HTTPException(status_code=403, detail="권한이 없습니다")
        
        # 적금 규칙 설정 조회
        rules = account_crud.get_account_saving_rules(db, account_id)
        
        # ORM 모델을 딕셔너리로 변환
        result = []
        for rule in rules:
            result.append({
                "USER_SAVING_RULED_ID": rule.USER_SAVING_RULED_ID,
                "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
                "SAVING_RULE_DETAIL_ID": rule.SAVING_RULE_DETAIL_ID,
                "PLAYER_TYPE_ID": rule.PLAYER_TYPE_ID,
                "USER_SAVING_RULED_AMOUNT": rule.USER_SAVING_RULED_AMOUNT,
                "PLAYER_ID": rule.PLAYER_ID
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 설정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 설정 조회 중 오류 발생: {str(e)}"
        )