from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Reddit API Credentials
redditClientId = os.getenv('redditId')
redditClientSecret = os.getenv('redditSecret')
redditUserAgent = os.getenv('redditAgent', 'BuffetTrader_v0.1 by MikeMazzetti')

# PostgreSQL Database Credentials
dbName = os.getenv('dbName', 'buffet_db')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPass')
dbHost = os.getenv('dbHost', 'localhost')
dbPort = os.getenv('dbPort', '5432')

# Interactive Brokers (IBKR) Credentials
ibkrHost = os.getenv('ibHost', '127.0.0.1')
ibkrPort = int(os.getenv('ibPort', '7497'))
ibkrClientId = int(os.getenv('ibId', '1'))

# TRADING PARAMETERS 
targetSubreddits = ['wallstreetbets']  # subreddits
targetUsers = ['INSERT_USER']  # to track user posts
stockKeywords = ['AAPL', 'TSLA', 'GME', 'AMC']  # Tickers looking for, add your own
maxCommentsPerFetch = 100  # Number of comments scraped per search
tradeRiskPerStock = 0.001
# add own additional parameters if wanted