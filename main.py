import os
import requests
import psycopg2
from datetime import datetime

API_KEY = os.getenv('COINGECKO_API_KEY')
DB_URL = os.getenv('DATABASE_URL')
COINS = "bitcoin,ethereum,solana,cardano"

def run_scraper():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': COINS,
        'vs_currencies': 'usd',
        'include_market_cap': 'true',
        'include_24hr_change': 'true'
    }
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": API_KEY
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    for coin_id, stats in data.items():
        cur.execute("""
            INSERT INTO crypto_prices (coin, price, market_cap, change_24h, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            coin_id, 
            stats['usd'], 
            stats['usd_market_cap'], 
            stats['usd_24h_change'], 
            datetime.now()
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Scraped {len(data)} coins at {datetime.now()}")

if __name__ == "__main__":
    run_scraper()