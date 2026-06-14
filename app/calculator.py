CARBON_FACTORS = {
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
        'renewable': 0.5,
        'mixed': 2.5,
        'fossil': 5.0,
    },
    'consumption': {
        'minimalist': 1.0,
        'moderate': 2.5,
        'high': 4.5,
        'excessive': 7.0,
    },
}


def validate_inputs(data):
    errors = []
    transport_type = data.get('transport_type', '').strip().lower()
    if transport_type not in CARBON_FACTORS['transport']:
        errors.append('Invalid transport type.')

    try:
        transport_distance = float(data.get('transport_distance', 0))
        if transport_distance < 0 or transport_distance > 1000:
            errors.append('Transport distance must be between 0 and 1000 km per week.')
    except (ValueError, TypeError):
        errors.append('Transport distance must be a valid number.')

    diet = data.get('diet', '').strip().lower()
    if diet not in CARBON_FACTORS['diet']:
        errors.append('Invalid diet type.')

    energy = data.get('energy', '').strip().lower()
    if energy not in CARBON_FACTORS['energy']:
        errors.append('Invalid energy source.')

    consumption = data.get('consumption', '').strip().lower()
    if consumption not in CARBON_FACTORS['consumption']:
        errors.append('Invalid consumption level.')

    return errors


def calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption):
    transport_factor = CARBON_FACTORS['transport'][transport_type]
    diet_factor = CARBON_FACTORS['diet'][diet]
    energy_factor = CARBON_FACTORS['energy'][energy]
    consumption_factor = CARBON_FACTORS['consumption'][consumption]

    transport_emissions = transport_factor * transport_distance * 52 / 1000
    diet_emissions = diet_factor * 365 / 1000
    energy_emissions = energy_factor * 12
    consumption_emissions = consumption_factor * 12

    total = round(transport_emissions + diet_emissions + energy_emissions + consumption_emissions, 2)

    breakdown = {
        'transport': round(transport_emissions, 2),
        'diet': round(diet_emissions, 2),
        'energy': round(energy_emissions, 2),
        'consumption': round(consumption_emissions, 2),
    }

    return {'total': total, 'breakdown': breakdown}


def get_category(total):
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
