'use client'

import { OfficerState, RiskLevel } from '@/lib/types'
import { 
  User, 
  Heart, 
  Activity, 
  MapPin, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Battery,
  Wifi
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface OfficerListProps {
  officers: OfficerState[]
  selectedOfficer: OfficerState | null
  onOfficerSelect: (officer: OfficerState) => void
  onSubscribe: (officerId: string) => void
  onUnsubscribe: (officerId: string) => void
}

export default function OfficerList({ 
  officers, 
  selectedOfficer, 
  onOfficerSelect,
  onSubscribe,
  onUnsubscribe 
}: OfficerListProps) {
  const getRiskColor = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getRiskIcon = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'high': return <AlertTriangle className="h-4 w-4 text-red-600" />
      case 'medium': return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'low': return <CheckCircle className="h-4 w-4 text-green-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const formatLastSeen = (lastSeen: string) => {
    try {
      return formatDistanceToNow(new Date(lastSeen), { addSuffix: true })
    } catch {
      return 'Unknown'
    }
  }

  const getBatteryColor = (batteryLevel?: number) => {
    if (!batteryLevel) return 'text-gray-400'
    if (batteryLevel > 0.5) return 'text-green-500'
    if (batteryLevel > 0.2) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getNetworkIcon = (networkStatus?: string) => {
    switch (networkStatus) {
      case 'wifi': return <Wifi className="h-4 w-4 text-green-500" />
      case 'cellular': return <Wifi className="h-4 w-4 text-blue-500" />
      case 'offline': return <Wifi className="h-4 w-4 text-red-500" />
      default: return <Wifi className="h-4 w-4 text-gray-400" />
    }
  }

  if (officers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <User className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">No Officers Active</p>
        <p className="text-sm">Waiting for officer data...</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {officers.map((officer) => (
        <div
          key={officer.id}
          className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
            selectedOfficer?.id === officer.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          }`}
          onClick={() => onOfficerSelect(officer)}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-600" />
              <div>
                <h3 className="font-semibold text-gray-900">{officer.name}</h3>
                <p className="text-sm text-gray-600">{officer.badgeNumber}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getRiskIcon(officer.riskLevel)}
              <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(officer.riskLevel)}`}>
                {officer.riskLevel.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Department */}
          <p className="text-sm text-gray-600 mb-3">{officer.department}</p>

          {/* Status Indicators */}
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className="flex items-center space-x-1">
              <Heart className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {officer.heartRate ? `${officer.heartRate} BPM` : 'N/A'}
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <Activity className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {officer.activityType || 'Unknown'}
              </span>
            </div>
          </div>

          {/* Location */}
          {officer.latitude && officer.longitude && (
            <div className="flex items-center space-x-1 mb-3">
              <MapPin className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {officer.latitude.toFixed(4)}, {officer.longitude.toFixed(4)}
              </span>
            </div>
          )}

          {/* Alerts */}
          {officer.fallDetected && (
            <div className="flex items-center space-x-1 mb-3 text-red-600">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm font-medium">FALL DETECTED</span>
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-3">
              <span>{formatLastSeen(officer.lastSeen)}</span>
              {officer.batteryLevel && (
                <div className="flex items-center space-x-1">
                  <Battery className={`h-3 w-3 ${getBatteryColor(officer.batteryLevel)}`} />
                  <span>{Math.round(officer.batteryLevel * 100)}%</span>
                </div>
              )}
            </div>
            <div className="flex items-center space-x-1">
              {getNetworkIcon(officer.networkStatus)}
              <span>{officer.networkStatus || 'Unknown'}</span>
            </div>
          </div>

          {/* Risk Score Bar */}
          <div className="mt-2">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Risk Score</span>
              <span>{Math.round(officer.riskScore * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  officer.riskLevel === 'high' ? 'bg-red-500' :
                  officer.riskLevel === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(officer.riskScore * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
