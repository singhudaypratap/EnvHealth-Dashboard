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

# Dictionary of city coordinates (lat,lon)
CITY_COORDS = {
    "Delhi": "28.7041,77.1025",
    "Mumbai": "19.0760,72.8777",
    "Jaipur": "26.9124,75.7873",
    "Chennai": "13.0827,80.2707",
    "Kolkata": "22.5726,88.3639",
    "Bengaluru": "12.9716,77.5946"
}

# --- Real-time summary using OpenAQ ---
@app.get("/summary")
def summary(city: str = Query("Delhi")):
    """
    Returns real-time PM2.5 data for a given city using OpenAQ (measurements API).
    """
    coords = CITY_COORDS.get(city, CITY_COORDS["Delhi"])  # default to Delhi
    url = "https://api.openaq.org/v2/measurements"
    params = {
        "coordinates": coords,
        "radius": 50000,
        "parameter": "pm25",
        "limit": 1,
        "sort": "desc",
        "order_by": "datetime"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            meas = data["results"][0]
            val = meas["value"]
            return {
                "city": city,
                "current_pm25": val,
                "recent_rain_mm": 0,   # rainfall integration later
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
    coords = CITY_COORDS.get(city, CITY_COORDS["Delhi"])
    url = "https://api.openaq.org/v2/measurements"
    params = {
        "coordinates": coords,
        "radius": 50000,
        "parameter": "pm25",
        "limit": 1,
        "sort": "desc",
        "order_by": "datetime"
    }

    val = None
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            val = data["results"][0]["value"]
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
            "lat": float(coords.split(",")[0]),
            "lon": float(coords.split(",")[1]),
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
    Returns last N days of synthetic daily data (placeholder).
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


# --- Root route for status (handles GET & HEAD) ---
@app.get("/")
def root():
    return {
        "status": "EnvHealth API is live ✅",
        "endpoints": ["/summary", "/forecast", "/data/daily"]
    }

@app.head("/")
def root_head():
    return {"status": "ok"}
