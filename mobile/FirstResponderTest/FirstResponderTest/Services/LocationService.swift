/*
Location Service for First Responder Risk Monitoring
Handles GPS location tracking and updates
*/

import Foundation
import CoreLocation
import Combine

class LocationService: NSObject, ObservableObject {
    static let shared = LocationService()
    
    private let locationManager = CLLocationManager()
    
    @Published var currentLocation: CLLocation?
    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published var isLocationEnabled = false
    @Published var locationError: String?
    
    private override init() {
        super.init()
        setupLocationManager()
    }
    
    private func setupLocationManager() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.distanceFilter = 10 // Update every 10 meters
    }
    
    func requestLocationPermission() {
        switch authorizationStatus {
        case .notDetermined:
            locationManager.requestWhenInUseAuthorization()
        case .denied, .restricted:
            // Handle denied permission
            locationError = "Location permission denied. Please enable in Settings."
        case .authorizedWhenInUse, .authorizedAlways:
            startLocationUpdates()
        @unknown default:
            break
        }
    }
    
    func startLocationUpdates() {
        guard authorizationStatus == .authorizedWhenInUse || authorizationStatus == .authorizedAlways else {
            requestLocationPermission()
            return
        }
        
        locationManager.startUpdatingLocation()
        isLocationEnabled = true
        locationError = nil
    }
    
    func stopLocationUpdates() {
        locationManager.stopUpdatingLocation()
        isLocationEnabled = false
    }
    
    func getCurrentLocation() -> CLLocation? {
        return currentLocation
    }
    
    func getLocationData() -> LocationData? {
        guard let location = currentLocation else { return nil }
        
        return LocationData(
            latitude: location.coordinate.latitude,
            longitude: location.coordinate.longitude,
            altitude: location.altitude,
            accuracy: location.horizontalAccuracy,
            horizontalAccuracy: location.horizontalAccuracy,
            verticalAccuracy: location.verticalAccuracy,
            speed: location.speed >= 0 ? location.speed : nil,
            course: location.course >= 0 ? location.course : nil,
            courseAccuracy: location.courseAccuracy >= 0 ? location.courseAccuracy : nil
        )
    }
}

// MARK: - CLLocationManagerDelegate

extension LocationService: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        
        currentLocation = location
        locationError = nil
        
        // Post notification for location update
        NotificationCenter.default.post(
            name: .locationUpdated,
            object: nil,
            userInfo: ["location": location]
        )
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        locationError = error.localizedDescription
        print("Location error: \(error.localizedDescription)")
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        authorizationStatus = status
        
        switch status {
        case .authorizedWhenInUse, .authorizedAlways:
            startLocationUpdates()
        case .denied, .restricted:
            isLocationEnabled = false
            locationError = "Location access denied"
        case .notDetermined:
            break
        @unknown default:
            break
        }
    }
}

// MARK: - Location Data Model

struct LocationData: Codable {
    let latitude: Double
    let longitude: Double
    let altitude: Double?
    let accuracy: Double?
    let horizontalAccuracy: Double?
    let verticalAccuracy: Double?
    let speed: Double?
    let course: Double?
    let courseAccuracy: Double?
}

// MARK: - Notifications

extension Notification.Name {
    static let locationUpdated = Notification.Name("locationUpdated")
}

