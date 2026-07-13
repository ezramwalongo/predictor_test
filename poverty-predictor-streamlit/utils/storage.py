"""
Data Storage Utility - Manage prediction history using CSV
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional


class PredictionStorage:
    """Store and retrieve prediction history"""
    
    def __init__(self, storage_dir: str = 'data'):
        self.storage_dir = storage_dir
        self.csv_file = os.path.join(storage_dir, 'predictions.csv')
        
        # Create directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize CSV if it doesn't exist
        if not os.path.exists(self.csv_file):
            self._create_csv()
    
    def _create_csv(self):
        """Create empty CSV with headers"""
        columns = [
            'timestamp',
            'region',
            'district',
            'household_size',
            'residence',
            'water_source',
            'toilet_type',
            'has_electricity',
            'has_mobile_phone',
            'has_radio',
            'has_television',
            'has_refrigerator',
            'has_bicycle',
            'has_motorcycle',
            'has_car',
            'probability',
            'classification',
            'score',
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(self.csv_file, index=False)
    
    def save_prediction(self, features: Dict, result: Dict) -> bool:
        """
        Save prediction to CSV
        
        Args:
            features: Input household characteristics
            result: Prediction result
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read existing data
            df = pd.read_csv(self.csv_file)
            
            # Create new row
            new_row = {
                'timestamp': datetime.now().isoformat(),
                'region': features.get('region', 'Unknown'),
                'district': features.get('district', 'Unknown'),
                'household_size': features.get('householdSize'),
                'residence': features.get('residence'),
                'water_source': features.get('waterSource'),
                'toilet_type': features.get('toiletType'),
                'has_electricity': int(features.get('hasElectricity', 0)),
                'has_mobile_phone': int(features.get('hasMobilePhone', 0)),
                'has_radio': int(features.get('hasRadio', 0)),
                'has_television': int(features.get('hasTelevision', 0)),
                'has_refrigerator': int(features.get('hasRefrigerator', 0)),
                'has_bicycle': int(features.get('hasBicycle', 0)),
                'has_motorcycle': int(features.get('hasMotorcycle', 0)),
                'has_car': int(features.get('hasCar', 0)),
                'probability': result.get('probability'),
                'classification': result.get('classification'),
                'score': result.get('score'),
            }
            
            # Append new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            
            return True
        
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return False
    
    def get_all_predictions(self) -> pd.DataFrame:
        """Get all predictions"""
        try:
            df = pd.read_csv(self.csv_file)
            if len(df) > 0:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error reading predictions: {e}")
            return pd.DataFrame()
    
    def get_statistics(self) -> Dict:
        """Get statistics from predictions"""
        df = self.get_all_predictions()
        
        if len(df) == 0:
            return {
                'total': 0,
                'poor': 0,
                'non_poor': 0,
                'poor_percentage': 0.0,
            }
        
        total = len(df)
        poor = len(df[df['classification'] == 'poor'])
        non_poor = len(df[df['classification'] == 'non-poor'])
        poor_percentage = (poor / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'poor': poor,
            'non_poor': non_poor,
            'poor_percentage': round(poor_percentage, 1),
        }
    
    def get_predictions_by_residence(self) -> Dict:
        """Get prediction counts by residence type"""
        df = self.get_all_predictions()
        
        if len(df) == 0:
            return {'Urban': 0, 'Rural': 0}
        
        residence_map = {1: 'Urban', 0: 'Rural'}
        
        counts = df['residence'].value_counts().to_dict()
        
        return {
            residence_map.get(k, str(k)): v
            for k, v in counts.items()
        }
    
    def get_poverty_rate_by_residence(self) -> Dict:
        """Get poverty rate by residence type"""
        df = self.get_all_predictions()
        
        if len(df) == 0:
            return {'Urban': 0.0, 'Rural': 0.0}
        
        residence_map = {1: 'Urban', 0: 'Rural'}
        
        result = {}
        for residence_code, residence_name in residence_map.items():
            subset = df[df['residence'] == residence_code]
            if len(subset) > 0:
                poor_count = len(subset[subset['classification'] == 'poor'])
                poverty_rate = (poor_count / len(subset) * 100)
                result[residence_name] = round(poverty_rate, 1)
            else:
                result[residence_name] = 0.0
        
        return result
    
    def get_poverty_trend(self, days: int = 10) -> pd.DataFrame:
        """Get poverty trend over last N days"""
        df = self.get_all_predictions()
        
        if len(df) == 0:
            return pd.DataFrame()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Filter last N days
        df = df[df['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(days=days)]
        
        # Group by date and count poor
        trend = df.groupby('date').apply(
            lambda x: {
                'date': x['date'].iloc[0],
                'total': len(x),
                'poor': len(x[x['classification'] == 'poor']),
                'poverty_rate': round(len(x[x['classification'] == 'poor']) / len(x) * 100, 1)
            }
        ).reset_index(drop=True)
        
        return pd.DataFrame(trend)
    
    def filter_predictions(
        self,
        residence: Optional[int] = None,
        poverty_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Filter predictions based on criteria"""
        df = self.get_all_predictions()
        
        if len(df) == 0:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Apply filters
        if residence is not None:
            df = df[df['residence'] == residence]
        
        if poverty_level is not None:
            df = df[df['classification'] == poverty_level]
        
        if start_date is not None:
            df = df[df['timestamp'] >= start_date]
        
        if end_date is not None:
            df = df[df['timestamp'] <= end_date]
        
        return df.sort_values('timestamp', ascending=False)
    
    def export_csv(self, filename: str = 'predictions_export.csv') -> str:
        """Export all predictions to CSV"""
        df = self.get_all_predictions()
        export_path = os.path.join(self.storage_dir, filename)
        df.to_csv(export_path, index=False)
        return export_path


# Initialize global storage instance
storage = PredictionStorage()
