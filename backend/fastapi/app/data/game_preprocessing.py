import os
import pandas as pd
from datetime import datetime, timedelta

# 오늘 날짜 기준 하루 전 구하기
current_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
log_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
input_folder_path = f'crawled_data/{current_date}'
output_folder_path = f'processed_data'

# 출력 폴더 생성
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 입력 폴더에서 batting과 log_box 파일 목록 가져오기
batting_files = [f for f in os.listdir(input_folder_path) if '_batting.csv' in f]
log_box_files = [f for f in os.listdir(input_folder_path) if '_log_boxes.csv' in f]

# if not batting_files or not log_box_files:
#     raise FileNotFoundError(f"❌ 필요한 파일이 없습니다: {input_folder_path}")

# 결과를 저장할 리스트
result_data = []

# 경기별 처리
for batting_file, log_box_file in zip(batting_files, log_box_files):
    # 파일 경로 정의
    batting_file_path = os.path.join(input_folder_path, batting_file)
    log_box_file_path = os.path.join(input_folder_path, log_box_file)

    # 파일 이름에서 팀 정보 추출
    away_team, home_team = batting_file.replace('_batting.csv', '').split('-')

    # 데이터 로드
    batting = pd.read_csv(batting_file_path)
    log_box = pd.read_csv(log_box_file_path)

    # 1. **batting 데이터 정제**
    df_team_total = batting[batting['타순'] == '팀 합계'].copy()

    # BB+HBP 컬럼 추가 (결측값은 0으로 처리 후 합산)
    df_team_total['BB'] = pd.to_numeric(df_team_total['BB'], errors='coerce').fillna(0)
    df_team_total['HBP'] = pd.to_numeric(df_team_total['HBP'], errors='coerce').fillna(0)
    df_team_total['사구'] = df_team_total['BB'] + df_team_total['HBP']

    # 기록으로 사용할 컬럼 지정
    include_cols = ['H', 'R', 'HR', 'SO', 'GDP']
    stat_cols = [col for col in batting.columns if col in include_cols]
    stat_cols.append('사구')

    # 각 팀 합계 행을 순회하며 기록과 값을 추출하여 저장
    for idx, row in df_team_total.iterrows():
        team_name = row['팀 이름']
        for stat in stat_cols:
            stat_value = row[stat]
            if pd.notna(stat_value):  # 값이 존재하는 경우만 추가
                result_data.append({
                    '날짜': log_date,
                    '팀': team_name,
                    '기록': stat,
                    '기록값': stat_value
                })

    # 경기 결과 계산 (득점 비교)
    team_scores = df_team_total[['팀 이름', 'R']].set_index('팀 이름')['R'].to_dict()
    away_score, home_score = team_scores.get(away_team, 0), team_scores.get(home_team, 0)

    if away_score > home_score:
        away_result, home_result = 'W', 'L'
    elif away_score < home_score:
        away_result, home_result = 'L', 'W'
    else:
        away_result, home_result = 'D', 'D'

    result_data.append({
        '날짜': log_date,
        '팀': away_team,
        '기록': '경기결과',
        '기록값': away_result
    })
    result_data.append({
        '날짜': log_date,
        '팀': home_team,
        '기록': '경기결과',
        '기록값': home_result
    })

    # 2. **log_box 데이터 정제**
    def count_keyword_occurrences(row, keyword):
        count = 0
        for col in row.index:
            if isinstance(row[col], str) and keyword in row[col]:
                keyword_section = row[col].split(f'{keyword} : ')[-1]
                players = [p.strip() for p in keyword_section.split(')') if p.strip()]
                count += len(players)
        return count

    # 도루 성공 및 실책 계산
    log_box['도루'] = log_box.apply(lambda row: count_keyword_occurrences(row, '도루성공'), axis=1)
    log_box['실책'] = log_box.apply(lambda row: count_keyword_occurrences(row, '실책'), axis=1)

    # log_box 데이터를 result_data에 추가
    for _, row in log_box.iterrows():
        team_name = row['팀명']
        
        # 도루성공 추가
        result_data.append({
            '날짜': current_date,
            '팀': team_name,
            '기록': '도루',
            '기록값': row['도루']
        })
        
        # 실책 추가
        result_data.append({
            '날짜': current_date,
            '팀': team_name,
            '기록': '실책',
            '기록값': row['실책']
        })

# 최종 DataFrame 생성 및 저장
df_log_combined = pd.DataFrame(result_data)
# 날짜, 팀, 기록값 순으로 정렬
df_log_combined_sorted = df_log_combined.sort_values(by=['날짜', '팀', '기록'])

output_file_path = os.path.join(output_folder_path, f'{current_date}-play_log.csv')
df_log_combined_sorted.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"✅ {output_file_path} 파일이 성공적으로 생성되었습니다.")