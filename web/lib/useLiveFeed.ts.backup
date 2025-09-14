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
              ...message.data,
              id: message.data.officer_id
            }
          } else {
            // New officer
            updatedOfficers.push({
              ...message.data,
              id: message.data.officer_id,
              fallDetected: false,
              workoutActive: false
            })
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
        
        // Fetch officers
        const officersResponse = await fetch(`${apiUrl}/api/v1/ingest/officers`)
        if (officersResponse.ok) {
          const officersData = await officersResponse.json()
          setOfficers(officersData.officers || [])
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
