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

@router.post("/create", response_model=account_schema.AccountCreateResponse)
async def create_account(
    request: account_schema.AccountCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """모든 정보를 한 번에 전송하여 적금 가입"""
    try:
        logger.info(f"적금 가입 요청: 사용자 ID {current_user.USER_ID}")
        
        # 1. 팀 존재 여부 확인
        team = db.query(models.Team).filter(models.Team.TEAM_ID == request.TEAM_ID).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선택한 팀이 존재하지 않습니다"
            )
        
        # 2. 목표 설정 유효성 검사
        if request.SAVING_GOAL <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="저축 목표액은 0보다 커야 합니다"
            )
        
        if request.DAILY_LIMIT <= 0 or request.MONTH_LIMIT <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="일일 한도와 월 한도는 0보다 커야 합니다"
            )
        
        if request.MONTH_LIMIT < request.DAILY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="월 한도는 일일 한도보다 커야 합니다"
            )
        
        # 3. 규칙 유효성 검사
        if not request.saving_rules or len(request.saving_rules) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="적어도 하나의 적금 규칙을 설정해야 합니다"
            )
        
        for rule in request.saving_rules:
            # 규칙 타입 확인
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
            ).first()
            
            if not rule_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"규칙 타입 ID {rule.SAVING_RULE_TYPE_ID}이 존재하지 않습니다"
                )
                
            # 기록 타입 확인
            record_type = db.query(models.RecordType).filter(
                models.RecordType.RECORD_TYPE_ID == rule.RECORD_TYPE_ID
            ).first()
            
            if not record_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"기록 타입 ID {rule.RECORD_TYPE_ID}이 존재하지 않습니다"
                )
                
            # 선수 규칙인 경우 선수 ID 확인
            if rule_type.SAVING_RULE_TYPE_NAME in ["투수", "타자"] and not rule.PLAYER_ID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{rule_type.SAVING_RULE_TYPE_NAME} 규칙에는 선수 ID가 필요합니다"
                )
                
            if rule.PLAYER_ID:
                player = db.query(models.Player).filter(models.Player.PLAYER_ID == rule.PLAYER_ID).first()
                if not player:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"선수 ID {rule.PLAYER_ID}이 존재하지 않습니다"
                    )
                    
                # 선수 타입 확인
                if rule_type.SAVING_RULE_TYPE_NAME == "투수" and player.PLAYER_TYPE_ID != 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="투수 규칙에는 투수 선수만 선택 가능합니다"
                    )
                    
                if rule_type.SAVING_RULE_TYPE_NAME == "타자" and player.PLAYER_TYPE_ID != 2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="타자 규칙에는 타자 선수만 선택 가능합니다"
                    )
            
            # 적립 금액 확인
            if rule.USER_SAVING_RULED_AMOUNT <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="적립 금액은 0보다 커야 합니다"
                )
        
        # 4. 출금 계좌 유효성 확인
        if not request.SOURCE_ACCOUNT or len(request.SOURCE_ACCOUNT.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="출금 계좌번호를 입력해주세요"
            )
        
        # 5. 금융 API를 통해 계좌번호 발급
        from router.user.user_ssafy_api_utils import create_demand_deposit_account
        SAVING_CODE = os.getenv("SAVING_CODE")
        account_num = await create_demand_deposit_account(current_user.USER_KEY, SAVING_CODE)
        
        # 6. 계좌 생성
        db_account = models.Account(
            USER_ID=current_user.USER_ID,
            TEAM_ID=request.TEAM_ID,
            ACCOUNT_NUM=account_num,
            INTEREST_RATE=2.5,  # 기본 이자율
            SAVING_GOAL=request.SAVING_GOAL,
            DAILY_LIMIT=request.DAILY_LIMIT,
            MONTH_LIMIT=request.MONTH_LIMIT,
            SOURCE_ACCOUNT=request.SOURCE_ACCOUNT,
            TOTAL_AMOUNT=0,
            created_at=datetime.now()
        )
        db.add(db_account)
        db.flush()  # 임시 커밋하여 ID 생성
        
        # 7. 적금 규칙 추가
        saved_rules = []
        for rule in request.saving_rules:
            # 규칙 타입 확인
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
            ).first()
            
            # 규칙 타입에 따른 player_id와 player_type_id 설정
            player_id = None
            player_type_id = None
            
            if rule_type.SAVING_RULE_TYPE_NAME in ["투수", "타자"] and rule.PLAYER_ID:
                player_id = rule.PLAYER_ID
                player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
                if player:
                    player_type_id = player.PLAYER_TYPE_ID
            
            # 적금 규칙 목록에서 해당 규칙 찾기
            saving_rule = db.query(models.SavingRuleList).filter(
                models.SavingRuleList.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID,
                models.SavingRuleList.RECORD_TYPE_ID == rule.RECORD_TYPE_ID
            ).first()
            
            if not saving_rule:
                logger.warning(f"해당 조합의 적금 규칙을 찾을 수 없음: 타입 {rule.SAVING_RULE_TYPE_ID}, 기록 {rule.RECORD_TYPE_ID}")
                continue
            
            # 규칙 상세 찾기
            rule_detail_query = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_ID == saving_rule.SAVING_RULE_ID
            )
            
            if player_type_id:
                rule_detail_query = rule_detail_query.filter(models.SavingRuleDetail.PLAYER_TYPE_ID == player_type_id)
            else:
                rule_detail_query = rule_detail_query.filter(models.SavingRuleDetail.PLAYER_TYPE_ID.is_(None))
                
            rule_detail = rule_detail_query.first()
            
            if not rule_detail:
                logger.warning(f"해당 조합의 적금 규칙 상세를 찾을 수 없음: 규칙 ID {saving_rule.SAVING_RULE_ID}, 선수 타입 ID {player_type_id}")
                continue
            
            # 사용자 적금 규칙 생성
            db_user_rule = models.UserSavingRule(
                ACCOUNT_ID=db_account.ACCOUNT_ID,
                SAVING_RULE_TYPE_ID=rule.SAVING_RULE_TYPE_ID,
                SAVING_RULE_DETAIL_ID=rule_detail.SAVING_RULE_DETAIL_ID,
                PLAYER_TYPE_ID=player_type_id,
                USER_SAVING_RULED_AMOUNT=rule.USER_SAVING_RULED_AMOUNT,
                PLAYER_ID=player_id
            )
            db.add(db_user_rule)
            db.flush()
            
            # 기록 타입 정보 가져오기
            record_type = db.query(models.RecordType).filter(
                models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
            ).first()
            
            # 저장된 규칙 정보 구성
            rule_info = {
                "USER_SAVING_RULED_ID": db_user_rule.USER_SAVING_RULED_ID,
                "rule_type_name": rule_type.SAVING_RULE_TYPE_NAME,
                "record_name": record_type.RECORD_NAME if record_type else None,
                "amount": rule.USER_SAVING_RULED_AMOUNT
            }
            
            # 선수 정보 추가
            if player_id:
                player = db.query(models.Player).filter(models.Player.PLAYER_ID == player_id).first()
                if player:
                    rule_info["player_name"] = player.PLAYER_NAME
            
            saved_rules.append(rule_info)
        
        # 최종 커밋
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"적금 계좌 생성 완료: 계정 ID {db_account.ACCOUNT_ID}, 계좌번호 {account_num}")
        
        # 응답 데이터 구성
        response = {
            "ACCOUNT_ID": db_account.ACCOUNT_ID,
            "ACCOUNT_NUM": db_account.ACCOUNT_NUM,
            "TEAM_ID": db_account.TEAM_ID,
            "SAVING_GOAL": db_account.SAVING_GOAL,
            "DAILY_LIMIT": db_account.DAILY_LIMIT,
            "MONTH_LIMIT": db_account.MONTH_LIMIT,
            "SOURCE_ACCOUNT": db_account.SOURCE_ACCOUNT,
            "TOTAL_AMOUNT": db_account.TOTAL_AMOUNT,
            "INTEREST_RATE": db_account.INTEREST_RATE,
            "created_at": db_account.created_at.isoformat(),
            "saving_rules": saved_rules
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 가입 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 가입 중 오류 발생: {str(e)}"
        )

# # 계정 생성
# @router.post("/", response_model=account_schema.AccountResponse)
# async def create_account(
#     account: account_schema.AccountCreate, 
#     db: Session = Depends(get_db), 
#     current_user: models.User = Depends(get_current_user)
# ):
#     try:
#         logger.info(f"계정 생성 시도: 사용자 ID {current_user.USER_ID}")
        
#         # CRUD 함수 호출하여 계정 생성
#         new_account = await account_crud.create_account(
#             db=db,
#             user_id=current_user.USER_ID,
#             team_id=account.TEAM_ID,
#             saving_goal=account.SAVING_GOAL,
#             daily_limit=account.DAILY_LIMIT,
#             month_limit=account.MONTH_LIMIT,
#             source_account=account.SOURCE_ACCOUNT,
#             user_key=current_user.USER_KEY
#         )
        
#         logger.info(f"계정 생성 완료: 계정 ID {new_account.ACCOUNT_ID}")
#         return new_account
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"계정 생성 중 예상치 못한 오류: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"계정 생성 중 오류 발생: {str(e)}"
#         )

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

# # 계정 정보 업데이트
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

# 적금 계좌 초기 세팅 계좌 번호 제외
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
        
        # ORM 모델을 딕셔너리로 변환하면서 필요한 정보만 포함
        result = []
        for saving in savings:
            # 적금 규칙 유형 이름 조회
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == saving.SAVING_RULED_TYPE_ID
            ).first()
            rule_type_name = rule_type.SAVING_RULE_TYPE_NAME if rule_type else None
            
            # 기록 유형 이름 조회
            record_type_name = None
            # 적금 규칙 상세 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
            ).first()
            
            if rule_detail:
                # 해당 적금 규칙 조회
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if saving_rule:
                    # 기록 유형 이름 조회
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                    ).first()
                    record_type_name = record_type.RECORD_NAME if record_type else None
            
            # 선수 이름 (해당되는 경우)
            player_name = None
            if rule_type and rule_type.SAVING_RULE_TYPE_NAME not in ["기본 규칙", "상대팀"]:
                # 사용자 적금 규칙 조회
                user_rule = db.query(models.UserSavingRule).filter(
                    models.UserSavingRule.ACCOUNT_ID == account_id,
                    models.UserSavingRule.SAVING_RULE_DETAIL_ID == saving.SAVING_RULED_DETAIL_ID
                ).first()
                
                if user_rule and user_rule.PLAYER_ID:
                    player = db.query(models.Player).filter(
                        models.Player.PLAYER_ID == user_rule.PLAYER_ID
                    ).first()
                    
                    if player:
                        player_name = player.PLAYER_NAME
            
            # 결과 딕셔너리 구성 - 간소화된 버전
            saving_dict = {
                "DAILY_SAVING_ID": saving.DAILY_SAVING_ID,
                "DATE": saving.DATE,
                "COUNT": saving.COUNT,
                "DAILY_SAVING_AMOUNT": saving.DAILY_SAVING_AMOUNT,
                "RULE_TYPE_NAME": rule_type_name,
                "RECORD_TYPE_NAME": record_type_name,
                "PLAYER_NAME": player_name
            }
            
            result.append(saving_dict)
        
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
        
        # ORM 모델을 딕셔너리로 변환하면서 관련 정보 포함
        result = []
        for rule in rules:
            # 적금 규칙 타입 이름 조회
            rule_type = db.query(models.SavingRuleType).filter(
                models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
            ).first()
            rule_type_name = rule_type.SAVING_RULE_TYPE_NAME if rule_type else None
            
            # 적금 규칙 상세 조회
            rule_detail = db.query(models.SavingRuleDetail).filter(
                models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
            ).first()
            
            # 기록 유형 이름 조회
            record_name = None
            if rule_detail:
                # 적금 규칙 조회
                saving_rule = db.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if saving_rule:
                    # 기록 유형 이름 조회
                    record_type = db.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == saving_rule.RECORD_TYPE_ID
                    ).first()
                    record_name = record_type.RECORD_NAME if record_type else None
            
            # 선수 타입 이름 조회
            player_type = None
            if rule.PLAYER_TYPE_ID:
                player_type_obj = db.query(models.PlayerType).filter(
                    models.PlayerType.PLAYER_TYPE_ID == rule.PLAYER_TYPE_ID
                ).first()
                player_type = player_type_obj.PLAYER_TYPE_NAME if player_type_obj else None
            
            # 선수 이름 조회
            player_name = None
            if rule.PLAYER_ID:
                player = db.query(models.Player).filter(
                    models.Player.PLAYER_ID == rule.PLAYER_ID
                ).first()
                player_name = player.PLAYER_NAME if player else None
            
            # 결과 딕셔너리 구성
            rule_dict = {
                "USER_SAVING_RULED_ID": rule.USER_SAVING_RULED_ID,
                "ACCOUNT_ID": rule.ACCOUNT_ID,
                "SAVING_RULE_TYPE_ID": rule.SAVING_RULE_TYPE_ID,
                "SAVING_RULE_TYPE_NAME": rule_type_name,
                "SAVING_RULE_DETAIL_ID": rule.SAVING_RULE_DETAIL_ID,
                "PLAYER_TYPE_ID": rule.PLAYER_TYPE_ID,
                "PLAYER_TYPE_NAME": player_type,
                "USER_SAVING_RULED_AMOUNT": rule.USER_SAVING_RULED_AMOUNT,
                "PLAYER_ID": rule.PLAYER_ID,
                "PLAYER_NAME": player_name,
                "RECORD_NAME": record_name
            }
            
            result.append(rule_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"적금 규칙 설정 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적금 규칙 설정 조회 중 오류 발생: {str(e)}"
        )