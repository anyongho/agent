from agents import Agent, Runner
import json
import asyncio

class TrumpAnalyzer:
    def __init__(self):
        self.agent = Agent(
            name="트럼프 트윗 분석 에이전트",
            instructions=(
                "You are an expert who analyzes Donald Trump's tweets for economic and stock market implications. "
                "For each tweet, respond only according to the instructions below.\n\n"
                "Instructions:\n"
                "1) impact_on_market: 'Direct' if specific companies or CEOs are mentioned, 'Indirect' if it affects sectors or economy, 'No' if not impactful.\n"
                "2) sentiment_score: a float between -1.0 (strongly negative) and 1.0 (strongly positive) with one decimal place.\n"
                "3) market_impact_score: a float between 0.0 (no market impact) and 1.0 (very strong market impact).\n"
                "4) keywords: list up to 5 main companies, CEOs, or economic terms in order of importance.\n"
                "5) sector: list all applicable sectors affected by the tweet, choose from [Financials, Information Technology, Health Care, Consumer Discretionary, Communication Services, Industrials, Consumer Staples, Energy, Real Estate, Materials, Utilities]. "
                "If a specific company is mentioned, include the company name.\n"
                "6) reason: one concise English sentence explaining your reason about market impact.\n\n"
                "Respond strictly in valid JSON format with these exact keys: impact_on_market, sentiment_score, market_impact_score, keywords, sector, reason.\n"
                "Do not include any markdown formatting or code blocks."
            )
        )

    async def analyze_tweet(self, tweet_text):
        try:
            print(f"🤖 AI 분석 중: {tweet_text[:50]}...")
            result = await Runner.run(self.agent, tweet_text)
            response_text = result.final_output

            # JSON Parsing
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            analysis = json.loads(response_text)
            print(f"✅ 분석 완료: {analysis.get('impact_on_market')} | 영향도: {analysis.get('market_impact_score')}")
            return analysis
        except Exception as e:
            print(f"⚠️ 분석 오류: {e}")
            return {
                "impact_on_market": "Error",
                "sentiment_score": 0.0,
                "market_impact_score": 0.0,
                "keywords": [],
                "sector": [],
                "reason": f"분석 오류: {str(e)}"
            }
