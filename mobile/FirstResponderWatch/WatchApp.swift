import SwiftUI
import HealthKit
import CoreMotion
import WatchConnectivity

@main
struct FirstResponderWatchApp: App {
    @StateObject private var workoutService = WorkoutService()
    @StateObject private var heartRateStream = HeartRateStream()
    @StateObject private var motionService = MotionService()
    @StateObject private var wcSession = WCSessionManager()
    
    var body: some Scene {
        WindowGroup {
            OnDutyView()
                .environmentObject(workoutService)
                .environmentObject(heartRateStream)
                .environmentObject(motionService)
                .environmentObject(wcSession)
        }
    }
}
