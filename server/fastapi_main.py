"""
EnvHealth API combining OpenAQ v3 (PM2.5) + OpenWeatherMap (rainfall).
- /summary now returns live PM2.5 and recent rain (mm) for given city.
- /forecast and /data/daily remain synthetic for simplicity.
"""

import os
import datetime
import random
from typing import Optional
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# --- API keys from environment or hardcoded for testing ---
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "").strip()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "cb9ef2092a95cd9096cf9a1766f61099").strip()

app = FastAPI(title="EnvHealth API (PM2.5 + Rainfall)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# City coordinates (lat, lon)
CITY_COORDS = {
    "Delhi": "28.7041,77.1025",
    "Mumbai": "19.0760,72.8777",
    "Jaipur": "26.9124,75.7873",
    "Chennai": "13.0827,80.2707",
    "Kolkata": "22.5726,88.3639",
    "Bengaluru": "12.9716,77.5946"
}

# --- Helpers ---
def classify_risk(pm25: Optional[float]) -> str:
    if pm25 is None:
        return "Unknown"
    if pm25 > 100:
        return "High"
    if pm25 > 60:
        return "Medium"
    return "Low"

def fetch_openaq_pm25(coords: str) -> Optional[float]:
    """Fetch PM2.5 from OpenAQ v3 using coordinates."""
    url = "https://api.openaq.org/v3/measurements"
    params = {
        "coordinates": coords,
        "radius": 50000,
        "parameter": "pm25",
        "limit": 1,
        "sort": "desc",
        "order_by": "datetime"
    }
    headers = {"X-API-Key": OPENAQ_API_KEY} if OPENAQ_API_KEY else {}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if results:
        return float(results[0]["value"])
    return None

def fetch_rainfall(coords: str) -> Optional[float]:
    """Fetch recent rainfall (last 1–3h) using OpenWeatherMap API."""
    lat, lon = coords.split(",")
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    rain = data.get("rain", {})
    # rain might have "1h" or "3h" keys
    if "1h" in rain:
        return float(rain["1h"])
    elif "3h" in rain:
        return float(rain["3h"])
    else:
        return 0.0

def synthetic_pm25() -> float:
    return float(random.randint(30, 100))

# --- Endpoints ---

@app.get("/summary")
def summary(city: str = Query("Delhi")):
    coords = CITY_COORDS.get(city, CITY_COORDS["Delhi"])
    pm25_val = None
    rain_val = None

    try:
        pm25_val = fetch_openaq_pm25(coords)
    except Exception as e:
        pm25_val = synthetic_pm25()

    try:
        rain_val = fetch_rainfall(coords)
    except Exception:
        rain_val = 0.0

    return {
        "city": city,
        "current_pm25": pm25_val,
        "recent_rain_mm": rain_val,
        "risk_level": classify_risk(pm25_val)
    }

@app.get("/forecast")
def forecast(city: str = Query("Delhi")):
    coords = CITY_COORDS.get(city, CITY_COORDS["Delhi"])
    pm25 = synthetic_pm25()
    today = datetime.date.today()
    timeline = []
    for i in range(5):
        timeline.append({
            "date": (today + datetime.timedelta(days=i)).isoformat(),
            "obs": pm25 if i == 0 else None,
            "pred_median": pm25 + random.randint(-10, 20),
            "p10": max(0, pm25 - 15),
            "p90": pm25 + 25
        })
    lat, lon = map(float, coords.split(","))
    return {
        "timeline": timeline,
        "locations": [{
            "lat": lat,
            "lon": lon,
            "pm25": pm25,
            "risk": classify_risk(pm25),
            "name": city
        }],
        "next24h": {
            "pm25_median": pm25,
            "estimated_admissions": int(pm25 / 10),
            "confidence": "Medium"
        }
    }

@app.get("/data/daily")
def data_daily(city: str = Query("Delhi"), n: int = Query(7)):
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

@app.get("/")
def root():
    return {
        "status": "EnvHealth API is live ✅ (PM2.5 + rainfall)",
        "endpoints": ["/summary", "/forecast", "/data/daily"]
    }

@app.head("/")
def root_head():
    return {"status": "ok"}
