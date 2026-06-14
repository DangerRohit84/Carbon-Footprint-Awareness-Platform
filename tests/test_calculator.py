import pytest
from app.calculator import (
    validate_inputs,
    calculate_carbon_footprint,
    get_category,
    CARBON_FACTORS,
)


class TestValidateInputs:
    def test_valid_inputs(self):
        data = {
            'transport_type': 'bicycle',
            'transport_distance': '50',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert errors == []

    def test_invalid_transport_type(self):
        data = {
            'transport_type': 'rocket',
            'transport_distance': '50',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert 'Invalid transport type.' in errors

    def test_negative_distance(self):
        data = {
            'transport_type': 'car',
            'transport_distance': '-10',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert any('Transport distance' in e for e in errors)

    def test_oversized_distance(self):
        data = {
            'transport_type': 'car',
            'transport_distance': '2000',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert any('Transport distance' in e for e in errors)

    def test_invalid_diet(self):
        data = {
            'transport_type': 'walk',
            'transport_distance': '10',
            'diet': 'carnivore',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert 'Invalid diet type.' in errors

    def test_invalid_energy(self):
        data = {
            'transport_type': 'walk',
            'transport_distance': '10',
            'diet': 'vegan',
            'energy': 'nuclear',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert 'Invalid energy source.' in errors

    def test_invalid_consumption(self):
        data = {
            'transport_type': 'walk',
            'transport_distance': '10',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'superhigh',
        }
        errors = validate_inputs(data)
        assert 'Invalid consumption level.' in errors

    def test_non_numeric_distance(self):
        data = {
            'transport_type': 'car',
            'transport_distance': 'abc',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert any('valid number' in e for e in errors)


class TestCalculateCarbonFootprint:
    def test_minimal_footprint(self):
        result = calculate_carbon_footprint('walk', 0, 'vegan', 'renewable', 'minimalist')
        assert result['total'] >= 0
        assert all(k in result['breakdown'] for k in ['transport', 'diet', 'energy', 'consumption'])

    def test_maximal_footprint(self):
        result = calculate_carbon_footprint('car', 1000, 'omnivore_high', 'fossil', 'excessive')
        assert result['total'] > 10
        assert result['breakdown']['transport'] > 10

    def test_bicycle_zero_emissions_transport(self):
        result = calculate_carbon_footprint('bicycle', 100, 'vegan', 'renewable', 'minimalist')
        assert result['breakdown']['transport'] == 0

    def test_breakdown_values(self):
        result = calculate_carbon_footprint('car', 100, 'omnivore_medium', 'mixed', 'moderate')
        breakdown = result['breakdown']
        assert breakdown['transport'] > 0
        assert breakdown['diet'] > 0
        assert breakdown['energy'] > 0
        assert breakdown['consumption'] > 0
        assert abs(sum(breakdown.values()) - result['total']) < 0.01

    def test_known_values(self):
        result = calculate_carbon_footprint('car', 100, 'omnivore_low', 'renewable', 'moderate')
        transport_factor = CARBON_FACTORS['transport']['car']
        diet_factor = CARBON_FACTORS['diet']['omnivore_low']
        energy_factor = CARBON_FACTORS['energy']['renewable']
        consumption_factor = CARBON_FACTORS['consumption']['moderate']
        expected = round(
            transport_factor * 100 * 52 / 1000
            + diet_factor * 365 / 1000
            + energy_factor * 12
            + consumption_factor * 12,
            2,
        )
        assert result['total'] == expected


class TestGetCategory:
    def test_excellent(self):
        assert get_category(1.0) == 'excellent'

    def test_good(self):
        assert get_category(3.0) == 'good'

    def test_average(self):
        assert get_category(6.0) == 'average'

    def test_above_average(self):
        assert get_category(10.0) == 'above_average'

    def test_high(self):
        assert get_category(15.0) == 'high'

    def test_boundary_excellent_good(self):
        assert get_category(2.5) == 'excellent'
        assert get_category(2.51) == 'good'
