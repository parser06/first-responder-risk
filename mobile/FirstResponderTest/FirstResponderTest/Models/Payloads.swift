/*
Data Payloads for First Responder Risk Monitoring
*/

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
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        officerId = try container.decode(String.self, forKey: .officerId)
        heartRate = try container.decode(Double.self, forKey: .heartRate)
        timestamp = try container.decode(Date.self, forKey: .timestamp)
        confidence = try container.decode(Double.self, forKey: .confidence)
        source = try container.decode(String.self, forKey: .source)
        
        // Handle metadata decoding
        if let metadataData = try container.decodeIfPresent(Data.self, forKey: .metadata) {
            metadata = try JSONSerialization.jsonObject(with: metadataData) as? [String: Any]
        } else {
            metadata = nil
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(officerId, forKey: .officerId)
        try container.encode(heartRate, forKey: .heartRate)
        try container.encode(ISO8601DateFormatter().string(from: timestamp), forKey: .timestamp)
        try container.encode(confidence, forKey: .confidence)
        try container.encode(source, forKey: .source)
        
        // Handle metadata encoding
        if let metadata = metadata {
            let metadataData = try JSONSerialization.data(withJSONObject: metadata)
            try container.encode(metadataData, forKey: .metadata)
        } else {
            try container.encodeNil(forKey: .metadata)
        }
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

struct LocationData: Codable {
    let latitude: Double
    let longitude: Double
    let accuracy: Double?
    let speed: Double?
    let course: Double?
    let altitude: Double?
    let timestamp: String?
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
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        type = try container.decode(String.self, forKey: .type)
        timestamp = try container.decode(Date.self, forKey: .timestamp)
        
        // Handle data decoding
        if let dataData = try container.decodeIfPresent(Data.self, forKey: .data) {
            data = try JSONSerialization.jsonObject(with: dataData) as? [String: Any]
        } else {
            data = nil
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(type, forKey: .type)
        try container.encode(ISO8601DateFormatter().string(from: timestamp), forKey: .timestamp)
        
        // Handle data encoding
        if let data = data {
            let dataData = try JSONSerialization.data(withJSONObject: data)
            try container.encode(dataData, forKey: .data)
        } else {
            try container.encodeNil(forKey: .data)
        }
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

// MARK: - Event Metadata

struct EventMetadata: Codable {
    let heartRate: Double?
    let activityType: String?
    let confidence: Double?
    let duration: Double?
    let additionalInfo: String?
    
    enum CodingKeys: String, CodingKey {
        case heartRate, activityType, confidence, duration, additionalInfo
    }
}

// MARK: - API Request/Response Models

struct IngestDataRequest: Codable {
    let officerId: String
    let deviceId: String
    let timestamp: String
    let sensorData: SensorData
    let locationData: LocationData
}

struct SensorData: Codable {
    let heartRate: Double?
    let heartRateVariability: Double?
    let activityType: String?
    let activityConfidence: Double?
    let fallDetected: Bool
    let fallConfidence: Double?
    let workoutActive: Bool
    let batteryLevel: Double?
    let networkStatus: String?
}

struct RiskEventCreate: Codable {
    let officerId: String
    let eventType: String
    let riskLevel: String
    let riskScore: Double
    let description: String?
    let location: LocationData?
    let metadata: EventMetadata?
}

struct OfficerProfileRequest: Codable {
    let officerId: String
    let maxHeartRate: Double?
    let restingHeartRate: Double?
    let age: Int?
    let weight: Double?
    let height: Double?
    let fitnessLevel: String?
}

struct OfficerProfileResponse: Codable {
    let officerId: String
    let maxHeartRate: Double?
    let restingHeartRate: Double?
    let age: Int?
    let weight: Double?
    let height: Double?
    let fitnessLevel: String?
    let lastUpdated: String
}
