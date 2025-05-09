import config
import reddit_scraper
import sentiment_analyzer
import trading_logic
import database_manager
import ibkr_trader
import time

def dailyRoutine():
    print(f"Starting daily routine at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n[PHASE 1: Initializing Database]")
    database_manager.initDb()
    print("Database check complete.")

    print("\n[PHASE 2: Scraping Reddit]")
    redditInst = reddit_scraper.getReddit()
    if redditInst:
        reddit_scraper.scrapeReddit(
            redditInst,
            config.targetSubreddits,
            config.stockKeywords,
            limit=config.maxCommentsPerFetch // len(config.targetSubreddits) if config.targetSubreddits else config.maxCommentsPerFetch
        )
        print("Reddit scraping complete.")
    else:
        print("Failed to initialize Reddit. Skipping scraping.")

    print("\n[PHASE 3: Sentiment Analysis]")
    sentiment_analyzer.processComments(batchSize=200)
    print("Sentiment analysis complete.")

    print("\n[PHASE 4: Trading Decisions]")
    trades = trading_logic.decideTrades(config.stockKeywords)
    if trades:
        print("\nTrades to Consider:")
        for trade in trades:
            print(f"  {trade['action']} {trade['symbol']} (Qty: {trade['quantity']}) - {trade['reason']}")
    else:
        print("No trading actions decided.")

    print("\n[PHASE 5: IBKR Trading]")
    execTrades = False
    
    if execTrades:
        actTrades = [t for t in trades if t['action'] != 'HOLD' and t['quantity'] > 0]
        if actTrades:
            print("Executing trades...")
            ibkr_trader.executeTradesIbkr(actTrades)
            print("Trade execution complete.")
        else:
            print("No trades to execute.")
    else:
        print("Trading is DISABLED. Only paper trades active.Set execTrades = True to enable")

    print(f"Daily routine finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    dailyRoutine()

   
