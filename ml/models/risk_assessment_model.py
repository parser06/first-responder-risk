"""
Real-time Risk Assessment Model for First Responders
Uses heart rate features to predict risk levels
"""

import numpy as np
import joblib
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from ..features.heart_rate_features import HeartRateFeatures

@dataclass
class RiskPrediction:
    """Risk prediction result"""
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    risk_score: float  # 0-1 scale
    confidence: float  # Model confidence
    contributing_factors: Dict[str, float]  # Which features contributed most
    recommendations: List[str]  # Suggested actions
    timestamp: datetime

class RiskAssessmentModel:
    """Real-time risk assessment using heart rate data"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        self.feature_importance = None
        
        # Risk thresholds (can be adjusted based on training data)
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }
    
    def train(self, training_data: List[Dict], labels: List[str]):
        """
        Train the risk assessment model
        
        Args:
            training_data: List of feature dictionaries
            labels: List of risk level labels ('low', 'medium', 'high', 'critical')
        """
        print("Training risk assessment model...")
        
        # Convert to numpy arrays
        X = np.array([self._extract_features_from_dict(data) for data in training_data])
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Train anomaly detector
        self.anomaly_detector.fit(X_train_scaled)
        
        # Get feature importance
        self.feature_importance = dict(zip(
            self._get_feature_names(),
            self.model.feature_importances_
        ))
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Test accuracy: {test_score:.3f}")
        
        # Print feature importance
        print("\nFeature Importance:")
        for feature, importance in sorted(self.feature_importance.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {feature}: {importance:.3f}")
        
        self.is_trained = True
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'feature_importance': self.feature_importance
        }
    
    def predict_risk(self, features: HeartRateFeatures) -> RiskPrediction:
        """
        Predict risk level from heart rate features
        
        Args:
            features: HeartRateFeatures object
            
        Returns:
            RiskPrediction object
        """
        if not self.is_trained:
            return self._create_default_prediction(features)
        
        # Extract features
        X = self._extract_features_from_object(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Predict risk level
        risk_proba = self.model.predict_proba(X_scaled)[0]
        risk_classes = self.model.classes_
        
        # Get prediction with highest probability
        max_idx = np.argmax(risk_proba)
        predicted_risk = risk_classes[max_idx]
        confidence = risk_proba[max_idx]
        
        # Calculate risk score (weighted average)
        risk_score = self._calculate_risk_score(risk_proba, risk_classes)
        
        # Detect anomalies
        anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
        is_anomaly = anomaly_score < -0.1  # Threshold for anomaly detection
        
        # Get contributing factors
        contributing_factors = self._get_contributing_factors(features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            predicted_risk, risk_score, features, is_anomaly
        )
        
        return RiskPrediction(
            risk_level=predicted_risk,
            risk_score=risk_score,
            confidence=confidence,
            contributing_factors=contributing_factors,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _extract_features_from_object(self, features: HeartRateFeatures) -> np.ndarray:
        """Extract features from HeartRateFeatures object"""
        return np.array([
            features.current_hr,
            features.mean_hr,
            features.std_hr,
            features.min_hr,
            features.max_hr,
            features.hr_trend,
            features.hr_acceleration,
            features.rmssd,
            features.sdnn,
            features.pnn50,
            features.hr_reserve,
            features.intensity_percentage,
            features.hr_anomaly_score,
            features.stress_indicator,
            features.fatigue_indicator,
            features.time_since_start,
            self._encode_activity(features.recent_activity),
            self._encode_intensity_zone(features.intensity_zone)
        ])
    
    def _extract_features_from_dict(self, data: Dict) -> np.ndarray:
        """Extract features from dictionary (for training)"""
        return np.array([
            data.get('current_hr', 0),
            data.get('mean_hr', 0),
            data.get('std_hr', 0),
            data.get('min_hr', 0),
            data.get('max_hr', 0),
            data.get('hr_trend', 0),
            data.get('hr_acceleration', 0),
            data.get('rmssd', 0),
            data.get('sdnn', 0),
            data.get('pnn50', 0),
            data.get('hr_reserve', 0),
            data.get('intensity_percentage', 0),
            data.get('hr_anomaly_score', 0),
            data.get('stress_indicator', 0),
            data.get('fatigue_indicator', 0),
            data.get('time_since_start', 0),
            self._encode_activity(data.get('recent_activity', 'unknown')),
            self._encode_intensity_zone(data.get('intensity_zone', 'unknown'))
        ])
    
    def _encode_activity(self, activity: str) -> float:
        """Encode activity type to numeric"""
        activity_map = {
            'increasing': 1.0,
            'stable': 0.0,
            'decreasing': -1.0,
            'unknown': 0.0
        }
        return activity_map.get(activity, 0.0)
    
    def _encode_intensity_zone(self, zone: str) -> float:
        """Encode intensity zone to numeric"""
        zone_map = {
            'rest': 0.0,
            'light': 0.25,
            'moderate': 0.5,
            'vigorous': 0.75,
            'max': 1.0,
            'unknown': 0.0
        }
        return zone_map.get(zone, 0.0)
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretation"""
        return [
            'current_hr', 'mean_hr', 'std_hr', 'min_hr', 'max_hr',
            'hr_trend', 'hr_acceleration', 'rmssd', 'sdnn', 'pnn50',
            'hr_reserve', 'intensity_percentage', 'hr_anomaly_score',
            'stress_indicator', 'fatigue_indicator', 'time_since_start',
            'recent_activity', 'intensity_zone'
        ]
    
    def _calculate_risk_score(self, risk_proba: np.ndarray, risk_classes: np.ndarray) -> float:
        """Calculate weighted risk score"""
        risk_weights = {
            'low': 0.1,
            'medium': 0.4,
            'high': 0.7,
            'critical': 1.0
        }
        
        weighted_score = 0.0
        for i, risk_class in enumerate(risk_classes):
            weight = risk_weights.get(risk_class, 0.0)
            weighted_score += risk_proba[i] * weight
        
        return weighted_score
    
    def _get_contributing_factors(self, features: HeartRateFeatures) -> Dict[str, float]:
        """Get contributing factors for the prediction"""
        if not self.feature_importance:
            return {}
        
        # Get top contributing factors
        factors = {}
        feature_values = self._extract_features_from_object(features)
        feature_names = self._get_feature_names()
        
        for i, (name, importance) in enumerate(self.feature_importance.items()):
            if i < len(feature_values):
                # Weight by both importance and current value
                contribution = importance * abs(feature_values[i])
                factors[name] = contribution
        
        # Normalize contributions
        total_contribution = sum(factors.values())
        if total_contribution > 0:
            factors = {k: v / total_contribution for k, v in factors.items()}
        
        return factors
    
    def _generate_recommendations(self, risk_level: str, risk_score: float, 
                                features: HeartRateFeatures, is_anomaly: bool) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == 'critical' or risk_score > 0.9:
            recommendations.extend([
                "IMMEDIATE ATTENTION REQUIRED",
                "Consider emergency response",
                "Check officer status immediately",
                "Activate backup support"
            ])
        elif risk_level == 'high' or risk_score > 0.7:
            recommendations.extend([
                "High risk detected - monitor closely",
                "Consider taking a break",
                "Check for signs of stress or fatigue",
                "Ensure backup is available"
            ])
        elif risk_level == 'medium' or risk_score > 0.4:
            recommendations.extend([
                "Moderate risk - continue monitoring",
                "Consider reducing intensity",
                "Stay alert for changes"
            ])
        else:
            recommendations.append("All clear - continue normal operations")
        
        # Add specific recommendations based on features
        if features.stress_indicator > 0.7:
            recommendations.append("High stress detected - consider stress management")
        
        if features.fatigue_indicator > 0.6:
            recommendations.append("Fatigue detected - consider rest")
        
        if features.hr_anomaly_score > 0.8:
            recommendations.append("Unusual heart rate pattern - investigate")
        
        if is_anomaly:
            recommendations.append("Anomalous pattern detected - manual review recommended")
        
        return recommendations
    
    def _create_default_prediction(self, features: HeartRateFeatures) -> RiskPrediction:
        """Create default prediction when model is not trained"""
        # Simple rule-based fallback
        risk_score = 0.0
        risk_level = "low"
        
        if features.current_hr > 0:
            if features.current_hr > 180:
                risk_score = 0.9
                risk_level = "critical"
            elif features.current_hr > 160:
                risk_score = 0.7
                risk_level = "high"
            elif features.current_hr > 140:
                risk_score = 0.4
                risk_level = "medium"
        
        return RiskPrediction(
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=0.5,
            contributing_factors={},
            recommendations=["Model not trained - using basic rules"],
            timestamp=datetime.now()
        )
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'anomaly_detector': self.anomaly_detector,
                'feature_importance': self.feature_importance,
                'risk_thresholds': self.risk_thresholds
            }
            joblib.dump(model_data, filepath)
            print(f"Model saved to {filepath}")
        else:
            print("No trained model to save")
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.anomaly_detector = model_data['anomaly_detector']
            self.feature_importance = model_data['feature_importance']
            self.risk_thresholds = model_data['risk_thresholds']
            self.is_trained = True
            print(f"Model loaded from {filepath}")
        except Exception as e:
            print(f"Error loading model: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Test the risk assessment model
    model = RiskAssessmentModel()
    
    # Create some sample training data
    training_data = []
    labels = []
    
    # Generate synthetic training data
    np.random.seed(42)
    for i in range(1000):
        # Simulate different risk scenarios
        if i < 200:  # Low risk
            hr = np.random.normal(70, 10)
            label = 'low'
        elif i < 500:  # Medium risk
            hr = np.random.normal(120, 15)
            label = 'medium'
        elif i < 800:  # High risk
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
    results = model.train(training_data, labels)
    print(f"Training completed with accuracy: {results['test_accuracy']:.3f}")
    
    # Test prediction
    from ..features.heart_rate_features import HeartRateFeatures
    
    test_features = HeartRateFeatures(
        current_hr=160.0,
        mean_hr=140.0,
        std_hr=15.0,
        min_hr=120.0,
        max_hr=170.0,
        hr_trend=2.5,
        hr_acceleration=0.8,
        rmssd=25.0,
        sdnn=15.0,
        pnn50=8.0,
        resting_hr=65.0,
        max_hr_est=190.0,
        hr_reserve=75.0,
        intensity_zone="vigorous",
        intensity_percentage=80.0,
        hr_anomaly_score=0.3,
        stress_indicator=0.6,
        fatigue_indicator=0.4,
        time_since_start=45.0,
        recent_activity="increasing",
        timestamp=datetime.now()
    )
    
    prediction = model.predict_risk(test_features)
    print(f"\nRisk Prediction:")
    print(f"  Level: {prediction.risk_level}")
    print(f"  Score: {prediction.risk_score:.3f}")
    print(f"  Confidence: {prediction.confidence:.3f}")
    print(f"  Recommendations: {prediction.recommendations}")
