from database_manager import get_recent_sentiments_for_stock

def calculate_sentiment_score(stock_symbol, hours_ago=24):
    # Calculates sentiment score for a stock based on recent Reddit comments.

    sentiments = get_recent_sentiments_for_stock(stock_symbol, hours_ago=hours_ago)
    if not sentiments:
        return 0.0  # Neutral if no recent sentiment

    # Average of sentiment scores
    avg_sentiment = sum(sentiments) / len(sentiments)
    print(f"Stock: {stock_symbol}, Avg Sentiment: {avg_sentiment:.4f}, Num Sentiments: {len(sentiments)}")
    return avg_sentiment

def decide_trades(target_stocks):

    # Decides which trades to make based on sentiment scores.
    # Returns a list of trade actions.
    trades_to_make = []
    for stock_symbol_config in target_stocks:
        # Remove '$' if present and convert to uppercase
        stock_symbol = stock_symbol_config.replace('$', '').upper()

        sentiment_score = calculate_sentiment_score(stock_symbol, hours_ago=24)  # Analyze last 24 hours
        print(f"Calculated sentiment score for {stock_symbol}: {sentiment_score:.4f}")

        # Trading logic based on sentiment thresholds
        if sentiment_score > 0.3:  # Strong positive sentiment
            trades_to_make.append({
                'action': 'BUY',
                'symbol': stock_symbol,
                'quantity': 1,  
                'reason': f'Positive sentiment: {sentiment_score:.4f}'
            })
        elif sentiment_score < -0.3:  # Strong negative sentiment
            trades_to_make.append({
                'action': 'SELL',
                'symbol': stock_symbol,
                'quantity': 1,  
                'reason': f'Negative sentiment: {sentiment_score:.4f}'
            })
        else:
            trades_to_make.append({
                'action': 'HOLD',
                'symbol': stock_symbol,
                'quantity': 0,
                'reason': f'Neutral sentiment: {sentiment_score:.4f}'
            })
    return trades_to_make