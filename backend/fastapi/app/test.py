import sys
import os
import random
from datetime import datetime, date, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 현재 파일 위치를 기준으로 상위 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 환경 변수 설정을 위한 dotenv 불러오기
from dotenv import load_dotenv
load_dotenv()

# models 및 database 모듈 가져오기
import models
from database import engine

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

def create_dummy_saving_data(account_id=2, days=30):
    """
    일정 기간 동안의 daily_saving 및 daily_transfer 더미 데이터 생성
    
    Args:
        account_id (int): 사용할 계정 ID
        days (int): 생성할 데이터의 일수
    """
    try:
        # 계정 존재 여부 확인
        account = session.query(models.Account).filter(models.Account.ACCOUNT_ID == account_id).first()
        if not account:
            print(f"계정 ID {account_id}가 존재하지 않습니다.")
            return False
            
        print(f"계정 ID {account_id}에 대한 더미 데이터 생성 시작...")
        
        # 선수 기록 규칙 리스트 (기록 타입 ID - 1:승리, 4:안타, 5:홈런, 8:삼진 등)
        record_types = [1, 4, 5, 6, 8, 9]
        
        # 적금 규칙 타입 리스트 (1: 기본 규칙, 2: 투수, 3: 타자, 4: 상대팀)
        rule_types = [1, 2, 3, 4]
        
        # 적금 규칙 상세 정보 가져오기
        rule_details = session.query(models.SavingRuleDetail).all()
        rule_detail_ids = [detail.SAVING_RULE_DETAIL_ID for detail in rule_details]
        
        # 기존 더미 데이터 삭제 (덮어쓰기를 위해)
        existing_savings = session.query(models.DailySaving).filter(
            models.DailySaving.ACCOUNT_ID == account_id
        ).all()
        
        existing_transfers = session.query(models.DailyTransfer).filter(
            models.DailyTransfer.ACCOUNT_ID == account_id
        ).all()
        
        for saving in existing_savings:
            session.delete(saving)
        
        for transfer in existing_transfers:
            session.delete(transfer)
        
        session.commit()
        print(f"기존 더미 데이터 삭제 완료")
        
        # 현재 날짜에서 days일 전부터 어제까지의 날짜 생성
        end_date = datetime.now().date() - timedelta(days=1)  # 어제까지
        start_date = end_date - timedelta(days=days-1)  # days일 전
        
        # 일별 총 적립액을 저장할 딕셔너리
        daily_total_savings = {}
        
        total_savings_created = 0
        total_transfers_created = 0
        
        # 날짜별로 반복
        current_date = start_date
        while current_date <= end_date:
            daily_saving_count = random.randint(2, 5)  # 하루에 2~5개의 적립 내역 생성
            daily_total_amount = 0
            
            for _ in range(daily_saving_count):
                # 랜덤 규칙 타입 및 상세 ID 선택
                rule_type_id = random.choice(rule_types)
                rule_detail_id = random.choice(rule_detail_ids)
                
                # 적립 횟수 및 금액 랜덤 생성
                count = random.randint(1, 3)
                amount = random.choice([500, 1000, 2000, 3000, 5000]) * count
                
                # DailySaving 레코드 생성
                daily_saving = models.DailySaving(
                    ACCOUNT_ID=account_id,
                    DATE=current_date,
                    SAVING_RULED_DETAIL_ID=rule_detail_id,
                    SAVING_RULED_TYPE_ID=rule_type_id,
                    COUNT=count,
                    DAILY_SAVING_AMOUNT=amount,
                    created_at=datetime.now()
                )
                session.add(daily_saving)
                daily_total_amount += amount
                total_savings_created += 1
            
            # 해당 날짜의 총 적립액 저장
            daily_total_savings[current_date] = daily_total_amount
            
            # 다음 날짜로 이동
            current_date += timedelta(days=1)
        
        # 일별 이체 내역 생성
        for transfer_date, amount in daily_total_savings.items():
            # DailyTransfer 레코드 생성
            daily_transfer = models.DailyTransfer(
                ACCOUNT_ID=account_id,
                DATE=transfer_date,
                AMOUNT=amount,
                created_at=datetime.now(),
                TEXT = f"기본 메시지 {random.randint(1,10)}"
            )
            session.add(daily_transfer)
            total_transfers_created += 1
        
        # 변경사항 커밋
        session.commit()
        
        print(f"더미 데이터 생성 완료!")
        print(f"- 생성된 일별 적립 내역: {total_savings_created}건")
        print(f"- 생성된 일별 이체 내역: {total_transfers_created}건")
        
        # 현재 계정 잔액 업데이트 (DailySaving 금액 합계)
        total_amount = sum(daily_total_savings.values())
        account.TOTAL_AMOUNT = total_amount
        session.commit()
        print(f"계정 총 잔액을 {total_amount}원으로 업데이트했습니다.")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"더미 데이터 생성 중 오류 발생: {str(e)}")
        return False
    
if __name__ == "__main__":
    try:
        # 파라미터 파싱 (선택사항)
        import argparse
        
        parser = argparse.ArgumentParser(description='적금 더미 데이터 생성기')
        parser.add_argument('--account', type=int, default=1, help='계정 ID (기본값: 1)')
        parser.add_argument('--days', type=int, default=30, help='생성할 데이터의 일수 (기본값: 30)')
        
        args = parser.parse_args()
        
        # 더미 데이터 생성
        create_dummy_saving_data(account_id=args.account, days=args.days)
        
    except Exception as e:
        print(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()