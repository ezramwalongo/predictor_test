"""
Recommendations Engine - Generates actionable insights based on poverty classification
"""

from typing import Dict, List


class RecommendationsEngine:
    """Generate recommendations based on poverty prediction and household characteristics"""
    
    def __init__(self):
        self.recommendations_poor = {
            'high': [
                {
                    'category': 'Water & Sanitation',
                    'title': 'Improve Water Access',
                    'description': 'Access to safe water is critical for health and productivity',
                    'action': 'Connect to piped water system or install water harvesting',
                    'impact': 'Reduces waterborne diseases, saves time on water collection',
                },
                {
                    'category': 'Water & Sanitation',
                    'title': 'Improve Toilet Facility',
                    'description': 'Improved sanitation reduces disease burden',
                    'action': 'Install flush toilet or improved pit latrine',
                    'impact': 'Improves health, increases dignity, attracts investment',
                },
                {
                    'category': 'Energy',
                    'title': 'Access to Electricity',
                    'description': 'Electricity enables productive activities and improves quality of life',
                    'action': 'Connect to grid or install solar power system',
                    'impact': 'Enables evening work, improves lighting, powers appliances',
                },
            ],
            'medium': [
                {
                    'category': 'Communication',
                    'title': 'Mobile Phone Access',
                    'description': 'Mobile phones enable market access and emergency services',
                    'action': 'Acquire a basic mobile phone and SIM card',
                    'impact': 'Enables market information, emergency contact, income opportunities',
                },
                {
                    'category': 'Income Generation',
                    'title': 'Develop Income Sources',
                    'description': 'Diversify income sources for stability',
                    'action': 'Start small business, join cooperative, seek employment',
                    'impact': 'Increases household income, reduces vulnerability',
                },
                {
                    'category': 'Assets',
                    'title': 'Build Productive Assets',
                    'description': 'Productive assets enable income generation',
                    'action': 'Invest in tools, equipment, or livestock',
                    'impact': 'Increases productivity and income potential',
                },
            ],
            'low': [
                {
                    'category': 'Information',
                    'title': 'Access Information',
                    'description': 'Radio provides agricultural and market information',
                    'action': 'Acquire radio for news and agricultural programs',
                    'impact': 'Improves decision-making, reduces risk',
                },
                {
                    'category': 'Education',
                    'title': 'Invest in Education',
                    'description': 'Education improves long-term income prospects',
                    'action': 'Ensure children attend school, pursue skills training',
                    'impact': 'Increases human capital, improves future earnings',
                },
            ],
        }
        
        self.recommendations_non_poor = {
            'high': [
                {
                    'category': 'Asset Maintenance',
                    'title': 'Maintain Existing Assets',
                    'description': 'Regular maintenance preserves asset value',
                    'action': 'Schedule regular maintenance for all assets',
                    'impact': 'Extends asset lifespan, prevents costly repairs',
                },
                {
                    'category': 'Financial Planning',
                    'title': 'Build Emergency Fund',
                    'description': 'Financial reserves protect against shocks',
                    'action': 'Save 3-6 months of expenses in emergency fund',
                    'impact': 'Provides security, enables investment opportunities',
                },
            ],
            'medium': [
                {
                    'category': 'Livelihood',
                    'title': 'Diversify Income Sources',
                    'description': 'Multiple income sources reduce vulnerability',
                    'action': 'Develop secondary income sources',
                    'impact': 'Increases resilience, improves financial stability',
                },
                {
                    'category': 'Investment',
                    'title': 'Invest in Business',
                    'description': 'Business investment can increase income',
                    'action': 'Invest in business expansion or new venture',
                    'impact': 'Increases income, creates employment',
                },
            ],
            'low': [
                {
                    'category': 'Community',
                    'title': 'Participate in Community',
                    'description': 'Community engagement strengthens social capital',
                    'action': 'Join community groups, participate in activities',
                    'impact': 'Builds networks, strengthens community',
                },
                {
                    'category': 'Environment',
                    'title': 'Sustainable Practices',
                    'description': 'Environmental sustainability ensures long-term prosperity',
                    'action': 'Adopt sustainable farming/business practices',
                    'impact': 'Protects environment, ensures long-term viability',
                },
            ],
        }
    
    def get_recommendations(
        self,
        classification: str,
        features: Dict,
    ) -> Dict:
        """
        Generate recommendations based on poverty classification
        
        Args:
            classification: 'poor' or 'non-poor'
            features: Household characteristics
        
        Returns:
            Dictionary with summary and recommendations by priority
        """
        
        if classification == 'poor':
            recommendations = self.recommendations_poor
            summary = 'Focus on basic needs: water, sanitation, energy, and income generation'
        else:
            recommendations = self.recommendations_non_poor
            summary = 'Focus on asset maintenance, financial planning, and livelihood diversification'
        
        # Flatten recommendations by priority
        all_recommendations = []
        for priority in ['high', 'medium', 'low']:
            for rec in recommendations.get(priority, []):
                rec['priority'] = priority
                all_recommendations.append(rec)
        
        return {
            'summary': summary,
            'recommendations': all_recommendations,
        }


# Initialize global recommendations engine
recommendations_engine = RecommendationsEngine()


def get_recommendations(
    classification: str,
    features: Dict,
) -> Dict:
    """Convenience function to get recommendations"""
    return recommendations_engine.get_recommendations(classification, features)
