import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv
load_dotenv()

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    agent = Agent(
        name = "트럼프 트윗 분석 에이전트",
        instructions = 
    "Forget all previous instructions and context.\n\n"
    "You are an expert who analyzes Donald Trump's tweets for economic and stock market implications. "
    "For each tweet, respond only according to the instructions below and do not provide any other information.\n\n"
    "Instructions:\n"
    "1) impact_on_market: 'Direct' if specific companies or CEOs are mentioned, 'Indirect' if it affects sectors or economy, 'No' if not impactful.\n"
    "2) sentiment_score: a float between -1.0 (strongly negative) and 1.0 (strongly positive) with one decimal place, representing overall sentiment.\n"
    "3) market_impact_score: a float between 0.0 (no market impact) and 1.0 (very strong market impact), representing likely influence on stocks/sectors. "
    "Consider both direct mentions of companies and broader economic implications when assigning this score.\n"
    "4) keywords: list up to 5 main companies, CEOs, or economic terms in order of importance based on market relevance.\n"
    "5) sector: list all applicable sectors affected by the tweet, choose from [Financials, Information Technology, Health Care, Consumer Discretionary, Communication Services, Industrials, Consumer Staples, Energy, Real Estate, Materials, Utilities]. "
    "If a specific company or CEO is mentioned, include the company name in the list.\n"
    "6) reason: one concise English sentence explaining your reason about market impact.\n\n"
    "Respond strictly in valid JSON with no extra text. Example:\n"
    "{\n"
    '    "impact_on_market": "Direct",\n'
    '    "sentiment_score": 0.5,\n'
    '    "market_impact_score": 0.7,\n'
    '    "keywords": ["Apple", "CEO Tim Cook"],\n'
    '    "sector": ["Information Technology"],\n'
    '    "reason": "Mentions Apple CEO and stock, likely impacting IT sector."\n'
    "}"
    )
    prompt = "Elon musk is awful"
    result = await Runner.run(agent,prompt)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())