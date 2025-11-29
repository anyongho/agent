import pandas as pd
import os
import ast
from supabase import create_client
from config import Config

# ---------------------------------------------------------
# 1. Supabase 연결
# ---------------------------------------------------------
if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
    print("❌ .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
    exit()

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# ---------------------------------------------------------
# 2. 엑셀 파일 읽기
# ---------------------------------------------------------
excel_file = 'merged_all_excel.xlsx'
if not os.path.exists(excel_file):
    print(f"❌ {excel_file} 파일이 없습니다.")
    exit()

print(f"📂 {excel_file} 읽는 중...")
df = pd.read_excel(excel_file)

# ---------------------------------------------------------
# 3. 데이터 변환 (Schema Mapping)
# ---------------------------------------------------------
# Excel Column -> Supabase Column
# time_str -> time_str
# time -> time
# content -> content
# url -> url
# act_on_market -> impact_on_market
# sentiment_score -> sentiment_score
# market_impact_score -> market_impact_score
# keywords -> keywords (Clean string format)
# sector -> sector (Clean string format)
# reason -> reason

mapped_data = []

for index, row in df.iterrows():
    try:
        # 키워드/섹터 문자열 정리 (['a', 'b'] -> a, b)
        # 웹사이트가 리스트 문자열을 그대로 원하면 이 부분은 주석 처리하거나 수정해야 함
        # 현재는 깔끔한 텍스트로 변환하여 저장
        
        keywords_raw = row.get('keywords', '')
        sector_raw = row.get('sector', '')
        
        # 만약 "['Apple', 'Tesla']" 같은 문자열이라면 파싱해서 "Apple, Tesla"로 변환
        # (웹사이트 로직에 따라 이 부분은 조정 가능)
        try:
            if isinstance(keywords_raw, str) and keywords_raw.startswith('['):
                k_list = ast.literal_eval(keywords_raw)
                keywords_clean = ", ".join(k_list)
            else:
                keywords_clean = str(keywords_raw)
        except:
            keywords_clean = str(keywords_raw)

        try:
            if isinstance(sector_raw, str) and sector_raw.startswith('['):
                s_list = ast.literal_eval(sector_raw)
                sector_clean = ", ".join(s_list)
            else:
                sector_clean = str(sector_raw)
        except:
            sector_clean = str(sector_raw)

        item = {
            "time_str": str(row.get('time_str', '')),
            "time": str(row.get('time', '')), # Supabase에 TEXT로 저장하거나, FLOAT라면 변환 필요
            "content": str(row.get('content', '')),
            "url": str(row.get('url', '')),
            "impact_on_market": str(row.get('act_on_market', row.get('impact_on_market', ''))), # 컬럼명 변경 대응
            "sentiment_score": float(row.get('sentiment_score', 0.0)),
            "market_impact_score": float(row.get('market_impact_score', 0.0)),
            "keywords": keywords_clean,
            "sector": sector_clean,
            "reason": str(row.get('reason', ''))
        }
        
        # 필수 값 체크 (URL 없으면 스킵)
        if not item['url'] or item['url'] == 'nan':
            continue
            
        mapped_data.append(item)
        
    except Exception as e:
        print(f"⚠️ Row {index} 변환 실패: {e}")

print(f"✅ {len(mapped_data)}개 데이터 변환 완료.")

# ---------------------------------------------------------
# 4. Supabase 업로드
# ---------------------------------------------------------
batch_size = 100
print(f"🚀 Supabase 업로드 시작 (총 {len(mapped_data)}개, 배치 사이즈 {batch_size})")

for i in range(0, len(mapped_data), batch_size):
    batch = mapped_data[i:i + batch_size]
    try:
        response = supabase.table("posts").upsert(batch, on_conflict="url").execute()
        print(f"   - {i} ~ {i+len(batch)} 저장 완료")
    except Exception as e:
        print(f"   ❌ 배치 저장 실패 ({i}): {e}")

print("🎉 마이그레이션 완료!")
