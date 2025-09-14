'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { OfficerState, RiskEvent, SystemAlert } from './types'

interface UseLiveFeedReturn {
  officers: OfficerState[]
  alerts: (RiskEvent | SystemAlert)[]
  connectionStatus: 'connected'
  subscribeToOfficer: (officerId: string) => void
  unsubscribeFromOfficer: (officerId: string) => void
  sendMessage: (message: any) => void
}

// Transform API response (snake_case) to frontend format (camelCase)
function transformApiOfficerToOfficerState(apiOfficer: any): OfficerState {
  return {
    id: apiOfficer.officer_id,
    name: apiOfficer.name,
    badgeNumber: apiOfficer.badge_number,
    department: apiOfficer.department,
    isActive: apiOfficer.is_active ?? true,
    isOnDuty: apiOfficer.is_on_duty ?? true,
    riskLevel: apiOfficer.risk_level || 'low',
    riskScore: apiOfficer.risk_score || 0.0,
    lastSeen: apiOfficer.last_seen,
    
    // Health data (with defaults for missing fields)
    heartRate: apiOfficer.heart_rate,
    heartRateVariability: apiOfficer.heart_rate_variability,
    activityType: apiOfficer.activity_type,
    activityConfidence: apiOfficer.activity_confidence,
    fallDetected: apiOfficer.fall_detected || false,
    fallConfidence: apiOfficer.fall_confidence,
    workoutActive: apiOfficer.workout_active || false,
    
    // Location data
    latitude: apiOfficer.latitude,
    longitude: apiOfficer.longitude,
    accuracy: apiOfficer.accuracy,
    speed: apiOfficer.speed,
    course: apiOfficer.course,
    
    // Device info
    deviceId: apiOfficer.device_id || '',
    appVersion: apiOfficer.app_version,
    batteryLevel: apiOfficer.battery_level,
    networkStatus: apiOfficer.network_status
  }
}

export function useLiveFeed(): UseLiveFeedReturn {
  const [officers, setOfficers] = useState<OfficerState[]>([])
  const [alerts, setAlerts] = useState<(RiskEvent | SystemAlert)[]>([])
  const [connectionStatus] = useState<'connected'>('connected')

  const pollRef = useRef<NodeJS.Timeout | null>(null)

  const fetchOfficers = useCallback(async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'
    try {
      const res = await fetch(`${apiUrl}/api/officers`)
      if (!res.ok) return
      const data = await res.json()
      const normalized: OfficerState[] = (data.officers || []).map((o: any) => ({
        id: o.id,
        name: o.name,
        badgeNumber: o.badgeNumber,
        department: o.department,
        isActive: o.isActive,
        isOnDuty: o.isOnDuty,
        riskLevel: o.riskLevel,
        riskScore: o.riskScore ?? 0,
        lastSeen: o.lastSeen,
        heartRate: o.heartRate,
        activityType: o.activityType,
        fallDetected: o.fallDetected ?? false,
        latitude: o.latitude,
        longitude: o.longitude,
        accuracy: o.accuracy,
        deviceId: o.deviceId || '',
        appVersion: o.appVersion,
        batteryLevel: o.batteryLevel,
        networkStatus: o.networkStatus,
        workoutActive: false,
      }))
      setOfficers(normalized)
    } catch (e) {
      console.error('Polling error', e)
    }
  }, [])

  // Start polling on mount
  useEffect(() => {
    fetchOfficers()
    pollRef.current = setInterval(fetchOfficers, 3000)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [fetchOfficers])

  const noop = () => {}

  return {
    officers,
    alerts,
    connectionStatus,
    subscribeToOfficer: noop,
    unsubscribeFromOfficer: noop,
    sendMessage: noop,
  }
}
