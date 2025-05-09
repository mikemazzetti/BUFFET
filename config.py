from dotenv import load_dotenv
import os

load_dotenv()

redditClientId = os.getenv('redditId')
redditClientSecret = os.getenv('redditSecret')
redditUserAgent = os.getenv('redditAgent')

dbName = os.getenv('dbName')
dbUser = os.getenv('dbUser')
dbPassword = os.getenv('dbPass')
dbHost = os.getenv('dbHost')
dbPort = os.getenv('dbPort')

ibkrHost = os.getenv('ibHost')
ibkrPort = int(os.getenv('ibPort'))
ibkrClientId = int(os.getenv('ibId'))

# PRAW PARAMETERS
targetSubreddits = ['wallstreetbets']  # subreddits
targetUsers = ['INSERT_USER']  # to track user posts
stockKeywords = ['AAPL', 'TSLA', 'GME', 'AMC']  # Tickers looking for, add your own
maxCommentsPerFetch = 100  # Number of comments scraped per search
tradeRiskPerStock = 0.001
# add own additional parameters if wanted