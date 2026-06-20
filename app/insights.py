"""Insights engine for personalized recommendations.

Provides carbon footprint analysis including reduction tips,
global average comparison, and forest offset estimation.
"""

from typing import Any, Dict, List

__all__ = [
    'TIPS',
    'CATEGORY_MESSAGES',
    'get_personalized_tips',
    'get_global_comparison',
    'estimate_forest_offset',
]

TIPS: Dict[str, List[Dict[str, Any]]] = {
    'transport': [
        {
            'tip': 'Walk or cycle for short trips '
                   '- zero emissions and great exercise!',
            'saving': 0.3,
        },
        {
            'tip': 'Use public transport instead of a car whenever possible.',
            'saving': 0.6,
        },
        {
            'tip': 'Carpool with colleagues or neighbors '
                   'to reduce per-person emissions.',
            'saving': 0.5,
        },
        {
            'tip': 'Switch to an electric or hybrid vehicle '
                   'for your next car purchase.',
            'saving': 0.8,
        },
        {
            'tip': 'Plan errands efficiently to minimize driving distance.',
            'saving': 0.2,
        },
        {
            'tip': 'Work from home when possible '
                   'to eliminate commute emissions.',
            'saving': 1.0,
        },
        {
            'tip': 'Maintain proper tire pressure '
                   'to improve fuel efficiency.',
            'saving': 0.1,
        },
    ],
    'diet': [
        {
            'tip': 'Try having one meat-free day per week - it adds up!',
            'saving': 0.4,
        },
        {
            'tip': 'Reduce food waste by planning meals '
                   'and storing food properly.',
            'saving': 0.3,
        },
        {
            'tip': 'Choose locally sourced and seasonal produce.',
            'saving': 0.2,
        },
        {
            'tip': 'Transition to a plant-based diet '
                   'for the largest dietary impact.',
            'saving': 1.5,
        },
        {
            'tip': 'Compost food scraps '
                   'instead of sending them to landfill.',
            'saving': 0.2,
        },
        {
            'tip': 'Avoid single-use plastics and packaging '
                   'when grocery shopping.',
            'saving': 0.1,
        },
    ],
    'energy': [
        {
            'tip': 'Switch to a renewable energy provider for your home.',
            'saving': 2.0,
        },
        {
            'tip': 'Install solar panels to generate clean energy.',
            'saving': 3.0,
        },
        {
            'tip': 'Use LED bulbs and energy-efficient appliances.',
            'saving': 0.5,
        },
        {
            'tip': 'Improve home insulation '
                   'to reduce heating and cooling needs.',
            'saving': 0.8,
        },
        {
            'tip': 'Unplug electronics when not in use '
                   'to avoid phantom energy drain.',
            'saving': 0.2,
        },
        {
            'tip': 'Set your thermostat a few degrees lower '
                   'in winter and higher in summer.',
            'saving': 0.4,
        },
        {
            'tip': 'Use a smart power strip '
                   'to automatically cut power to idle devices.',
            'saving': 0.15,
        },
    ],
    'consumption': [
        {
            'tip': 'Buy second-hand items '
                   'instead of new whenever possible.',
            'saving': 0.5,
        },
        {
            'tip': 'Repair items instead of replacing them.',
            'saving': 0.4,
        },
        {
            'tip': 'Borrow or rent items you use infrequently.',
            'saving': 0.3,
        },
        {
            'tip': 'Choose products with minimal '
                   'and recyclable packaging.',
            'saving': 0.2,
        },
        {
            'tip': 'Invest in high-quality items that last longer.',
            'saving': 0.6,
        },
        {
            'tip': 'Practice minimalism - '
                   'buy only what you truly need.',
            'saving': 1.0,
        },
        {
            'tip': 'Support brands with strong '
                   'environmental commitments.',
            'saving': 0.3,
        },
    ],
}

CATEGORY_MESSAGES: Dict[str, str] = {
    'excellent': (
        'Outstanding! Your carbon footprint is exceptionally low. '
        'You are a true environmental steward!'
    ),
    'good': (
        'Great job! Your carbon footprint is below average. '
        'Keep up the sustainable habits!'
    ),
    'average': (
        'Your carbon footprint is around the global average. '
        'There is room for improvement in every category.'
    ),
    'above_average': (
        'Your carbon footprint is above average. '
        'Consider making changes in high-impact areas '
        'like transport and diet.'
    ),
    'high': (
        'Your carbon footprint is high. '
        'Small changes in daily habits '
        'can make a big difference over time.'
    ),
}


def get_personalized_tips(
    breakdown: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Return up to 3 tips per category, sorted by highest impact first."""
    tips: List[Dict[str, Any]] = []
    sorted_cats = sorted(
        breakdown.items(), key=lambda x: x[1], reverse=True,
    )
    for category, value in sorted_cats:
        if value > 0:
            cat_tips: List[Dict[str, Any]] = TIPS.get(category, [])
            tips.append({
                'category': category,
                'value': value,
                'suggestions': cat_tips[:3],
            })
    return tips


def get_global_comparison(total: float) -> Dict[str, str]:
    """Compare the user's footprint to the global average."""
    avg: float = 4.8
    if total < avg * 0.5:
        comp: str = 'significantly_below'
        msg: str = (
            'Your footprint is significantly below '
            'the global average of 4.8 tons CO2e per year.'
        )
    elif total < avg:
        comp = 'below'
        msg = (
            'Your footprint is below '
            'the global average of 4.8 tons CO2e per year.'
        )
    elif total < avg * 1.5:
        comp = 'above'
        msg = (
            'Your footprint is above '
            'the global average of 4.8 tons CO2e per year.'
        )
    else:
        comp = 'significantly_above'
        msg = (
            'Your footprint is significantly above '
            'the global average of 4.8 tons CO2e per year.'
        )
    return {'comparison': comp, 'message': msg}


def estimate_forest_offset(total: float) -> Dict[str, Any]:
    """Estimate trees and forest area to offset annual footprint."""
    trees: int = round(total * 5)
    hectares: float = round(total * 0.02, 2)
    return {'trees': trees, 'hectares': hectares}
