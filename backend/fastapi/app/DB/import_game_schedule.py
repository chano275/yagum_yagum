import sys
import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

# 현재 파일 위치를 기준으로 상위 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# models 및 database 모듈 가져오기
import models
from database import engine
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

def import_game_schedule():
    try:
        # CSV 파일 경로 설정 - 여러 가능한 경로 시도
        possible_paths = [
            os.path.join(project_root, 'fastapi', 'app', 'baseball_data', 'game_schedule', '2025_season_games.csv'),
            os.path.join(project_root, 'app', 'baseball_data', 'game_schedule', '2025_season_games.csv'),
            os.path.join(project_root, 'baseball_data', 'game_schedule', '2025_season_games.csv'),
            os.path.join(project_root, 'backend', 'fastapi', 'app', 'baseball_data', 'game_schedule', '2025_season_games.csv')
        ]

        csv_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_file_path = path
                break

        if csv_file_path is None:
            print("오류: CSV 파일을 찾을 수 없습니다. 다음 경로에서 파일을 확인하세요:")
            for i, path in enumerate(possible_paths, 1):
                print(f"{i}. {path}")
            return

        print(f"CSV 파일을 찾았습니다: {csv_file_path}")

        # CSV 파일 읽기 (칼럼 이름 없음)
        df = pd.read_csv(csv_file_path, header=None, names=['날짜', '원정', '홈'])
        print(f"CSV 파일을 읽었습니다. 총 {len(df)} 개의 경기 일정이 있습니다.")

        # 팀 이름과 ID 매핑 (team 테이블 기준)
        team_mapping = {}
        teams = session.query(models.Team).all()
        for team in teams:
            # 팀 이름에서 접미사 제거 (예: "KIA 타이거즈" -> "KIA")
            team_short_name = team.TEAM_NAME.split(' ')[0]
            team_mapping[team_short_name] = team.TEAM_ID
            
        # CSV에 있는 팀 약칭에 대한 매핑 추가
        team_alias = {
            "롯데": "롯데 자이언츠",
            "두산": "두산 베어스",
            "NC": "NC 다이노스",
            "KIA": "KIA 타이거즈",
            "SSG": "SSG 랜더스",
            "한화": "한화 이글스",
            "삼성": "삼성 라이온즈",
            "키움": "키움 히어로즈",
            "LG": "LG 트윈스",
            "KT": "KT 위즈"
        }
        
        # 약칭으로 직접 매핑 생성
        direct_team_mapping = {}
        for alias, full_name in team_alias.items():
            for team in teams:
                if team.TEAM_NAME == full_name:
                    direct_team_mapping[alias] = team.TEAM_ID
                    break

        print("팀 매핑 정보:")
        for team_name, team_id in team_mapping.items():
            print(f"{team_name}: {team_id}")

        # CSV 칼럼 확인
        print(f"CSV 칼럼: {df.columns.tolist()}")

        # 필요한 칼럼 확인
        required_columns = ['날짜', '원정','홈']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"CSV 파일에 필요한 칼럼이 없습니다: {missing_columns}")
            # 칼럼 이름이 다를 수 있으므로 비슷한 칼럼이 있는지 확인
            for col in df.columns:
                print(f"- {col}")
            return

        # 이미 등록된 경기 확인 (중복 방지)
        existing_games = {}
        for game in session.query(models.GameSchedule).all():
            date_str = game.DATE.strftime('%Y-%m-%d')
            key = f"{date_str}_{game.HOME_TEAM_ID}_{game.AWAY_TEAM_ID}"
            existing_games[key] = True

        # CSV 데이터 처리 및 DB에 삽입
        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                # 날짜 파싱 ("YYMMDD" 형식)
                date_str = str(row['날짜']).strip()
                try:
                    # "YYMMDD" 형식 (예: 250322)
                    if len(date_str) == 6:
                        # 앞의 두 자리가 25인 경우 2025년으로 처리
                        year = 2000 + int(date_str[:2])
                        month = int(date_str[2:4])
                        day = int(date_str[4:6])
                        game_date = datetime(year, month, day).date()
                    else:
                        print(f"잘못된 날짜 형식: {date_str}")
                        error_count += 1
                        continue
                except ValueError as e:
                    print(f"날짜 변환 오류: {date_str} - {str(e)}")
                    error_count += 1
                    continue

                # 팀 이름에서 팀 ID 매핑
                away_team_name = str(row['원정']).strip()
                home_team_name = str(row['홈']).strip()
                
                # 직접 매핑 시도
                home_team_id = direct_team_mapping.get(home_team_name)
                away_team_id = direct_team_mapping.get(away_team_name)
                
                # 직접 매핑이 실패하면 부분 일치로 찾기
                if home_team_id is None:
                    for team_name, team_id in team_mapping.items():
                        if team_name in home_team_name:
                            home_team_id = team_id
                            break
                
                if away_team_id is None:
                    for team_name, team_id in team_mapping.items():
                        if team_name in away_team_name:
                            away_team_id = team_id
                            break

                if home_team_id is None:
                    print(f"홈팀을 찾을 수 없습니다: {home_team_name}")
                    error_count += 1
                    continue

                if away_team_id is None:
                    print(f"원정팀을 찾을 수 없습니다: {away_team_name}")
                    error_count += 1
                    continue

                # 중복 확인
                key = f"{game_date}_{home_team_id}_{away_team_id}"
                if key in existing_games:
                    print(f"중복 경기: {game_date} {home_team_name} vs {away_team_name}")
                    skipped_count += 1
                    continue

                # 게임 일정 생성
                game_schedule = models.GameSchedule(
                    DATE=game_date,
                    HOME_TEAM_ID=home_team_id,
                    AWAY_TEAM_ID=away_team_id
                )
                
                session.add(game_schedule)
                existing_games[key] = True
                inserted_count += 1
                
                # 100개마다 커밋
                if inserted_count % 100 == 0:
                    session.commit()
                    print(f"{inserted_count}개 경기 일정 추가됨...")

            except Exception as e:
                print(f"경기 일정 처리 중 오류 발생: {str(e)}")
                error_count += 1

        # 최종 커밋
        session.commit()
        
        print(f"\n경기 일정 가져오기 완료:")
        print(f"- 추가된 경기: {inserted_count}개")
        print(f"- 중복 건너뛴 경기: {skipped_count}개")
        print(f"- 오류 발생: {error_count}개")

    except Exception as e:
        session.rollback()
        print(f"처리 중 오류 발생: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    import_game_schedule()