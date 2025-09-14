"""
Data Payloads for First Responder Risk Monitoring
"""

import Foundation

// MARK: - Heart Rate Data

struct HeartRatePayload: Codable {
    let officerId: String
    let heartRate: Double
    let timestamp: Date
    let confidence: Double
    let source: String
    let metadata: [String: Any]?
    
    enum CodingKeys: String, CodingKey {
        case officerId, heartRate, timestamp, confidence, source, metadata
    }
    
    init(officerId: String, heartRate: Double, timestamp: Date, confidence: Double = 1.0, source: String = "watch", metadata: [String: Any]? = nil) {
        self.officerId = officerId
        self.heartRate = heartRate
        self.timestamp = timestamp
        self.confidence = confidence
        self.source = source
        self.metadata = metadata
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(officerId, forKey: .officerId)
        try container.encode(heartRate, forKey: .heartRate)
        try container.encode(ISO8601DateFormatter().string(from: timestamp), forKey: .timestamp)
        try container.encode(confidence, forKey: .confidence)
        try container.encode(source, forKey: .source)
        try container.encodeIfPresent(metadata, forKey: .metadata)
    }
}

// MARK: - Motion Data

struct MotionPayload: Codable {
    let officerId: String
    let acceleration: AccelerationData
    let gyroscope: GyroscopeData
    let timestamp: Date
    let fallDetected: Bool
    let fallConfidence: Double?
    
    struct AccelerationData: Codable {
        let x: Double
        let y: Double
        let z: Double
    }
    
    struct GyroscopeData: Codable {
        let x: Double
        let y: Double
        let z: Double
    }
}

// MARK: - Location Data

struct LocationPayload: Codable {
    let officerId: String
    let latitude: Double
    let longitude: Double
    let altitude: Double?
    let accuracy: Double?
    let horizontalAccuracy: Double?
    let verticalAccuracy: Double?
    let speed: Double?
    let course: Double?
    let courseAccuracy: Double?
    let timestamp: Date
}

// MARK: - Workout Data

struct WorkoutPayload: Codable {
    let officerId: String
    let workoutType: String
    let startTime: Date
    let endTime: Date?
    let duration: TimeInterval
    let isActive: Bool
    let heartRateData: [HeartRateDataPoint]
    let motionData: [MotionDataPoint]
    
    struct HeartRateDataPoint: Codable {
        let value: Double
        let timestamp: Date
    }
    
    struct MotionDataPoint: Codable {
        let acceleration: MotionPayload.AccelerationData
        let gyroscope: MotionPayload.GyroscopeData
        let timestamp: Date
    }
}

// MARK: - Risk Assessment

struct RiskAssessmentPayload: Codable {
    let officerId: String
    let riskLevel: String
    let riskScore: Double
    let confidence: Double
    let contributingFactors: [String: Double]
    let recommendations: [String]
    let timestamp: Date
    let features: HeartRateFeatures
}

struct HeartRateFeatures: Codable {
    let currentHR: Double
    let meanHR: Double
    let stdHR: Double
    let intensityZone: String
    let intensityPercentage: Double
    let hrAnomalyScore: Double
    let stressIndicator: Double
    let fatigueIndicator: Double
    let recentActivity: String
    let timeSinceStart: Double
}

// MARK: - Alert Data

struct AlertPayload: Codable {
    let alertId: String
    let officerId: String
    let alertType: String
    let severity: String
    let title: String
    let message: String
    let timestamp: Date
    let isActive: Bool
    let isAcknowledged: Bool
}

// MARK: - WebSocket Messages

struct WebSocketMessage: Codable {
    let type: String
    let timestamp: Date
    let data: [String: Any]?
    
    enum CodingKeys: String, CodingKey {
        case type, timestamp, data
    }
    
    init(type: String, timestamp: Date = Date(), data: [String: Any]? = nil) {
        self.type = type
        self.timestamp = timestamp
        self.data = data
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(type, forKey: .type)
        try container.encode(ISO8601DateFormatter().string(from: timestamp), forKey: .timestamp)
        try container.encodeIfPresent(data, forKey: .data)
    }
}

struct OfficerUpdateMessage: Codable {
    let type: String
    let officerId: String
    let riskLevel: String
    let riskScore: Double
    let location: LocationData?
    let lastSeen: String
    let timestamp: Date
}

struct RiskEventMessage: Codable {
    let type: String
    let eventId: String
    let officerId: String
    let eventType: String
    let riskLevel: String
    let description: String
    let location: LocationData?
    let timestamp: Date
}

struct SystemAlertMessage: Codable {
    let type: String
    let alertId: String
    let alertType: String
    let severity: String
    let title: String
    let message: String
    let officerId: String?
    let timestamp: Date
}
