from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz
from config import Config

def kst_to_et(kst_str):
    try:
        kst_dt = datetime.strptime(kst_str, "%b %d, %Y, %I:%M %p")
    except:
        return "N/A"
    kst_tz = pytz.timezone("Asia/Seoul")
    kst_dt = kst_tz.localize(kst_dt)
    et_tz = pytz.timezone("America/New_York")
    et_dt = kst_dt.astimezone(et_tz)
    return et_dt.strftime("%Y-%m-%d %H:%M:%S")

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    # Headless mode is often better for cloud/background agents, but let's keep it visible for now if user wants
    # options.add_argument("--headless") 
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36"
    )
    
    if Config.CHROME_DRIVER_PATH:
        service = Service(Config.CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # Fallback or use webdriver_manager if installed (recommended for future)
        driver = webdriver.Chrome(options=options)
        
    return driver

# def collect_new_posts(driver, existing_urls, max_count=100):
#     driver.get(Config.TRUTH_SOCIAL_URL)
#     time.sleep(4)

#     collected = []
#     seen_urls = set()

#     scroll_attempts = 0
#     max_scroll_attempts = Config.MAX_SCROLL_ATTEMPTS

#     while scroll_attempts < max_scroll_attempts:
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         posts = soup.find_all("div", attrs={"data-testid": "status-content"})

#         found_new = False

#         for post in posts:
#             parent = post.find_parent("div", attrs={"data-index": True})
#             if not parent:
#                 continue

#             time_tag = parent.find("time")

#             url = None
#             if time_tag:
#                 a = time_tag.find_parent("a", href=True)
#                 if a:
#                     href = a["href"]
#                     url = "https://truthsocial.com" + href if href.startswith("/") else href

#             if not url:
#                 continue

#             if url in seen_urls:
#                 continue
#             seen_urls.add(url)

#             # Check if already processed
#             if url in existing_urls:
#                 print("🎯 기존 데이터 도달 → 스크롤 종료")
#                 return collected

#             # Exclude ReTruths
#             status_info = parent.find("div", role="status-info")
#             if status_info and "ReTruthed" in status_info.get_text(strip=True):
#                 continue

#             # Content
#             text_parts = []
#             for elem in post.descendants:
#                 if getattr(elem, "name", None) == "br":
#                     text_parts.append("\n")
#                 elif isinstance(elem, str):
#                     t = elem.strip()
#                     if t:
#                         text_parts.append(t)

#             text = "".join(text_parts).strip()
#             if not text:
#                 continue

#             timestamp_raw = time_tag['title'] if time_tag and time_tag.has_attr('title') else "N/A"
#             et_time = kst_to_et(timestamp_raw) if timestamp_raw != "N/A" else "N/A"

#             # Preprocess content
#             from modules.preprocessor import preprocess_tweet
#             clean_content = preprocess_tweet(text)

#             collected.append({
#                 "time": et_time,
#                 "kst_time": timestamp_raw,
#                 "content": text,
#                 "clean_content": clean_content,
#                 "url": url
#             })

#             found_new = True
#             print(f"[수집] {len(collected)}개 URL 확보")

#             if len(collected) >= max_count:
#                 return collected

#         # Scroll down
#         driver.execute_script("window.scrollBy(0, 800);")
#         time.sleep(Config.SCROLL_PAUSE_TIME)
#         scroll_attempts += 1

#     return collected
def collect_new_posts(driver, existing_urls, max_count=450):
    driver.get("https://truthsocial.com/@realDonaldTrump")
    time.sleep(4)

    collected = []
    seen_urls = set()

    scroll_attempts = 0
    max_scroll_attempts = 450  # 넉넉하게

    prev_height = 0

    while scroll_attempts < max_scroll_attempts:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.find_all("div", attrs={"data-testid": "status-content"})

        found_new = False

        for post in posts:
            parent = post.find_parent("div", attrs={"data-index": True})
            if not parent:
                continue

            time_tag = parent.find("time")

            url = None
            if time_tag:
                a = time_tag.find_parent("a", href=True)
                if a:
                    href = a["href"]
                    url = "https://truthsocial.com" + href if href.startswith("/") else href

            if not url:
                continue

            if url in seen_urls:
                continue
            seen_urls.add(url)

            # 이미 엑셀에 있는 게시물 → 여기가 "종료 조건"
            if url in existing_urls:
                print("🎯 기존 데이터 도달 → 스크롤 종료")
                return collected

            # 리트루스 제외
            status_info = parent.find("div", role="status-info")
            if status_info and "ReTruthed" in status_info.get_text(strip=True):
                continue

            # 본문
            text_parts = []
            for elem in post.descendants:
                if getattr(elem, "name", None) == "br":
                    text_parts.append("\n")
                elif isinstance(elem, str):
                    t = elem.strip()
                    if t:
                        text_parts.append(t)

            text = "".join(text_parts).strip()
            if not text:
                continue

            timestamp_raw = time_tag['title'] if time_tag and time_tag.has_attr('title') else "N/A"
            et_time = kst_to_et(timestamp_raw) if timestamp_raw != "N/A" else "N/A"

            collected.append({
                "time": et_time,
                "kst_time": timestamp_raw,
                "content": text,
                "url": url
            })

            found_new = True

            print(f"[수집] {len(collected)}개 URL 확보")

            if len(collected) >= max_count:
                return collected

        # 스크롤 다운
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(2.0)

        scroll_attempts += 1

    return collected
