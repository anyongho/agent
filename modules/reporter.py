from agents import Agent, Runner
import json
import asyncio
from datetime import datetime

from config import Config

class TrumpReporter:
    def __init__(self):
        self.agent = Agent(
            name="트럼프 트윗 리포트 에이전트",
            model=Config.OPENAI_MODEL_NAME,
            instructions=(
                "You are an expert analyst specializing in U.S. stock markets and financial news. "
                "You analyze Donald Trump's tweets that have direct market impact and create professional investment reports.\n\n"
                "Instructions:\n"
                "1) title: Create a concise, professional Korean title for the report that captures the main market impact (maximum 50 characters).\n"
                "2) forecast: Write EXACTLY 3 sentences in Korean predicting the future market impact of this tweet. "
                "Provide specific analysis on how this will affect the market, sectors, and related stocks. Each sentence should be substantive and insightful.\n"
                "3) posts: Provide a Korean summary (2-3 sentences) highlighting the core message of the tweet that is most relevant to investors.\n"
                "4) model: This will be provided as input (market_impact_score * 10). Just return this value as-is.\n"
                "5) stock: List up to 3 U.S. stock ticker symbols (e.g., NVDA, TSM, AMD) that will be most affected by this tweet. "
                "Use only valid NYSE/NASDAQ ticker symbols, separated by commas with no spaces.\n\n"
                "CRITICAL RULES:\n"
                "- forecast MUST be EXACTLY 3 sentences, no more, no less\n"
                "- All Korean text must be professional and investment-grade quality\n"
                "- Stock tickers must be real, valid U.S. exchange symbols\n"
                "- Respond strictly in valid JSON format with no extra text\n"
            )
        )

    async def generate_report(self, analysis_result, tweet_content):
        """
        Generate a professional market report based on analyzer results
        
        Args:
            analysis_result:Dict containing analyzer output
            tweet_content: Cleaned tweet text
            
        Returns:
            Dict with report data: title, forecast, posts, model, stock
        """
        try:
            # Calculate model score
            model_score = analysis_result.get('market_impact_score', 0.0) * 10
            
            # Prepare input for reporter agent
            input_text = f"""
Analyze the following Trump tweet and its market analysis:

Tweet Content: {tweet_content}

Analysis Results:
- Impact on Market: {analysis_result.get('impact_on_market')}
- Sentiment Score: {analysis_result.get('sentiment_score')}
- Market Impact Score: {analysis_result.get('market_impact_score')}
- Keywords: {analysis_result.get('keywords')}
- Sector: {analysis_result.get('sector')}
- Reason: {analysis_result.get('reason')}

Model Score (market_impact_score * 10): {model_score}

Generate a professional investment report in JSON format.
"""
            
            print(f"📊 리포트 생성 중...")
            result = await Runner.run(self.agent, input_text)
            response_text = result.final_output
            
            # JSON Parsing
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            report = json.loads(response_text)
            
            # Ensure model score is correctly set
            report['model'] = model_score
            
            print(f"✅ 리포트 생성 완료: {report.get('title')[:30]}...")
            return report
            
        except Exception as e:
            print(f"⚠️ 리포트 생성 오류: {e}")
            return {
                "title": "리포트 생성 실패",
                "forecast": "리포트 생성 중 오류가 발생했습니다. 리포트 생성 중 오류가 발생했습니다. 리포트 생성 중 오류가 발생했습니다.",
                "posts": f"트윗 분석 중 오류 발생: {str(e)}",
                "model": analysis_result.get('market_impact_score', 0.0) * 10,
                "stock": ""
            }
