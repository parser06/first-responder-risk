'use client'

import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Icon } from 'leaflet'
import { AlertTriangle, Users, Activity, MapPin, Wifi, WifiOff } from 'lucide-react'
import OfficerList from '@/components/OfficerList'
import AlertBanner from '@/components/AlertBanner'
import { useLiveFeed } from '@/lib/useLiveFeed'
import { OfficerState, RiskLevel } from '@/lib/types'

// Fix for Next.js and Leaflet
import 'leaflet/dist/leaflet.css'
import dynamic from 'next/dynamic'

// Dynamically import the map to avoid SSR issues
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false })

export default function Dashboard() {
  const [officers, setOfficers] = useState<OfficerState[]>([])
  const [selectedOfficer, setSelectedOfficer] = useState<OfficerState | null>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  
  const { 
    officers: liveOfficers, 
    alerts: liveAlerts, 
    connectionStatus,
    subscribeToOfficer,
    unsubscribeFromOfficer 
  } = useLiveFeed()

  useEffect(() => {
    setOfficers(liveOfficers)
    setIsConnected(connectionStatus === 'connected')
  }, [liveOfficers, connectionStatus])

  useEffect(() => {
    setAlerts(liveAlerts)
  }, [liveAlerts])

  const getRiskColor = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'high': return 'text-red-600'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  const getRiskCounts = () => {
    const counts = { high: 0, medium: 0, low: 0 }
    officers.forEach(officer => {
      counts[officer.riskLevel]++
    })
    return counts
  }

  const riskCounts = getRiskCounts()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">
                First Responder Risk Monitoring
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                {isConnected ? (
                  <Wifi className="h-5 w-5 text-green-500" />
                ) : (
                  <WifiOff className="h-5 w-5 text-red-500" />
                )}
                <span className="ml-2 text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Alerts Banner */}
      {alerts.length > 0 && (
        <div className="bg-red-50 border-b border-red-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
            {alerts.map((alert, index) => (
              <AlertBanner key={index} alert={alert} />
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Officers</p>
                <p className="text-2xl font-semibold text-gray-900">{officers.length}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 font-bold text-sm">H</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Risk</p>
                <p className="text-2xl font-semibold text-red-600">{riskCounts.high}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-bold text-sm">M</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Medium Risk</p>
                <p className="text-2xl font-semibold text-yellow-600">{riskCounts.medium}</p>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold text-sm">L</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Low Risk</p>
                <p className="text-2xl font-semibold text-green-600">{riskCounts.low}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map View */}
          <div className="lg:col-span-2">
            <div className="card h-96">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Officer Locations
                </h2>
                <div className="text-sm text-gray-500">
                  {officers.length} officers active
                </div>
              </div>
              <div className="h-80">
                <MapView 
                  officers={officers}
                  selectedOfficer={selectedOfficer}
                  onOfficerSelect={setSelectedOfficer}
                />
              </div>
            </div>
          </div>

          {/* Officer List */}
          <div className="lg:col-span-1">
            <div className="card h-96">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Officer Status
                </h2>
                <div className="text-sm text-gray-500">
                  Real-time updates
                </div>
              </div>
              <div className="h-80 overflow-y-auto">
                <OfficerList 
                  officers={officers}
                  selectedOfficer={selectedOfficer}
                  onOfficerSelect={setSelectedOfficer}
                  onSubscribe={subscribeToOfficer}
                  onUnsubscribe={unsubscribeFromOfficer}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Officer Details */}
        {selectedOfficer && (
          <div className="mt-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Officer Details: {selectedOfficer.name}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Basic Info</h4>
                  <div className="space-y-2">
                    <p><span className="font-medium">Badge:</span> {selectedOfficer.badgeNumber}</p>
                    <p><span className="font-medium">Department:</span> {selectedOfficer.department}</p>
                    <p><span className="font-medium">Status:</span> 
                      <span className={`ml-2 ${getRiskColor(selectedOfficer.riskLevel)}`}>
                        {selectedOfficer.riskLevel.toUpperCase()}
                      </span>
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Health Data</h4>
                  <div className="space-y-2">
                    <p><span className="font-medium">Heart Rate:</span> {selectedOfficer.heartRate || 'N/A'} BPM</p>
                    <p><span className="font-medium">Activity:</span> {selectedOfficer.activityType || 'Unknown'}</p>
                    <p><span className="font-medium">Fall Detected:</span> 
                      <span className={`ml-2 ${selectedOfficer.fallDetected ? 'text-red-600' : 'text-green-600'}`}>
                        {selectedOfficer.fallDetected ? 'YES' : 'NO'}
                      </span>
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Location</h4>
                  <div className="space-y-2">
                    <p><span className="font-medium">Latitude:</span> {selectedOfficer.latitude?.toFixed(6) || 'N/A'}</p>
                    <p><span className="font-medium">Longitude:</span> {selectedOfficer.longitude?.toFixed(6) || 'N/A'}</p>
                    <p><span className="font-medium">Accuracy:</span> {selectedOfficer.accuracy ? `${selectedOfficer.accuracy.toFixed(0)}m` : 'N/A'}</p>
                    <p><span className="font-medium">Last Update:</span> {selectedOfficer.lastSeen}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
