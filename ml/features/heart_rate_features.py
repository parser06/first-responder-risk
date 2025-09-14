"""
Real-time Heart Rate Feature Extraction for Risk Assessment
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class HeartRateSample:
    """Single heart rate measurement"""
    value: float
    timestamp: datetime
    confidence: float = 1.0
    source: str = "watch"

@dataclass
class HeartRateFeatures:
    """Extracted features from heart rate data"""
    # Basic statistics
    current_hr: float
    mean_hr: float
    std_hr: float
    min_hr: float
    max_hr: float
    
    # Trend analysis
    hr_trend: float  # slope over time window
    hr_acceleration: float  # second derivative
    
    # Variability metrics
    rmssd: float  # Root Mean Square of Successive Differences
    sdnn: float   # Standard Deviation of NN intervals
    pnn50: float  # Percentage of NN50 intervals
    
    # Intensity zones
    resting_hr: float
    max_hr: float
    hr_reserve: float
    intensity_zone: str  # 'rest', 'light', 'moderate', 'vigorous', 'max'
    intensity_percentage: float
    
    # Risk indicators
    hr_anomaly_score: float
    stress_indicator: float
    fatigue_indicator: float
    
    # Temporal features
    time_since_start: float  # minutes since monitoring started
    recent_activity: str  # 'increasing', 'decreasing', 'stable'
    
    timestamp: datetime

class HeartRateFeatureExtractor:
    """Real-time heart rate feature extraction"""
    
    def __init__(self, window_size: int = 60, min_samples: int = 10):
        """
        Initialize feature extractor
        
        Args:
            window_size: Number of samples to use for feature calculation
            min_samples: Minimum samples required for reliable features
        """
        self.window_size = window_size
        self.min_samples = min_samples
        self.hr_buffer: List[HeartRateSample] = []
        self.baseline_hr = None
        self.max_hr = None
        self.age = 30  # Default age, should be set per officer
        
    def set_officer_profile(self, age: int, resting_hr: float = None):
        """Set officer-specific parameters"""
        self.age = age
        self.max_hr = 220 - age  # Karvonen formula
        if resting_hr:
            self.baseline_hr = resting_hr
        else:
            self.baseline_hr = 60 + (0.4 * (self.max_hr - 60))  # Estimated resting HR
    
    def add_sample(self, hr_value: float, timestamp: datetime, confidence: float = 1.0) -> HeartRateFeatures:
        """
        Add new heart rate sample and extract features
        
        Args:
            hr_value: Heart rate in BPM
            timestamp: When the measurement was taken
            confidence: Measurement confidence (0-1)
            
        Returns:
            HeartRateFeatures object with all extracted features
        """
        # Add new sample to buffer
        sample = HeartRateSample(hr_value, timestamp, confidence)
        self.hr_buffer.append(sample)
        
        # Keep only recent samples
        if len(self.hr_buffer) > self.window_size:
            self.hr_buffer = self.hr_buffer[-self.window_size:]
        
        # Extract features
        return self._extract_features()
    
    def _extract_features(self) -> HeartRateFeatures:
        """Extract all features from current buffer"""
        if len(self.hr_buffer) < self.min_samples:
            return self._create_default_features()
        
        # Get heart rate values and timestamps
        hr_values = np.array([s.value for s in self.hr_buffer])
        timestamps = np.array([s.timestamp for s in self.hr_buffer])
        
        # Basic statistics
        current_hr = hr_values[-1]
        mean_hr = np.mean(hr_values)
        std_hr = np.std(hr_values)
        min_hr = np.min(hr_values)
        max_hr = np.max(hr_values)
        
        # Trend analysis
        hr_trend = self._calculate_trend(hr_values, timestamps)
        hr_acceleration = self._calculate_acceleration(hr_values, timestamps)
        
        # Variability metrics (simplified for real-time)
        rmssd = self._calculate_rmssd(hr_values)
        sdnn = std_hr
        pnn50 = self._calculate_pnn50(hr_values)
        
        # Intensity analysis
        intensity_zone, intensity_percentage = self._calculate_intensity(current_hr)
        hr_reserve = self._calculate_hr_reserve(current_hr)
        
        # Risk indicators
        hr_anomaly_score = self._calculate_anomaly_score(hr_values)
        stress_indicator = self._calculate_stress_indicator(hr_values)
        fatigue_indicator = self._calculate_fatigue_indicator(hr_values)
        
        # Temporal features
        time_since_start = self._calculate_time_since_start()
        recent_activity = self._classify_recent_activity(hr_values)
        
        return HeartRateFeatures(
            current_hr=current_hr,
            mean_hr=mean_hr,
            std_hr=std_hr,
            min_hr=min_hr,
            max_hr=max_hr,
            hr_trend=hr_trend,
            hr_acceleration=hr_acceleration,
            rmssd=rmssd,
            sdnn=sdnn,
            pnn50=pnn50,
            resting_hr=self.baseline_hr,
            max_hr_est=self.max_hr,
            hr_reserve=hr_reserve,
            intensity_zone=intensity_zone,
            intensity_percentage=intensity_percentage,
            hr_anomaly_score=hr_anomaly_score,
            stress_indicator=stress_indicator,
            fatigue_indicator=fatigue_indicator,
            time_since_start=time_since_start,
            recent_activity=recent_activity,
            timestamp=datetime.now()
        )
    
    def _calculate_trend(self, hr_values: np.ndarray, timestamps: np.ndarray) -> float:
        """Calculate heart rate trend (slope)"""
        if len(hr_values) < 2:
            return 0.0
        
        # Convert timestamps to seconds since first sample
        time_seconds = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
        
        # Linear regression to find slope
        if len(time_seconds) > 1:
            slope, _ = np.polyfit(time_seconds, hr_values, 1)
            return slope
        return 0.0
    
    def _calculate_acceleration(self, hr_values: np.ndarray, timestamps: np.ndarray) -> float:
        """Calculate heart rate acceleration (second derivative)"""
        if len(hr_values) < 3:
            return 0.0
        
        # Calculate first derivative (velocity)
        hr_velocity = np.diff(hr_values)
        time_diffs = np.diff([(t - timestamps[0]).total_seconds() for t in timestamps])
        
        if len(hr_velocity) > 1 and np.all(time_diffs[1:] > 0):
            # Calculate second derivative (acceleration)
            hr_acceleration = np.diff(hr_velocity) / time_diffs[1:]
            return np.mean(hr_acceleration)
        
        return 0.0
    
    def _calculate_rmssd(self, hr_values: np.ndarray) -> float:
        """Calculate RMSSD (simplified for real-time)"""
        if len(hr_values) < 2:
            return 0.0
        
        # Convert HR to RR intervals (approximate)
        rr_intervals = 60000 / hr_values  # Convert BPM to milliseconds
        
        # Calculate RMSSD
        rr_diffs = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(rr_diffs**2))
        
        return rmssd
    
    def _calculate_pnn50(self, hr_values: np.ndarray) -> float:
        """Calculate pNN50 (percentage of NN50 intervals)"""
        if len(hr_values) < 2:
            return 0.0
        
        # Convert HR to RR intervals
        rr_intervals = 60000 / hr_values
        
        # Calculate differences
        rr_diffs = np.abs(np.diff(rr_intervals))
        
        # Count differences > 50ms
        nn50_count = np.sum(rr_diffs > 50)
        total_intervals = len(rr_diffs)
        
        return (nn50_count / total_intervals) * 100 if total_intervals > 0 else 0.0
    
    def _calculate_intensity(self, current_hr: float) -> Tuple[str, float]:
        """Calculate exercise intensity zone"""
        if not self.max_hr or not self.baseline_hr:
            return "unknown", 0.0
        
        hr_reserve = self.max_hr - self.baseline_hr
        intensity_percentage = ((current_hr - self.baseline_hr) / hr_reserve) * 100
        
        if intensity_percentage < 20:
            return "rest", intensity_percentage
        elif intensity_percentage < 40:
            return "light", intensity_percentage
        elif intensity_percentage < 60:
            return "moderate", intensity_percentage
        elif intensity_percentage < 80:
            return "vigorous", intensity_percentage
        else:
            return "max", intensity_percentage
    
    def _calculate_hr_reserve(self, current_hr: float) -> float:
        """Calculate heart rate reserve percentage"""
        if not self.max_hr or not self.baseline_hr:
            return 0.0
        
        hr_reserve = self.max_hr - self.baseline_hr
        return ((current_hr - self.baseline_hr) / hr_reserve) * 100
    
    def _calculate_anomaly_score(self, hr_values: np.ndarray) -> float:
        """Calculate anomaly score for current heart rate"""
        if len(hr_values) < 3:
            return 0.0
        
        # Use Z-score for anomaly detection
        mean_hr = np.mean(hr_values[:-1])  # Exclude current value
        std_hr = np.std(hr_values[:-1])
        
        if std_hr > 0:
            z_score = abs(hr_values[-1] - mean_hr) / std_hr
            # Normalize to 0-1 scale
            anomaly_score = min(z_score / 3.0, 1.0)  # 3-sigma rule
            return anomaly_score
        
        return 0.0
    
    def _calculate_stress_indicator(self, hr_values: np.ndarray) -> float:
        """Calculate stress indicator based on HR variability"""
        if len(hr_values) < 5:
            return 0.0
        
        # Lower HRV indicates higher stress
        rmssd = self._calculate_rmssd(hr_values)
        
        # Normalize RMSSD (typical range: 20-60ms)
        if rmssd > 0:
            stress_score = max(0, 1 - (rmssd - 20) / 40)  # Higher score = more stress
            return min(stress_score, 1.0)
        
        return 0.0
    
    def _calculate_fatigue_indicator(self, hr_values: np.ndarray) -> float:
        """Calculate fatigue indicator based on HR patterns"""
        if len(hr_values) < 10:
            return 0.0
        
        # Look for increasing HR at rest (fatigue indicator)
        recent_hr = np.mean(hr_values[-5:])  # Last 5 samples
        earlier_hr = np.mean(hr_values[-10:-5])  # Previous 5 samples
        
        if earlier_hr > 0:
            hr_increase = (recent_hr - earlier_hr) / earlier_hr
            fatigue_score = max(0, hr_increase * 2)  # Scale the increase
            return min(fatigue_score, 1.0)
        
        return 0.0
    
    def _calculate_time_since_start(self) -> float:
        """Calculate time since monitoring started (minutes)"""
        if not self.hr_buffer:
            return 0.0
        
        start_time = self.hr_buffer[0].timestamp
        current_time = datetime.now()
        return (current_time - start_time).total_seconds() / 60.0
    
    def _classify_recent_activity(self, hr_values: np.ndarray) -> str:
        """Classify recent heart rate activity pattern"""
        if len(hr_values) < 5:
            return "unknown"
        
        recent_values = hr_values[-5:]
        trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
        
        if trend > 2:
            return "increasing"
        elif trend < -2:
            return "decreasing"
        else:
            return "stable"
    
    def _create_default_features(self) -> HeartRateFeatures:
        """Create default features when insufficient data"""
        return HeartRateFeatures(
            current_hr=0.0,
            mean_hr=0.0,
            std_hr=0.0,
            min_hr=0.0,
            max_hr=0.0,
            hr_trend=0.0,
            hr_acceleration=0.0,
            rmssd=0.0,
            sdnn=0.0,
            pnn50=0.0,
            resting_hr=self.baseline_hr or 60.0,
            max_hr_est=self.max_hr or 190.0,
            hr_reserve=0.0,
            intensity_zone="unknown",
            intensity_percentage=0.0,
            hr_anomaly_score=0.0,
            stress_indicator=0.0,
            fatigue_indicator=0.0,
            time_since_start=0.0,
            recent_activity="unknown",
            timestamp=datetime.now()
        )

# Example usage and testing
if __name__ == "__main__":
    # Test the feature extractor
    extractor = HeartRateFeatureExtractor(window_size=30, min_samples=5)
    extractor.set_officer_profile(age=30, resting_hr=65)
    
    # Simulate some heart rate data
    import random
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    for i in range(20):
        # Simulate increasing heart rate with some noise
        hr_value = 70 + i * 2 + random.uniform(-3, 3)
        timestamp = base_time + timedelta(seconds=i * 10)
        
        features = extractor.add_sample(hr_value, timestamp)
        print(f"Sample {i+1}: HR={hr_value:.1f}, Intensity={features.intensity_zone}, "
              f"Anomaly={features.hr_anomaly_score:.2f}, Stress={features.stress_indicator:.2f}")
