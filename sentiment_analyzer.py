from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database_manager import get_comments_for_sentiment_analysis, update_comment_sentiment

def analyze_sentiment_vader(text):
    # Analyzes sentiment of text using VADER. Returns compound score.
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text)
    return vs['compound'] # Compound score ranges from -1 (most negative) to +1 (most positive)

def process_comments_for_sentiment(batch_size=100):
    # Fetches comments from Database, analyzes sentiment, and updates Database.

    print("Fetching comments for sentiment analysis...")
    comments_to_process = get_comments_for_sentiment_analysis(limit=batch_size)

    if not comments_to_process:
        print("No new comments to analyze.")
        return

    print(f"Found {len(comments_to_process)} comments to analyze.")
    analyzed_count = 0
    for comment_id, comment_body in comments_to_process:
        try:
            sentiment_score = analyze_sentiment_vader(comment_body)
            if update_comment_sentiment(comment_id, sentiment_score):
                analyzed_count +=1
            else:
                print(f"Failed to update sentiment for comment ID: {comment_id}")
        except Exception as e:
            print(f"Error analyzing sentiment for comment {comment_id}: {e}")
    print(f"Sentiment analysis complete for {analyzed_count} comments.")