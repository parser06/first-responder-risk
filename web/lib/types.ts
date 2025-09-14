// Type definitions for the First Responder Risk Monitoring system

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'

export type EventType = 
  | 'high_risk' 
  | 'fall_detected' 
  | 'sos' 
  | 'heart_rate_anomaly' 
  | 'motion_anomaly' 
  | 'location_anomaly'

export interface OfficerState {
  id: string
  name: string
  badgeNumber: string
  department: string
  isActive: boolean
  isOnDuty: boolean
  riskLevel: RiskLevel
  riskScore: number
  lastSeen: string
  
  // Health data
  heartRate?: number
  heartRateVariability?: number
  activityType?: string
  activityConfidence?: number
  fallDetected: boolean
  fallConfidence?: number
  workoutActive: boolean
  
  // Location data
  latitude?: number
  longitude?: number
  accuracy?: number
  speed?: number
  course?: number
  
  // Device info
  deviceId: string
  appVersion?: string
  batteryLevel?: number
  networkStatus?: string
}

export interface HealthData {
  heartRate?: number
  heartRateVariability?: number
  acceleration?: {
    x: number
    y: number
    z: number
  }
  gyroscope?: {
    x: number
    y: number
    z: number
  }
  activityType?: string
  activityConfidence?: number
  fallDetected: boolean
  fallConfidence?: number
  workoutActive: boolean
  workoutDuration?: number
}

export interface LocationData {
  latitude: number
  longitude: number
  altitude?: number
  accuracy?: number
  horizontalAccuracy?: number
  verticalAccuracy?: number
  speed?: number
  course?: number
  courseAccuracy?: number
}

export interface RiskEvent {
  id: string
  officerId: string
  eventType: EventType
  riskLevel: RiskLevel
  riskScore: number
  description?: string
  occurredAt: string
  isAcknowledged: boolean
  isResolved: boolean
  location?: {
    latitude: number
    longitude: number
  }
  metadata?: Record<string, any>
}

export interface SystemAlert {
  id: string
  alertType: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  officerId?: string
  riskEventId?: string
  isActive: boolean
  isAcknowledged: boolean
  createdAt: string
}

export interface WebSocketMessage {
  type: string
  timestamp: string
  data?: any
}

export interface OfficerUpdateMessage extends WebSocketMessage {
  type: 'officer_update'
  officerId: string
  riskLevel: RiskLevel
  riskScore: number
  location?: LocationData
  lastSeen: string
}

export interface RiskEventMessage extends WebSocketMessage {
  type: 'risk_event'
  eventId: string
  officerId: string
  eventType: EventType
  riskLevel: RiskLevel
  description: string
  location?: LocationData
}

export interface SystemAlertMessage extends WebSocketMessage {
  type: 'system_alert'
  alertId: string
  alertType: string
  severity: string
  title: string
  message: string
  officerId?: string
}

export interface RiskAssessment {
  riskScore: number
  riskLevel: RiskLevel
  factors: Record<string, number>
  confidence: number
  recommendations: string[]
  timestamp: string
}

export interface MapMarker {
  id: string
  position: [number, number]
  riskLevel: RiskLevel
  officer: OfficerState
}

export interface DashboardStats {
  totalOfficers: number
  highRiskOfficers: number
  mediumRiskOfficers: number
  lowRiskOfficers: number
  activeAlerts: number
  lastUpdate: string
}
