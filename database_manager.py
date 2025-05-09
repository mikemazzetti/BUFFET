import psycopg2
from psycopg2 import sql
import config

def getDbConn():
    try:
        conn = psycopg2.connect(
            dbname=config.dbName,
            user=config.dbUser,
            password=config.dbPassword,
            host=config.dbHost,
            port=config.dbPort
        )
        return conn
    except psycopg2.Error as e:
        print(f"DB connection error: {e}")
        return None

def initDb():
    conn = getDbConn()
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
                    stock_symbols VARCHAR(255),
                    sentiment_score FLOAT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("DB initialized.")
    except psycopg2.Error as e:
        print(f"DB init error: {e}")
    finally:
        if conn:
            conn.close()

def insertComment(comData):
    conn = getDbConn()
    if not conn:
        return False

    sql = """
        INSERT INTO reddit_comments 
        (id, subreddit, author, body, created_utc, permalink, stock_symbols)
        VALUES (%s, %s, %s, %s, TO_TIMESTAMP(%s), %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                comData['id'],
                comData['subreddit'],
                comData['author'],
                comData['body'],
                comData['created_utc'],
                comData['permalink'],
                ','.join(comData.get('stock_symbols', []))
            ))
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error inserting comment {comData.get('id', '')}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def getCommentsForSentiment(limit=100):
    conn = getDbConn()
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
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching comments: {e}")
        return []
    finally:
        if conn:
            conn.close()

def updateSentiment(comId, sentScore):
    conn = getDbConn()
    if not conn:
        return False
    sql = """
        UPDATE reddit_comments
        SET sentiment_score = %s, processed_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (sentScore, comId))
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error updating sentiment for {comId}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def getRecentSentiments(sym, hrs=24):
    conn = getDbConn()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            query = sql.SQL("""
                SELECT sentiment_score FROM reddit_comments
                WHERE stock_symbols LIKE %s
                  AND sentiment_score IS NOT NULL
                  AND created_utc >= NOW() - INTERVAL '%s hours'
                ORDER BY created_utc DESC;
            """)
            pattern = f"%{sym}%"
            cur.execute(query, (pattern, hrs))
            return [item[0] for item in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Error fetching sentiments for {sym}: {e}")
        return []
    finally:
        if conn:
            conn.close()

