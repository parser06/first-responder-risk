import Foundation
import WatchConnectivity
import Combine

class WCBridge: NSObject, ObservableObject {
    @Published var isWatchConnected = false
    @Published var isHealthMonitoring = false
    @Published var lastHealthData: [String: Any] = [:]
    
    private var session: WCSession?
    
    override init() {
        super.init()
        
        if WCSession.isSupported() {
            session = WCSession.default
            session?.delegate = self
            session?.activate()
        }
    }
    
    func startHealthMonitoring() {
        guard let session = session, session.isReachable else {
            print("Watch not reachable")
            return
        }
        
        let message = ["action": "start_health_monitoring"]
        session.sendMessage(message, replyHandler: { response in
            DispatchQueue.main.async {
                self.isHealthMonitoring = true
            }
        }) { error in
            print("Error starting health monitoring: \(error.localizedDescription)")
        }
    }
    
    func stopHealthMonitoring() {
        guard let session = session, session.isReachable else {
            print("Watch not reachable")
            return
        }
        
        let message = ["action": "stop_health_monitoring"]
        session.sendMessage(message, replyHandler: { response in
            DispatchQueue.main.async {
                self.isHealthMonitoring = false
            }
        }) { error in
            print("Error stopping health monitoring: \(error.localizedDescription)")
        }
    }
    
    func sendLocationToWatch(_ location: CLLocation) {
        guard let session = session, session.isReachable else { return }
        
        let locationData: [String: Any] = [
            "latitude": location.coordinate.latitude,
            "longitude": location.coordinate.longitude,
            "accuracy": location.horizontalAccuracy,
            "timestamp": location.timestamp.timeIntervalSince1970
        ]
        
        session.sendMessage(["location": locationData], replyHandler: nil) { error in
            print("Error sending location to watch: \(error.localizedDescription)")
        }
    }
}

// MARK: - WCSessionDelegate
extension WCBridge: WCSessionDelegate {
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        DispatchQueue.main.async {
            self.isWatchConnected = (activationState == .activated)
        }
        
        if let error = error {
            print("Watch session activation failed: \(error.localizedDescription)")
        } else {
            print("Watch session activated successfully")
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
        // Reactivate session
        session.activate()
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        DispatchQueue.main.async {
            if let healthData = message["healthData"] as? [String: Any] {
                self.lastHealthData = healthData
                print("Received health data from watch: \(healthData)")
            }
        }
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any], replyHandler: @escaping ([String : Any]) -> Void) {
        DispatchQueue.main.async {
            if let action = message["action"] as? String {
                switch action {
                case "get_status":
                    replyHandler([
                        "isConnected": self.isWatchConnected,
                        "isHealthMonitoring": self.isHealthMonitoring
                    ])
                default:
                    replyHandler(["error": "Unknown action"])
                }
            }
        }
    }
}
