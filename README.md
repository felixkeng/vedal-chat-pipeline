```markdown
# ⚡ Vedal Chat Pipeline

**Real-time Twitch chat analytics pipeline** for the `vedal987` Twitch channel.

Collects live chat via Twitch IRC (WebSockets), stores it in MySQL, computes real-time analytics, and streams updates to a live dashboard via FastAPI WebSockets.

---

## Features

- Live Twitch chat collector
- Real-time analytics engine
- WebSocket-powered live dashboard
- Hype spike detection
- Subscriber ratio tracking
- Top words analysis
- Messages-per-minute visualization
- Historical VOD chat downloader

---

## Tech Stack

**Backend:** Python, FastAPI, WebSockets, MySQL  
**Frontend:** Vanilla HTML/CSS/JS (live updates)  
**Data Source:** Twitch IRC WebSocket + GraphQL API

---

## Project Structure

```txt
vedal-chat-pipeline/
├── collector.py      # Live Twitch IRC collector
├── analytics.py      # Analytics + hype logic
├── api.py            # FastAPI + WebSocket server
├── database.py       # MySQL setup
├── seed.py           # Historical VOD downloader
├── config.py         # Config & DB settings
├── dashboard.html    # Real-time dashboard
├── requirements.txt
└── README.md
```

### Architecture

```
Twitch IRC
    ↓
collector.py → MySQL Database
    ↓
analytics.py → FastAPI WebSocket Server
    ↓
dashboard.html
```

---

## How It Works

### 1. Live Chat Collection
`collector.py` connects anonymously to Twitch IRC via WebSockets, joins the channel, parses messages, and stores them in MySQL.

**Stored fields:** username, message, subscriber status, moderator status, timestamp, channel.

### 2. Analytics Engine (`analytics.py`)
- **Messages Per Minute** – Tracks velocity and detects hype spikes
- **Top Words** – Most frequent words (stopwords filtered)
- **Hype Score** – `recent_messages / average_messages`
  - > 2.0 → 🔥 **HYPE**
  - > 1.2 → 📈 **Active**
  - else → 😴 **Quiet**
- **Subscriber Ratio** – Percentage of sub messages

### 3. Real-Time Dashboard
`api.py` serves a FastAPI WebSocket endpoint. Dashboard updates every 5 seconds with:
- Total messages
- Unique chatters
- Hype score & status
- Subscriber ratio
- Top words
- Messages per minute chart

---

## Database Schema

**Main tables:**

- `chat_messages` – Raw chat logs
- `chat_stats` – Aggregated stats per time window
- `top_words` – Trending words per window

---

## Installation & Setup

1. **Clone**
   ```bash
   git clone <repo-url>
   cd vedal-chat-pipeline
   ```

2. **Virtual Environment**
   ```bash
   # Windows
   python -m venv venv && venv\Scripts\activate
   # macOS/Linux
   python3 -m venv venv && source venv/bin/activate
   ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **MySQL**
   ```sql
   CREATE DATABASE vedal_chat;
   ```
   Update credentials in `config.py`, then:
   ```bash
   python database.py
   ```

---

## Running the Project

**Start collector:**
```bash
python collector.py
```

**Start dashboard:**
```bash
python api.py
```
Open: http://localhost:8002

---

## Historical Data

Run the VOD downloader:
```bash
python seed.py
```
Supports pagination, retries, duplicate prevention, and batch inserts.

---

## Example Output

```
── Hype Score ───────────────
recent_msgs: 412
avg_per_min: 180.5
hype_score: 2.28
status: 🔥 HYPE
```

---

## Future Improvements

- Sentiment analysis
- Emote tracking
- Stream event detection
- Redis caching
- Docker support
- Multi-channel support
- ML-based hype prediction
- Grafana dashboards

---

## Key Concepts Demonstrated

- WebSocket networking
- IRC protocol parsing
- Real-time data pipelines
- Async Python & FastAPI
- Live dashboard architecture

---

## Notes

- Uses anonymous Twitch login
- Automatic reconnect on disconnect
- Dashboard refreshes every 5 seconds
- Twitch IRC is a modified WebSocket protocol

---

**Author:** Real-time streaming analytics project for Twitch chat analysis  
**License:** MIT
```

This version is significantly shorter, better organized, and much easier to scan while retaining all important information.