import praw
import config
import re
from database_manager import insert_comment

def getReddit():
    try:
        reddit = praw.Reddit(
            client_id=config.redditClientId,
            client_secret=config.redditClientSecret,
            user_agent=config.redditUserAgent
        )
        print(f"Reddit ready. Read-only: {reddit.read_only}")
        return reddit
    except Exception as e:
        print(f"Reddit initialization error: {e}")
        return None

def getSymbols(text):
    syms = set(re.findall(r"(?:^|\s)(\$[A-Z]{1,5}\b|[A-Z]{2,5}\b)(?=\s|,|\.|$)", text))
    return [s.replace('$', '').upper() for s in syms if s.upper() in config.stockKeywords or s.replace('$', '').upper() in config.stockKeywords]

def scrapeReddit(reddit, subs, keys, limit=100):
    if not reddit:
        print("No Reddit instance.")
        return

    count = 0
    for sub in subs:
        try:
            print(f"Scraping r/{sub}")
            subreddit = reddit.subreddit(sub)
            for com in subreddit.comments(limit=limit + 50):
                body = com.body.lower()
                syms = getSymbols(com.body)

                if any(k.lower().replace('$', '') in body for k in keys) or syms:
                    data = {
                        'id': com.id,
                        'subreddit': sub,
                        'author': com.author.name if com.author else '[deleted]',
                        'body': com.body,
                        'created_utc': com.created_utc,
                        'permalink': f"https://reddit.com{com.permalink}",
                        'stock_symbols': syms
                    }
                    if insert_comment(data):
                        count += 1
                    if count >= limit: 
                        break
            print(f"Done r/{sub}. Found {count} comments.")
        except praw.exceptions.PRAWException as e:
            print(f"PRAW error in r/{sub}: {e}")
        except Exception as e:
            print(f"Error in r/{sub}: {e}")
    print(f"Total comments found: {count}")

def filterStockSymbols(syms):
    return [s.replace('$', '').upper() for s in syms if s.upper() in config.stockKeywords or s.replace('$', '').upper() in config.stockKeywords]