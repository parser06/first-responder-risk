'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { OfficerState, RiskEvent, SystemAlert, WebSocketMessage } from './types'

interface UseLiveFeedReturn {
  officers: OfficerState[]
  alerts: (RiskEvent | SystemAlert)[]
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
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
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/live'
      wsRef.current = new WebSocket(wsUrl)
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setConnectionStatus('connected')
        
        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
              type: 'ping',
              timestamp: new Date().toISOString()
            }))
          }
        }, 30000) // 30 seconds
        
        // Clear any pending reconnection
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }
      
      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected')
        setConnectionStatus('disconnected')
        
        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
          heartbeatIntervalRef.current = null
        }
        
        // Attempt to reconnect after 5 seconds
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...')
            connect()
          }, 5000)
        }
      }
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }
      
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
      setConnectionStatus('error')
    }
  }, [])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'pong':
        // Heartbeat response - connection is alive
        break
        
      case 'officer_update':
        setOfficers(prev => {
          const updatedOfficers = [...prev]
          const officerIndex = updatedOfficers.findIndex(o => o.id === message.data.officer_id)
          
          if (officerIndex >= 0) {
            updatedOfficers[officerIndex] = {
              ...updatedOfficers[officerIndex],
              ...transformApiOfficerToOfficerState(message.data)
            }
          } else {
            // New officer
            updatedOfficers.push(transformApiOfficerToOfficerState(message.data))
          }
          
          return updatedOfficers
        })
        break
        
      case 'risk_event':
        setAlerts(prev => {
          const newAlert = {
            id: message.data.event_id,
            officerId: message.data.officer_id,
            eventType: message.data.event_type,
            riskLevel: message.data.risk_level,
            riskScore: message.data.risk_score || 0,
            description: message.data.description,
            occurredAt: message.timestamp,
            isAcknowledged: false,
            isResolved: false,
            location: message.data.location
          }
          
          // Add to beginning of alerts array
          return [newAlert, ...prev.slice(0, 49)] // Keep last 50 alerts
        })
        break
        
      case 'system_alert':
        setAlerts(prev => {
          const newAlert = {
            id: message.data.alert_id,
            alertType: message.data.alert_type,
            severity: message.data.severity,
            title: message.data.title,
            message: message.data.message,
            officerId: message.data.officer_id,
            isActive: true,
            isAcknowledged: false,
            createdAt: message.timestamp
          }
          
          return [newAlert, ...prev.slice(0, 49)] // Keep last 50 alerts
        })
        break
        
      default:
        console.log('Unknown message type:', message.type)
    }
  }, [])

  const subscribeToOfficer = useCallback((officerId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        officer_id: officerId
      }))
    }
  }, [])

  const unsubscribeFromOfficer = useCallback((officerId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        officer_id: officerId
      }))
    }
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  // Connect on mount
  useEffect(() => {
    connect()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current)
      }
    }
  }, [connect])

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        
        // Fetch officers and normalize to OfficerState shape
        const officersResponse = await fetch(`${apiUrl}/api/v1/ingest/officers`)
        if (officersResponse.ok) {
          const officersData = await officersResponse.json()
<<<<<<< HEAD
          // Transform the API response to match our frontend format
          const transformedOfficers = (officersData.officers || []).map(transformApiOfficerToOfficerState)
          setOfficers(transformedOfficers)
=======
          const normalized = (officersData.officers || []).map((o: any) => ({
            id: o.officer_id,
            name: o.name,
            badgeNumber: o.badge_number,
            department: o.department,
            isActive: o.is_active,
            isOnDuty: o.is_on_duty,
            riskLevel: o.risk_level,
            riskScore: o.risk_score ?? 0,
            lastSeen: o.last_seen,
            // Defaults; live updates will enrich these
            fallDetected: false,
            workoutActive: false,
            deviceId: o.device_id || '',
          }))
          setOfficers(normalized)
>>>>>>> 2d6a24b (cleanup)
        }
        
        // Fetch recent alerts (if endpoint exists)
        // This would be implemented based on your API
        
      } catch (error) {
        console.error('Error fetching initial data:', error)
      }
    }
    
    if (connectionStatus === 'connected') {
      fetchInitialData()
    }
  }, [connectionStatus])

  return {
    officers,
    alerts,
    connectionStatus,
    subscribeToOfficer,
    unsubscribeFromOfficer,
    sendMessage
  }
}
