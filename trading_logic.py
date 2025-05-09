from database_manager import getRecentSentiments

def calcSentiment(sym, hrs=24):
    sents = getRecentSentiments(sym, hrs)
    if not sents:
        return 0.0  

    avgSent = sum(sents) / len(sents)
    print(f"Stock: {sym}, Sentiment: {avgSent:.4f}, Count: {len(sents)}")
    return avgSent

def decideTrades(stocks):
    trades = []
    for stockCfg in stocks:
        sym = stockCfg.replace('$', '').upper()

        sent = calcSentiment(sym, hrs=24)  
        print(f"Score for {sym}: {sent:.4f}")

        if sent > 0.3:  
            trades.append({
                'action': 'BUY',
                'symbol': sym,
                'quantity': 1,  
                'reason': f'Positive sentiment: {sent:.4f}'
            })
        elif sent < -0.3:  
            trades.append({
                'action': 'SELL',
                'symbol': sym,
                'quantity': 1,  
                'reason': f'Negative sentiment: {sent:.4f}'
            })
        else:
            trades.append({
                'action': 'HOLD',
                'symbol': sym,
                'quantity': 0,
                'reason': f'Neutral sentiment: {sent:.4f}'
            })
    return trades