import Foundation
import HealthKit
import Combine

class WorkoutService: NSObject, ObservableObject {
    private let healthStore = HKHealthStore()
    private var workoutSession: HKWorkoutSession?
    private var workoutBuilder: HKLiveWorkoutBuilder?
    
    @Published var isWorkoutActive = false
    @Published var workoutDuration: TimeInterval = 0
    @Published var currentHeartRate: Double = 0
    @Published var averageHeartRate: Double = 0
    
    private var workoutStartDate: Date?
    private var timer: Timer?
    
    override init() {
        super.init()
        requestHealthKitPermissions()
    }
    
    private func requestHealthKitPermissions() {
        guard HKHealthStore.isHealthDataAvailable() else {
            print("HealthKit not available")
            return
        }
        
        let typesToRead: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .heartRate)!,
            HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!,
            HKObjectType.workoutType()
        ]
        
        healthStore.requestAuthorization(toShare: nil, read: typesToRead) { success, error in
            if let error = error {
                print("HealthKit authorization error: \(error.localizedDescription)")
            } else {
                print("HealthKit authorization granted: \(success)")
            }
        }
    }
    
    func startWorkout() {
        guard !isWorkoutActive else { return }
        
        let configuration = HKWorkoutConfiguration()
        configuration.activityType = .other
        configuration.locationType = .unknown
        
        do {
            workoutSession = try HKWorkoutSession(healthStore: healthStore, configuration: configuration)
            workoutBuilder = workoutSession?.associatedWorkoutBuilder()
            
            workoutSession?.delegate = self
            workoutBuilder?.delegate = self
            
            workoutSession?.startActivity(with: Date())
            workoutBuilder?.beginCollection(at: Date()) { success, error in
                if let error = error {
                    print("Error beginning workout collection: \(error.localizedDescription)")
                }
            }
            
            DispatchQueue.main.async {
                self.isWorkoutActive = true
                self.workoutStartDate = Date()
                self.startTimer()
            }
            
        } catch {
            print("Error starting workout: \(error.localizedDescription)")
        }
    }
    
    func stopWorkout() {
        guard isWorkoutActive else { return }
        
        workoutSession?.end()
        workoutBuilder?.endCollection(at: Date()) { success, error in
            if let error = error {
                print("Error ending workout collection: \(error.localizedDescription)")
            }
        }
        
        workoutBuilder?.finishWorkout { workout, error in
            if let error = error {
                print("Error finishing workout: \(error.localizedDescription)")
            }
        }
        
        DispatchQueue.main.async {
            self.isWorkoutActive = false
            self.workoutStartDate = nil
            self.stopTimer()
        }
    }
    
    private func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            self.updateWorkoutDuration()
        }
    }
    
    private func stopTimer() {
        timer?.invalidate()
        timer = nil
    }
    
    private func updateWorkoutDuration() {
        guard let startDate = workoutStartDate else { return }
        workoutDuration = Date().timeIntervalSince(startDate)
    }
}

// MARK: - HKWorkoutSessionDelegate
extension WorkoutService: HKWorkoutSessionDelegate {
    func workoutSession(_ workoutSession: HKWorkoutSession, didChangeTo toState: HKWorkoutSessionState, from fromState: HKWorkoutSessionState, date: Date) {
        DispatchQueue.main.async {
            switch toState {
            case .running:
                self.isWorkoutActive = true
            case .ended:
                self.isWorkoutActive = false
            default:
                break
            }
        }
    }
    
    func workoutSession(_ workoutSession: HKWorkoutSession, didFailWithError error: Error) {
        print("Workout session failed: \(error.localizedDescription)")
    }
}

// MARK: - HKLiveWorkoutBuilderDelegate
extension WorkoutService: HKLiveWorkoutBuilderDelegate {
    func workoutBuilder(_ workoutBuilder: HKLiveWorkoutBuilder, didCollectDataOf collectedTypes: Set<HKSampleType>) {
        for type in collectedTypes {
            guard let quantityType = type as? HKQuantityType else { continue }
            
            let statistics = workoutBuilder.statistics(for: quantityType)
            
            switch quantityType {
            case HKQuantityType.quantityType(forIdentifier: .heartRate):
                if let heartRate = statistics?.mostRecentQuantity()?.doubleValue(for: HKUnit(from: "count/min")) {
                    DispatchQueue.main.async {
                        self.currentHeartRate = heartRate
                    }
                }
            default:
                break
            }
        }
    }
    
    func workoutBuilderDidCollectEvent(_ workoutBuilder: HKLiveWorkoutBuilder) {
        // Handle workout events
    }
}
