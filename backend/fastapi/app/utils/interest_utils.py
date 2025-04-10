# utils/interest_utils.py
import logging
from sqlalchemy.orm import Session
from datetime import date

import models

logger = logging.getLogger(__name__)

async def recalculate_interest_history(db: Session, account_id: int):
    """
    계정의 이자를 현재 금리(기본 금리 + 우대 금리)로 소급 적용합니다.
    전날의 잔액을 기준으로 이자를 계산합니다.
    
    Args:
        db (Session): 데이터베이스 세션
        account_id (int): 계정 ID
    
    Returns:
        dict: 재계산 결과 요약 정보
    """
    try:
        logger.info(f"계정 ID {account_id}의 이자 소급 적용 시작 (전날 잔액 기준)")
        
        # 계정 정보 조회
        account = db.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            logger.warning(f"계정 ID {account_id}를 찾을 수 없습니다.")
            return {"status": "error", "message": "계정을 찾을 수 없습니다."}
        
        # 현재 총 이자율 계산 (기본 금리 + 우대 금리)
        from router.mission import mission_crud
        interest_details = mission_crud.calculate_account_interest_details(db, account_id)
        current_total_rate = interest_details['total_interest_rate']
        
        # 계정의 모든 일일 잔액 기록 조회 (날짜순)
        daily_balances = db.query(models.DailyBalances).filter(
            models.DailyBalances.ACCOUNT_ID == account_id
        ).order_by(models.DailyBalances.DATE).all()
        
        # 재계산 결과 통계
        total_recalculated = 0
        adjusted_days = 0
        
        # 각 일자별 이자 재계산
        for i in range(1, len(daily_balances)):
            current_balance = daily_balances[i]
            previous_balance = daily_balances[i-1]
            
            # 현재 날짜와 전날 날짜가 연속되는지 확인
            if (current_balance.DATE - previous_balance.DATE).days != 1:
                logger.warning(f"계정 ID {account_id}: {previous_balance.DATE}와 {current_balance.DATE} 사이에 날짜가 누락되었습니다.")
                # 이자 계산은 계속 진행
            
            # 전날 잔액을 기준으로 현재 금리로 일일 이자 계산
            daily_interest_rate = current_total_rate / 100 / 365
            new_daily_interest = round(previous_balance.CLOSING_BALANCE * daily_interest_rate)
            
            # 기존 이자와 비교하여 다른 경우에만 업데이트
            if current_balance.DAILY_INTEREST != new_daily_interest:
                # 조정금액 계산
                adjustment = new_daily_interest - current_balance.DAILY_INTEREST
                total_recalculated += adjustment
                adjusted_days += 1
                
                # 이자 업데이트
                current_balance.DAILY_INTEREST = new_daily_interest
                
                logger.info(f"계정 ID {account_id}, 날짜 {current_balance.DATE}: "
                          f"이자를 {current_balance.DAILY_INTEREST}원에서 {new_daily_interest}원으로 조정 "
                          f"(전날({previous_balance.DATE}) 잔액 {previous_balance.CLOSING_BALANCE}원 기준)")
        
        # 변경사항 커밋
        db.commit()
        
        # 결과 요약
        result = {
            "status": "success",
            "account_id": account_id,
            "total_recalculated": total_recalculated,
            "adjusted_days": adjusted_days,
            "current_interest_rate": current_total_rate
        }
        
        logger.info(f"계정 ID {account_id}의 이자 소급 적용 완료: {adjusted_days}일, 총 {total_recalculated}원 조정 (전날 잔액 기준)")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"이자 소급 적용 중 오류 발생: {str(e)}")
        return {"status": "error", "message": f"이자 소급 적용 중 오류 발생: {str(e)}"}