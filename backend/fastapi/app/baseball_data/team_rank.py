import pandas as pd

# 팀 목록
teams = ['KIA', '삼성', 'LG', '두산', 'KT', 'SSG', '롯데', '한화', 'NC', '키움']

# 초기 데이터 생성
data = {
    '팀': teams,
    '승': [0] * len(teams),
    '무': [0] * len(teams),
    '패': [0] * len(teams),
    '승률': [0.000] * len(teams),
    '순위': [0] * len(teams)
}

# DataFrame 생성
df = pd.DataFrame(data)

# 승률 계산 (초기값은 모두 0)
df['승률'] = df['승'] / (df['승'] + df['패']).replace({0: 1})  # 패가 0일 때 1로 대체하여 계산 방지
df['승률'] = df['승률'].round(3)  # 소수점 셋째 자리까지 반올림

# 순위 계산 (동률 처리)
df['순위'] = df['승률'].rank(method='min', ascending=False).astype(int)

# CSV 파일 저장
df.to_csv('current_rank.csv', index=False)
