/*
Watch Connectivity Bridge for First Responder Risk Monitoring
Handles communication between iPhone and Apple Watch
*/

import Foundation
import WatchConnectivity
import Combine

class WCBridge: NSObject, ObservableObject {
    static let shared = WCBridge()
    
    @Published var isWatchConnected = false
    @Published var isWatchAppInstalled = false
    @Published var lastMessage: [String: Any]?
    @Published var connectionError: String?
    
    private override init() {
        super.init()
        setupWatchConnectivity()
    }
    
    private func setupWatchConnectivity() {
        guard WCSession.isSupported() else {
            connectionError = "Watch Connectivity not supported"
            return
        }
        
        WCSession.default.delegate = self
        WCSession.default.activate()
    }
    
    // MARK: - Send Data to Watch
    
    func sendHeartRateData(_ heartRate: Double, timestamp: Date) {
        let message = [
            "type": "heart_rate",
            "heart_rate": heartRate,
            "timestamp": ISO8601DateFormatter().string(from: timestamp)
        ] as [String : Any]
        
        sendMessage(message)
    }
    
    func sendRiskLevel(_ riskLevel: String, riskScore: Double) {
        let message = [
            "type": "risk_update",
            "risk_level": riskLevel,
            "risk_score": riskScore,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ] as [String : Any]
        
        sendMessage(message)
    }
    
    func sendAlert(_ alert: String, severity: String) {
        let message = [
            "type": "alert",
            "alert": alert,
            "severity": severity,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ] as [String : Any]
        
        sendMessage(message)
    }
    
    func sendLocationData(_ location: LocationData) {
        let message = [
            "type": "location",
            "latitude": location.latitude,
            "longitude": location.longitude,
            "accuracy": location.accuracy ?? 0,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ] as [String : Any]
        
        sendMessage(message)
    }
    
    private func sendMessage(_ message: [String: Any]) {
        guard WCSession.default.isReachable else {
            connectionError = "Watch not reachable"
            return
        }
        
        WCSession.default.sendMessage(message, replyHandler: { response in
            print("Watch response: \(response)")
        }, errorHandler: { error in
            self.connectionError = error.localizedDescription
            print("Watch communication error: \(error.localizedDescription)")
        })
    }
    
    // MARK: - Receive Data from Watch
    
    func handleWatchMessage(_ message: [String: Any]) {
        lastMessage = message
        
        guard let type = message["type"] as? String else { return }
        
        switch type {
        case "heart_rate":
            handleHeartRateFromWatch(message)
        case "motion_data":
            handleMotionDataFromWatch(message)
        case "fall_detected":
            handleFallDetectionFromWatch(message)
        case "workout_status":
            handleWorkoutStatusFromWatch(message)
        default:
            print("Unknown message type: \(type)")
        }
    }
    
    private func handleHeartRateFromWatch(_ message: [String: Any]) {
        guard let heartRate = message["heart_rate"] as? Double,
              let timestampString = message["timestamp"] as? String,
              let timestamp = ISO8601DateFormatter().date(from: timestampString) else {
            return
        }
        
        // Forward to API client
        Task {
            do {
                let response = try await APIClient.shared.submitHeartRateData(
                    officerId: "current_officer", // This should be dynamic
                    heartRate: heartRate,
                    timestamp: timestamp
                )
                
                // Send risk assessment back to watch
                sendRiskLevel(response.risk_level, riskScore: response.risk_score)
                
            } catch {
                print("Error submitting heart rate data: \(error)")
            }
        }
    }
    
    private func handleMotionDataFromWatch(_ message: [String: Any]) {
        // Handle motion data from watch
        print("Received motion data from watch: \(message)")
    }
    
    private func handleFallDetectionFromWatch(_ message: [String: Any]) {
        // Handle fall detection from watch
        print("Fall detected by watch: \(message)")
        
        // Send alert to watch
        sendAlert("FALL DETECTED", severity: "critical")
    }
    
    private func handleWorkoutStatusFromWatch(_ message: [String: Any]) {
        // Handle workout status from watch
        print("Workout status from watch: \(message)")
    }
}

// MARK: - WCSessionDelegate

extension WCBridge: WCSessionDelegate {
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async {
            if let error = error {
                self.connectionError = error.localizedDescription
            } else {
                self.isWatchConnected = activationState == .activated
                self.isWatchAppInstalled = session.isWatchAppInstalled
                self.connectionError = nil
            }
        }
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {
        DispatchQueue.main.async {
            self.isWatchConnected = false
        }
    }
    
    func sessionDidDeactivate(_ session: WCSession) {
        DispatchQueue.main.async {
            self.isWatchConnected = false
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        DispatchQueue.main.async {
            self.handleWatchMessage(message)
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
        DispatchQueue.main.async {
            self.handleWatchMessage(message)
        }
        
        // Send acknowledgment back to watch
        replyHandler(["status": "received"])
    }
}
