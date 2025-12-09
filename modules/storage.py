import os
import pandas as pd
from supabase import create_client, Client
from config import Config

class Storage:
    def __init__(self):
        self.supabase: Client = None
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                print("✅ Supabase 연결 성공")
            except Exception as e:
                print(f"⚠️ Supabase 연결 실패: {e}")
        else:
            print("⚠️ Supabase 설정이 없습니다. 로컬 엑셀 파일만 사용합니다.")

    def save_results(self, new_posts, analysis_results):
        """
        Save results to both Supabase and Excel (as backup)
        Returns: Dictionary mapping tweet URLs to their database IDs
        """
        url_id_map = {}
        
        # 1. Save to Supabase
        if self.supabase:
            url_id_map = self._save_to_supabase(analysis_results)

        # 2. Save to Excel (Legacy/Backup)
        self._save_to_excel(analysis_results)
        
        return url_id_map

    def _save_to_supabase(self, results):
        """
        Save analysis results to Supabase posts table
        Returns: List of inserted/updated post IDs with their tweet URLs
        """
        try:
            # Prepare data for Supabase
            # Unified Schema Mapping
            data_to_insert = []
            for item in results:
                row = {
                    "url": item.get('tweet_url'),
                    "content": item.get('tweet_content'),
                    "time_str": item.get('time_str'),
                    "time": item.get('time'), # Ensure this key exists in results or map from posted_time
                    "impact_on_market": item.get('impact_on_market'),
                    "sentiment_score": item.get('sentiment_score'),
                    "market_impact_score": item.get('market_impact_score'),
                    "keywords": item.get('keywords'),
                    "sector": item.get('sector'),
                    "reason": item.get('reason')
                }
                data_to_insert.append(row)

            if data_to_insert:
                response = self.supabase.table("posts").upsert(data_to_insert, on_conflict="url").execute()
                print(f"✅ Supabase 저장 완료: {len(data_to_insert)}개 항목")
                
                # Return list of (url, id) tuples for report generation
                inserted_data = response.data
                url_id_map = {}
                if inserted_data:
                    for record in inserted_data:
                        url_id_map[record.get('url')] = record.get('id')
                return url_id_map
            return {}
        except Exception as e:
            print(f"⚠️ Supabase 저장 오류: {e}")
            return {}

    def _save_to_excel(self, results, filename="trump_posts_AI_analysis.xlsx"):
        if not results:
            return

        try:
            if os.path.exists(filename):
                df_existing = pd.read_excel(filename)
                df_new = pd.DataFrame(results)
                df_combined = pd.concat([df_new, df_existing], ignore_index=True)
                df_combined.drop_duplicates(subset=['tweet_url'], keep='first', inplace=True)
            else:
                df_combined = pd.DataFrame(results)

            df_combined.to_excel(filename, index=False, engine='openpyxl')
            print(f"✅ 엑셀 저장 완료: {filename}")
        except Exception as e:
            print(f"⚠️ 엑셀 저장 오류: {e}")

    def get_existing_urls(self, excel_path="trump_posts_scraped.xlsx"):
        # Ideally fetch from Supabase too, but for now keep local cache for scraper efficiency
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                return set(df['url'].astype(str))
            except:
                return set()
        return set()

    def save_raw_posts(self, posts, excel_path="trump_posts_scraped.xlsx"):
        # Save raw scraped data to Excel (scraper cache)
        if not posts:
            return
            
        try:
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
                new_df = pd.DataFrame(posts)
                df = pd.concat([new_df, df], ignore_index=True)
                df.drop_duplicates(subset=['url'], keep='first', inplace=True)
            else:
                df = pd.DataFrame(posts)
            
            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"⚠️ Raw 데이터 저장 오류: {e}")

    def save_report_to_supabase(self, post_id, report_data, tweet_time_str):
        """
        Save report data to Supabase analyze table
        
        Args:
            post_id: ID from posts table
            report_data: Dict containing title, forecast, posts, model, stock
            tweet_time_str: Original tweet timestamp (KST)
        """
        if not self.supabase:
            print("⚠️ Supabase 연결이 없어 리포트를 저장할 수 없습니다.")
            return
        
        try:
            from datetime import datetime
            
            report_row = {
                "id": post_id,
                "title": report_data.get('title', ''),
                "time": datetime.now().isoformat(),  # 리포트 생성 시간
                "forecast": report_data.get('forecast', ''),
                "posts": report_data.get('posts', ''),
                "model": report_data.get('model', 0.0),
                "stock": report_data.get('stock', '')
            }
            
            response = self.supabase.table("analyze").upsert(report_row, on_conflict="id").execute()
            print(f"✅ 리포트 저장 완료 (ID: {post_id}): {report_data.get('title')[:30]}...")
            
        except Exception as e:
            print(f"⚠️ 리포트 저장 오류: {e}")
