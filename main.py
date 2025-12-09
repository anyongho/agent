import asyncio
import time
import sys
import os
import re

# Add current directory to path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.scraper import get_driver, collect_new_posts
from modules.analyzer import TrumpAnalyzer
from modules.reporter import TrumpReporter
from modules.storage import Storage
from modules.preprocessor import preprocess_tweet
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

async def process_new_posts(new_posts, analyzer, reporter, storage):
    results = []
    print(f"\n{'='*60}")
    print(f"🤖 AI 분석 시작: {len(new_posts)}개 트윗")
    print(f"{'='*60}\n")

    for i, post in enumerate(new_posts, 1):
        print(f"\n[{i}/{len(new_posts)}] 분석 중...")
        
        # Use cleaned content for analysis
        target_content = preprocess_tweet(post['content'])
        
        if not target_content:
            print(f"⚠️ 전처리 후 내용 없음 (Skip): {post.get('url')}")
            continue
        analysis = await analyzer.analyze_tweet(target_content)
        
        result_data = {
            'time': post['time'],          # US Time (Numeric/String)
            'time_str': post['kst_time'], # KST Time String (time_str)
            'tweet_content': target_content, # Save cleaned content to DB
            'original_content': post['content'], # Optional: keep original if needed
            'tweet_url': post.get('url', None),
            'impact_on_market': analysis.get('impact_on_market', 'Unknown'),
            'sentiment_score': analysis.get('sentiment_score', 0.0),
            'market_impact_score': analysis.get('market_impact_score', 0.0),
            'keywords': ', '.join(analysis.get('keywords', [])) if isinstance(analysis.get('keywords'), list) else str(analysis.get('keywords', '')),
            'sector': ', '.join(analysis.get('sector', [])) if isinstance(analysis.get('sector'), list) else str(analysis.get('sector', '')),
            'reason': analysis.get('reason', '')
        }
        results.append(result_data)

    # Save results to posts table and get IDs
    url_id_map = storage.save_results(new_posts, results)
    
    # Generate reports for high-impact tweets
    print(f"\n{'='*60}")
    print(f"📊 리포트 생성 대상 확인 중...")
    print(f"{'='*60}\n")
    
    
    # Helper function to check if last sentence contains ticker symbols
    def has_ticker_in_last_sentence(reason_text):
        """
        Check if the last sentence of reason contains ticker symbols
        Expected format: "NVDA, TSM, AMD." or "NVDA."
        """
        if not reason_text:
            return False
        
        # Split by period and get the last non-empty sentence
        sentences = [s.strip() for s in reason_text.split('.') if s.strip()]
        if not sentences:
            return False
        
        last_sentence = sentences[-1]
        
        # Pattern: One or more uppercase ticker symbols (1-5 letters) separated by commas
        # Example: "NVDA, TSM, AMD" or "NVDA" or "AAPL, MSFT"
        ticker_pattern = r'^[A-Z]{1,5}(\s*,\s*[A-Z]{1,5})*$'
        
        return bool(re.match(ticker_pattern, last_sentence))
    
    for result_data in results:
        impact = result_data.get('impact_on_market')
        score = result_data.get('market_impact_score', 0.0)
        tweet_url = result_data.get('tweet_url')
        reason = result_data.get('reason', '')
        
        # Check conditions: 
        # 1) Direct impact 
        # 2) score >= 0.5
        # 3) reason의 마지막 문장에 티커가 있는지
        if impact == 'Direct' and score >= 0.5 and has_ticker_in_last_sentence(reason):
            print(f"\n✅ 리포트 생성 조건 만족 (영향도: {score}, 티커 확인됨)")
            
            # Get post ID from url_id_map
            post_id = url_id_map.get(tweet_url)
            
            if post_id:
                # Generate report
                report = await reporter.generate_report(
                    {
                        'impact_on_market': impact,
                        'sentiment_score': result_data.get('sentiment_score'),
                        'market_impact_score': score,
                        'keywords': result_data.get('keywords'),
                        'sector': result_data.get('sector'),
                        'reason': reason
                    },
                    result_data.get('tweet_content')
                )
                
                # Save report to analyze table
                storage.save_report_to_supabase(
                    post_id,
                    report,
                    result_data.get('time_str')
                )
            else:
                print(f"⚠️ Post ID를 찾을 수 없습니다: {tweet_url}")
        else:
            has_ticker = has_ticker_in_last_sentence(reason)
            print(f"⏭️ 리포트 생성 조건 미충족 (Impact: {impact}, Score: {score}, Ticker: {has_ticker})")

async def main_async():
    storage = Storage()
    analyzer = TrumpAnalyzer()
    reporter = TrumpReporter()
    
    # Load existing URLs to avoid duplicates
    existing_urls = storage.get_existing_urls()
    
    driver = get_driver()
    
    try:
        new_posts = collect_new_posts(driver, existing_urls, max_count=100)
        
        if new_posts:
            print(f"\n✅ {len(new_posts)}개 신규 글 발견")
            
            # Save raw data first (cache)
            storage.save_raw_posts(new_posts)
            
            # Notify
            send_notification(len(new_posts))
            
            # Analyze, Generate Reports, and Save to DB/Excel
            await process_new_posts(new_posts, analyzer, reporter, storage)
            
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
