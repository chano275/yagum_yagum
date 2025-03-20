import datetime
import secrets
import hashlib
import json


def generate_api_header(api_name, user_key=None, api_key=None, institution_code="00100", fintech_app_no="001"):
    """
    API 요청에 필요한 공통 헤더를 자동으로 생성하는 함수
    
    Args:
        api_name (str): API 이름
        user_key (str, optional): 사용자 KEY. 지정하지 않으면 무작위로 생성합니다.
        api_key (str, optional): API KEY. 지정하지 않으면 무작위로 생성합니다.
        institution_code (str, optional): 기관코드. 기본값은 "00100"
        fintech_app_no (str, optional): 핀테크 앱 인증번호. 기본값은 "001"
    
    Returns:
        dict: API 요청에 필요한 헤더 정보
    """
    # 현재 날짜와 시간
    now = datetime.datetime.now()
    transmission_date = now.strftime("%Y%m%d")
    transmission_time = now.strftime("%H%M%S")
    
    # Institution Transaction Unique No 생성 (YYYYMMDD + 임의의 12자리 숫자)
    unique_no_suffix = ''.join([str(secrets.randbelow(10)) for _ in range(12)])
    institution_transaction_unique_no = f"{transmission_date}{unique_no_suffix}"
    
    # API 서비스 코드 (API 이름과 동일하게 설정)
    api_service_code = api_name
    
    # # USER KEY와 API KEY 생성 (지정되지 않은 경우)
    # if user_key is None:
    #     user_key = hashlib.sha256(f"user_{secrets.token_hex(16)}".encode()).hexdigest()[:40]
    
    # if api_key is None:
    #     api_key = hashlib.sha256(f"api_{secrets.token_hex(16)}".encode()).hexdigest()[:40]
    
    # 헤더 딕셔너리 생성
    header = {
        "apiName": api_name,
        "transmissionDate": transmission_date,
        "transmissionTime": transmission_time,
        "institutionCode": institution_code,
        "fintechAppNo": fintech_app_no,
        "apiServiceCode": api_service_code,
        "institutionTransactionUniqueNo": institution_transaction_unique_no,
        "apiKey": api_key,
        # "userKey": user_key
    }
    
    if user_key is not None:
        header["userKey"] = user_key


    return header


def generate_full_request(api_name, body=None, user_key=None, api_key=None, institution_code="00100", fintech_app_no="001"):
    """
    API 요청 전체(헤더 + 바디)를 생성하는 함수
    
    Args:
        api_name (str): API 이름
        body (dict, optional): 요청 바디. 없으면 빈 딕셔너리로 설정됩니다.
        user_key (str, optional): 사용자 KEY
        api_key (str, optional): API KEY
        institution_code (str, optional): 기관코드
        fintech_app_no (str, optional): 핀테크 앱 인증번호
    
    Returns:
        dict: API 요청 전체 (헤더 + 바디)
    """
    header = generate_api_header(
        api_name=api_name,
        user_key=user_key,
        api_key=api_key,
        institution_code=institution_code,
        fintech_app_no=fintech_app_no
    )
    
    request = {
        "Header": header
    }
    
    # 바디가 있는 경우 추가
    if body:
        request["Body"] = body
    
    return request


def get_request_json(api_name, body=None, user_key=None, api_key=None, institution_code="00100", fintech_app_no="001"):
    """
    API 요청 전체를 JSON 문자열로 반환하는 함수
    
    Args:
        api_name (str): API 이름
        body (dict, optional): 요청 바디
        user_key (str, optional): 사용자 KEY
        api_key (str, optional): API KEY
        institution_code (str, optional): 기관코드
        fintech_app_no (str, optional): 핀테크 앱 인증번호
    
    Returns:
        str: JSON 형식의 API 요청 문자열
    """
    request = generate_full_request(
        api_name=api_name,
        body=body,
        user_key=user_key,
        api_key=api_key,
        institution_code=institution_code,
        fintech_app_no=fintech_app_no
    )
    
    return json.dumps(request, ensure_ascii=False, indent=2)
