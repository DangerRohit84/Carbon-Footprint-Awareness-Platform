"""Carbon footprint calculation engine.

Maps lifestyle inputs (transport, diet, energy, consumption) to
CO2-equivalent emissions using established carbon factors.
"""

from typing import Any, Dict, List

__all__ = [
    'CARBON_FACTORS',
    'validate_inputs',
    'calculate_carbon_footprint',
    'get_category',
]

# Carbon factors in tons CO2e per unit.
# Transport: per km traveled. Diet: per day.
# Energy and consumption: per month.
CARBON_FACTORS: Dict[str, Dict[str, float]] = {
    'transport': {
        'car': 0.24,
        'bus': 0.08,
        'train': 0.04,
        'bicycle': 0.0,
        'walk': 0.0,
        'motorcycle': 0.16,
        'ev': 0.08,
    },
    'diet': {
        'vegan': 1.5,
        'vegetarian': 2.0,
        'pescatarian': 2.5,
        'omnivore_low': 3.0,
        'omnivore_medium': 4.5,
        'omnivore_high': 6.5,
    },
    'energy': {
        'renewable': 0.05,
        'mixed': 0.25,
        'fossil': 0.5,
    },
    'consumption': {
        'minimalist': 0.1,
        'moderate': 0.25,
        'high': 0.5,
        'excessive': 0.8,
    },
}


def validate_inputs(data: Dict[str, Any]) -> List[str]:
    """Validate all user inputs. Returns list of error messages."""
    errors: List[str] = []
    transport_type: str = data.get('transport_type', '').strip().lower()
    if transport_type not in CARBON_FACTORS['transport']:
        errors.append('Invalid transport type.')
    try:
        distance: float = float(data.get('transport_distance', 0))
        if distance < 0 or distance > 1000:
            errors.append(
                'Transport distance must be between 0 and 1000 km per week.'
            )
    except (ValueError, TypeError):
        errors.append('Transport distance must be a valid number.')
    diet: str = data.get('diet', '').strip().lower()
    if diet not in CARBON_FACTORS['diet']:
        errors.append('Invalid diet type.')
    energy: str = data.get('energy', '').strip().lower()
    if energy not in CARBON_FACTORS['energy']:
        errors.append('Invalid energy source.')
    consumption: str = data.get('consumption', '').strip().lower()
    if consumption not in CARBON_FACTORS['consumption']:
        errors.append('Invalid consumption level.')
    return errors


def calculate_carbon_footprint(
    transport_type: str,
    transport_distance: float,
    diet: str,
    energy: str,
    consumption: str,
) -> Dict[str, Any]:
    """Calculate annual carbon footprint in tons CO2e from lifestyle inputs.

    Returns dict with total, per-category breakdown, and category label.
    """
    tf: float = CARBON_FACTORS['transport'].get(transport_type, 0)
    df: float = CARBON_FACTORS['diet'].get(diet, 0)
    ef: float = CARBON_FACTORS['energy'].get(energy, 0)
    cf: float = CARBON_FACTORS['consumption'].get(consumption, 0)
    transport_emissions: float = tf * transport_distance * 52 / 1000
    diet_emissions: float = df * 365 / 1000
    energy_emissions: float = ef * 12
    consumption_emissions: float = cf * 12
    total: float = round(
        transport_emissions + diet_emissions
        + energy_emissions + consumption_emissions,
        2,
    )
    breakdown: Dict[str, float] = {
        'transport': round(transport_emissions, 2),
        'diet': round(diet_emissions, 2),
        'energy': round(energy_emissions, 2),
        'consumption': round(consumption_emissions, 2),
    }
    category: str = get_category(total)
    return {'total': total, 'breakdown': breakdown, 'category': category}


def get_category(total: float) -> str:
    """Classify a footprint total into a qualitative tier."""
    if total <= 2.5:
        return 'excellent'
    elif total <= 5.0:
        return 'good'
    elif total <= 8.0:
        return 'average'
    elif total <= 12.0:
        return 'above_average'
    else:
        return 'high'
