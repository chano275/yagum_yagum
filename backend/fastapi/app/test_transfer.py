import asyncio
import sys
from database import SessionLocal
from router.account import account_crud

async def test_account_transfer():
    # 커맨드 라인 인수 파싱
    if len(sys.argv) < 3:
        print("사용법: python test_account_transfer.py <계정ID> <금액>")
        return
    
    account_id = int(sys.argv[1])
    amount = int(sys.argv[2])
    
    # 데이터베이스 연결
    db = SessionLocal()
    
    try:
        # 송금 실행
        result = await account_crud.transfer_to_saving_account(db, account_id, amount)
        print("송금 성공!")
        print(f"계정 ID: {account_id}")
        print(f"송금 금액: {amount}원")
        print(f"새 계좌 잔액: {result['account'].TOTAL_AMOUNT}원")
    except Exception as e:
        print("송금 실패:", str(e))
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_account_transfer())