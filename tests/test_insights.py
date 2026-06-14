from app.insights import (
    get_personalized_tips,
    get_global_comparison,
    estimate_forest_offset,
    CATEGORY_MESSAGES,
    TIPS,
)


class TestGetPersonalizedTips:
    def test_returns_tips_for_all_categories(self):
        breakdown = {'transport': 5.0, 'diet': 3.0, 'energy': 2.0, 'consumption': 1.0}
        tips = get_personalized_tips(breakdown)
        assert len(tips) == 4
        assert tips[0]['category'] == 'transport'

    def test_skips_zero_value_categories(self):
        breakdown = {'transport': 5.0, 'diet': 0, 'energy': 2.0, 'consumption': 0}
        tips = get_personalized_tips(breakdown)
        assert len(tips) == 2
        categories = [t['category'] for t in tips]
        assert 'diet' not in categories
        assert 'consumption' not in categories

    def test_tips_have_required_fields(self):
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
        breakdown = {'transport': 1.0, 'diet': 5.0, 'energy': 2.0, 'consumption': 3.0}
        tips = get_personalized_tips(breakdown)
        values = [t['value'] for t in tips]
        assert values == sorted(values, reverse=True)

    def test_empty_breakdown(self):
        tips = get_personalized_tips({})
        assert tips == []

    def test_all_zero_breakdown(self):
        tips = get_personalized_tips({'transport': 0, 'diet': 0, 'energy': 0, 'consumption': 0})
        assert tips == []

    def test_returns_max_3_suggestions_per_category(self):
        breakdown = {'transport': 5.0}
        tips = get_personalized_tips(breakdown)
        assert len(tips[0]['suggestions']) <= 3


class TestGetGlobalComparison:
    def test_significantly_below(self):
        result = get_global_comparison(1.0)
        assert result['comparison'] == 'significantly_below'

    def test_below(self):
        result = get_global_comparison(3.0)
        assert result['comparison'] == 'below'

    def test_above(self):
        result = get_global_comparison(6.0)
        assert result['comparison'] == 'above'

    def test_significantly_above(self):
        result = get_global_comparison(10.0)
        assert result['comparison'] == 'significantly_above'

    def test_boundary(self):
        result = get_global_comparison(4.8)
        assert result['comparison'] == 'above'

    def test_message_present(self):
        result = get_global_comparison(3.0)
        assert 'message' in result
        assert len(result['message']) > 0

    def test_zero_total(self):
        result = get_global_comparison(0)
        assert result['comparison'] == 'significantly_below'

    def test_negative_total(self):
        result = get_global_comparison(-5)
        assert result['comparison'] == 'significantly_below'


class TestEstimateForestOffset:
    def test_returns_dict(self):
        result = estimate_forest_offset(5.0)
        assert 'trees' in result
        assert 'hectares' in result

    def test_correct_calculation(self):
        result = estimate_forest_offset(10.0)
        assert result['trees'] == 50
        assert result['hectares'] == 0.2

    def test_zero_total(self):
        result = estimate_forest_offset(0)
        assert result['trees'] == 0
        assert result['hectares'] == 0.0

    def test_negative_total(self):
        result = estimate_forest_offset(-5)
        assert result['trees'] == -25
        assert result['hectares'] == -0.1


class TestConstants:
    def test_category_messages_exists(self):
        expected_categories = {'excellent', 'good', 'average', 'above_average', 'high'}
        assert expected_categories == set(CATEGORY_MESSAGES.keys())

    def test_tips_cover_all_categories(self):
        expected_categories = {'transport', 'diet', 'energy', 'consumption'}
        assert expected_categories == set(TIPS.keys())

    def test_all_tips_have_required_fields(self):
        for category, tips in TIPS.items():
            for tip in tips:
                assert 'tip' in tip
                assert 'saving' in tip
                assert isinstance(tip['saving'], (int, float))
