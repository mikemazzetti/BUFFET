import praw
import config
import re
from database_manager import insert_comment

def get_reddit_instance():
    # Initializes and returns a PRAW instance.
    try:
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
        print(f"PRAW Reddit instance created. Read-only: {reddit.read_only}")
        return reddit
    except Exception as e:
        print(f"Error creating PRAW Reddit instance: {e}")
        return None

def extract_stock_symbols(text):
    # Extracts stock symbols from text.
    # Simple regex for cashtags or common uppercase tickers
    symbols = set(re.findall(r"(?:^|\s)(\$[A-Z]{1,5}\b|[A-Z]{2,5}\b)(?=\s|,|\.|$)", text))
    # Remove the '$' if present, or keep it if preferred
    return [s.replace('$', '').upper() for s in symbols if s.upper() in config.STOCK_KEYWORDS or s.replace('$', '').upper() in config.STOCK_KEYWORDS]


def scrape_subreddits(reddit, subreddits, keywords, limit_per_subreddit=100):
    # Scrapes comments from specified subreddits for given keywords.
    if not reddit:
        print("Reddit instance not available.")
        return

    comments_scraped_count = 0
    for sub_name in subreddits:
        try:
            print(f"Scraping subreddit: r/{sub_name}")
            subreddit = reddit.subreddit(sub_name)
            # Iterate through new comments. Can also use submissions and their comments.
            for comment in subreddit.comments(limit=limit_per_subreddit + 50): # Fetch bit more to filter
                # Basic keyword filtering 
                comment_body_lower = comment.body.lower()
                mentioned_keywords = extract_stock_symbols(comment.body) # Extract relevant stock symbols

                if any(keyword.lower().replace('$', '') in comment_body_lower for keyword in keywords) or mentioned_keywords:
                    comment_data = {
                        'id': comment.id,
                        'subreddit': sub_name,
                        'author': comment.author.name if comment.author else '[deleted]',
                        'body': comment.body,
                        'created_utc': comment.created_utc,
                        'permalink': f"https://reddit.com{comment.permalink}",
                        'stock_symbols': mentioned_keywords
                    }
                    if insert_comment(comment_data):
                        comments_scraped_count += 1
                    if comments_scraped_count >= limit_per_subreddit: 
                        break
            print(f"Finished r/{sub_name}. Scraped {comments_scraped_count} relevant comments so far.")
        except praw.exceptions.PRAWException as e:
            print(f"PRAW error scraping r/{sub_name}: {e}")
        except Exception as e:
            print(f"General error scraping r/{sub_name}: {e}")
    print(f"Total relevant comments scraped and attempted to insert: {comments_scraped_count}")