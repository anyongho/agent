import re
import pandas as pd

def preprocess_tweet(tweet):
    """
    트윗 텍스트를 전처리합니다.
    - 소문자 변환
    - 멘션, 해시태그, URL 제거
    - 특수문자 제거
    - 공백 정리
    """
    if pd.isna(tweet):
        return ''
    
    # 1. 소문자 변환
    tweet = tweet.lower()
    
    # 2. 패턴 제거
    tweet = re.sub(r'@\S+', '', tweet)           # 멘션 제거
    tweet = re.sub(r'\B#\S+', '', tweet)         # 해시태그 제거
    tweet = re.sub(r'http\S+', '', tweet)        # URL 제거
    
    # 3. 텍스트 정제
    tweet = ' '.join(re.findall(r'\w+', tweet)) # 특수문자 제거 (단어만 남김)
    tweet = re.sub(r'\s+[a-zA-Z]\s+', ' ', tweet) # 단일 문자 제거
    tweet = re.sub(r'\s+', ' ', tweet).strip()     # 공백 정리
    tweet = tweet.replace('"', '\\"')            # 큰따옴표 이스케이프
    
    return tweet

def is_valid_tweet(content):
    """
    전처리된 트윗이 유효한지 검사합니다.
    - RT(리트윗) 제거
    - 빈 문자열 제거
    """
    if not content:
        return False
        
    # RT 제거 (전처리 후에는 보통 'rt'로 시작하거나 포함될 수 있음, 원본 로직 참고)
    # 원본 로직: df = df[~df['content'].str.startswith("rt", na=False)]
    if content.startswith("rt ") or content == "rt":
        return False
        
    return True
