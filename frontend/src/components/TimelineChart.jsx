import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Area } from 'recharts'
export default function TimelineChart({forecast}){
  const data = (forecast && forecast.timeline) ? forecast.timeline.map(d=>({date:d.date, obs:d.obs, pred_median:d.pred_median, p10:d.p10, p90:d.p90})) : []
  return (
    <div style={{width:'100%', height:300}}>
      <LineChart width={1000} height={300} data={data} margin={{top:5,right:30,left:20,bottom:5}}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='date' />
        <YAxis />
        <Tooltip />
        <Area type='monotone' dataKey='p90' stroke='#fcd34d' fillOpacity={0.1} />
        <Area type='monotone' dataKey='p10' stroke='#fde68a' fillOpacity={0.1} />
        <Line type='monotone' dataKey='pred_median' stroke='#1f77b4' dot={{r:2}} />
        <Line type='monotone' dataKey='obs' stroke='#ff7f0e' dot={{r:2}} />
      </LineChart>
    </div>
  )
}
