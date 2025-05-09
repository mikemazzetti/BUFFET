# BUFFET, a Reddit Scraping Machine Learning Stock Sentiment Trader

A Python program that analyzes Reddit comments for stock sentiment and suggests trading decisions and will execute trades via Interactive Brokers (IBKR).

## Features

- Built an NLP-Powered stock trader using Python, to determine stock sentiment from Reddit, and make investments 
- Uses PRAW for scraping reddit comments into a PostgreSQL database, with VADER applied for sentiment scoring of stock
- Utilized IBKR’s API to make automated daily trades based on levered sentiment scores and individual historical ticker prices 


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

3. Fill out config.py file with your credentials, and additional parameters for reddit comment scraping.

4. Set up PostgreSQL database locally.


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
