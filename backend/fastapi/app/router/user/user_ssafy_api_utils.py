import requests
import json
import os
from fastapi import HTTPException, status
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수에서 API 정보 가져오기
SSAFY_API_BASE_URL = os.getenv("SSAFY_API_BASE_URL").rstrip("/")
MEMBER_ENDPOINT = f"{SSAFY_API_BASE_URL}/member"
MEMBER_SEARCH_ENDPOINT = f"{SSAFY_API_BASE_URL}/member/search"

# API 키와 기관 코드 설정
DEFAULT_API_KEY = os.getenv("SSAFY_API_KEY", "")

async def check_user_exists(email: str, api_key: str = DEFAULT_API_KEY):
    """
    사용자 이메일로 등록된 userKey가 있는지 확인
    """
    # API 요청 데이터 구성
    try:
        # 직접 요청 구조 생성 (API 문서 형식 따름)
        request_data = {
            "userId": email,
            "apiKey": api_key
        }
        
        logger.info(f"사용자 조회 요청 URL: {MEMBER_SEARCH_ENDPOINT}")
        logger.info(f"사용자 조회 요청 데이터: {json.dumps(request_data)}")
        
        response = requests.post(
            MEMBER_SEARCH_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 헤더: {dict(response.headers)}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인 - 기존 사용자 없음 케이스 처리
        if response.status_code == 400:
            response_text = response.text
            # E4003은 존재하지 않는 ID라는 의미로, 이는 오류가 아닌 정상적인 결과입니다
            if "E4003" in response_text:
                logger.info("사용자를 찾을 수 없음 (정상 응답)")
                return None
        
        # 정상 응답 처리
        if response.status_code in [200,201]:
            try:
                response_data = response.json()
                logger.info(f"응답 데이터: {json.dumps(response_data)}")
                
                # 응답 형식에 따라 적절히 파싱
                if isinstance(response_data, dict):
                    # userKey가 직접 있는 경우
                    if "userKey" in response_data:
                        return response_data
                    # userId, userName 등의 키가 있는 경우
                    if "userId" in response_data:
                        return response_data
                    
                return response_data  # 기타 경우
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"API 응답 파싱 오류: {str(e)}"
                )
        
        # 기타 오류 처리
        logger.error(f"API 오류 응답: {response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"금융 API 오류: {response.text}"
        )
        
    except requests.RequestException as e:
        logger.error(f"API 연결 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"금융 API 연결 오류: {str(e)}"
        )

async def register_user(email: str, username: str, api_key: str = DEFAULT_API_KEY):
    """
    금융 API에 새 사용자를 등록하고 userKey를 발급받음
    """
    try:
        # 직접 요청 구조 생성 (API 문서 형식 따름)
        request_data = {
            "userId": email,
            "apiKey": api_key
        }
        
        logger.info(f"사용자 등록 요청 URL: {MEMBER_ENDPOINT}")
        logger.info(f"사용자 등록 요청 데이터: {json.dumps(request_data)}")
        
        response = requests.post(
            MEMBER_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 헤더: {dict(response.headers)}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인
        response_text = response.text
        
        # 응답이 JSON 형식인지 확인
        try:
            response_data = json.loads(response_text)
            
            # userKey가 응답에 포함되어 있는지 확인
            if "userKey" in response_data:
                user_key = response_data["userKey"]
                logger.info(f"발급받은 사용자 키: {user_key}")
                return user_key
            
            # 응답 코드 확인
            if "responseCode" in response_data:
                code = response_data["responseCode"]
                message = response_data.get("responseMessage", "알 수 없는 오류")
                
                # 이미 등록된 사용자 처리
                if code == "E4002":
                    logger.info(f"이미 등록된 사용자: {message}")
                    return None
                
                # 기타 오류
                logger.error(f"API 오류 응답: {code} - {message}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"금융 API 오류: {code} - {message}"
                )
            
            # 예상치 못한 응답 형식
            logger.error(f"예상치 못한 응답 형식: {response_text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"예상치 못한 API 응답 형식: {response_text}"
            )
            
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 오류: {response_text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API 응답 파싱 오류: 유효하지 않은 JSON 형식"
            )
        
    except requests.RequestException as e:
        logger.error(f"API 연결 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"금융 API 연결 오류: {str(e)}"
        )

async def get_or_create_user_key(email: str, username: str, api_key: str = DEFAULT_API_KEY):
    """
    사용자 이메일로 userKey를 조회하거나, 없으면 새로 생성
    """
    try:
        logger.info(f"사용자 키 조회/생성 시작: 이메일={email}, 이름={username}")
        
        # 기존 사용자 확인
        user_info = await check_user_exists(email, api_key)
        
        if user_info and user_info.get("userKey"):
            logger.info(f"기존 사용자 키 반환: {user_info.get('userKey')}")
            return user_info.get("userKey")
        
        # 신규 사용자 등록 시도
        logger.info("신규 사용자 등록 시작")
        user_key = await register_user(email, username, api_key)
        
        # 신규 등록 실패하고 이미 존재하는 ID인 경우 (E4002) 조회 다시 시도
        if user_key is None:
            logger.info("사용자가 이미 존재하는 것으로 판단되어 다시 조회 시도")
            # 짧은 대기 시간 추가 (선택사항)
            import asyncio
            await asyncio.sleep(0.5)
            
            user_info = await check_user_exists(email, api_key)
            if user_info and "userKey" in user_info:
                logger.info(f"재조회 성공: {user_info.get('userKey')}")
                return user_info.get("userKey")
            else:
                logger.error("재조회 실패: userKey를 찾을 수 없음")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="userKey를 가져오지 못했습니다"
                )
        
        return user_key
            
    except Exception as e:
        logger.error(f"사용자 키 조회/생성 오류: {str(e)}")
        raise

# 입출금 통장 개설설
async def create_demand_deposit_account(user_key, account_type_unique_no="999-1-0146508f197d4c", api_key=None):
    """
    금융 API를 통해 입출금 계좌 개설
    """
    try:
        # API 이름 및 URL 설정
        api_name = "createDemandDepositAccount"
        api_url = f"{SSAFY_API_BASE_URL}/edu/demandDeposit/createDemandDepositAccount"
        
        # API 키 설정
        if api_key is None:
            api_key = DEFAULT_API_KEY
        
        # 현재 사용 중인 generate_api_header 함수를 그대로 사용
        from utils.api_header_utils import generate_api_header
        
        # 헤더 생성
        header = generate_api_header(
            api_name=api_name,
            user_key=user_key,
            api_key=api_key
        )
        
        # 전체 요청 데이터 구성
        request_data = {
            "Header": header,
            "accountTypeUniqueNo": account_type_unique_no
        }
        
        logger.info(f"입출금 계좌 개설 요청 URL: {api_url}")
        logger.info(f"입출금 계좌 개설 요청 데이터: {json.dumps(request_data)}")
        
        # API 요청
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인
        response_data = response.json()
        
        # 응답 코드 확인
        header = response_data.get("Header", {})
        response_code = header.get("responseCode")
        
        if response_code != "H0000":
            response_message = header.get("responseMessage", "알 수 없는 오류")
            logger.error(f"API 오류 응답: {response_code} - {response_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"금융 API 오류: {response_code} - {response_message}"
            )
        
        # 계좌 정보 확인
        rec = response_data.get("REC", {})
        account_no = rec.get("accountNo")
        
        if not account_no:
            logger.error("계좌번호를 찾을 수 없음")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="계좌번호를 가져오지 못했습니다"
            )
        
        logger.info(f"생성된 계좌번호: {account_no}")
        return account_no
            
    except Exception as e:
        logger.error(f"계좌 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계좌 생성 중 오류 발생: {str(e)}"
        )
    

async def transfer_money(user_key, withdrawal_account, deposit_account, amount, llm_text, api_key=None):
    """
    금융 API를 통해 계좌 간 송금 처리
    
    Args:
        user_key (str): 사용자 키
        withdrawal_account (str): 출금 계좌번호
        deposit_account (str): 입금 계좌번호
        amount (int): 송금 금액
        api_key (str, optional): API 키
    
    Returns:
        dict: 송금 결과 정보
    """
    try:
        # API 이름 및 URL 설정
        api_name = "updateDemandDepositAccountTransfer"
        api_url = f"{SSAFY_API_BASE_URL}/edu/demandDeposit/updateDemandDepositAccountTransfer"
        
        # API 키 설정
        if api_key is None:
            api_key = DEFAULT_API_KEY
        
        # 헤더 생성 
        from utils.api_header_utils import generate_api_header
        header = generate_api_header(
            api_name=api_name,
            user_key=user_key,
            api_key=api_key
        )
        
        # 전체 요청 데이터 구성
        request_data = {
            "Header": header,
            "depositAccountNo": deposit_account,  # 입금계좌번호
            "transactionBalance": str(amount),    # 거래금액 (문자열로 변환)
            "withdrawalAccountNo": withdrawal_account,  # 출금계좌번호
            "depositTransactionSummary": "야금야금 출금",  # 거래 요약정보 (입금계좌)
            "withdrawalTransactionSummary": llm_text  # 거래 요약정보 (출금계좌)
        }
        
        logger.info(f"송금 요청 URL: {api_url}")
        logger.info(f"송금 요청 데이터: {json.dumps(request_data)}")
        
        # API 요청
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인
        response_data = response.json()
        
        # 응답 코드 확인
        header = response_data.get("Header", {})
        response_code = header.get("responseCode")
        
        if response_code != "H0000":
            response_message = header.get("responseMessage", "알 수 없는 오류")
            logger.error(f"API 오류 응답: {response_code} - {response_message}")
            raise Exception(f"금융 API 오류: {response_code} - {response_message}")
        
        # 송금 결과 정보
        result = response_data.get("REC", {})
        
        logger.info(f"송금 완료: {withdrawal_account} -> {deposit_account}, 금액: {amount}")
        return result
            
    except Exception as e:
        logger.error(f"송금 중 오류: {str(e)}")
        raise    


async def get_account_balance(user_key, account_num, api_key=None):
    """
    금융 API를 통해 계좌 잔액 조회
    
    Args:
        user_key (str): 사용자 키
        account_num (str): 계좌번호
        api_key (str, optional): API 키
    
    Returns:
        int: 계좌 잔액
    """
    try:
        # API 이름 및 URL 설정
        api_name = "inquireDemandDepositAccountBalance"  # API 이름도 수정
        api_url = f"{SSAFY_API_BASE_URL}/edu/demandDeposit/inquireDemandDepositAccountBalance"  # URL도 수정
        
        # API 키 설정
        if api_key is None:
            api_key = DEFAULT_API_KEY
        
        # 헤더 생성
        from utils.api_header_utils import generate_api_header
        header = generate_api_header(
            api_name=api_name,
            user_key=user_key,
            api_key=api_key
        )
        
        # 전체 요청 데이터 구성
        request_data = {
            "Header": header,
            "accountNo": account_num
        }
        
        logger.info(f"계좌 잔액 조회 요청 URL: {api_url}")
        logger.info(f"계좌 잔액 조회 요청 데이터: {json.dumps(request_data)}")
        
        # API 요청
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인
        response_data = response.json()
        
        # 응답 코드 확인
        header = response_data.get("Header", {})
        response_code = header.get("responseCode")
        
        if response_code != "H0000":
            response_message = header.get("responseMessage", "알 수 없는 오류")
            logger.error(f"API 오류 응답: {response_code} - {response_message}")
            raise Exception(f"금융 API 오류: {response_code} - {response_message}")
        
        # 계좌 잔액 정보 - 여기를 수정
        rec = response_data.get("REC", {})
        balance = rec.get("accountBalance")  # 'balance'에서 'accountBalance'로 수정
        
        if balance is None:
            logger.error("계좌 잔액 정보를 찾을 수 없음")
            raise Exception("계좌 잔액 정보를 찾을 수 없음")
        
        # 문자열로 받은 잔액을 정수로 변환
        balance_int = int(balance)
        
        logger.info(f"계좌 잔액 조회 완료: {balance_int}")
        return balance_int
            
    except Exception as e:
        logger.error(f"계좌 잔액 조회 중 오류: {str(e)}")
        raise

async def init_money(user_key, account_num,api_key=None):
    """
    금융 API를 통해 초기 입출금 계좌 금액 생성
    
    Args:
        user_key (str): 사용자 키
        account_num (str): 계좌번호
        api_key (str, optional): API 키
    
    Returns:
        dict: 입금 결과
    """
    try:
        # API 이름 및 URL 설정
        api_name = "updateDemandDepositAccountDeposit"  # API 이름도 수정
        api_url = f"{SSAFY_API_BASE_URL}/edu/demandDeposit/updateDemandDepositAccountDeposit"  # URL도 수정
        
        # API 키 설정
        if api_key is None:
            api_key = DEFAULT_API_KEY
        
        # 헤더 생성
        from utils.api_header_utils import generate_api_header
        header = generate_api_header(
            api_name=api_name,
            user_key=user_key,
            api_key=api_key
        )
        
        # 전체 요청 데이터 구성
        request_data = {
            "Header": header,
            "accountNo": account_num,
            "transactionBalance": "30000000",
            "transactionSummary": "초기 금액액"
        }
        
        logger.info(f"계좌 입금 요청 URL: {api_url}")
        logger.info(f"계좌 입금 요청 데이터: {json.dumps(request_data)}")
        
        # API 요청
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"API 응답 상태 코드: {response.status_code}")
        logger.info(f"API 응답 본문: {response.text}")
        
        # 응답 확인
        response_data = response.json()
        
        # 응답 코드 확인
        header = response_data.get("Header", {})
        response_code = header.get("responseCode")
        
        if response_code != "H0000":
            response_message = header.get("responseMessage", "알 수 없는 오류")
            logger.error(f"API 오류 응답: {response_code} - {response_message}")
            raise Exception(f"금융 API 오류: {response_code} - {response_message}")
        
        # 계좌 잔액 정보 - 여기를 수정
        rec = response_data.get("REC", {})
        
        logger.info(f"계좌 입금 요청 완료: {rec}")
        return rec
            
    except Exception as e:
        logger.error(f"계좌 입금 요청청 중 오류: {str(e)}")
        raise