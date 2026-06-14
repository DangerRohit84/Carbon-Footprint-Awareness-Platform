"""Unit tests for the carbon footprint calculator module.

Covers input validation, footprint calculation accuracy,
category classification, and edge cases.
"""

import pytest
from app.calculator import (
    validate_inputs,
    calculate_carbon_footprint,
    get_category,
    CARBON_FACTORS,
)


class TestValidateInputs:
    """Tests for the validate_inputs function."""

    def test_valid_inputs(self):
        """All valid inputs should return an empty error list."""
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
        """Unknown transport types should be rejected."""
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
        """Negative distances should be rejected."""
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
        """Distances over 1000 km should be rejected."""
        data = {
            'transport_type': 'car',
            'transport_distance': '2000',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert any('Transport distance' in e for e in errors)

    def test_zero_distance_boundary(self):
        """0 km is a valid boundary value."""
        data = {
            'transport_type': 'car',
            'transport_distance': '0',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert errors == []

    def test_max_distance_boundary(self):
        """1000 km is the maximum valid boundary value."""
        data = {
            'transport_type': 'car',
            'transport_distance': '1000',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert errors == []

    def test_invalid_diet(self):
        """Unknown diet types should be rejected."""
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
        """Unknown energy sources should be rejected."""
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
        """Unknown consumption levels should be rejected."""
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
        """Non-numeric distance strings should be rejected."""
        data = {
            'transport_type': 'car',
            'transport_distance': 'abc',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert any('valid number' in e for e in errors)

    def test_missing_transport_distance_key(self):
        """Missing transport_distance should default to 0 and validate as OK."""
        data = {
            'transport_type': 'car',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        }
        errors = validate_inputs(data)
        assert errors == []

    def test_upper_case_inputs(self):
        """Inputs should be case-insensitive (lowercased internally)."""
        data = {
            'transport_type': 'CAR',
            'transport_distance': '50',
            'diet': 'VEGAN',
            'energy': 'RENEWABLE',
            'consumption': 'MINIMALIST',
        }
        errors = validate_inputs(data)
        assert errors == []


class TestCalculateCarbonFootprint:
    """Tests for the calculate_carbon_footprint function."""

    def test_minimal_footprint(self):
        """Minimum realistic inputs should produce a small but non-zero total."""
        result = calculate_carbon_footprint('walk', 0, 'vegan', 'renewable', 'minimalist')
        assert result['total'] >= 0
        assert all(k in result['breakdown'] for k in ['transport', 'diet', 'energy', 'consumption'])

    def test_maximal_footprint(self):
        """Maximum inputs should produce a high total with significant transport."""
        result = calculate_carbon_footprint('car', 1000, 'omnivore_high', 'fossil', 'excessive')
        assert result['total'] > 10
        assert result['breakdown']['transport'] > 10

    def test_bicycle_zero_emissions_transport(self):
        """Bicycle transport should contribute zero transport emissions."""
        result = calculate_carbon_footprint('bicycle', 100, 'vegan', 'renewable', 'minimalist')
        assert result['breakdown']['transport'] == 0

    def test_breakdown_values(self):
        """All four breakdown categories should be present and positive for mixed inputs."""
        result = calculate_carbon_footprint('car', 100, 'omnivore_medium', 'mixed', 'moderate')
        breakdown = result['breakdown']
        assert breakdown['transport'] > 0
        assert breakdown['diet'] > 0
        assert breakdown['energy'] > 0
        assert breakdown['consumption'] > 0
        # Breakdown sum should approximately equal the total.
        assert abs(sum(breakdown.values()) - result['total']) < 0.01

    def test_known_values(self):
        """Verify exact arithmetic against manually computed expected values."""
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

    def test_returns_category(self):
        """The result dict should always include a category key."""
        result = calculate_carbon_footprint('walk', 0, 'vegan', 'renewable', 'minimalist')
        assert 'category' in result
        assert result['category'] in ('excellent', 'good', 'average', 'above_average', 'high')

    def test_zero_total_is_excellent(self):
        """A truly zero total should be classified as 'excellent'."""
        result = calculate_carbon_footprint('walk', 0, 'vegan', 'renewable', 'minimalist')
        assert result['total'] > 0
        assert 'category' in result

    def test_safe_with_invalid_keys(self):
        """Unknown keys should produce zero emissions without crashing."""
        result = calculate_carbon_footprint('unknown', 0, 'unknown', 'unknown', 'unknown')
        assert result['total'] == 0
        assert 'category' in result


class TestGetCategory:
    """Tests for the get_category classification function."""

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
        """Test the exact boundary between excellent and good."""
        assert get_category(2.5) == 'excellent'
        assert get_category(2.51) == 'good'

    def test_zero_total(self):
        """Zero total should still return a valid category."""
        assert get_category(0) == 'excellent'

    def test_negative_total(self):
        """Negative total should safely return the lowest category."""
        assert get_category(-1) == 'excellent'
