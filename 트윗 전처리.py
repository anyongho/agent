import pandas as pd
import re

# === 1. 원본 엑셀 불러오기 ===
input_file = "trump_posts_scraped.xlsx"
output_file = "trump_posts_cleaned.xlsx"
df = pd.read_excel(input_file)

# === 2. RT 트윗 제거 (원본 기준) ===
rt_prefixes = ("RT @", "RT:", "RT ")
df = df[~df['content'].str.startswith(rt_prefixes, na=False)].copy()

# === 3. 트윗 전처리 함수 ===
def preprocess_tweet(tweet):
    if pd.isna(tweet):
        return ''
    tweet = tweet.lower()
    tweet = re.sub(r'@\S+', '', tweet)           # 멘션 제거
    tweet = re.sub(r'\B#\S+', '', tweet)         # 해시태그 제거
    tweet = re.sub(r'http\S+', '', tweet)        # URL 제거
    tweet = ' '.join(re.findall(r'\w+', tweet)) # 특수문자 제거
    tweet = re.sub(r'\s+[a-zA-Z]\s+', ' ', tweet) # 단일 문자 제거
    tweet = re.sub(r'\s+', ' ', tweet).strip()     # 공백 정리
    tweet = tweet.replace('"', '\\"')            # 큰따옴표 이스케이프
    return tweet

# === 4. content 컬럼만 clean tweet으로 변경 ===
df['content'] = df['content'].apply(preprocess_tweet)

# === 5. 전처리 후 RT 트윗 제거 ===
df = df[~df['content'].str.startswith("rt", na=False)].copy()

# === 6. content가 빈 문자열 또는 null인 트윗 제거 ===
df = df[df['content'].str.strip() != ''].copy()

# === 7. 엑셀로 저장 ===
df.to_excel(output_file, index=False)
print(f"✅ 전처리 완료: '{output_file}' 파일 생성됨")
