"""
Officer State Model for First Responder Risk Monitoring
"""

import Foundation
import CoreLocation

struct OfficerState: Codable, Identifiable {
    let id: String
    let name: String
    let badgeNumber: String
    let department: String
    let isActive: Bool
    let isOnDuty: Bool
    let riskLevel: RiskLevel
    let riskScore: Double
    let lastSeen: String
    
    // Health data
    let heartRate: Double?
    let heartRateVariability: Double?
    let activityType: String?
    let activityConfidence: Double?
    let fallDetected: Bool
    let fallConfidence: Double?
    let workoutActive: Bool
    
    // Location data
    let latitude: Double?
    let longitude: Double?
    let accuracy: Double?
    let speed: Double?
    let course: Double?
    
    // Device info
    let deviceId: String
    let appVersion: String?
    let batteryLevel: Double?
    let networkStatus: String?
    
    enum CodingKeys: String, CodingKey {
        case id, name, badgeNumber, department, isActive, isOnDuty
        case riskLevel, riskScore, lastSeen
        case heartRate, heartRateVariability, activityType, activityConfidence
        case fallDetected, fallConfidence, workoutActive
        case latitude, longitude, accuracy, speed, course
        case deviceId, appVersion, batteryLevel, networkStatus
    }
}

enum RiskLevel: String, CaseIterable, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    var displayName: String {
        switch self {
        case .low: return "Low Risk"
        case .medium: return "Medium Risk"
        case .high: return "High Risk"
        case .critical: return "Critical Risk"
        }
    }
    
    var color: String {
        switch self {
        case .low: return "green"
        case .medium: return "yellow"
        case .high: return "orange"
        case .critical: return "red"
        }
    }
}

enum EventType: String, CaseIterable, Codable {
    case highRisk = "high_risk"
    case fallDetected = "fall_detected"
    case sos = "sos"
    case heartRateAnomaly = "heart_rate_anomaly"
    case motionAnomaly = "motion_anomaly"
    case locationAnomaly = "location_anomaly"
}

struct RiskEvent: Codable, Identifiable {
    let id: String
    let officerId: String
    let eventType: EventType
    let riskLevel: RiskLevel
    let riskScore: Double
    let description: String?
    let occurredAt: String
    let isAcknowledged: Bool
    let isResolved: Bool
    let location: LocationData?
    let metadata: EventMetadata?
    
    enum CodingKeys: String, CodingKey {
        case id, officerId, eventType, riskLevel, riskScore, description
        case occurredAt, isAcknowledged, isResolved, location, metadata
    }
}

struct SystemAlert: Codable, Identifiable {
    let id: String
    let alertType: String
    let severity: AlertSeverity
    let title: String
    let message: String
    let officerId: String?
    let riskEventId: String?
    let isActive: Bool
    let isAcknowledged: Bool
    let createdAt: String
}

enum AlertSeverity: String, CaseIterable, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    var displayName: String {
        switch self {
        case .low: return "Low"
        case .medium: return "Medium"
        case .high: return "High"
        case .critical: return "Critical"
        }
    }
    
    var color: String {
        switch self {
        case .low: return "blue"
        case .medium: return "yellow"
        case .high: return "orange"
        case .critical: return "red"
        }
    }
}

struct DashboardStats: Codable {
    let totalOfficers: Int
    let highRiskOfficers: Int
    let mediumRiskOfficers: Int
    let lowRiskOfficers: Int
    let activeAlerts: Int
    let lastUpdate: String
}

// MARK: - API Response Models

struct OfficerListResponse: Codable {
    let officers: [OfficerResponse]
    let totalCount: Int
    let lastUpdate: String
}

struct OfficerResponse: Codable, Identifiable {
    let id: String
    let badgeNumber: String
    let name: String
    let department: String
    let phone: String
    let email: String
    let isActive: Bool
    let isOnDuty: Bool
    let currentRiskLevel: RiskLevel
    let currentRiskScore: Double
    let deviceId: String
    let appVersion: String
    let lastSeen: String
    let createdAt: String
    let updatedAt: String
}
