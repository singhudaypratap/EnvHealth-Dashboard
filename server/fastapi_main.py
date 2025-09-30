from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd, os, json
app = FastAPI(title="RealTime EnvHealth Prototype API")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'proposal_prototype'))
DAILY_CSV = os.path.join(BASE_DIR, 'synthetic_daily.csv')
FORECAST_CSV = os.path.join(BASE_DIR, 'forecast_results.csv')
def read_daily(city=None, n=7):
    try:
        df = pd.read_csv(DAILY_CSV, parse_dates=['date'])
    except Exception:
        return []
    if city and 'city' in df.columns:
        df = df[df['city']==city]
    df = df.sort_values('date')
    return df.tail(n).to_dict(orient='records')
def read_forecast():
    try:
        df = pd.read_csv(FORECAST_CSV, parse_dates=['date'])
    except Exception:
        return {"timeline": []}
    timeline = []
    for _, row in df.iterrows():
        timeline.append({
            'date': row['date'].date().isoformat() if not pd.isnull(row['date']) else None,
            'obs': float(row['obs_next_day_adm']),
            'pred_median': float(row['pred_median']),
            'p10': float(row['pred_p10']),
            'p90': float(row['pred_p90'])
        })
    locations = [{'lat':26.9124,'lon':75.7873,'pm25':72,'pm25_p10':60,'pm25_p90':90,'risk':'High','name':'Center'}]
    next24h = {'pm25_median':72,'pm25_p10':60,'pm25_p90':90,'estimated_admissions':int(df['pred_median'].iloc[-1]) if len(df)>0 else 0,'confidence':'High'}
    return {'timeline': timeline, 'locations': locations, 'next24h': next24h}
@app.get('/summary')
def summary(city: str = Query('DemoCity')):
    rows = read_daily(city=city, n=1)
    if rows:
        last = rows[-1]
        return {'city': city, 'current_pm25': round(float(last.get('avg_pm25', 0)),1), 'recent_rain_mm': round(float(last.get('daily_rain_mm',0)),1), 'risk_level': 'Medium'}
    return {'city': city, 'current_pm25': None, 'recent_rain_mm': None, 'risk_level': 'Unknown'}
@app.get('/forecast')
def forecast(city: str = Query('DemoCity')):
    return read_forecast()
@app.get('/data/daily')
def data_daily(city: str = Query(None), n: int = Query(30)):
    return read_daily(city=city, n=n)
