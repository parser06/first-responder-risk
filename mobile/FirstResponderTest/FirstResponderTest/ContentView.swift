/*
Simple ContentView for First Responder Risk Monitoring
This version works with the services we just created
*/

import SwiftUI
import CoreLocation

struct ContentView: View {
    @StateObject private var locationService = LocationService.shared
    @StateObject private var apiClient = APIClient.shared
    @StateObject private var watchBridge = WCBridge.shared
    
    @State private var isOnDuty = false
    @State private var currentHeartRate: Double = 0
    @State private var riskLevel: String = "low"
    @State private var riskScore: Double = 0.0
    @State private var lastUpdate: Date = Date()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                VStack {
                    Text("First Responder")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Risk Monitoring System")
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                .padding(.top)
                
                // Status Cards
                VStack(spacing: 16) {
                    // Duty Status
                    DutyStatusCard(isOnDuty: $isOnDuty)
                    
                    // Heart Rate Card
                    HeartRateCard(
                        heartRate: currentHeartRate,
                        riskLevel: riskLevel,
                        riskScore: riskScore
                    )
                    
                    // Location Card
                    LocationCard(
                        location: locationService.currentLocation,
                        isEnabled: locationService.isLocationEnabled
                    )
                    
                    // Watch Connection Card
                    WatchConnectionCard(
                        isConnected: watchBridge.isWatchConnected,
                        isAppInstalled: watchBridge.isWatchAppInstalled
                    )
                }
                
                Spacer()
                
                // Action Buttons
                VStack(spacing: 12) {
                    Button(action: toggleDutyStatus) {
                        Text(isOnDuty ? "End Duty" : "Start Duty")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(isOnDuty ? Color.red : Color.green)
                            .cornerRadius(10)
                    }
                    
                    Button(action: requestLocationPermission) {
                        Text("Enable Location")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                    .disabled(locationService.isLocationEnabled)
                }
                .padding(.horizontal)
                
                // Last Update
                Text("Last Update: \(lastUpdate, formatter: timeFormatter)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.bottom)
            }
            .navigationBarHidden(true)
        }
        .onAppear {
            setupServices()
        }
    }
    
    private func setupServices() {
        // Check server connection
        Task {
            await apiClient.checkServerHealth()
        }
        
        // Request location permission
        locationService.requestLocationPermission()
    }
    
    private func toggleDutyStatus() {
        isOnDuty.toggle()
        
        if isOnDuty {
            startMonitoring()
        } else {
            stopMonitoring()
        }
    }
    
    private func startMonitoring() {
        // Start location updates
        locationService.startLocationUpdates()
        
        // Start heart rate monitoring (this would be handled by Watch)
        // For now, simulate some data
        simulateHeartRateData()
    }
    
    private func stopMonitoring() {
        // Stop location updates
        locationService.stopLocationUpdates()
    }
    
    private func requestLocationPermission() {
        locationService.requestLocationPermission()
    }
    
    private func simulateHeartRateData() {
        // This would normally come from the Apple Watch
        // For demo purposes, we'll simulate some data
        Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            let simulatedHR = Double.random(in: 60...180)
            currentHeartRate = simulatedHR
            
            // Simulate risk assessment
            if simulatedHR > 160 {
                riskLevel = "high"
                riskScore = 0.8
            } else if simulatedHR > 140 {
                riskLevel = "medium"
                riskScore = 0.5
            } else {
                riskLevel = "low"
                riskScore = 0.2
            }
            
            lastUpdate = Date()
        }
    }
}

// MARK: - Status Cards

struct DutyStatusCard: View {
    @Binding var isOnDuty: Bool
    
    var body: some View {
        HStack {
            Image(systemName: isOnDuty ? "shield.fill" : "shield")
                .foregroundColor(isOnDuty ? .green : .gray)
                .font(.title2)
            
            VStack(alignment: .leading) {
                Text("Duty Status")
                    .font(.headline)
                Text(isOnDuty ? "ON DUTY" : "OFF DUTY")
                    .font(.subheadline)
                    .foregroundColor(isOnDuty ? .green : .gray)
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

struct HeartRateCard: View {
    let heartRate: Double
    let riskLevel: String
    let riskScore: Double
    
    var body: some View {
        HStack {
            Image(systemName: "heart.fill")
                .foregroundColor(.red)
                .font(.title2)
            
            VStack(alignment: .leading) {
                Text("Heart Rate")
                    .font(.headline)
                Text("\(Int(heartRate)) BPM")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Risk: \(riskLevel.uppercased())")
                    .font(.subheadline)
                    .foregroundColor(riskColor)
            }
            
            Spacer()
            
            // Risk Score Bar
            VStack {
                Text("\(Int(riskScore * 100))%")
                    .font(.caption)
                ProgressView(value: riskScore)
                    .progressViewStyle(LinearProgressViewStyle(tint: riskColor))
                    .frame(width: 60)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
    
    private var riskColor: Color {
        switch riskLevel {
        case "low": return .green
        case "medium": return .yellow
        case "high": return .orange
        case "critical": return .red
        default: return .gray
        }
    }
}

struct LocationCard: View {
    let location: CLLocation?
    let isEnabled: Bool
    
    var body: some View {
        HStack {
            Image(systemName: "location.fill")
                .foregroundColor(isEnabled ? .blue : .gray)
                .font(.title2)
            
            VStack(alignment: .leading) {
                Text("Location")
                    .font(.headline)
                
                if let location = location {
                    Text("\(location.coordinate.latitude, specifier: "%.4f"), \(location.coordinate.longitude, specifier: "%.4f")")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                } else {
                    Text(isEnabled ? "Getting location..." : "Location disabled")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

struct WatchConnectionCard: View {
    let isConnected: Bool
    let isAppInstalled: Bool
    
    var body: some View {
        HStack {
            Image(systemName: "applewatch")
                .foregroundColor(isConnected ? .green : .gray)
                .font(.title2)
            
            VStack(alignment: .leading) {
                Text("Apple Watch")
                    .font(.headline)
                
                if isConnected {
                    Text("Connected")
                        .font(.subheadline)
                        .foregroundColor(.green)
                } else if isAppInstalled {
                    Text("App installed, not connected")
                        .font(.subheadline)
                        .foregroundColor(.orange)
                } else {
                    Text("Not connected")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

// MARK: - Formatters

private let timeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.timeStyle = .medium
    return formatter
}()

// MARK: - Preview

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
