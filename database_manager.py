import psycopg2
from psycopg2 import sql
import config

def get_db_connection():
    # Establishes connection to PostgreSQL database. 
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def initialize_db():
    # Creates tables if they don't already exist.
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reddit_comments (
                    id VARCHAR(10) PRIMARY KEY,
                    subreddit VARCHAR(255) NOT NULL,
                    author VARCHAR(255),
                    body TEXT NOT NULL,
                    created_utc TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    permalink VARCHAR(512),
                    stock_symbols VARCHAR(255), -- Comma-separated symbols mentioned
                    sentiment_score FLOAT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            print("Database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def insert_comment(comment_data):
    # Inserts single comment into reddit_comments table.
    conn = get_db_connection()
    if not conn:
        return False

    sql_query = """
        INSERT INTO reddit_comments (id, subreddit, author, body, created_utc, permalink, stock_symbols)
        VALUES (%s, %s, %s, %s, TO_TIMESTAMP(%s), %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """ # Avoid duplicate entries if script reruns
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query, (
                comment_data['id'],
                comment_data['subreddit'],
                comment_data['author'],
                comment_data['body'],
                comment_data['created_utc'],
                comment_data['permalink'],
                ','.join(comment_data.get('stock_symbols', [])) # Store as CSV
            ))
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error inserting comment {comment_data.get('id', '')}: {e}")
        conn.rollback() # Rollback in case of error
        return False
    finally:
        if conn:
            conn.close()

def get_comments_for_sentiment_analysis(limit=100):
    # Retrieves comments that haven't had sentiment analysis.
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, body FROM reddit_comments
                WHERE sentiment_score IS NULL
                ORDER BY created_utc DESC
                LIMIT %s;
            """, (limit,))
            comments = cur.fetchall()
            return comments # Returns (id, body) list
    except psycopg2.Error as e:
        print(f"Error fetching comments for sentiment analysis: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_comment_sentiment(comment_id, sentiment_score):
    # Updates sentiment score for a given comment.
    conn = get_db_connection()
    if not conn:
        return False
    sql_query = """
        UPDATE reddit_comments
        SET sentiment_score = %s, processed_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query, (sentiment_score, comment_id))
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error updating sentiment for comment {comment_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_recent_sentiments_for_stock(stock_symbol, hours_ago=24):
    # Retrieves recent sentiment scores for specific stock.
    # Assumes stock_symbols column contains comma-separated symbols.
    
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            # Query looks for stock symbol within string
            query = sql.SQL("""
                SELECT sentiment_score FROM reddit_comments
                WHERE stock_symbols LIKE %s
                  AND sentiment_score IS NOT NULL
                  AND created_utc >= NOW() - INTERVAL '%s hours'
                ORDER BY created_utc DESC;
            """)


            pattern = f"%{stock_symbol}%"
            cur.execute(query, (pattern, hours_ago))
            sentiments = [item[0] for item in cur.fetchall()]
            return sentiments
    except psycopg2.Error as e:
        print(f"Error fetching recent sentiments for {stock_symbol}: {e}")
        return []
    finally:
        if conn:
            conn.close()

