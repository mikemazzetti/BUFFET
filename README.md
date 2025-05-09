# BUFFET, a Reddit Scraping Machine Learning Stock Sentiment Trader

A Python program that analyzes Reddit comments for stock sentiment and suggests trading decisions and will execute trades via Interactive Brokers (IBKR).

## Features

- Built an NLP-Powered stock trader using Python, to determine stock sentiment from Reddit, and make investments 
- Uses PRAW for scraping reddit comments into a PostgreSQL database, with VADER applied for sentiment scoring of stock
- Utilized IBKR's API to make automated daily trades based on levered sentiment scores and individual historical ticker prices 


## Requirements

- Python 3.7+ would be needed
- PostgreSQL database would need to be setup locally
- Reddit API credentials, can be set up here https://old.reddit.com/prefs/apps
- Interactive Brokers account and TWS/Gateway credentials, IKBR account needed to run. https://www.interactivebrokers.ca/en/home.php

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reddit-stock-sentiment.git
cd reddit-stock-sentiment
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your credentials:
```bash
# Reddit API Credentials
redditId=your_reddit_client_id
redditSecret=your_reddit_client_secret
redditAgent=BUFFET by MikeMazzetti

# PostgreSQL Database Credentials
dbName=buffet_db
dbUser=your_db_username
dbPass=your_db_password
dbHost=localhost
dbPort=5432

# Interactive Brokers (IBKR) Credentials
ibHost=127.0.0.1
ibPort=7497  # 7497 for paper trading, 7496 for live
ibId=1
```

4. Set up PostgreSQL database locally.

Note: The `.env` file is ignored by Git for security. Never commit your actual credentials to version control.

## Environment Variables Explained

- Reddit Credentials:
  - `redditId`: Your Reddit API client ID from https://old.reddit.com/prefs/apps
  - `redditSecret`: Your Reddit API client secret
  - `redditAgent`: User agent string for Reddit API

- PostgreSQL Credentials:
  - `dbName`: Database name (default: buffet_db)
  - `dbUser`: Your PostgreSQL username
  - `dbPass`: Your PostgreSQL password
  - `dbHost`: Database host (default: localhost)
  - `dbPort`: Database port (default: 5432)

- IBKR Credentials:
  - `ibHost`: IBKR TWS/Gateway host (default: 127.0.0.1)
  - `ibPort`: IBKR port (7497 for paper trading, 7496 for live)
  - `ibId`: IBKR client ID (default: 1)

## Usage

Run the program:
```bash
python main.py
```


## Safety Features

- Trading is disabled by default, only simulated.
- Set execute_trades_flag = True in main.py to enable real trading
- I would highly recommended to test with a paper trading account first if used, I am not responsible for money lost.

## License

MIT License 
