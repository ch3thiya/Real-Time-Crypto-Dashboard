# Real Time Cryptocurrency Data Pipeline & Live Dashboard

A fully autonomous, serverless ETL pipeline that ingests, stores, and visualizes high frequency cryptocurrency market data.   [Dashboard](https://crypto-dashboard-ch3thiya.streamlit.app/)

## Overview

The primary objective of this project was to engineer a robust, hands off data infrastructure. While the frontend provides immediate market insights, the core value lies in the data’s journey navigating networking hurdles, ensuring data integrity through normalization, and orchestrating everything through automated CI/CD workflows.

## Pipeline Focus

Rather than just building a dashboard, this project focuses on core Data Engineering fundamentals:

- **Orchestration:** Moving beyond local scripts to 24/7 automated CRON jobs  
- **Connectivity:** Solving IPv4 to IPv6 networking gaps in cloud environments  
- **Data Integrity:** Aligning microsecond timestamps for accurate time series analysis  
- **Persistence:** Transitioning from ephemeral data to a persistent PostgreSQL warehouse  

## Architecture & Data Flow

The system is built on a modular, zero maintenance stack:

- **Extraction:** Python based scraper triggered by GitHub Actions every 60 minutes  
- **Ingestion:** Real time data from the CoinGecko API (BNB, Ethereum, Solana, Litecoin)  
- **Storage:** Supabase (PostgreSQL) with Supavisor connection pooling  
- **Processing:** Data cleaning and timestamp normalization using Pandas  
- **Visualization:** Streamlit dashboard with Altair charts and non zero Y axis scaling  

## Setup Guide

### Prerequisites

- CoinGecko Demo API Key  
- Supabase account with PostgreSQL  
- GitHub account  

### Database Configuration

```sql
CREATE TABLE crypto_prices (
    id SERIAL PRIMARY KEY,
    coin TEXT,
    price FLOAT,
    market_cap FLOAT,
    change_24h FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Disable Row Level Security if required:

```sql
ALTER TABLE crypto_prices DISABLE ROW LEVEL SECURITY;
```

### Repository Secrets

Add the following secrets in GitHub Actions:

- `DATABASE_URL` – Supabase pooler connection string  
- `COINGECKO_API_KEY` – CoinGecko API key  

### Automation

The scraper runs via:

```
.github/workflows/hourly_scrape.yml
```

You can manually trigger it from the GitHub Actions tab.

### Streamlit Deployment

```toml
[connections.postgresql]
url = "your_supabase_pooler_url"
```

## Technical Challenges

### IPv6 Networking Wall
GitHub Actions runs on IPv4 while many databases default to IPv6. This was resolved using Supavisor, which provides an IPv4-compatible endpoint.

### Microsecond Timestamp Trap
Microsecond differences caused misaligned charts. Timestamps were normalized to the nearest minute to synchronize all assets per scrape.
