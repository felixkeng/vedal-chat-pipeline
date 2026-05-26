import asyncio
import websockets
import re
from datetime import datetime
import mysql.connector
from config import DB_CONFIG, TWITCH_IRC_URI, TWITCH_NICK, TWITCH_TOKEN, TWITCH_CHANNEL

# ─────────────────────────────────────────
# TWITCH CHAT COLLECTOR
#
# Twitch chat is IRC over WebSocket.
# IRC is a protocol from 1988 — older than the web itself.
# Twitch wraps it in WebSocket so browsers can connect.
#
# Anonymous connection flow:
# 1. Connect to wss://irc-ws.chat.twitch.tv:443
# 2. Send PASS and NICK (anonymous credentials)
# 3. Request tags capability (gives us subscriber/mod info)
# 4. JOIN the channel
# 5. Listen for PRIVMSG (chat messages)
# ─────────────────────────────────────────

# Regex to parse a raw IRC message
# Example raw line:
# @badges=subscriber/0;mod=0 :username!username@username.tmi.twitch.tv PRIVMSG #vedal987 :hello chat
IRC_RE = re.compile(
    r"^(?:@(?P<tags>[^ ]*) )?:(?P<user>[^!]+)![^ ]+ PRIVMSG #\S+ :(?P<message>.+)$"
)

def parse_tags(raw_tags: str) -> dict:
    """Parse IRC tags into a dict. Tags look like: badge=sub/0;mod=1;color=#FF0000"""
    result = {}
    for part in raw_tags.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k] = v
    return result

def insert_message(username: str, message: str, is_sub: bool, is_mod: bool):
    """Store one chat message in the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chat_messages (username, message, is_subscriber, is_moderator, channel)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, message, is_sub, is_mod, TWITCH_CHANNEL))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Insert error: {e}")

async def collect():
    print(f"[Collector] Connecting to Twitch IRC...")
    print(f"[Collector] Channel: #{TWITCH_CHANNEL}")
    print(f"[Collector] Anonymous mode — no account needed")
    print()

    while True:
        try:
            async with websockets.connect(TWITCH_IRC_URI) as ws:
                # ── Handshake ─────────────────────────────
                await ws.send(f"PASS {TWITCH_TOKEN}")
                await ws.send(f"NICK {TWITCH_NICK}")
                # Request tags so we get subscriber/mod info
                await ws.send("CAP REQ :twitch.tv/tags")
                await ws.send(f"JOIN #{TWITCH_CHANNEL}")

                print(f"[Collector] Joined #{TWITCH_CHANNEL} — listening for messages...")

                msg_count = 0

                async for raw in ws:
                    # ── Keep-alive ────────────────────────
                    # Twitch sends PING every 5 minutes
                    # Must respond with PONG or get disconnected
                    if raw.startswith("PING"):
                        await ws.send("PONG :tmi.twitch.tv")
                        print("[Collector] PING ↔ PONG")
                        continue

                    # ── Parse message ─────────────────────
                    for line in raw.strip().split("\r\n"):
                        match = IRC_RE.match(line)
                        if not match:
                            continue

                        tags_raw = match.group("tags") or ""
                        username = match.group("user")
                        message  = match.group("message")
                        tags     = parse_tags(tags_raw)

                        is_sub = tags.get("subscriber", "0") == "1"
                        is_mod = tags.get("mod", "0") == "1"

                        # Store in DB
                        insert_message(username, message, is_sub, is_mod)

                        msg_count += 1
                        # Print every message to terminal so you can see it working
                        sub_tag = "[SUB]" if is_sub else ""
                        mod_tag = "[MOD]" if is_mod else ""
                        print(f"[{msg_count}] {sub_tag}{mod_tag} {username}: {message}")

        except Exception as e:
            print(f"[Collector] Connection error: {e}")
            print("[Collector] Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(collect())