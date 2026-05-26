import os
from dotenv import load_dotenv

load_dotenv()

# ── Twitch IRC config ─────────────────────────
TWITCH_NICK     = "justinfan12345"
TWITCH_TOKEN    = "SCHMOOPIIE"
TWITCH_CHANNEL  = "vedal987"
TWITCH_IRC_URI  = "wss://irc-ws.chat.twitch.tv:443"

# ── Database config ───────────────────────────
DB_CONFIG = {
    "database": os.getenv("DB_NAME", "vedal_chat"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
}