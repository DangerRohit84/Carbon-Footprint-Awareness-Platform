"""Carbon footprint calculation engine.

Maps lifestyle inputs (transport, diet, energy, consumption) to
CO2-equivalent emissions using established carbon factors.
"""

from typing import Dict, List, Any

# Carbon factors in tons CO2e per unit.
# Transport: per km traveled.
# Diet: per day.
# Energy and consumption: per month.
CARBON_FACTORS: Dict[str, Dict[str, float]] = {
    'transport': {
        'car': 0.24,       # Petrol/diesel car
        'bus': 0.08,       # City bus
        'train': 0.04,     # Rail transit
        'bicycle': 0.0,    # Zero-emission
        'walk': 0.0,       # Zero-emission
        'motorcycle': 0.16,
        'ev': 0.08,        # Electric vehicle (grid-dependent)
    },
    'diet': {
        'vegan': 1.5,
        'vegetarian': 2.0,
        'pescatarian': 2.5,
        'omnivore_low': 3.0,     # Meat 1-2x / week
        'omnivore_medium': 4.5,  # Meat daily
        'omnivore_high': 6.5,    # Meat multiple times daily
    },
    'energy': {
        'renewable': 0.05,  # Solar / wind / hydro
        'mixed': 0.25,      # Grid average mix
        'fossil': 0.5,      # Coal / gas
    },
    'consumption': {
        'minimalist': 0.1,
        'moderate': 0.25,
        'high': 0.5,
        'excessive': 0.8,
    },
}


def validate_inputs(data: Dict[str, Any]) -> List[str]:
    """Validate all user-supplied inputs. Returns a list of error messages (empty if valid)."""
    errors: List[str] = []

    transport_type: str = data.get('transport_type', '').strip().lower()
    if transport_type not in CARBON_FACTORS['transport']:
        errors.append('Invalid transport type.')

    # Distance must be a non-negative number within a realistic range.
    try:
        transport_distance: float = float(data.get('transport_distance', 0))
        if transport_distance < 0 or transport_distance > 1000:
            errors.append('Transport distance must be between 0 and 1000 km per week.')
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
    Factor lookups use .get() with a default of 0 for safety.
    """
    transport_factor: float = CARBON_FACTORS['transport'].get(transport_type, 0)
    diet_factor: float = CARBON_FACTORS['diet'].get(diet, 0)
    energy_factor: float = CARBON_FACTORS['energy'].get(energy, 0)
    consumption_factor: float = CARBON_FACTORS['consumption'].get(consumption, 0)

    # Annualize: weekly distance * 52 weeks / 1000 to convert kg to tons.
    transport_emissions: float = transport_factor * transport_distance * 52 / 1000
    # Daily diet * 365 days / 1000.
    diet_emissions: float = diet_factor * 365 / 1000
    # Monthly factors * 12 months.
    energy_emissions: float = energy_factor * 12
    consumption_emissions: float = consumption_factor * 12

    total: float = round(
        transport_emissions + diet_emissions + energy_emissions + consumption_emissions, 2,
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
    """Classify a footprint total into a qualitative tier for display."""
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
