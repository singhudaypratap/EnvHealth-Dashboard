import React from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
export default function MapView({forecast}){
  const center=[26.9124,75.7873]
  return (
    <div className='h-96'>
      <MapContainer center={center} zoom={10} className='h-full rounded'>
        <TileLayer url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
        {forecast && forecast.locations && forecast.locations.map((loc,i)=>{
          const color = loc.risk==='High'? '#c0392b' : loc.risk==='Medium'? '#f39c12' : '#27ae60'
          const radius = Math.min(20, 5 + (loc.pm25/20))
          return (<CircleMarker key={i} center={[loc.lat, loc.lon]} radius={radius} pathOptions={{color}}>
            <Popup><div className='text-sm'><div><strong>{loc.name || 'Location'}</strong></div><div>PM2.5: {loc.pm25} µg/m³</div><div>Risk: {loc.risk}</div></div></Popup>
          </CircleMarker>)
        })}
      </MapContainer>
    </div>
  )
}
