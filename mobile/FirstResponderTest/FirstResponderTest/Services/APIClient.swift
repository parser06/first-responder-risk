/*
API Client for First Responder Risk Monitoring
Handles communication with the backend server
*/

import Foundation
import Combine

class APIClient: ObservableObject {
    static let shared = APIClient()
    
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared
    
    @Published var isConnected = false
    @Published var lastError: String?
    
    private init() {}
    
    // MARK: - Heart Rate Data Submission
    
    func submitHeartRateData(
        officerId: String,
        heartRate: Double,
        timestamp: Date,
        confidence: Double = 1.0,
        metadata: [String: Any]? = nil
    ) async throws -> HeartRateResponse {
        
        let url = URL(string: "\(baseURL)/ml/heart-rate/process")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let heartRateData = HeartRateData(
            officer_id: officerId,
            heart_rate: heartRate,
            timestamp: ISO8601DateFormatter().string(from: timestamp),
            confidence: confidence,
            source: "watch",
            metadata: metadata
        )
        
        let requestBody = RiskAssessmentRequest(
            officer_id: officerId,
            heart_rate_data: [heartRateData],
            officer_profile: nil
        )
        
        request.httpBody = try JSONEncoder().encode(requestBody)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        let heartRateResponse = try JSONDecoder().decode(HeartRateResponse.self, from: data)
        isConnected = true
        lastError = nil
        
        return heartRateResponse
    }
    
    // MARK: - Officer Profile Management
    
    func setOfficerProfile(
        officerId: String,
        age: Int,
        restingHR: Double? = nil,
        maxHR: Double? = nil
    ) async throws {
        
        let url = URL(string: "\(baseURL)/ml/heart-rate/officer/profile")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let profile = [
            "age": age,
            "resting_hr": restingHR as Any,
            "max_hr": maxHR as Any
        ]
        
        let requestBody = [
            "officer_id": officerId,
            "profile": profile
        ] as [String : Any]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
    }
    
    // MARK: - Health Check
    
    func checkServerHealth() async -> Bool {
        do {
            let url = URL(string: "\(baseURL)/health")!
            let (_, response) = try await session.data(from: url)
            
            if let httpResponse = response as? HTTPURLResponse,
               httpResponse.statusCode == 200 {
                isConnected = true
                lastError = nil
                return true
            }
        } catch {
            lastError = error.localizedDescription
        }
        
        isConnected = false
        return false
    }
    
    // MARK: - Data Models
    
    struct HeartRateData: Codable {
        let officer_id: String
        let heart_rate: Double
        let timestamp: String
        let confidence: Double
        let source: String
        let metadata: [String: Any]?
        
        enum CodingKeys: String, CodingKey {
            case officer_id, heart_rate, timestamp, confidence, source, metadata
        }
        
        init(officer_id: String, heart_rate: Double, timestamp: String, confidence: Double, source: String, metadata: [String: Any]?) {
            self.officer_id = officer_id
            self.heart_rate = heart_rate
            self.timestamp = timestamp
            self.confidence = confidence
            self.source = source
            self.metadata = metadata
        }
        
        func encode(to encoder: Encoder) throws {
            var container = encoder.container(keyedBy: CodingKeys.self)
            try container.encode(officer_id, forKey: .officer_id)
            try container.encode(heart_rate, forKey: .heart_rate)
            try container.encode(timestamp, forKey: .timestamp)
            try container.encode(confidence, forKey: .confidence)
            try container.encode(source, forKey: .source)
            try container.encodeIfPresent(metadata, forKey: .metadata)
        }
    }
    
    struct RiskAssessmentRequest: Codable {
        let officer_id: String
        let heart_rate_data: [HeartRateData]
        let officer_profile: [String: Any]?
        
        enum CodingKeys: String, CodingKey {
            case officer_id, heart_rate_data, officer_profile
        }
        
        init(officer_id: String, heart_rate_data: [HeartRateData], officer_profile: [String: Any]?) {
            self.officer_id = officer_id
            self.heart_rate_data = heart_rate_data
            self.officer_profile = officer_profile
        }
        
        func encode(to encoder: Encoder) throws {
            var container = encoder.container(keyedBy: CodingKeys.self)
            try container.encode(officer_id, forKey: .officer_id)
            try container.encode(heart_rate_data, forKey: .heart_rate_data)
            try container.encodeIfPresent(officer_profile, forKey: .officer_profile)
        }
    }
    
    struct HeartRateResponse: Codable {
        let officer_id: String
        let risk_level: String
        let risk_score: Double
        let confidence: Double
        let contributing_factors: [String: Double]
        let recommendations: [String]
        let timestamp: String
        let features: HeartRateFeatures
    }
    
    struct HeartRateFeatures: Codable {
        let current_hr: Double
        let mean_hr: Double
        let std_hr: Double
        let intensity_zone: String
        let intensity_percentage: Double
        let hr_anomaly_score: Double
        let stress_indicator: Double
        let fatigue_indicator: Double
        let recent_activity: String
        let time_since_start: Double
    }
}

enum APIError: Error {
    case invalidResponse
    case networkError
    case decodingError
    
    var localizedDescription: String {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .networkError:
            return "Network connection error"
        case .decodingError:
            return "Failed to decode response"
        }
    }
}
