"""Integration tests for Flask routes and the FootprintRecord model.

Tests page rendering, form submission, API endpoints,
security headers, HTTP methods, and model behavior.
"""

from app.models import FootprintRecord, MAX_RECORDS


# -------- Page rendering tests --------

def test_index_returns_200(client):
    """Home page should load successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'EcoTrack' in response.data


def test_calculator_returns_200(client):
    """Calculator page should load successfully."""
    response = client.get('/calculator')
    assert response.status_code == 200
    assert b'Carbon Footprint Calculator' in response.data


def test_tips_returns_200(client):
    """Tips page should load successfully."""
    response = client.get('/tips')
    assert response.status_code == 200
    assert b'Tips' in response.data


def test_history_returns_200(client):
    """History page should load successfully (even when empty)."""
    response = client.get('/history')
    assert response.status_code == 200


def test_history_empty_state(client):
    """Empty history should show the 'no calculations yet' message."""
    response = client.get('/history')
    assert b'No calculations yet' in response.data


# -------- Form submission tests --------

def test_calculate_post_valid(client):
    """Valid form data should redirect to results page."""
    response = client.post('/calculate', data={
        'transport_type': 'bicycle',
        'transport_distance': '50',
        'diet': 'vegan',
        'energy': 'renewable',
        'consumption': 'minimalist',
        'csrf_token': 'test',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your Carbon Footprint Results' in response.data


def test_calculate_post_invalid_shows_errors(client):
    """Invalid form data should re-render with error messages."""
    response = client.post('/calculate', data={
        'transport_type': 'invalid',
        'transport_distance': '50',
        'diet': 'vegan',
        'energy': 'renewable',
        'consumption': 'minimalist',
        'csrf_token': 'test',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid transport type' in response.data


# -------- API endpoint tests --------

def test_api_calculate_valid(client):
    """Valid JSON payload should return a successful API response."""
    response = client.post('/api/calculate', json={
        'transport_type': 'car',
        'transport_distance': '100',
        'diet': 'omnivore_medium',
        'energy': 'mixed',
        'consumption': 'moderate',
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'result' in data
    assert 'category' in data
    assert 'tips' in data
    assert 'comparison' in data


def test_api_calculate_invalid(client):
    """Invalid JSON payload should return a 400 error with details."""
    response = client.post('/api/calculate', json={
        'transport_type': 'invalid',
        'transport_distance': '100',
        'diet': 'vegan',
        'energy': 'renewable',
        'consumption': 'minimalist',
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'errors' in data


def test_api_calculate_missing_data(client):
    """Empty JSON body should return a 400 error."""
    response = client.post('/api/calculate', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


# -------- History integration test --------

def test_history_after_calculation(client):
    """After submitting a valid calculation, the history page should show it."""
    client.post('/calculate', data={
        'transport_type': 'walk',
        'transport_distance': '10',
        'diet': 'vegetarian',
        'energy': 'renewable',
        'consumption': 'moderate',
        'csrf_token': 'test',
    }, follow_redirects=True)
    response = client.get('/history')
    assert response.status_code == 200
    assert b'walk' in response.data.lower() or b'Walk' in response.data


# -------- Security tests --------

def test_security_headers(client):
    """All responses should include security-related HTTP headers."""
    response = client.get('/')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert 'Content-Security-Policy' in response.headers


# -------- HTTP method tests --------

def test_get_on_calculate_post_returns_405(client):
    """GET requests to the POST-only /calculate route should return 405."""
    response = client.get('/calculate')
    assert response.status_code == 405


def test_api_calculate_form_encoded_fallback(client):
    """Form-encoded POST to the JSON API should be rejected."""
    response = client.post('/api/calculate', data={
        'transport_type': 'car',
        'transport_distance': '100',
        'diet': 'omnivore_medium',
        'energy': 'mixed',
        'consumption': 'moderate',
    })
    assert response.status_code == 400


# -------- Model tests --------

class TestFootprintRecord:
    """Tests for the FootprintRecord in-memory model."""

    def test_save_and_get_all(self):
        """Saving a record should make it appear in get_all()."""
        result = {'total': 5.0, 'breakdown': {'transport': 2.0}, 'category': 'average'}
        record = FootprintRecord({
            'transport_type': 'car', 'diet': 'omnivore_low',
            'energy': 'mixed', 'consumption': 'moderate',
        }, result, 100)
        FootprintRecord.save(record)
        all_records = FootprintRecord.get_all()
        assert len(all_records) == 1
        assert all_records[0]['total'] == 5.0
        assert all_records[0]['category'] == 'average'

    def test_get_recent(self):
        """get_recent should return the most recent N records."""
        for i in range(5):
            result = {'total': float(i), 'breakdown': {}, 'category': 'good'}
            record = FootprintRecord({}, result, 0)
            FootprintRecord.save(record)
        recent = FootprintRecord.get_recent(2)
        assert len(recent) == 2

    def test_max_records_cap(self):
        """The record store should not exceed MAX_RECORDS entries."""
        for i in range(MAX_RECORDS + 10):
            result = {'total': float(i), 'breakdown': {}, 'category': 'good'}
            record = FootprintRecord({}, result, 0)
            FootprintRecord.save(record)
        assert len(FootprintRecord._records) == MAX_RECORDS

    def test_to_dict_format(self):
        """to_dict should produce a correctly structured dictionary."""
        result = {'total': 3.5, 'breakdown': {'transport': 1.0}, 'category': 'good'}
        record = FootprintRecord({
            'transport_type': 'bicycle', 'diet': 'vegan',
            'energy': 'renewable', 'consumption': 'minimalist',
        }, result, 50)
        d = record.to_dict()
        assert d['total'] == 3.5
        assert d['transport_type'] == 'bicycle'
        assert d['transport_distance'] == 50
        assert 'timestamp' in d
