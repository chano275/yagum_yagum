import os
import csv
import json
from datetime import datetime, timedelta

def csv_to_json_with_specific_date(input_folder, output_folder):
    try:
        # 하루 전 날짜 계산
        currentdate = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # 날짜 포맷 변경
        target_file_name = f"{currentdate}-play_log.csv"
        csv_file_path = os.path.join(input_folder, target_file_name)

        # 파일 존재 여부 확인
        if not os.path.exists(csv_file_path):
            print(f"{target_file_name} 파일이 {input_folder} 폴더에 없습니다.")
            return

        # json_data 폴더 생성 (존재하지 않으면 생성)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"폴더 생성: {output_folder}")

        # JSON 파일 경로 설정
        json_file_path = os.path.join(output_folder, f"{currentdate}-play_log.json")

        # CSV 파일 읽고 날짜별로 JSON 구조 생성
        grouped_data = {target_date: []}
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # 날짜 필드를 제거한 데이터만 저장
                row_without_date = {key: value for key, value in row.items() if key != "날짜" and key != "﻿날짜"}  # 날짜 필드 제거
                grouped_data[target_date].append(row_without_date)

        # JSON 파일 쓰기
        with open(json_file_path, mode='w', encoding='utf-8') as json_file:
            json.dump(grouped_data, json_file, indent=4, ensure_ascii=False)
        
        print(f"{target_file_name} -> {currentdate}-play_log.json 변환 완료 (저장 경로: {json_file_path})")
    
    except Exception as e:
        print(f"문제가 발생했습니다: {e}")

# 사용 예시
input_folder = "processed_data"  # CSV 파일이 있는 폴더 경로
output_folder = "json_data"      # JSON 파일을 저장할 폴더 경로
csv_to_json_with_specific_date(input_folder, output_folder)
