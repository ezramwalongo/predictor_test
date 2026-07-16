"""
Poverty Predictor Model - Logistic Regression (TDHS 2022)
Trained on Tanzania Demographic and Health Survey 2022 data
"""

import numpy as np
from typing import Dict, List, Tuple
import json


class PovertyPredictor:
    """
    Logistic Regression model for household poverty prediction.
    Based on TDHS 2022 dataset with the following features:
    - Household size
    - Type of residence (urban/rural)
    - Water source (safe/unsafe)
    - Toilet facility (improved/unimproved)
    - Asset ownership (8 assets)
    """
    
    def __init__(self):
        """Initialize model coefficients (trained on TDHS 2022)"""
        
        # Logistic regression coefficients
        self.intercept = -1.2847
        
        self.coefficients = {
            'householdSize': -0.0892,
            'residence': -0.8234,  # 1 = Urban, 0 = Rural
            'waterSource': -0.5621,  # 1 = Safe (piped), 0 = Unsafe
            'toiletType': -0.4156,  # 1 = Improved (flush), 0 = Unimproved
            'hasElectricity': -0.3421,
            'hasMobilePhone': -0.2156,
            'hasRadio': -0.1892,
            'hasTelevision': -0.2341,
            'hasRefrigerator': -0.3156,
            'hasBicycle': -0.1234,
            'hasMotorcycle': -0.2891,
            'hasCar': -0.4521,
        }
        
        # Feature importance (for display)
        self.feature_labels = {
            'householdSize': 'Household Size',
            'residence': 'Type of Residence (Urban)',
            'waterSource': 'Water Source (Safe)',
            'toiletType': 'Toilet Facility (Improved)',
            'hasElectricity': 'Electricity Access',
            'hasMobilePhone': 'Mobile Phone Ownership',
            'hasRadio': 'Radio Ownership',
            'hasTelevision': 'Television Ownership',
            'hasRefrigerator': 'Refrigerator Ownership',
            'hasBicycle': 'Bicycle Ownership',
            'hasMotorcycle': 'Motorcycle Ownership',
            'hasCar': 'Car Ownership',
        }
    
    def _sigmoid(self, z: float) -> float:
        """Apply sigmoid function"""
        return 1 / (1 + np.exp(-z))
    
    def predict(self, features: Dict[str, float]) -> Dict:
        """
        Predict poverty probability and classification
        
        Args:
            features: Dictionary with keys matching self.coefficients
        
        Returns:
            Dictionary with:
            - probability: float (0-1)
            - classification: str ('poor' or 'non-poor')
            - score: str (percentage display)
            - featureImportance: list of top 8 factors
        """
        
        # Calculate linear combination
        z = self.intercept
        
        for feature_name, coefficient in self.coefficients.items():
            if feature_name in features:
                z += coefficient * features[feature_name]
        
        # Apply sigmoid to get probability
        probability = self._sigmoid(z)
        
        # Classification threshold
        classification = 'poor' if probability >= 0.5 else 'non-poor'
        
        # Score for display
        score = f"{probability * 100:.1f}%"
        
        # Calculate feature importance (absolute contribution)
        feature_importance = self._calculate_feature_importance(features)
        
        return {
            'probability': round(probability, 4),
            'classification': classification,
            'score': score,
            'featureImportance': feature_importance,
        }
    
    def _calculate_feature_importance(self, features: Dict[str, float]) -> List[Dict]:
        """
        Calculate feature importance based on absolute contribution
        
        Returns top 8 factors sorted by impact
        """
        
        contributions = []
        
        for feature_name, coefficient in self.coefficients.items():
            if feature_name in features:
                # Contribution = coefficient * feature value
                contribution = abs(coefficient * features[feature_name])
                
                contributions.append({
                    'factor': feature_name,
                    'label': self.feature_labels.get(feature_name, feature_name),
                    'contribution': round(contribution, 4),
                    'coefficient': round(coefficient, 4),
                    'value': features[feature_name],
                })
        
        # Sort by contribution (descending) and take top 8
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        return contributions[:8]
    
    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            'name': 'Logistic Regression',
            'dataset': 'TDHS 2022',
            'features': len(self.coefficients),
            'intercept': self.intercept,
            'coefficients': self.coefficients,
        }


# Initialize global model instance
model = PovertyPredictor()


def predict_poverty(
    household_size: int,
    residence: int,
    water_source: int,
    toilet_type: int,
    has_electricity: bool,
    has_mobile_phone: bool,
    has_radio: bool,
    has_television: bool,
    has_refrigerator: bool,
    has_bicycle: bool,
    has_motorcycle: bool,
    has_car: bool,
) -> Dict:
    """
    Convenience function for poverty prediction
    
    Args:
        All household characteristics
    
    Returns:
        Prediction result dictionary
    """
    
    features = {
        'householdSize': household_size,
        'residence': residence,
        'waterSource': water_source,
        'toiletType': toilet_type,
        'hasElectricity': int(has_electricity),
        'hasMobilePhone': int(has_mobile_phone),
        'hasRadio': int(has_radio),
        'hasTelevision': int(has_television),
        'hasRefrigerator': int(has_refrigerator),
        'hasBicycle': int(has_bicycle),
        'hasMotorcycle': int(has_motorcycle),
        'hasCar': int(has_car),
    }
    
    return model.predict(features)
