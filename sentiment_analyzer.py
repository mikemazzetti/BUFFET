from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database_manager import getCommentsForSentiment, updateSentiment

def analyzeSent(text):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text)
    return vs['compound']

def processComments(batchSize=100):
    print("Fetching comments...")
    comments = getCommentsForSentiment(limit=batchSize)

    if not comments:
        print("No comments to analyze sentiment.")
        return

    print(f"Found {len(comments)} comments.")
    analyzed = 0
    for comId, comText in comments:
        try:
            sent = analyzeSent(comText)
            if updateSentiment(comId, sent):
                analyzed += 1
            else:
                print(f"Failed to update comment {comId}")
        except Exception as e:
            print(f"Error analyzing comment sentiment for{comId}: {e}")
    print(f"Sentiment Analysis complete: {analyzed} comments")