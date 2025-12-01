import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Chrome Driver (Optional if using webdriver_manager)
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
    
    # Analysis
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano")
    
    # Scraper
    TRUTH_SOCIAL_URL = "https://truthsocial.com/@realDonaldTrump"
    SCROLL_PAUSE_TIME = 2.0
    MAX_SCROLL_ATTEMPTS = 200
