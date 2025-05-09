# Reddit API
REDDIT_CLIENT_ID = "INSERT_REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET = "INSERT_REDDIT_CLIENT_SECRET"
REDDIT_USER_AGENT = "BuffetTrader_v0.1 by MikeMazzetti" # Follow Reddit API guidelines

# PostgreSQL Database 
DB_NAME = "buffet_db"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost" # Or DB host
DB_PORT = "5432"      # Default port

# IBKR API Settings 
IBKR_HOST = '127.0.0.1' # Typically localhost
IBKR_PORT = 7497        # 7497 for TWS Paper Trading, 7496 for TWS Live
IBKR_CLIENT_ID = 1      # Insert your own IKBR client ID

# Trading Parameters
TARGET_SUBREDDITS = ['wallstreetbets'] # Example subreddits
STOCK_KEYWORDS = ['$AAPL', '$TSLA', 'GME', 'AMC'] # Tickers looking for, add your own
MAX_COMMENTS_PER_FETCH = 100 # Number of comments fetch per search
TRADE_RISK_PER_STOCK = 0.001 # % of total account investedper trade