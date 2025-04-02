import os
import csv
from glob import glob
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  # 첫 10,000바이트 샘플링
        result = chardet.detect(rawdata)
        return result['encoding']

def sort_csv_files(input_folder):
    try:
        # 폴더 존재 여부 확인
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"폴더가 존재하지 않습니다: {input_folder}")

        csv_files = glob(os.path.join(input_folder, "*.csv"))
        if not csv_files:
            print("CSV 파일이 폴더에 없습니다.")
            return

        for csv_file_path in csv_files:
            # 1. 인코딩 감지
            encoding = detect_encoding(csv_file_path)
            print(f"{os.path.basename(csv_file_path)} 인코딩: {encoding}")

            # 2. CSV 파일 읽기 (감지된 인코딩으로)
            with open(csv_file_path, 'r', encoding=encoding, errors='replace') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                if '등번호' not in csv_reader.fieldnames:
                    raise KeyError(f"'등번호' 컬럼이 없습니다: {csv_file_path}")
                
                # 3. 데이터 정렬 (등번호 숫자 변환 실패 시 기본값 처리)
                sorted_data = sorted(csv_reader, key=lambda row: (
                    int(row['등번호']) if row['등번호'].isdigit() else float('inf'),
                    row['포지션'],
                    row['이름']
                ))

            # 4. UTF-8로 재저장 (엑셀 호환)
            with open(csv_file_path, 'w', encoding='utf-8-sig', newline='') as csv_file:  # BOM 추가
                writer = csv.DictWriter(csv_file, fieldnames=csv_reader.fieldnames)
                writer.writeheader()
                writer.writerows(sorted_data)
            
            print(f"{os.path.basename(csv_file_path)} 정렬 완료")

    except Exception as e:
        print(f"오류 발생: {str(e)}")

# 실행
sort_csv_files("player_processing")
