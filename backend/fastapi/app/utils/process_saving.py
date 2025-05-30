# process_savings.py
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import date, datetime, timedelta

# 현재 스크립트 위치 기준으로 절대 경로 구성
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 데이터베이스 연결
from dotenv import load_dotenv
load_dotenv()

# 모듈 import를 위한 경로 설정
import sys
sys.path.append(project_root)
import models
from database import engine
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_savings_for_date(game_date=None, session=None):
    """
    특정 날짜의 게임 기록을 기반으로 사용자 적금 규칙에 따라 적립금을 처리합니다.
    하루에 계정별로 한 번만 DailyTransfer에 총합을 저장합니다.
    중복 레코드 추가를 방지합니다.
    
    Args:
        game_date (date, optional): 처리할 게임 날짜. 기본값은 오늘.
        session (Session, optional): SQLAlchemy 세션. None이면 새 세션을 생성합니다.
    
    Returns:
        dict: 처리 결과 요약 정보
    """
    
    # 날짜 설정 (기본값: 어제)
    if game_date is None:
        game_date = datetime.now().date() - timedelta(days=1)
    
    # 월의 시작일과 끝일 계산 (월간 한도 확인용)
    month_start = game_date.replace(day=1)
    if game_date.month == 12:
        next_month = game_date.replace(year=game_date.year + 1, month=1, day=1)
    else:
        next_month = game_date.replace(month=game_date.month + 1, day=1)
    month_end = next_month - timedelta(days=1)
    
    # 세션 관리
    close_session = False
    if session is None:
        Session = sessionmaker(bind=engine)
        session = Session()
        close_session = True
    
    try:
        logger.info(f"[{game_date}] 적금 규칙에 따른 적립금 처리 시작...")
        
        # 처리 결과 요약용 변수
        total_saved = 0
        processed_accounts = 0
        savings_count = 0
        skipped_count = 0  # 중복으로 건너뛴 건수
        
        # 1. 팀별 기록 통계 조회
        team_stats = {}
        game_logs = session.query(models.GameLog).filter(
            models.GameLog.DATE == game_date
        ).all()
        
        for log in game_logs:
            if log.TEAM_ID not in team_stats:
                team_stats[log.TEAM_ID] = {}
            
            team_stats[log.TEAM_ID][log.RECORD_TYPE_ID] = log.COUNT
        
        # 2. 선수별 기록 통계 조회
        player_stats = {}
        player_records = session.query(models.PlayerRecord).filter(
            models.PlayerRecord.DATE == game_date
        ).all()
        
        for record in player_records:
            if record.PLAYER_ID not in player_stats:
                player_stats[record.PLAYER_ID] = {
                    'team_id': record.TEAM_ID,
                    'records': {}
                }
            
            player_stats[record.PLAYER_ID]['records'][record.RECORD_TYPE_ID] = record.COUNT
        
        # 3. 모든 계정 조회
        accounts = session.query(models.Account).all()
        
        # 계정별 일일 총액을 저장할 딕셔너리
        account_daily_totals = {}

        # 해당 날짜에 이미 처리된 규칙 목록 조회 (중복 방지용)
        existing_savings = session.query(
            models.DailySaving.ACCOUNT_ID, 
            models.DailySaving.SAVING_RULED_DETAIL_ID,
            models.DailySaving.SAVING_RULED_TYPE_ID
        ).filter(
            models.DailySaving.DATE == game_date
        ).all()
        
        # 중복 체크를 위한 집합 생성 (account_id, rule_detail_id, rule_type_id)
        processed_rules = set()
        for saving in existing_savings:
            processed_rules.add((saving.ACCOUNT_ID, saving.SAVING_RULED_DETAIL_ID, saving.SAVING_RULED_TYPE_ID))
        
        logger.info(f"[{game_date}] 이미 처리된 규칙 수: {len(processed_rules)}")

        for account in accounts:
            account_total_saved = 0  # 이 계정에 적립된 총액
            account_savings_count = 0  # 이 계정의 적립 건수
            
            # 일일 한도 확인 (이미 이체된 금액)
            already_transferred_today = session.query(func.sum(models.DailyTransfer.AMOUNT)).filter(
                models.DailyTransfer.ACCOUNT_ID == account.ACCOUNT_ID,
                models.DailyTransfer.DATE == game_date
            ).scalar() or 0
            
            # 월간 한도 확인 (이미 이체된 금액)
            already_transferred_this_month = session.query(func.sum(models.DailyTransfer.AMOUNT)).filter(
                models.DailyTransfer.ACCOUNT_ID == account.ACCOUNT_ID,
                models.DailyTransfer.DATE >= month_start,
                models.DailyTransfer.DATE <= game_date
            ).scalar() or 0
            
            # 현재 처리 과정에서 누적되는 금액 (여러 규칙 처리 시 합산)
            daily_accumulated = already_transferred_today
            monthly_accumulated = already_transferred_this_month
            
            # 3.1. 팀 관련 규칙 처리 (기본 규칙, 상대팀)
            team_rules = session.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account.ACCOUNT_ID,
                models.UserSavingRule.PLAYER_ID.is_(None)  # 선수 ID가 NULL인 규칙
            ).all()
            
            for rule in team_rules:
                # 중복 체크: 이미 처리된 규칙이면 건너뜀
                rule_key = (account.ACCOUNT_ID, rule.SAVING_RULE_DETAIL_ID, rule.SAVING_RULE_TYPE_ID)
                if rule_key in processed_rules:
                    logger.info(f"계정 ID {account.ACCOUNT_ID}: 규칙 {rule.SAVING_RULE_DETAIL_ID}는 이미 처리되었으므로 건너뜁니다.")
                    skipped_count += 1
                    continue
                
                # 규칙 상세 정보 조회
                rule_detail = session.query(models.SavingRuleDetail).filter(
                    models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
                ).first()
                
                if not rule_detail:
                    continue
                
                # 적금 규칙 조회
                saving_rule = session.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if not saving_rule:
                    continue
                
                record_type_id = saving_rule.RECORD_TYPE_ID
                
                # 적금 규칙 타입 확인
                rule_type = session.query(models.SavingRuleType).filter(
                    models.SavingRuleType.SAVING_RULE_TYPE_ID == rule.SAVING_RULE_TYPE_ID
                ).first()
                
                if not rule_type:
                    continue
                
                # 기본 규칙: 응원 팀의 기록에 따라 적립
                if rule_type.SAVING_RULE_TYPE_NAME == "기본 규칙":
                    # 응원 팀의 통계 조회
                    team_id = account.TEAM_ID
                    
                    # 스윕 규칙 처리 (기록 유형 ID가 7인 경우, 스윕)
                    if record_type_id == 7:  # 스윕 기록 처리
                        # 최근 3일간의 날짜 계산
                        three_days_ago = game_date - timedelta(days=2)  # 오늘 포함 3일
                        
                        # 최근 3일간의 게임 일정 조회
                        recent_games = session.query(models.GameSchedule).filter(
                            models.GameSchedule.DATE >= three_days_ago,
                            models.GameSchedule.DATE <= game_date,
                            ((models.GameSchedule.HOME_TEAM_ID == team_id) | 
                             (models.GameSchedule.AWAY_TEAM_ID == team_id))
                        ).order_by(models.GameSchedule.DATE).all()
                        
                        # 최근 3일간의 승리 기록 조회 (기록 유형 ID가 1인 경우, 승리)
                        recent_wins = session.query(models.GameLog).filter(
                            models.GameLog.DATE >= three_days_ago,
                            models.GameLog.DATE <= game_date,
                            models.GameLog.TEAM_ID == team_id,
                            models.GameLog.RECORD_TYPE_ID == 1  # 승리 기록 유형
                        ).order_by(models.GameLog.DATE).all()
                        
                        # 스윕 확인
                        sweep_count = 0
                        
                        # 최근 3경기가 있는지 확인
                        if len(recent_games) >= 3:
                            # 경기 상대팀 확인
                            opponents = []
                            for game in recent_games:
                                if game.HOME_TEAM_ID == team_id:
                                    opponents.append(game.AWAY_TEAM_ID)
                                else:
                                    opponents.append(game.HOME_TEAM_ID)
                            
                            # 최근 3경기의 상대팀이 모두 같은지 확인
                            if len(set(opponents[:3])) == 1:  # 첫 3개의 상대팀이 동일한지 확인
                                # 최근 3일간 이 팀의 승리 횟수 확인
                                if len(recent_wins) >= 3:
                                    # 동일한 상대에 대한 3연승 확인
                                    # 여기서는 단순화를 위해 3일 연속 승리가 있으면 스윕으로 간주
                                    sweep_count = 1
                                    print(f"스윕 감지: 팀 {team_id}가 최근 3일간 동일한 상대팀 {opponents[0]}에 대해 연승")
                        
                        # 스윕이 확인되면 적립금 처리
                        if sweep_count > 0:
                            # 적립 금액 계산
                            saving_amount = rule.USER_SAVING_RULED_AMOUNT * sweep_count
                            
                            # 일일 한도 확인 및 조정
                            if daily_accumulated + saving_amount > account.DAILY_LIMIT:
                                original_amount = saving_amount
                                saving_amount = max(0, account.DAILY_LIMIT - daily_accumulated)
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 일일 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                            
                            # 월간 한도 확인 및 조정
                            if monthly_accumulated + saving_amount > account.MONTH_LIMIT:
                                original_amount = saving_amount
                                saving_amount = max(0, account.MONTH_LIMIT - monthly_accumulated)
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 월간 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                            
                            # 이체할 금액이 0 이하라면 건너뜀
                            if saving_amount <= 0:
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 이체 금액이 0원 이하여서 이체를 건너뜁니다.")
                                continue
                            
                            # 누적 변수 업데이트
                            daily_accumulated += saving_amount
                            monthly_accumulated += saving_amount
                            
                            # DailySaving에 기록
                            daily_saving = models.DailySaving(
                                ACCOUNT_ID=account.ACCOUNT_ID,
                                DATE=game_date,
                                SAVING_RULED_DETAIL_ID=rule.SAVING_RULE_DETAIL_ID,
                                SAVING_RULED_TYPE_ID=rule.SAVING_RULE_TYPE_ID,
                                COUNT=sweep_count,
                                DAILY_SAVING_AMOUNT=saving_amount,
                                created_at=datetime.now()
                            )
                            session.add(daily_saving)
                            
                            # 처리된 규칙 집합에 추가 (중복 방지)
                            processed_rules.add(rule_key)
                            
                            # 계정 통계 업데이트
                            account_total_saved += saving_amount
                            account_savings_count += 1
                            
                            # 계정별 일일 총액 업데이트
                            if account.ACCOUNT_ID not in account_daily_totals:
                                account_daily_totals[account.ACCOUNT_ID] = 0
                            account_daily_totals[account.ACCOUNT_ID] += saving_amount
                            
                            logger.info(f"계정 ID {account.ACCOUNT_ID}: 기본 규칙 - 스윕 {sweep_count}회 발생, {saving_amount}원 적립")
                    
                    # 일반 기록 처리 (스윕 외 다른 기록)
                    elif (team_id in team_stats and 
                          record_type_id in team_stats[team_id] and 
                          team_stats[team_id][record_type_id] > 0):
                        
                        count = team_stats[team_id][record_type_id]
                        
                        # 적립 금액 계산
                        saving_amount = rule.USER_SAVING_RULED_AMOUNT * count
                        
                        # 일일 한도 확인 및 조정
                        if daily_accumulated + saving_amount > account.DAILY_LIMIT:
                            original_amount = saving_amount
                            saving_amount = max(0, account.DAILY_LIMIT - daily_accumulated)
                            logger.info(f"계정 ID {account.ACCOUNT_ID}: 일일 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                        
                        # 월간 한도 확인 및 조정
                        if monthly_accumulated + saving_amount > account.MONTH_LIMIT:
                            original_amount = saving_amount
                            saving_amount = max(0, account.MONTH_LIMIT - monthly_accumulated)
                            logger.info(f"계정 ID {account.ACCOUNT_ID}: 월간 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                        
                        # 이체할 금액이 0 이하라면 건너뜀
                        if saving_amount <= 0:
                            logger.info(f"계정 ID {account.ACCOUNT_ID}: 이체 금액이 0원 이하여서 이체를 건너뜁니다.")
                            continue
                        
                        # 누적 변수 업데이트
                        daily_accumulated += saving_amount
                        monthly_accumulated += saving_amount
                        
                        # DailySaving에 기록
                        daily_saving = models.DailySaving(
                            ACCOUNT_ID=account.ACCOUNT_ID,
                            DATE=game_date,
                            SAVING_RULED_DETAIL_ID=rule.SAVING_RULE_DETAIL_ID,
                            SAVING_RULED_TYPE_ID=rule.SAVING_RULE_TYPE_ID,
                            COUNT=count,
                            DAILY_SAVING_AMOUNT=saving_amount,
                            created_at=datetime.now()
                        )
                        session.add(daily_saving)
                        
                        # 처리된 규칙 집합에 추가 (중복 방지)
                        processed_rules.add(rule_key)
                        
                        # 계정 통계 업데이트
                        account_total_saved += saving_amount
                        account_savings_count += 1
                        
                        # 계정별 일일 총액 업데이트
                        if account.ACCOUNT_ID not in account_daily_totals:
                            account_daily_totals[account.ACCOUNT_ID] = 0
                        account_daily_totals[account.ACCOUNT_ID] += saving_amount
                        
                        # 기록 유형 이름 조회
                        record_type = session.query(models.RecordType).filter(
                            models.RecordType.RECORD_TYPE_ID == record_type_id
                        ).first()
                        record_name = record_type.RECORD_NAME if record_type else f"기록 {record_type_id}"
                        
                        logger.info(f"계정 ID {account.ACCOUNT_ID}: 기본 규칙 - {record_name} 기록 {count}회 발생, {saving_amount}원 적립")
                
                # 상대팀 규칙: 상대 팀의 기록에 따라 적립
                elif rule_type.SAVING_RULE_TYPE_NAME == "상대팀":
                    team_id = account.TEAM_ID
                    # 해당 날짜에 account의 팀이 참여한 경기 일정에서 실제 상대팀만 추출
                    game_schedules = session.query(models.GameSchedule).filter(
                        models.GameSchedule.DATE == game_date,
                        (models.GameSchedule.HOME_TEAM_ID == team_id) | (models.GameSchedule.AWAY_TEAM_ID == team_id)
                    ).all()
                    opposing_teams = []
                    for game in game_schedules:
                        if game.HOME_TEAM_ID == team_id:
                            opposing_team_id = game.AWAY_TEAM_ID
                        else:
                            opposing_team_id = game.HOME_TEAM_ID
                        if opposing_team_id not in opposing_teams:
                            opposing_teams.append(opposing_team_id)
                    
                    for opposing_team_id in opposing_teams:
                        if opposing_team_id in team_stats and record_type_id in team_stats[opposing_team_id] and team_stats[opposing_team_id][record_type_id] > 0:
                            
                            count = team_stats[opposing_team_id][record_type_id]
                            
                            # 적립 금액 계산
                            saving_amount = rule.USER_SAVING_RULED_AMOUNT * count
                            
                            # 일일 한도 확인 및 조정
                            if daily_accumulated + saving_amount > account.DAILY_LIMIT:
                                original_amount = saving_amount
                                saving_amount = max(0, account.DAILY_LIMIT - daily_accumulated)
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 일일 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                            
                            # 월간 한도 확인 및 조정
                            if monthly_accumulated + saving_amount > account.MONTH_LIMIT:
                                original_amount = saving_amount
                                saving_amount = max(0, account.MONTH_LIMIT - monthly_accumulated)
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 월간 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                            
                            # 이체할 금액이 0 이하라면 건너뜀
                            if saving_amount <= 0:
                                logger.info(f"계정 ID {account.ACCOUNT_ID}: 이체 금액이 0원 이하여서 이체를 건너뜁니다.")
                                continue
                            
                            # 누적 변수 업데이트
                            daily_accumulated += saving_amount
                            monthly_accumulated += saving_amount
                            
                            # DailySaving에 기록
                            daily_saving = models.DailySaving(
                                ACCOUNT_ID=account.ACCOUNT_ID,
                                DATE=game_date,
                                SAVING_RULED_DETAIL_ID=rule.SAVING_RULE_DETAIL_ID,
                                SAVING_RULED_TYPE_ID=rule.SAVING_RULE_TYPE_ID,
                                COUNT=count,
                                DAILY_SAVING_AMOUNT=saving_amount,
                                created_at=datetime.now()
                            )
                            session.add(daily_saving)
                            
                            # 처리된 규칙 집합에 추가 (중복 방지)
                            processed_rules.add(rule_key)
                            
                            # 계정 통계 업데이트
                            account_total_saved += saving_amount
                            account_savings_count += 1
                            
                            # 계정별 일일 총액 업데이트
                            if account.ACCOUNT_ID not in account_daily_totals:
                                account_daily_totals[account.ACCOUNT_ID] = 0
                            account_daily_totals[account.ACCOUNT_ID] += saving_amount
                            
                            # 팀 이름과 기록 유형 이름 조회
                            opposing_team = session.query(models.Team).filter(
                                models.Team.TEAM_ID == opposing_team_id
                            ).first()
                            opposing_team_name = opposing_team.TEAM_NAME if opposing_team else f"팀 {opposing_team_id}"
                            
                            record_type = session.query(models.RecordType).filter(
                                models.RecordType.RECORD_TYPE_ID == record_type_id
                            ).first()
                            record_name = record_type.RECORD_NAME if record_type else f"기록 {record_type_id}"
                            
                            print(f"계정 ID {account.ACCOUNT_ID}: 상대팀 규칙 - {opposing_team_name}의 {record_name} 기록 {count}회 발생, {saving_amount}원 적립")
            
            # 3.2. 선수 관련 규칙 처리 (투수, 타자)
            player_rules = session.query(models.UserSavingRule).filter(
                models.UserSavingRule.ACCOUNT_ID == account.ACCOUNT_ID,
                models.UserSavingRule.PLAYER_ID.isnot(None)  # 선수 ID가 있는 규칙
            ).all()
            
            for rule in player_rules:
                # 중복 체크: 이미 처리된 규칙이면 건너뜀
                rule_key = (account.ACCOUNT_ID, rule.SAVING_RULE_DETAIL_ID, rule.SAVING_RULE_TYPE_ID)
                if rule_key in processed_rules:
                    logger.info(f"계정 ID {account.ACCOUNT_ID}: 규칙 {rule.SAVING_RULE_DETAIL_ID}는 이미 처리되었으므로 건너뜁니다.")
                    skipped_count += 1
                    continue
                
                # 이 선수의 기록이 있는지 확인
                if rule.PLAYER_ID not in player_stats:
                    continue
                
                # 규칙 상세 정보 조회
                rule_detail = session.query(models.SavingRuleDetail).filter(
                    models.SavingRuleDetail.SAVING_RULE_DETAIL_ID == rule.SAVING_RULE_DETAIL_ID
                ).first()
                
                if not rule_detail:
                    continue
                
                # 적금 규칙 조회
                saving_rule = session.query(models.SavingRuleList).filter(
                    models.SavingRuleList.SAVING_RULE_ID == rule_detail.SAVING_RULE_ID
                ).first()
                
                if not saving_rule:
                    continue
                
                record_type_id = saving_rule.RECORD_TYPE_ID
                
                # 선수의 해당 기록 조회
                records = player_stats[rule.PLAYER_ID]['records']
                if record_type_id in records and records[record_type_id] > 0:
                    count = records[record_type_id]
                    
                    # 적립 금액 계산
                    saving_amount = rule.USER_SAVING_RULED_AMOUNT * count
                    
                    # 일일 한도 확인 및 조정
                    if daily_accumulated + saving_amount > account.DAILY_LIMIT:
                        original_amount = saving_amount
                        saving_amount = max(0, account.DAILY_LIMIT - daily_accumulated)
                        logger.info(f"계정 ID {account.ACCOUNT_ID}: 일일 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                    
                    # 월간 한도 확인 및 조정
                    if monthly_accumulated + saving_amount > account.MONTH_LIMIT:
                        original_amount = saving_amount
                        saving_amount = max(0, account.MONTH_LIMIT - monthly_accumulated)
                        logger.info(f"계정 ID {account.ACCOUNT_ID}: 월간 한도 초과로 이체 금액 조정 ({original_amount}원 → {saving_amount}원)")
                    
                    # 이체할 금액이 0 이하라면 건너뜀
                    if saving_amount <= 0:
                        logger.info(f"계정 ID {account.ACCOUNT_ID}: 이체 금액이 0원 이하여서 이체를 건너뜁니다.")
                        continue
                    
                    # 누적 변수 업데이트
                    daily_accumulated += saving_amount
                    monthly_accumulated += saving_amount
                    
                    # DailySaving에 기록
                    daily_saving = models.DailySaving(
                        ACCOUNT_ID=account.ACCOUNT_ID,
                        DATE=game_date,
                        SAVING_RULED_DETAIL_ID=rule.SAVING_RULE_DETAIL_ID,
                        SAVING_RULED_TYPE_ID=rule.SAVING_RULE_TYPE_ID,
                        COUNT=count,
                        DAILY_SAVING_AMOUNT=saving_amount,
                        created_at=datetime.now()
                    )
                    session.add(daily_saving)
                    
                    # 처리된 규칙 집합에 추가 (중복 방지)
                    processed_rules.add(rule_key)
                    
                    # 계정 통계 업데이트
                    account_total_saved += saving_amount
                    account_savings_count += 1
                    
                    # 계정별 일일 총액 업데이트
                    if account.ACCOUNT_ID not in account_daily_totals:
                        account_daily_totals[account.ACCOUNT_ID] = 0
                    account_daily_totals[account.ACCOUNT_ID] += saving_amount
                    
                    # 선수 이름 조회
                    player = session.query(models.Player).filter(models.Player.PLAYER_ID == rule.PLAYER_ID).first()
                    player_name = player.PLAYER_NAME if player else f"선수 {rule.PLAYER_ID}"
                    
                    # 기록 유형 이름 조회
                    record_type = session.query(models.RecordType).filter(
                        models.RecordType.RECORD_TYPE_ID == record_type_id
                    ).first()
                    record_name = record_type.RECORD_NAME if record_type else f"기록 {record_type_id}"
                    
                    print(f"계정 ID {account.ACCOUNT_ID}: 선수 규칙 - 선수 {player_name}, {record_name} 기록 {count}회 발생, {saving_amount}원 적립")
            
            # 3.3. 계정에 적립된 내역이 있으면 통계에 추가
            if account_total_saved > 0:
                total_saved += account_total_saved
                processed_accounts += 1
                savings_count += account_savings_count
                print(f"계정 {account.ACCOUNT_ID} 총 적립액: {account_total_saved}원 ({account_savings_count}건)")

        # 4. 계정별 일일 총액을 DailyTransfer에 한 번씩만 저장
        for account_id, total_amount in account_daily_totals.items():
            # DailyTransfer에 하루에 한 번만 총액 저장
            daily_transfer = models.DailyTransfer(
                ACCOUNT_ID=account_id,
                DATE=game_date,
                AMOUNT=total_amount,
                created_at=datetime.now(),
                TEXT="출금예정!!"
            )
            session.add(daily_transfer)
        
        # 결과 커밋
        session.commit()
        
        # 처리 결과 요약 반환
        result = {
            "game_date": game_date,
            "total_saved": total_saved,
            "processed_accounts": processed_accounts,
            "savings_count": savings_count,
            "teams_count": len(team_stats),
            "players_count": len(player_stats),
            "daily_transfers": len(account_daily_totals)  # 일일 이체 건수는 계정 수와 동일
        }
        
        print(f"[{game_date}] 적립 처리 완료: {processed_accounts}개 계정, 총 {total_saved}원 적립 ({savings_count}건), 이체 {len(account_daily_totals)}건")
        return result
    
    except Exception as e:
        session.rollback()
        logger.error(f"오류 발생: {str(e)}", exc_info=True)
        raise
    finally:
        if close_session:
            session.close()
            
def process_recent_days(days=7):
   """
   최근 n일간의 적금 적립을 처리합니다.
   """
   today = date.today()
   
   # 데이터베이스 세션 생성
   Session = sessionmaker(bind=engine)
   session = Session()
   
   results = []
   try:
       for i in range(days):
           process_date = today - timedelta(days=i)
           print(f"\n처리 날짜: {process_date}")
           result = process_savings_for_date(process_date, session)
           results.append(result)
   finally:
       session.close()
   
   return results

def clear_existing_savings(game_date=None, session=None):
   """
   특정 날짜의 기존 적금 적립 내역을 삭제합니다.
   이미 적립된 내역을 다시 계산해야 할 경우 유용합니다.
   
   주의: 이 함수는 계정 잔액도 롤백합니다.
   """
   # 날짜 설정 (기본값: 오늘)
   if game_date is None:
       game_date = date.today()
   
   # 세션 관리
   close_session = False
   if session is None:
       Session = sessionmaker(bind=engine)
       session = Session()
       close_session = True
   
   try:
       print(f"[{game_date}] 기존 적금 적립 내역 삭제 시작...")
       
       # 해당 날짜의 모든 적립 내역 조회
       savings = session.query(models.DailySaving).filter(
           models.DailySaving.DATE == game_date
       ).all()
       
       deleted_count = 0
       total_amount = 0
       
       # 각 적립 내역에 대해 계정 잔액 롤백 및 삭제
       for saving in savings:
           # 계정 잔액 업데이트 (차감)
           account = session.query(models.Account).filter(
               models.Account.ACCOUNT_ID == saving.ACCOUNT_ID
           ).first()
           
           if account:
               account.TOTAL_AMOUNT -= saving.DAILY_SAVING_AMOUNT
               total_amount += saving.DAILY_SAVING_AMOUNT
           
           # 적립 내역 삭제
           session.delete(saving)
           deleted_count += 1
       
       # DailyTransfer 테이블의 해당 날짜 레코드도 삭제
       daily_transfers = session.query(models.DailyTransfer).filter(
           models.DailyTransfer.DATE == game_date
       ).all()
       
       for transfer in daily_transfers:
           session.delete(transfer)
       
       # 변경 사항 커밋
       session.commit()
       
       print(f"[{game_date}] 적금 적립 내역 삭제 완료: {deleted_count}건, 총 {total_amount}원")
       return {"date": game_date, "deleted_count": deleted_count, "total_amount": total_amount}
   
   except Exception as e:
       session.rollback()
       print(f"오류 발생: {str(e)}")
       raise
   finally:
       if close_session:
           session.close()

if __name__ == "__main__":
   import argparse
   
   parser = argparse.ArgumentParser(description='적금 규칙에 따른 적립금 처리')
   parser.add_argument('--date', type=str, help='처리할 날짜 (YYYY-MM-DD 형식, 기본값: 오늘)')
   parser.add_argument('--days', type=int, default=1, help='처리할 최근 일수 (기본값: 1)')
   parser.add_argument('--clear', action='store_true', help='기존 적립 내역 삭제 후 재처리')
   
   args = parser.parse_args()
   
   if args.date:
       # 특정 날짜 처리
       try:
           process_date = date.fromisoformat(args.date)
           
           if args.clear:
               clear_existing_savings(process_date)
           
           process_savings_for_date(process_date)
       except ValueError:
           print("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요.")
   else:
       # 최근 n일 처리
       if args.clear:
           # 최근 n일 데이터 삭제
           today = date.today()
           for i in range(args.days):
               process_date = today - timedelta(days=i)
               clear_existing_savings(process_date)
       
       # 최근 n일 처리
       process_recent_days(args.days)