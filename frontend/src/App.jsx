import React, { useEffect, useState } from 'react'
import axios from 'axios'
import MapView from './components/MapView'
import TimelineChart from './components/TimelineChart'

const API = process.env.REACT_APP_API_URL || ''

export default function App(){
  const [summary,setSummary] = useState(null)
  const [forecast,setForecast] = useState(null)
  const [loading,setLoading] = useState(true)
  useEffect(()=>{ async function load(){ setLoading(true); try{ const s = await axios.get(`${API}/summary`); setSummary(s.data); const f = await axios.get(`${API}/forecast`); setForecast(f.data);}catch(e){console.error(e)}finally{setLoading(false)}} load() },[])
  return (
    <div className='min-h-screen bg-gray-50'>
      <header className='bg-white shadow-sm'>
        <div className='max-w-6xl mx-auto py-4 px-6 flex items-center justify-between'>
          <h1 className='text-xl font-semibold text-sky-700'>Real-Time Environmental → Health Dashboard</h1>
          <div className='text-sm text-gray-600'>Demo</div>
        </div>
      </header>
      <main className='max-w-6xl mx-auto p-6 grid grid-cols-3 gap-6'>
        <section className='col-span-2 bg-white rounded shadow p-4'>
          <MapView forecast={forecast} />
        </section>
        <aside className='col-span-1 space-y-4'>
          <div className='bg-white rounded shadow p-4'>
            <h2 className='font-semibold'>Quick Summary</h2>
            {loading && <p className='text-sm text-gray-500'>Loading...</p>}
            {summary && (<div className='mt-2 text-sm text-gray-700'>
              <p><strong>PM2.5 (24h):</strong> {summary.current_pm25} µg/m³</p>
              <p><strong>Rain (24h):</strong> {summary.recent_rain_mm} mm</p>
              <p><strong>Forecast risk:</strong> {summary.risk_level}</p>
            </div>)}
          </div>
          <div className='bg-white rounded shadow p-4 text-sm text-gray-600'>
            <h3 className='font-semibold'>Actions</h3>
            <ul className='mt-2 list-disc ml-6'>
              <li>Pre-alert hospitals if admissions expected to rise &gt;10%</li>
              <li>Issue public advisory when PM2.5 &gt; 100 µg/m³</li>
              <li>Mobilize municipal pumps for flooded wards</li>
            </ul>
          </div>
        </aside>
        <section className='col-span-3 bg-white rounded shadow p-4'>
          <h2 className='font-semibold mb-2'>Forecast Timeline</h2>
          <TimelineChart forecast={forecast} />
        </section>
      </main>
      <footer className='max-w-6xl mx-auto p-6 text-sm text-gray-500'>Demo. Set REACT_APP_API_URL to point to backend.</footer>
    </div>
  )
}
