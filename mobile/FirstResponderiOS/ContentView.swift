import SwiftUI
import CoreLocation
import WatchConnectivity

struct ContentView: View {
    @StateObject private var locationService = LocationService()
    @StateObject private var apiClient = APIClient()
    @StateObject private var watchBridge = WCBridge()
    
    @State private var isOnDuty = false
    @State private var currentRiskLevel = "low"
    @State private var lastUpdate = Date()
    @State private var showingSettings = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 8) {
                    Text("First Responder")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text("Risk Monitoring System")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top)
                
                // Status Card
                VStack(spacing: 16) {
                    HStack {
                        Text("Status")
                            .font(.headline)
                        Spacer()
                        Circle()
                            .fill(statusColor)
                            .frame(width: 12, height: 12)
                    }
                    
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Risk Level")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(currentRiskLevel.uppercased())
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(statusColor)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text("Last Update")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text(lastUpdate, style: .relative)
                                .font(.caption)
                        }
                    }
                    
                    // Duty Toggle
                    Button(action: toggleDuty) {
                        HStack {
                            Image(systemName: isOnDuty ? "stop.circle.fill" : "play.circle.fill")
                            Text(isOnDuty ? "End Duty" : "Start Duty")
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isOnDuty ? Color.red : Color.green)
                        .cornerRadius(10)
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Health Data Display
                if isOnDuty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Health Monitoring")
                            .font(.headline)
                        
                        HStack {
                            VStack(alignment: .leading) {
                                Text("Heart Rate")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text("-- BPM")
                                    .font(.title3)
                                    .fontWeight(.semibold)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing) {
                                Text("Activity")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text("Unknown")
                                    .font(.title3)
                                    .fontWeight(.semibold)
                            }
                        }
                        
                        HStack {
                            VStack(alignment: .leading) {
                                Text("Location")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(locationService.currentLocation?.coordinate.latitude != nil ? 
                                     "Tracking" : "Not Available")
                                    .font(.caption)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing) {
                                Text("Watch Status")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                Text(watchBridge.isWatchConnected ? "Connected" : "Disconnected")
                                    .font(.caption)
                                    .foregroundColor(watchBridge.isWatchConnected ? .green : .red)
                            }
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
                
                Spacer()
                
                // Emergency Button
                Button(action: triggerEmergency) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                        Text("EMERGENCY SOS")
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .cornerRadius(10)
                }
                .disabled(!isOnDuty)
                .opacity(isOnDuty ? 1.0 : 0.5)
            }
            .padding()
            .navigationTitle("Risk Monitor")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Settings") {
                        showingSettings = true
                    }
                }
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
        }
        .onAppear {
            locationService.requestLocationPermission()
        }
    }
    
    private var statusColor: Color {
        switch currentRiskLevel {
        case "high": return .red
        case "medium": return .orange
        case "low": return .green
        default: return .gray
        }
    }
    
    private func toggleDuty() {
        isOnDuty.toggle()
        
        if isOnDuty {
            locationService.startLocationUpdates()
            watchBridge.startHealthMonitoring()
        } else {
            locationService.stopLocationUpdates()
            watchBridge.stopHealthMonitoring()
        }
    }
    
    private func triggerEmergency() {
        // Send emergency alert
        print("Emergency SOS triggered!")
        
        // Haptic feedback
        let impactFeedback = UIImpactFeedbackGenerator(style: .heavy)
        impactFeedback.impactOccurred()
        
        // Send to backend
        apiClient.sendEmergencyAlert()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
