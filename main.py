# main.py
import config
import reddit_scraper
import sentiment_analyzer
import trading_logic
import database_manager
import ibkr_trader
import time

def daily_trading_routine():
    print("------------------------------------")
    print(f"Starting daily trading routine at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------")

    # 1. Initialize Database
    print("\n[PHASE 1: Initializing Database]")
    database_manager.initialize_db()
    print("Database check/initialization complete.")

    # 2. Scrape Reddit
    print("\n[PHASE 2: Scraping Reddit Comments]")
    reddit_instance = reddit_scraper.get_reddit_instance()
    if reddit_instance:
        reddit_scraper.scrape_subreddits(
            reddit_instance,
            config.TARGET_SUBREDDITS,
            config.STOCK_KEYWORDS,
            limit_per_subreddit=config.MAX_COMMENTS_PER_FETCH // len(config.TARGET_SUBREDDITS) if config.TARGET_SUBREDDITS else config.MAX_COMMENTS_PER_FETCH
        )
        print("Reddit scraping complete.")
    else:
        print("Failed to initialize Reddit instance. Skipping scraping.")

    # 3. Perform Sentiment Analysis 
    print("\n[PHASE 3: Performing Sentiment Analysis]")
    sentiment_analyzer.process_comments_for_sentiment(batch_size=200)
    print("Sentiment analysis complete.")

    # 4. Make Trading Decisions 
    print("\n[PHASE 4: Making Trading Decisions]")
    trades_to_consider = trading_logic.decide_trades(config.STOCK_KEYWORDS)
    if trades_to_consider:
        print("\nTrades to Consider:")
        for trade in trades_to_consider:
            print(f"  {trade['action']} {trade['symbol']} (Qty: {trade['quantity']}) - Reason: {trade['reason']}")
    else:
        print("No specific trading actions decided.")

    # 5. Execute Trades via IBKR
    print("\n[PHASE 5: Executing Trades via IBKR]")
    execute_trades_flag = False  # Set to True to enable actual trading
    
    if execute_trades_flag:
        actionable_trades = [t for t in trades_to_consider if t['action'] != 'HOLD' and t['quantity'] > 0]
        if actionable_trades:
            print("Attempting to execute trades...")
            ibkr_trader.execute_trades_ibkr(actionable_trades)
            print("Trade execution phase complete.")
        else:
            print("No actionable trades to execute.")
    else:
        print("Trade execution is DISABLED. To enable, set 'execute_trades_flag = True'")

    print("------------------------------------")
    print(f"Daily trading routine finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------")


if __name__ == "__main__":
    # Run the routine once
    daily_trading_routine()

    # To run continuously every day, uncomment these lines:
    # import schedule
    # schedule.every().day.at("09:30").do(daily_trading_routine)  # Run at market open
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
