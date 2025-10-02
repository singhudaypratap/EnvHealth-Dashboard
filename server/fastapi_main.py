from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime, random

app = FastAPI(title="RealTime EnvHealth Prototype API")

# Enable CORS so Vercel frontend can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: restrict to your Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Real-time summary using OpenAQ ---
@app.get("/summary")
def summary(city: str = Query("Delhi")):
    """
    Returns real-time PM2.5 data for a given city using OpenAQ.
    Risk level is derived from PM2.5 value.
    """
    url = "https://api.openaq.org/v2/latest"
    params = {"city": city, "parameter": "pm25", "limit": 1}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            meas = data["results"][0]["measurements"][0]
            val = meas["value"]
            return {
                "city": city,
                "current_pm25": val,
                "recent_rain_mm": 0,   # placeholder until rainfall API is integrated
                "risk_level": "High" if val > 100 else "Medium" if val > 60 else "Low"
            }
    except Exception as e:
        return {
            "city": city,
            "current_pm25": None,
            "recent_rain_mm": None,
            "risk_level": "Unknown",
            "error": str(e)
        }

    return {"city": city, "current_pm25": None,
            "recent_rain_mm": None, "risk_level": "Unknown"}


# --- Simple forecast stub using current PM2.5 ---
@app.get("/forecast")
def forecast(city: str = Query("Delhi")):
    """
    Returns a simple forecast timeline derived from today's PM2.5.
    Generates synthetic predictions for next 5 days.
    """
    url = "https://api.openaq.org/v2/latest"
    params = {"city": city, "parameter": "pm25", "limit": 1}
    val = None
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            val = data["results"][0]["measurements"][0]["value"]
    except Exception:
        pass

    today = datetime.date.today()
    timeline = []
    if val:
        for i in range(5):
            timeline.append({
                "date": (today + datetime.timedelta(days=i)).isoformat(),
                "obs": None if i > 0 else val,
                "pred_median": val + random.randint(-10, 20),
                "p10": max(0, val - 15),
                "p90": val + 25
            })

    return {
        "timeline": timeline,
        "locations": [{
            "lat": 28.6139, "lon": 77.2090,
            "pm25": val or 0,
            "risk": "High" if val and val > 100 else "Medium" if val and val > 60 else "Low",
            "name": city
        }],
        "next24h": {
            "pm25_median": val or 0,
            "estimated_admissions": int(val/10) if val else 0,
            "confidence": "Medium" if val else "Low"
        }
    }


# --- Optional: Daily data placeholder ---
@app.get("/data/daily")
def data_daily(city: str = Query("Delhi"), n: int = Query(7)):
    """
    Returns last N days of synthetic daily data.
    """
    today = datetime.date.today()
    rows = []
    for i in range(n):
        rows.append({
            "date": (today - datetime.timedelta(days=i)).isoformat(),
            "city": city,
            "avg_pm25": random.randint(30, 120),
            "daily_rain_mm": random.randint(0, 20)
        })
    return rows
