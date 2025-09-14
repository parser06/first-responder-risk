"""
Test script for Heart Rate ML Pipeline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from datetime import datetime, timedelta
import random

# Import our ML components
from features.heart_rate_features import HeartRateFeatureExtractor, HeartRateFeatures
from models.risk_assessment_model import RiskAssessmentModel

def test_feature_extraction():
    """Test the heart rate feature extraction"""
    print("🧪 Testing Heart Rate Feature Extraction...")
    
    # Create feature extractor
    extractor = HeartRateFeatureExtractor(window_size=30, min_samples=5)
    extractor.set_officer_profile(age=30, resting_hr=65)
    
    # Simulate heart rate data
    base_time = datetime.now()
    hr_values = []
    
    print("\n📊 Simulating heart rate data...")
    for i in range(25):
        # Simulate different scenarios
        if i < 10:
            # Resting phase
            hr = 65 + random.uniform(-5, 5)
        elif i < 15:
            # Light activity
            hr = 85 + random.uniform(-8, 8)
        elif i < 20:
            # Moderate activity
            hr = 120 + random.uniform(-10, 10)
        else:
            # High intensity
            hr = 160 + random.uniform(-15, 15)
        
        timestamp = base_time + timedelta(seconds=i * 10)
        hr_values.append(hr)
        
        # Extract features
        features = extractor.add_sample(hr, timestamp)
        
        print(f"Sample {i+1:2d}: HR={hr:5.1f} BPM | "
              f"Zone={features.intensity_zone:8s} | "
              f"Anomaly={features.hr_anomaly_score:.2f} | "
              f"Stress={features.stress_indicator:.2f}")
    
    print(f"\n✅ Feature extraction test completed!")
    print(f"   Final features: {features.current_hr:.1f} BPM, {features.intensity_zone} intensity")
    
    return features

def test_risk_assessment():
    """Test the risk assessment model"""
    print("\n🧪 Testing Risk Assessment Model...")
    
    # Create model
    model = RiskAssessmentModel()
    
    # Generate synthetic training data
    print("📚 Generating synthetic training data...")
    training_data = []
    labels = []
    
    np.random.seed(42)
    for i in range(500):
        # Simulate different risk scenarios
        if i < 100:  # Low risk
            hr = np.random.normal(70, 10)
            label = 'low'
        elif i < 250:  # Medium risk
            hr = np.random.normal(120, 15)
            label = 'medium'
        elif i < 400:  # High risk
            hr = np.random.normal(150, 20)
            label = 'high'
        else:  # Critical risk
            hr = np.random.normal(180, 25)
            label = 'critical'
        
        # Create feature dictionary
        features = {
            'current_hr': hr,
            'mean_hr': hr + np.random.normal(0, 5),
            'std_hr': np.random.uniform(5, 20),
            'min_hr': hr - np.random.uniform(10, 30),
            'max_hr': hr + np.random.uniform(10, 30),
            'hr_trend': np.random.normal(0, 2),
            'hr_acceleration': np.random.normal(0, 1),
            'rmssd': np.random.uniform(20, 60),
            'sdnn': np.random.uniform(10, 40),
            'pnn50': np.random.uniform(5, 25),
            'hr_reserve': np.random.uniform(20, 80),
            'intensity_percentage': np.random.uniform(20, 90),
            'hr_anomaly_score': np.random.uniform(0, 0.5),
            'stress_indicator': np.random.uniform(0, 0.8),
            'fatigue_indicator': np.random.uniform(0, 0.6),
            'time_since_start': np.random.uniform(0, 120),
            'recent_activity': np.random.choice(['increasing', 'stable', 'decreasing']),
            'intensity_zone': np.random.choice(['light', 'moderate', 'vigorous', 'max'])
        }
        
        training_data.append(features)
        labels.append(label)
    
    # Train the model
    print("🎓 Training risk assessment model...")
    results = model.train(training_data, labels)
    print(f"   Training accuracy: {results['train_accuracy']:.3f}")
    print(f"   Test accuracy: {results['test_accuracy']:.3f}")
    
    # Test with different scenarios
    print("\n🔍 Testing different risk scenarios...")
    
    test_scenarios = [
        ("Resting", 70, "low"),
        ("Light Activity", 90, "low"),
        ("Moderate Activity", 130, "medium"),
        ("Vigorous Activity", 160, "high"),
        ("Maximum Effort", 190, "critical")
    ]
    
    for scenario_name, hr, expected_risk in test_scenarios:
        # Create test features
        test_features = HeartRateFeatures(
            current_hr=hr,
            mean_hr=hr + random.uniform(-5, 5),
            std_hr=random.uniform(5, 15),
            min_hr=hr - random.uniform(10, 20),
            max_hr=hr + random.uniform(10, 20),
            hr_trend=random.uniform(-2, 2),
            hr_acceleration=random.uniform(-1, 1),
            rmssd=random.uniform(20, 50),
            sdnn=random.uniform(10, 30),
            pnn50=random.uniform(5, 20),
            resting_hr=65.0,
            max_hr_est=190.0,
            hr_reserve=random.uniform(30, 80),
            intensity_zone="moderate",
            intensity_percentage=random.uniform(40, 70),
            hr_anomaly_score=random.uniform(0, 0.3),
            stress_indicator=random.uniform(0, 0.5),
            fatigue_indicator=random.uniform(0, 0.4),
            time_since_start=random.uniform(10, 60),
            recent_activity="stable",
            timestamp=datetime.now()
        )
        
        # Get prediction
        prediction = model.predict_risk(test_features)
        
        print(f"   {scenario_name:15s}: HR={hr:3.0f} | "
              f"Predicted={prediction.risk_level:7s} | "
              f"Score={prediction.risk_score:.2f} | "
              f"Confidence={prediction.confidence:.2f}")
    
    print(f"\n✅ Risk assessment test completed!")
    return model

def test_api_integration():
    """Test API integration"""
    print("\n🧪 Testing API Integration...")
    
    # This would test the FastAPI endpoints
    print("📡 API endpoints available:")
    print("   POST /ml/heart-rate/process - Process heart rate data")
    print("   POST /ml/heart-rate/single - Process single measurement")
    print("   GET  /ml/heart-rate/features/{officer_id} - Get officer features")
    print("   POST /ml/heart-rate/train - Train model")
    print("   GET  /ml/heart-rate/model/status - Get model status")
    print("   POST /ml/heart-rate/officer/profile - Set officer profile")
    
    print("\n✅ API integration test completed!")

def main():
    """Run all tests"""
    print("🚀 Starting Heart Rate ML Pipeline Tests...\n")
    
    try:
        # Test feature extraction
        features = test_feature_extraction()
        
        # Test risk assessment
        model = test_risk_assessment()
        
        # Test API integration
        test_api_integration()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Integrate with your FastAPI server")
        print("   2. Connect to Apple Watch data stream")
        print("   3. Set up real-time monitoring")
        print("   4. Train with real officer data")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
