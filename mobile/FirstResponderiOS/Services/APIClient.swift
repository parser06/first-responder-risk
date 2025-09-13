import Foundation
import Combine

class APIClient: ObservableObject {
    private let baseURL = "http://localhost:8000/api/v1"
    private let session = URLSession.shared
    private var cancellables = Set<AnyCancellable>()
    
    @Published var isConnected = false
    @Published var lastError: String?
    
    init() {
        // Test connection on init
        testConnection()
    }
    
    private func testConnection() {
        guard let url = URL(string: "\(baseURL)/health") else { return }
        
        session.dataTask(with: url) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.isConnected = false
                    self?.lastError = error.localizedDescription
                } else if let httpResponse = response as? HTTPURLResponse,
                          httpResponse.statusCode == 200 {
                    self?.isConnected = true
                    self?.lastError = nil
                } else {
                    self?.isConnected = false
                    self?.lastError = "Server returned error"
                }
            }
        }.resume()
    }
    
    func sendLocationData(_ location: CLLocation, officerId: String) {
        guard let url = URL(string: "\(baseURL)/ingest/data") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let locationData: [String: Any] = [
            "officer_id": officerId,
            "device_id": UIDevice.current.identifierForVendor?.uuidString ?? "unknown",
            "timestamp": ISO8601DateFormatter().string(from: location.timestamp),
            "location_data": [
                "latitude": location.coordinate.latitude,
                "longitude": location.coordinate.longitude,
                "altitude": location.altitude,
                "accuracy": location.horizontalAccuracy,
                "horizontal_accuracy": location.horizontalAccuracy,
                "vertical_accuracy": location.verticalAccuracy,
                "speed": location.speed,
                "course": location.course,
                "course_accuracy": location.courseAccuracy
            ]
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: locationData)
        } catch {
            print("Error encoding location data: \(error)")
            return
        }
        
        session.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.lastError = error.localizedDescription
                } else if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        print("Location data sent successfully")
                    } else {
                        self?.lastError = "Server returned status: \(httpResponse.statusCode)"
                    }
                }
            }
        }.resume()
    }
    
    func sendHealthData(_ healthData: [String: Any], officerId: String) {
        guard let url = URL(string: "\(baseURL)/ingest/data") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload: [String: Any] = [
            "officer_id": officerId,
            "device_id": UIDevice.current.identifierForVendor?.uuidString ?? "unknown",
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "sensor_data": healthData
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        } catch {
            print("Error encoding health data: \(error)")
            return
        }
        
        session.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.lastError = error.localizedDescription
                } else if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        print("Health data sent successfully")
                    } else {
                        self?.lastError = "Server returned status: \(httpResponse.statusCode)"
                    }
                }
            }
        }.resume()
    }
    
    func sendEmergencyAlert(officerId: String) {
        guard let url = URL(string: "\(baseURL)/ingest/data") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let emergencyData: [String: Any] = [
            "officer_id": officerId,
            "device_id": UIDevice.current.identifierForVendor?.uuidString ?? "unknown",
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "risk_level": "high",
            "risk_score": 1.0,
            "emergency": true
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: emergencyData)
        } catch {
            print("Error encoding emergency data: \(error)")
            return
        }
        
        session.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self?.lastError = error.localizedDescription
                } else if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        print("Emergency alert sent successfully")
                    } else {
                        self?.lastError = "Server returned status: \(httpResponse.statusCode)"
                    }
                }
            }
        }.resume()
    }
    
    func sendEmergencyAlert() {
        // This would use a stored officer ID
        let officerId = "default-officer-id" // In real app, this would be stored securely
        sendEmergencyAlert(officerId: officerId)
    }
}
