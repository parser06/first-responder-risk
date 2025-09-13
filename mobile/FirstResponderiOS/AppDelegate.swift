import UIKit
import CoreLocation
import WatchConnectivity

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    var window: UIWindow?
    var locationManager: CLLocationManager?
    var watchSession: WCSession?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Initialize location manager
        setupLocationManager()
        
        // Initialize Watch Connectivity
        setupWatchConnectivity()
        
        // Set up window
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = ContentView()
        window?.makeKeyAndVisible()
        
        return true
    }
    
    private func setupLocationManager() {
        locationManager = CLLocationManager()
        locationManager?.delegate = self
        locationManager?.desiredAccuracy = kCLLocationAccuracyBest
        locationManager?.distanceFilter = 10 // Update every 10 meters
    }
    
    private func setupWatchConnectivity() {
        if WCSession.isSupported() {
            watchSession = WCSession.default
            watchSession?.delegate = self
            watchSession?.activate()
        }
    }
}

// MARK: - CLLocationManagerDelegate
extension AppDelegate: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        
        // Send location to watch
        sendLocationToWatch(location)
        
        // Send to backend
        sendLocationToBackend(location)
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error.localizedDescription)")
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        switch status {
        case .authorizedWhenInUse, .authorizedAlways:
            locationManager?.startUpdatingLocation()
        case .denied, .restricted:
            print("Location access denied")
        case .notDetermined:
            locationManager?.requestWhenInUseAuthorization()
        @unknown default:
            break
        }
    }
    
    private func sendLocationToWatch(_ location: CLLocation) {
        guard let session = watchSession, session.isReachable else { return }
        
        let locationData: [String: Any] = [
            "latitude": location.coordinate.latitude,
            "longitude": location.coordinate.longitude,
            "accuracy": location.horizontalAccuracy,
            "timestamp": location.timestamp.timeIntervalSince1970
        ]
        
        session.sendMessage(locationData, replyHandler: nil) { error in
            print("Error sending location to watch: \(error.localizedDescription)")
        }
    }
    
    private func sendLocationToBackend(_ location: CLLocation) {
        // This will be implemented with the API client
        print("Sending location to backend: \(location.coordinate)")
    }
}

// MARK: - WCSessionDelegate
extension AppDelegate: WCSessionDelegate {
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        if let error = error {
            print("Watch session activation failed: \(error.localizedDescription)")
        } else {
            print("Watch session activated successfully")
        }
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {
        print("Watch session became inactive")
    }
    
    func sessionDidDeactivate(_ session: WCSession) {
        print("Watch session deactivated")
        // Reactivate session
        session.activate()
    }
    
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        // Handle messages from watch
        DispatchQueue.main.async {
            if let healthData = message["healthData"] as? [String: Any] {
                self.handleHealthDataFromWatch(healthData)
            }
        }
    }
    
    private func handleHealthDataFromWatch(_ healthData: [String: Any]) {
        // Process health data from watch
        print("Received health data from watch: \(healthData)")
        
        // Send to backend
        sendHealthDataToBackend(healthData)
    }
    
    private func sendHealthDataToBackend(_ healthData: [String: Any]) {
        // This will be implemented with the API client
        print("Sending health data to backend: \(healthData)")
    }
}
