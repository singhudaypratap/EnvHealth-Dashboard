
"""
ingest_openaq.py
Fetch hourly PM2.5 from OpenAQ for a given city or bounding box and save to CSV.
Requires: requests, pandas
Usage: python ingest_openaq.py --city "Jaipur" --out /path/to/proposal_prototype/openaq_hourly.csv
"""
import requests, pandas as pd, argparse, time
API_BASE = "https://api.openaq.org/v2/measurements"
def fetch_city(city, limit=10000):
    params = {"city": city, "parameter": "pm25", "limit": 10000, "page":1, "offset":0, "sort":"desc"}
    rows = []
    while True:
        r = requests.get(API_BASE, params=params, timeout=30)
        r.raise_for_status()
        j = r.json()
        results = j.get("results", [])
        if not results:
            break
        rows.extend(results)
        meta = j.get("meta", {})
        # break if pagination not present; otherwise increase page
        if "found" in meta and len(rows) >= meta.get("found", len(rows)):
            break
        params["page"] = params.get("page",1) + 1
        time.sleep(1)
    df = pd.json_normalize(rows)
    if not df.empty:
        df = df[['date.utc','parameter','value','unit','location','coordinates.latitude','coordinates.longitude']]
        df = df.rename(columns={'date.utc':'utc','coordinates.latitude':'lat','coordinates.longitude':'lon'})
    return df
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    df = fetch_city(args.city)
    df.to_csv(args.out, index=False)
