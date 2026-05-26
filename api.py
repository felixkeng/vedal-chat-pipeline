import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from analytics import (
    messages_per_minute, top_words, hype_score, sub_ratio, total_stats
)


app = FastAPI(title="Vedal Chat Pipeline")

# Connected dashboard WebSocket clients
dashboard_clients: list[WebSocket] = []


async def push_analytics():
    """
    Every 5 seconds, run all analytics queries and push results
    to all connected dashboard browsers via WebSocket.
    This is the same push pattern you built in protocol-wars.
    """
    while True:
        await asyncio.sleep(5)
        if not dashboard_clients:
            continue

        payload = {
            "total":   total_stats(),
            "hype":    hype_score(),
            "subs":    sub_ratio(),
            "words":   top_words(minutes_back=5, limit=15),
            "mpm":     messages_per_minute(minutes_back=15),
        }

        # Convert any non-serializable types (datetime etc)
        def clean(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)

        payload_str = json.dumps(payload, default=clean)

        dead = []
        for ws in dashboard_clients:
            try:
                await ws.send_text(payload_str)
            except Exception:
                dead.append(ws)
        for ws in dead:
            dashboard_clients.remove(ws)


@app.on_event("startup")
async def startup():
    asyncio.create_task(push_analytics())


@app.get("/")
async def dashboard():
    return FileResponse("dashboard.html")


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    dashboard_clients.append(websocket)
    try:
        # Send immediately on connect so dashboard isn't blank
        payload = {
            "total": total_stats(),
            "hype":  hype_score(),
            "subs":  sub_ratio(),
            "words": top_words(minutes_back=5, limit=15),
            "mpm":   messages_per_minute(minutes_back=15),
        }
        def clean(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)
        await websocket.send_text(json.dumps(payload, default=clean))

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_clients.remove(websocket)


if __name__ == "__main__":
    import webbrowser, threading
    def open_browser():
        import time; time.sleep(1.2)
        webbrowser.open("http://localhost:8002")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("api:app", host="0.0.0.0", port=8002, reload=False)