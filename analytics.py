import mysql.connector
from config import DB_CONFIG, TWITCH_CHANNEL
from datetime import datetime, timedelta
from collections import Counter
import re

# Words to ignore in top words analysis
STOPWORDS = {
    "the", "a", "an", "is", "it", "in", "on", "at", "to", "and", "or",
    "of", "for", "with", "this", "that", "i", "you", "he", "she", "we",
    "they", "my", "your", "his", "her", "its", "be", "are", "was", "were",
    "have", "has", "do", "does", "did", "will", "would", "can", "could",
    "not", "no", "so", "but", "if", "as", "by", "up", "out", "about",
    "just", "like", "more", "what", "when", "who", "how", "im", "its",
    "er", "th", "st", "nd", "rd"   # bot response artifacts
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def messages_per_minute(minutes_back=10) -> list[dict]:
    """
    How many messages per minute over the last N minutes.
    Good for detecting hype spikes — sudden jumps mean something happened.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            DATE_FORMAT(received_at, '%Y-%m-%d %H:%i:00') AS minute,
            COUNT(*) AS message_count,
            COUNT(DISTINCT username) AS unique_chatters,
            SUM(is_subscriber) AS sub_count
        FROM chat_messages
        WHERE channel = %s
          AND received_at >= NOW() - INTERVAL %s MINUTE
        GROUP BY minute
        ORDER BY minute ASC
    """, (TWITCH_CHANNEL, minutes_back))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def top_words(minutes_back=5, limit=20) -> list[dict]:
    """
    Most used words in the last N minutes.
    Filters out stopwords so you see actual Neuro emotes and memes.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT message FROM chat_messages
        WHERE channel = %s
          AND received_at >= NOW() - INTERVAL %s MINUTE
    """, (TWITCH_CHANNEL, minutes_back))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    word_counts = Counter()
    for row in rows:
        words = re.findall(r"[a-zA-Z0-9_]+", row["message"].lower())
        for word in words:
            if word not in STOPWORDS and len(word) > 2:
                word_counts[word] += 1

    return [
        {"word": word, "count": count}
        for word, count in word_counts.most_common(limit)
    ]


def hype_score(minutes_back=2) -> dict:
    """
    Compare message rate right now vs the average.
    Score > 1.5 = hype. Score > 3.0 = something big happened.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Messages in last 1 minute
    cur.execute("""
        SELECT COUNT(*) as count FROM chat_messages
        WHERE channel = %s AND received_at >= NOW() - INTERVAL 1 MINUTE
    """, (TWITCH_CHANNEL,))
    recent = cur.fetchone()["count"]

    # Average messages per minute over last 10 minutes
    cur.execute("""
        SELECT COUNT(*) / 10.0 as avg_per_min FROM chat_messages
        WHERE channel = %s AND received_at >= NOW() - INTERVAL 10 MINUTE
    """, (TWITCH_CHANNEL,))
    avg = cur.fetchone()["avg_per_min"] or 1

    cur.close()
    conn.close()

    score = round(recent / avg, 2) if avg > 0 else 0
    return {
        "recent_msgs": recent,
        "avg_per_min": round(float(avg), 2),
        "hype_score": score,
        "status": "🔥 HYPE" if score > 2 else ("📈 Active" if score > 1.2 else "😴 Quiet")
    }


def sub_ratio(minutes_back=10) -> dict:
    """What % of chatters are subscribers right now."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(is_subscriber) as subs
        FROM chat_messages
        WHERE channel = %s
          AND received_at >= NOW() - INTERVAL %s MINUTE
    """, (TWITCH_CHANNEL, minutes_back))
    row = cur.fetchone()
    cur.close()
    conn.close()

    total = row["total"] or 1
    subs  = int(row["subs"] or 0)
    return {
        "total_messages": total,
        "sub_messages": subs,
        "sub_ratio": round(subs / total * 100, 1)
    }


def total_stats() -> dict:
    """Overall stats since collector started."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            COUNT(*) as total_messages,
            COUNT(DISTINCT username) as unique_chatters,
            MIN(received_at) as since,
            MAX(received_at) as last_message
        FROM chat_messages
        WHERE channel = %s
    """, (TWITCH_CHANNEL,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


if __name__ == "__main__":
    print("=== VEDAL CHAT ANALYTICS ===\n")

    print("── Total Stats ──────────────")
    stats = total_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n── Hype Score ───────────────")
    hype = hype_score()
    for k, v in hype.items():
        print(f"  {k}: {v}")

    print("\n── Sub Ratio ────────────────")
    subs = sub_ratio()
    for k, v in subs.items():
        print(f"  {k}: {v}")

    print("\n── Top Words (last 5 min) ───")
    words = top_words(minutes_back=5, limit=10)
    for w in words:
        print(f"  {w['word']:<20} {w['count']}")

    print("\n── Messages Per Minute ──────")
    mpm = messages_per_minute(minutes_back=10)
    for row in mpm:
        bar = "█" * min(row["message_count"], 40)
        print(f"  {row['minute']}  {bar} {row['message_count']}")