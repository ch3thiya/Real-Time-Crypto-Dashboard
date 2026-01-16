import os, requests, psycopg2, sys
from datetime import datetime

API_KEY = os.getenv('COINGECKO_API_KEY')
DB_URL = os.getenv('DATABASE_URL')

def run_scraper():
    if not DB_URL:
        print("CRITICAL: DATABASE_URL IS EMPTY")
        sys.exit(1)

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'binancecoin,ethereum,solana,litecoin', 'vs_currencies': 'usd', 'include_market_cap': 'true', 'include_24hr_change': 'true'}
    headers = {"accept": "application/json", "x-cg-demo-api-key": API_KEY if API_KEY else ""}
    
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    try:
        with psycopg2.connect(DB_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS crypto_prices (
                        id SERIAL PRIMARY KEY,
                        coin TEXT,
                        price FLOAT,
                        market_cap FLOAT,
                        change_24h FLOAT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                for coin_id, stats in data.items():
                    cur.execute("""
                        INSERT INTO crypto_prices (coin, price, market_cap, change_24h, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (coin_id, stats['usd'], stats['usd_market_cap'], stats['usd_24h_change'], datetime.now()))
                
                print(f"SUCCESSFULLY INSERTED {len(data)} ROWS")

    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()