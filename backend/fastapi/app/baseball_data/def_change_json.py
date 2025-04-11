import os
import csv
import json
from datetime import datetime, timedelta

def get_yesterday_date():
    """어제 날짜를 반환"""
    return datetime.now() - timedelta(days=1)

def format_date(date, format_str):
    """날짜를 지정된 형식으로 포맷팅"""
    return date.strftime(format_str)

def create_folder_if_not_exists(folder_path):
    """폴더가 존재하지 않으면 생성"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더 생성: {folder_path}")
    return folder_path

def check_file_exists(file_path):
    """파일 존재 여부 확인"""
    if not os.path.exists(file_path):
        return False
    return True

def read_csv_and_group_by_date(csv_file_path, target_date):
    """CSV 파일을 읽고 날짜별로 그룹화"""
    grouped_data = {target_date: []}
    
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # 날짜 필드 제거하고 데이터만 저장
            row_without_date = {key: value for key, value in row.items() 
                               if key != "날짜" and key != "﻿날짜"}
            grouped_data[target_date].append(row_without_date)
    
    return grouped_data

def write_json_file(data, json_file_path):
    """데이터를 JSON 파일로 저장"""
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    return json_file_path

def csv_to_json_with_specific_date(input_folder="processed_data", output_folder="json_data"):
    """CSV 파일을 JSON으로 변환하는 메인 함수"""
    try:
        # 날짜 계산
        yesterday = get_yesterday_date()
        currentdate = format_date(yesterday, '%Y%m%d')
        target_date = format_date(yesterday, '%Y-%m-%d')
        
        # 파일 경로 설정
        target_file_name = f"{currentdate}-play_log.csv"
        csv_file_path = os.path.join(input_folder, target_file_name)
        
        # 파일 존재 확인
        if not check_file_exists(csv_file_path):
            print(f"{target_file_name} 파일이 {input_folder} 폴더에 없습니다.")
            return False
        
        # 출력 폴더 생성
        create_folder_if_not_exists(output_folder)
        
        # JSON 파일 경로 설정
        json_file_path = os.path.join(output_folder, f"{currentdate}-play_log.json")
        
        # CSV 파일 읽고 데이터 그룹화
        grouped_data = read_csv_and_group_by_date(csv_file_path, target_date)
        
        # JSON 파일 쓰기
        write_json_file(grouped_data, json_file_path)
        
        print(f"{target_file_name} -> {currentdate}-play_log.json 변환 완료 (저장 경로: {json_file_path})")
        return True
    
    except Exception as e:
        print(f"문제가 발생했습니다: {e}")
        return False

# 스크립트가 직접 실행될 때만 실행
if __name__ == "__main__":
    input_folder = "processed_data"  # CSV 파일이 있는 폴더 경로
    output_folder = "json_data"      # JSON 파일을 저장할 폴더 경로
    csv_to_json_with_specific_date(input_folder, output_folder)
