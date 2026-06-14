"""Unit tests for the insights module.

Covers personalized tips, global comparison, forest offset
estimation, and constants validation.
"""

from app.insights import (
    get_personalized_tips,
    get_global_comparison,
    estimate_forest_offset,
    CATEGORY_MESSAGES,
    TIPS,
)


class TestGetPersonalizedTips:
    """Tests for get_personalized_tips."""

    def test_returns_tips_for_all_categories(self):
        """All non-zero categories should appear in the tips list."""
        breakdown = {'transport': 5.0, 'diet': 3.0, 'energy': 2.0, 'consumption': 1.0}
        tips = get_personalized_tips(breakdown)
        assert len(tips) == 4
        # Highest value category should be first.
        assert tips[0]['category'] == 'transport'

    def test_skips_zero_value_categories(self):
        """Categories with zero value should not generate tips."""
        breakdown = {'transport': 5.0, 'diet': 0, 'energy': 2.0, 'consumption': 0}
        tips = get_personalized_tips(breakdown)
        assert len(tips) == 2
        categories = [t['category'] for t in tips]
        assert 'diet' not in categories
        assert 'consumption' not in categories

    def test_tips_have_required_fields(self):
        """Every tip suggestion should have a tip text and saving estimate."""
        breakdown = {'transport': 5.0, 'diet': 3.0, 'energy': 2.0, 'consumption': 1.0}
        tips = get_personalized_tips(breakdown)
        for area in tips:
            assert 'category' in area
            assert 'value' in area
            assert 'suggestions' in area
            for suggestion in area['suggestions']:
                assert 'tip' in suggestion
                assert 'saving' in suggestion

    def test_sorted_by_highest_value_first(self):
        """Categories should be sorted in descending order of impact."""
        breakdown = {'transport': 1.0, 'diet': 5.0, 'energy': 2.0, 'consumption': 3.0}
        tips = get_personalized_tips(breakdown)
        values = [t['value'] for t in tips]
        assert values == sorted(values, reverse=True)

    def test_empty_breakdown(self):
        """An empty breakdown should return an empty tips list."""
        tips = get_personalized_tips({})
        assert tips == []

    def test_all_zero_breakdown(self):
        """All-zero breakdown should return an empty tips list."""
        tips = get_personalized_tips({'transport': 0, 'diet': 0, 'energy': 0, 'consumption': 0})
        assert tips == []

    def test_returns_max_3_suggestions_per_category(self):
        """Each category should show at most 3 suggestions."""
        breakdown = {'transport': 5.0}
        tips = get_personalized_tips(breakdown)
        assert len(tips[0]['suggestions']) <= 3


class TestGetGlobalComparison:
    """Tests for get_global_comparison."""

    def test_significantly_below(self):
        """Total under 50% of global average."""
        assert get_global_comparison(1.0)['comparison'] == 'significantly_below'

    def test_below(self):
        """Total under global average but above 50%."""
        assert get_global_comparison(3.0)['comparison'] == 'below'

    def test_above(self):
        """Total between global average and 150%."""
        assert get_global_comparison(6.0)['comparison'] == 'above'

    def test_significantly_above(self):
        """Total over 150% of global average."""
        assert get_global_comparison(10.0)['comparison'] == 'significantly_above'

    def test_boundary(self):
        """Exactly at the global average."""
        assert get_global_comparison(4.8)['comparison'] == 'above'

    def test_message_present(self):
        """Comparison should always include a human-readable message."""
        result = get_global_comparison(3.0)
        assert 'message' in result
        assert len(result['message']) > 0

    def test_zero_total(self):
        """Zero total should be classified as significantly below."""
        assert get_global_comparison(0)['comparison'] == 'significantly_below'

    def test_negative_total(self):
        """Negative total should safely fall into significantly below."""
        assert get_global_comparison(-5)['comparison'] == 'significantly_below'


class TestEstimateForestOffset:
    """Tests for estimate_forest_offset."""

    def test_returns_dict(self):
        """Offset result should contain both trees and hectares."""
        result = estimate_forest_offset(5.0)
        assert 'trees' in result
        assert 'hectares' in result

    def test_correct_calculation(self):
        """Verify forest offset arithmetic: 5 trees and 0.02 hectares per ton."""
        result = estimate_forest_offset(10.0)
        assert result['trees'] == 50
        assert result['hectares'] == 0.2

    def test_zero_total(self):
        """Zero footprint needs zero offset."""
        result = estimate_forest_offset(0)
        assert result['trees'] == 0
        assert result['hectares'] == 0.0

    def test_negative_total(self):
        """Negative footprint should produce negative offset (edge case)."""
        result = estimate_forest_offset(-5)
        assert result['trees'] == -25
        assert result['hectares'] == -0.1


class TestConstants:
    """Tests for module-level constants."""

    def test_category_messages_exists(self):
        """All five categories should have a display message."""
        expected_categories = {'excellent', 'good', 'average', 'above_average', 'high'}
        assert expected_categories == set(CATEGORY_MESSAGES.keys())

    def test_tips_cover_all_categories(self):
        """All four lifestyle categories should have tips."""
        expected_categories = {'transport', 'diet', 'energy', 'consumption'}
        assert expected_categories == set(TIPS.keys())

    def test_all_tips_have_required_fields(self):
        """Every tip entry should have tip text and a numeric saving value."""
        for category, tips in TIPS.items():
            for tip in tips:
                assert 'tip' in tip
                assert 'saving' in tip
                assert isinstance(tip['saving'], (int, float))
