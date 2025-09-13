'use client'

import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Icon, LatLngTuple } from 'leaflet'
import { OfficerState, RiskLevel } from '@/lib/types'
import { useEffect } from 'react'

// Fix for default markers in react-leaflet
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Create custom icons for different risk levels
const createRiskIcon = (riskLevel: RiskLevel) => {
  const colors = {
    low: '#22c55e',
    medium: '#f59e0b', 
    high: '#ef4444'
  }
  
  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="${colors[riskLevel]}" stroke="white" stroke-width="2"/>
        <circle cx="12" cy="12" r="4" fill="white"/>
      </svg>
    `)}`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12]
  })
}

interface MapViewProps {
  officers: OfficerState[]
  selectedOfficer: OfficerState | null
  onOfficerSelect: (officer: OfficerState) => void
}

export default function MapView({ officers, selectedOfficer, onOfficerSelect }: MapViewProps) {
  const defaultCenter: LatLngTuple = [
    parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || '40.7128'),
    parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LNG || '-74.0060')
  ]
  const defaultZoom = parseInt(process.env.NEXT_PUBLIC_DEFAULT_ZOOM || '12')

  // Filter officers with valid location data
  const officersWithLocation = officers.filter(officer => 
    officer.latitude && officer.longitude
  )

  return (
    <MapContainer
      center={defaultCenter}
      zoom={defaultZoom}
      style={{ height: '100%', width: '100%' }}
      className="rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {officersWithLocation.map((officer) => (
        <Marker
          key={officer.id}
          position={[officer.latitude!, officer.longitude!]}
          icon={createRiskIcon(officer.riskLevel)}
          eventHandlers={{
            click: () => onOfficerSelect(officer)
          }}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-semibold text-gray-900">{officer.name}</h3>
              <p className="text-sm text-gray-600">Badge: {officer.badgeNumber}</p>
              <p className="text-sm text-gray-600">Department: {officer.department}</p>
              <div className="mt-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium risk-${officer.riskLevel}`}>
                  {officer.riskLevel.toUpperCase()} RISK
                </span>
              </div>
              {officer.heartRate && (
                <p className="text-sm text-gray-600 mt-1">
                  Heart Rate: {officer.heartRate} BPM
                </p>
              )}
              {officer.activityType && (
                <p className="text-sm text-gray-600">
                  Activity: {officer.activityType}
                </p>
              )}
              {officer.fallDetected && (
                <p className="text-sm text-red-600 font-medium">
                  ⚠️ FALL DETECTED
                </p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
      
      {/* Center map on selected officer */}
      {selectedOfficer && selectedOfficer.latitude && selectedOfficer.longitude && (
        <CenterMapOnOfficer 
          position={[selectedOfficer.latitude, selectedOfficer.longitude]} 
        />
      )}
    </MapContainer>
  )
}

// Component to center map on selected officer
function CenterMapOnOfficer({ position }: { position: LatLngTuple }) {
  const map = useMap()
  
  useEffect(() => {
    map.setView(position, map.getZoom())
  }, [map, position])
  
  return null
}
