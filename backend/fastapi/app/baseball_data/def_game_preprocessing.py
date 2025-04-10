import os
import pandas as pd
from datetime import datetime, timedelta

def get_yesterday_date():
    """어제 날짜를 반환"""
    return datetime.now() - timedelta(days=1)

def create_output_folder(output_folder_path):
    """출력 폴더 생성"""
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    print(f"출력 폴더 '{output_folder_path}' 생성 완료")

def load_batting_and_log_box_files(input_folder_path):
    """입력 폴더에서 batting과 log_box 파일 목록 가져오기"""
    batting_files = [f for f in os.listdir(input_folder_path) if '_batting.csv' in f]
    log_box_files = [f for f in os.listdir(input_folder_path) if '_log_boxes.csv' in f]
    return batting_files, log_box_files

def process_batting_data(batting_file_path, log_date):
    """batting 데이터 처리"""
    batting = pd.read_csv(batting_file_path)
    df_team_total = batting[batting['타순'] == '팀 합계'].copy()
    
    df_team_total['BB'] = pd.to_numeric(df_team_total['BB'], errors='coerce').fillna(0)
    df_team_total['HBP'] = pd.to_numeric(df_team_total['HBP'], errors='coerce').fillna(0)
    df_team_total['사구'] = df_team_total['BB'] + df_team_total['HBP']
    
    include_cols = ['H', 'R', 'HR', 'SO', 'GDP', '사구']
    stat_cols = [col for col in batting.columns if col in include_cols]
    
    result_data = []
    for _, row in df_team_total.iterrows():
        team_name = row['팀 이름']
        for stat in stat_cols:
            stat_value = row[stat]
            if pd.notna(stat_value):
                result_data.append({
                    '날짜': log_date,
                    '팀': team_name,
                    '기록': stat,
                    '기록값': stat_value
                })
    return result_data, df_team_total

def calculate_game_result(df_team_total, away_team, home_team, log_date):
    """경기 결과 계산"""
    team_scores = df_team_total[['팀 이름', 'R']].set_index('팀 이름')['R'].to_dict()
    away_score, home_score = team_scores.get(away_team, 0), team_scores.get(home_team, 0)
    
    if away_score > home_score:
        away_result, home_result = 'W', 'L'
    elif away_score < home_score:
        away_result, home_result = 'L', 'W'
    else:
        away_result, home_result = 'D', 'D'
    
    return [
        {'날짜': log_date, '팀': away_team, '기록': '경기결과', '기록값': away_result},
        {'날짜': log_date, '팀': home_team, '기록': '경기결과', '기록값': home_result}
    ], away_result

def update_current_rank(ranking_df, away_result, away_team, home_team):
    """current_rank.csv 업데이트"""
    if away_result == 'W':
        ranking_df.loc[ranking_df['팀'] == away_team, '승'] += 1
        ranking_df.loc[ranking_df['팀'] == home_team, '패'] += 1
    elif away_result == 'L':
        ranking_df.loc[ranking_df['팀'] == away_team, '패'] += 1
        ranking_df.loc[ranking_df['팀'] == home_team, '승'] += 1
    elif away_result == 'D':
        ranking_df.loc[ranking_df['팀'] == away_team, '무'] += 1
        ranking_df.loc[ranking_df['팀'] == home_team, '무'] += 1
    return ranking_df

def process_log_box_data(log_box, log_date):
    """log_box 데이터 처리"""
    def count_keyword_occurrences(row, keyword):
        count = 0
        for col in row.index:
            if isinstance(row[col], str) and keyword in row[col]:
                keyword_section = row[col].split(f'{keyword} : ')[-1]
                players = [p.strip() for p in keyword_section.split(')') if p.strip()]
                count += len(players)
        return count
    
    log_box['도루'] = log_box.apply(lambda row: count_keyword_occurrences(row, '도루성공'), axis=1)
    log_box['실책'] = log_box.apply(lambda row: count_keyword_occurrences(row, '실책'), axis=1)
    
    result_data = []
    for _, row in log_box.iterrows():
        team_name = row['팀명']
        result_data.extend([
            {'날짜': log_date, '팀': team_name, '기록': '도루', '기록값': row['도루']},
            {'날짜': log_date, '팀': team_name, '기록': '실책', '기록값': row['실책']}
        ])
    return result_data

def save_final_dataframe(df_log_combined_sorted, output_file_path):
    """최종 DataFrame 저장"""
    df_log_combined_sorted.to_csv(output_file_path, index=False, encoding='utf-8-sig')
    print(f"✅ {output_file_path} 파일이 성공적으로 생성되었습니다.")

def calculate_daily_rank(ranking_df):
    """일일 순위 계산"""
    ranking_df['승률'] = (ranking_df['승'] / (ranking_df['승'] + ranking_df['패']).replace({0: 1})).round(3)
    ranking_df['순위'] = ranking_df['승률'].rank(method='min', ascending=False).astype(int)
    return ranking_df

def save_daily_rank(ranking_df, daily_rank_path):
    """일일 순위 저장"""
    ranking_df = ranking_df.sort_values(by='순위', ascending=True).reset_index(drop=True)
    ranking_df.to_csv(daily_rank_path, index=False, encoding='utf-8-sig')
    print(f"✅ {daily_rank_path} 파일이 생성되었습니다.")

def main():
    yesterday = get_yesterday_date()
    current_date = yesterday.strftime('%Y%m%d')
    log_date = yesterday.strftime('%Y-%m-%d')
    input_folder_path = f'crawled_data/{current_date}'
    output_folder_path = 'processed_data'
    
    create_output_folder(output_folder_path)
    batting_files, log_box_files = load_batting_and_log_box_files(input_folder_path)
    
    result_data = []
    ranking_df = pd.read_csv('current_rank.csv')
    
    for batting_file, log_box_file in zip(batting_files, log_box_files):
        batting_file_path = os.path.join(input_folder_path, batting_file)
        log_box_file_path = os.path.join(input_folder_path, log_box_file)
        
        away_team, home_team = batting_file.replace('_batting.csv', '').split('-')
        
        batting_data, df_team_total = process_batting_data(batting_file_path, log_date)
        result_data.extend(batting_data)
        
        game_result, away_result = calculate_game_result(df_team_total, away_team, home_team, log_date)
        result_data.extend(game_result)
        
        ranking_df = update_current_rank(ranking_df, away_result, away_team, home_team)
        
        log_box = pd.read_csv(log_box_file_path)
        log_box_data = process_log_box_data(log_box, log_date)
        result_data.extend(log_box_data)
    
    df_log_combined = pd.DataFrame(result_data)
    df_log_combined_sorted = df_log_combined.sort_values(by=['날짜', '팀', '기록'])
    
    output_file_path = os.path.join(output_folder_path, f'{current_date}-play_log.csv')
    save_final_dataframe(df_log_combined_sorted, output_file_path)
    
    ranking_df.to_csv('current_rank.csv', index=False, encoding='utf-8-sig')
    print("✅ ranking 계산 완료!")
    
    daily_rank_folder = 'daily_rank'
    create_output_folder(daily_rank_folder)
    
    daily_rank_filename = f'{current_date}-rank.csv'
    daily_rank_path = os.path.join(daily_rank_folder, daily_rank_filename)
    
    ranking_df = calculate_daily_rank(ranking_df)
    save_daily_rank(ranking_df, daily_rank_path)

if __name__ == "__main__":
    main()
