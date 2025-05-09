# BUFFET, a Reddit Scraping Machine Learning Stock Sentiment Trader

A Python program that analyzes Reddit comments for stock sentiment and suggests trading decisions and will execute trades via Interactive Brokers (IBKR).

## Features

- Scrapes Reddit comments from specified subreddits
- Analyzes sentiment using VADER sentiment analysis
- Stores data in PostgreSQL database
- Makes trading decisions based on sentiment scores
- Execute trades via Interactive Brokers (IBKR)

## Requirements

- Python 3.7+
- PostgreSQL database
- Reddit API credentials
- Interactive Brokers account and TWS/Gateway

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

3. Fill out config.py file with your credentials 

4. Set up PostgreSQL database


## Usage

Run the program:
```bash
python main.py
```


## Safety Features

- Trading is disabled by default
- Set execute_trades_flag = True in main.py to enable trading
- Recommended to test with paper trading account first

## License

MIT License - see LICENSE file for details
