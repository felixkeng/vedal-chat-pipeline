import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def setup_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            received_at     TIMESTAMP DEFAULT NOW(),
            username        TEXT NOT NULL,
            message         TEXT NOT NULL,
            is_subscriber   BOOLEAN DEFAULT FALSE,
            is_moderator    BOOLEAN DEFAULT FALSE,
            channel         TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_stats (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            window_start    TIMESTAMP NOT NULL,
            channel         VARCHAR(100) NOT NULL,
            message_count   INT DEFAULT 0,
            unique_chatters INT DEFAULT 0,
            sub_count       INT DEFAULT 0,
            avg_msg_length  FLOAT DEFAULT 0,
            UNIQUE KEY unique_window (window_start, channel)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS top_words (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            window_start    TIMESTAMP NOT NULL,
            channel         VARCHAR(100) NOT NULL,
            word            VARCHAR(255) NOT NULL,
            count           INT DEFAULT 0
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("[DB] Tables ready.")

if __name__ == "__main__":
    setup_tables()