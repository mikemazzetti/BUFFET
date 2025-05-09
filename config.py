redditClientId = "INSERT_REDDIT_CLIENT_ID"
redditClientSecret = "INSERT_REDDIT_SECRET"
redditUserAgent = "BuffetTrader_v0.1 by MikeMazzetti" # Reddit API guidelines

dbName = "buffet_db"
dbUser = "your_db_user"
dbPassword = "your_db_password"
dbHost = "localhost" # DB host
dbPort = "5432"      # Default port

ibkrHost = '127.0.0.1' # default localhost
ibkrPort = 7497        # 7497 for TWS Paper Trading, 7496 for TWS Live
ibkrClientId = 1      # Insert IKBR client ID

# TRADING PARAMETERS 
targetSubreddits = ['wallstreetbets'] # subreddits
targetUsers = ['INSERT_USER'] # to track user posts
stockKeywords = ['AAPL', 'TSLA', 'GME', 'AMC'] # Tickers looking for, add your own
maxCommentsPerFetch = 100 # Number of comments scraped per search
tradeRiskPerStock = 0.001 # % of total account invested per trade
# add own additional parameters if wanted