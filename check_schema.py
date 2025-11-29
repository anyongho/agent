import pandas as pd
try:
    df = pd.read_excel('trump_posts_scraped.xlsx', nrows=1)
    print("SUCCESS")
    print(df.columns.tolist())
except Exception as e:
    print(f"ERROR: {e}")
