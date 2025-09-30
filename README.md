
Realtime EnvHealth - Deploy Package v2
=====================================
Folders:
- frontend/ : Vite + React + Tailwind app (ready for Vercel). Set REACT_APP_API_URL to backend URL.
- server/   : FastAPI backend (reads synthetic CSVs from proposal_prototype). Also includes ingest_openaq.py for local data fetch.
- proposal_prototype/ : place your synthetic or real CSVs here: synthetic_daily.csv, forecast_results.csv

How to deploy frontend on Vercel:
1. Push repo to GitHub.
2. In Vercel, create new project -> Import Git Repository -> select frontend folder.
3. Build command: npm run build ; Output directory: dist
4. Add Environment Variable REACT_APP_API_URL pointing to backend URL.
5. Deploy.

How to run backend locally:
1. cd server && python -m venv venv && source venv/bin/activate
2. pip install -r requirements.txt
3. Ensure proposal_prototype/synthetic_daily.csv exists one level up (create folder and copy files)
4. uvicorn fastapi_main:app --reload --port 8000

How to fetch OpenAQ data locally:
python server/ingest_openaq.py --city "Jaipur" --out proposal_prototype/openaq_jaipur.csv

