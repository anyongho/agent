import asyncio
import time
import sys
import os

# Add current directory to path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.scraper import get_driver, collect_new_posts
from modules.analyzer import TrumpAnalyzer
from modules.storage import Storage
from plyer import notification

def send_notification(count):
    try:
        notification.notify(
            title="🚨 새로운 트럼프 트윗 발견!",
            message=f"{count}개의 신규 트윗이 발견되었습니다. AI 분석을 시작합니다.",
            app_name="Trump Tweet Analyzer",
            timeout=10
        )
    except Exception as e:
        print(f"⚠️ 알림 전송 실패: {e}")

async def process_new_posts(new_posts, analyzer, storage):
    results = []
    print(f"\n{'='*60}")
    print(f"🤖 AI 분석 시작: {len(new_posts)}개 트윗")
    print(f"{'='*60}\n")

    for i, post in enumerate(new_posts, 1):
        print(f"\n[{i}/{len(new_posts)}] 분석 중...")
        analysis = await analyzer.analyze_tweet(post['content'])
        
        result_data = {
            'time': post['time'],          # US Time (Numeric/String)
            'posted_time': post['kst_time'], # KST Time String (time_str)
            'tweet_content': post['content'],
            'tweet_url': post.get('url', None),
            'impact_on_market': analysis.get('impact_on_market', 'Unknown'),
            'sentiment_score': analysis.get('sentiment_score', 0.0),
            'market_impact_score': analysis.get('market_impact_score', 0.0),
            'keywords': ', '.join(analysis.get('keywords', [])) if isinstance(analysis.get('keywords'), list) else str(analysis.get('keywords', '')),
            'sector': ', '.join(analysis.get('sector', [])) if isinstance(analysis.get('sector'), list) else str(analysis.get('sector', '')),
            'reason': analysis.get('reason', '')
        }
        results.append(result_data)

    # Save results
    storage.save_results(new_posts, results)

async def main_async():
    storage = Storage()
    analyzer = TrumpAnalyzer()
    
    # Load existing URLs to avoid duplicates
    existing_urls = storage.get_existing_urls()
    
    driver = get_driver()
    
    try:
        new_posts = collect_new_posts(driver, existing_urls, max_count=10)
        
        if new_posts:
            print(f"\n✅ {len(new_posts)}개 신규 글 발견")
            
            # Save raw data first (cache)
            storage.save_raw_posts(new_posts)
            
            # Notify
            send_notification(len(new_posts))
            
            # Analyze and Save to DB/Excel
            await process_new_posts(new_posts, analyzer, storage)
            
        else:
            print("🔄 신규 글 없음")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🚀 트럼프 트윗 분석 에이전트 시작 (Cloud Ready)")
    while True:
        try:
            asyncio.run(main_async())
            print("\n⏰ 1분 후 다시 실행합니다...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(30)
