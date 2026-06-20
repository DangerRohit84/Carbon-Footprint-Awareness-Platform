"""Integration tests for Flask routes, model, API, and security."""

import json
import os
from app.models import DATA_FILE, FootprintRecord, MAX_RECORDS


# -------- Page rendering tests --------

def test_index_returns_200(client):
    """Home page should return 200."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'EcoTrack' in response.data


def test_calculator_returns_200(client):
    """Calculator page should return 200."""
    response = client.get('/calculator')
    assert response.status_code == 200
    assert b'Carbon Footprint Calculator' in response.data


def test_tips_returns_200(client):
    """Tips page should return 200."""
    response = client.get('/tips')
    assert response.status_code == 200
    assert b'Tips' in response.data


def test_history_returns_200(client):
    """History page should return 200."""
    response = client.get('/history')
    assert response.status_code == 200


def test_history_empty_state(client):
    """Empty history should show no-calculations message."""
    response = client.get('/history')
    assert b'No calculations yet' in response.data


def test_404_returns_404(client):
    """Non-existent route should return 404."""
    response = client.get('/nonexistent')
    assert response.status_code == 404


# -------- Form submission tests --------

def test_calculate_post_valid(client):
    """Valid form submission should show results page."""
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
    """Invalid form submission should show error messages."""
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


def test_calculate_post_zero_distance(client):
    """Zero distance should be accepted and return results."""
    response = client.post('/calculate', data={
        'transport_type': 'walk',
        'transport_distance': '0',
        'diet': 'vegan',
        'energy': 'renewable',
        'consumption': 'minimalist',
        'csrf_token': 'test',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your Carbon Footprint Results' in response.data


def test_calculate_post_max_distance(client):
    """Max distance (1000 km) should be accepted."""
    response = client.post('/calculate', data={
        'transport_type': 'train',
        'transport_distance': '1000',
        'diet': 'vegetarian',
        'energy': 'mixed',
        'consumption': 'moderate',
        'csrf_token': 'test',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your Carbon Footprint Results' in response.data


# -------- API endpoint tests --------

def test_api_calculate_valid(client):
    """Valid API request should return 200 with result data."""
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
    """Invalid API request should return 400 with errors."""
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
    """Empty API request should return 400."""
    response = client.post('/api/calculate', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_api_calculate_all_edge_options(client):
    """API should accept all valid option combinations."""
    for t_type in ['walk', 'bicycle', 'bus', 'train', 'car',
                   'motorcycle', 'ev']:
        response = client.post('/api/calculate', json={
            'transport_type': t_type,
            'transport_distance': '50',
            'diet': 'vegan',
            'energy': 'renewable',
            'consumption': 'minimalist',
        })
        assert response.status_code == 200, f"Failed for {t_type}"


# -------- History integration tests --------

def test_history_after_calculation(client):
    """History should show a calculation after it is submitted."""
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


def test_history_shows_multiple_records(client):
    """History should show multiple records."""
    for _ in range(3):
        client.post('/calculate', data={
            'transport_type': 'car', 'transport_distance': '50',
            'diet': 'vegan', 'energy': 'renewable',
            'consumption': 'moderate', 'csrf_token': 'test',
        }, follow_redirects=True)
    response = client.get('/history')
    html = response.data.decode('utf-8')
    assert html.count('<tr>') >= 3


# -------- History export tests --------

def test_history_export_csv(client):
    """CSV export should include calculation data."""
    client.post('/calculate', data={
        'transport_type': 'bus', 'transport_distance': '30',
        'diet': 'vegan', 'energy': 'mixed',
        'consumption': 'moderate', 'csrf_token': 'test',
    }, follow_redirects=True)
    response = client.get('/history/export')
    assert response.status_code == 200
    assert response.content_type == 'text/csv; charset=utf-8'
    cd = 'attachment; filename=eco-track-history.csv'
    assert response.headers.get('Content-Disposition') == cd
    body = response.data.decode('utf-8')
    assert body.startswith('timestamp')
    assert 'bus' in body


def test_history_export_empty(client):
    """CSV export with no records should have only the header row."""
    response = client.get('/history/export')
    assert response.status_code == 200
    lines = response.data.decode('utf-8').strip().split('\n')
    assert len(lines) == 1
    expected = (
        'timestamp,transport_type,transport_distance,'
        'diet,energy,consumption,total,category'
    )
    assert lines[0] == expected


# -------- Trend computation tests --------

def test_trend_flat_for_single_record(client):
    """Single record should not generate a trend."""
    from app.routes import _compute_trends
    records = [{'total': 5.0, 'timestamp': '2024-01-01'}]
    trend = _compute_trends(records)
    assert trend['has_trend'] is False


def test_trend_down(client):
    """Decreasing total should show downward trend."""
    from app.routes import _compute_trends
    records = [
        {'total': 8.0, 'timestamp': '2024-01-01'},
        {'total': 5.0, 'timestamp': '2024-06-01'},
    ]
    trend = _compute_trends(records)
    assert trend['has_trend'] is True
    assert trend['direction'] == 'down'
    assert trend['change'] == 3.0


def test_trend_up(client):
    """Increasing total should show upward trend."""
    from app.routes import _compute_trends
    records = [
        {'total': 3.0, 'timestamp': '2024-01-01'},
        {'total': 6.0, 'timestamp': '2024-06-01'},
    ]
    trend = _compute_trends(records)
    assert trend['has_trend'] is True
    assert trend['direction'] == 'up'
    assert trend['change'] == 3.0


def test_trend_flat(client):
    """Unchanged total should show flat trend."""
    from app.routes import _compute_trends
    records = [
        {'total': 5.0, 'timestamp': '2024-01-01'},
        {'total': 5.0, 'timestamp': '2024-06-01'},
    ]
    trend = _compute_trends(records)
    assert trend['has_trend'] is True
    assert trend['direction'] == 'flat'
    assert trend['change'] == 0.0


def test_trend_uses_first_and_last_only(client):
    """Trend should compare first and last record only."""
    from app.routes import _compute_trends
    records = [
        {'total': 10.0, 'timestamp': '2024-01-01'},
        {'total': 8.0, 'timestamp': '2024-03-01'},
        {'total': 6.0, 'timestamp': '2024-06-01'},
    ]
    trend = _compute_trends(records)
    assert trend['has_trend'] is True
    assert trend['direction'] == 'down'
    assert trend['change'] == 4.0


# -------- Model edge case tests --------

def test_get_recent_empty():
    """get_recent on empty records should return empty list."""
    from app.models import FootprintRecord
    FootprintRecord._records = []
    FootprintRecord._loaded = True
    recent = FootprintRecord.get_recent(5)
    assert recent == []


def test_get_recent_more_than_available():
    """get_recent with limit > records should return all."""
    from app.models import FootprintRecord
    for i in range(3):
        FootprintRecord.save(FootprintRecord(
            {}, {'total': float(i), 'breakdown': {}, 'category': 'good'}, 0,
        ))
    recent = FootprintRecord.get_recent(100)
    assert len(recent) == 3


def test_max_records_exact():
    """Exactly MAX_RECORDS should stay within limit."""
    from app.models import FootprintRecord
    for i in range(MAX_RECORDS):
        FootprintRecord.save(FootprintRecord(
            {}, {'total': float(i), 'breakdown': {}, 'category': 'good'}, 0,
        ))
    assert len(FootprintRecord.get_all()) == MAX_RECORDS


def test_corrupted_json_handled(tmp_path):
    """Corrupted data file should not crash the app."""
    from app.models import DATA_FILE, FootprintRecord
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        f.write('{invalid json}')
    FootprintRecord._loaded = False
    records = FootprintRecord.get_all()
    assert records == []


# -------- Cache-control and header tests --------

def test_html_not_cached(client):
    """HTML responses should not have Cache-Control."""
    response = client.get('/')
    header = response.headers.get('Cache-Control', '')
    assert 'max-age' not in header


def test_hsts_header(client):
    """HSTS header should be present with correct value."""
    response = client.get('/')
    hsts = response.headers.get('Strict-Transport-Security')
    assert hsts == 'max-age=31536000; includeSubDomains'


def test_referrer_policy_header(client):
    """Referrer-Policy header should be present."""
    response = client.get('/')
    assert response.headers.get('Referrer-Policy') is not None


def test_permissions_policy_header(client):
    """Permissions-Policy header should be present."""
    response = client.get('/')
    assert response.headers.get('Permissions-Policy') is not None


# -------- Security tests --------

def test_security_headers(client):
    """All required security headers should be present."""
    response = client.get('/')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    hsts = 'max-age=31536000; includeSubDomains'
    assert response.headers.get('Strict-Transport-Security') == hsts
    assert 'Content-Security-Policy' in response.headers


def test_security_cookie_attributes(client):
    """Session cookies should have HttpOnly and SameSite=Lax."""
    with client:
        client.get('/')
        cookie_headers = [
            v for v in client.get('/').headers
            if v[0] == 'Set-Cookie'
        ]
        for header_val in cookie_headers:
            assert 'HttpOnly' in str(header_val)
            assert 'SameSite=Lax' in str(header_val)


def test_csp_does_not_allow_external_scripts(client):
    """CSP should not allow external script sources."""
    response = client.get('/')
    csp = response.headers.get('Content-Security-Policy', '')
    assert 'https://' not in csp or 'script-src' not in csp


# -------- HTTP method tests --------

def test_get_on_calculate_post_returns_405(client):
    """GET on POST-only route should return 405."""
    response = client.get('/calculate')
    assert response.status_code == 405


def test_api_calculate_form_encoded_fallback(client):
    """API with form-encoded data (not JSON) should return 400."""
    response = client.post('/api/calculate', data={
        'transport_type': 'car', 'transport_distance': '100',
        'diet': 'omnivore_medium', 'energy': 'mixed',
        'consumption': 'moderate',
    })
    assert response.status_code == 400


# -------- Persistence tests --------

def test_records_persist_to_disk(client):
    """Records should persist to the JSON data file."""
    client.post('/calculate', data={
        'transport_type': 'train', 'transport_distance': '200',
        'diet': 'vegetarian', 'energy': 'renewable',
        'consumption': 'minimalist', 'csrf_token': 'test',
    }, follow_redirects=True)
    assert os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'r') as f:
        saved = json.load(f)
    assert len(saved) >= 1
    assert saved[-1]['transport_type'] == 'train'


def test_records_load_from_disk_on_start(client):
    """Records should reload from disk after clearing in-memory state."""
    client.post('/calculate', data={
        'transport_type': 'bus', 'transport_distance': '30',
        'diet': 'vegan', 'energy': 'mixed',
        'consumption': 'moderate', 'csrf_token': 'test',
    }, follow_redirects=True)
    FootprintRecord._records = []
    FootprintRecord._loaded = False
    records = FootprintRecord.get_all()
    assert len(records) >= 1
    assert records[-1]['transport_type'] == 'bus'


# -------- Model tests --------

class TestFootprintRecord:
    """Tests for the FootprintRecord in-memory model."""

    def test_save_and_get_all(self):
        """Saved record should be retrievable."""
        record_data = {
            'transport_type': 'car', 'diet': 'omnivore_low',
            'energy': 'mixed', 'consumption': 'moderate',
        }
        result = {
            'total': 5.0, 'breakdown': {'transport': 2.0},
            'category': 'average',
        }
        record = FootprintRecord(record_data, result, 100)
        FootprintRecord.save(record)
        all_records = FootprintRecord.get_all()
        assert len(all_records) == 1
        assert all_records[0]['total'] == 5.0
        assert all_records[0]['category'] == 'average'

    def test_get_recent(self):
        """get_recent should return the most recent N records."""
        for i in range(5):
            FootprintRecord.save(FootprintRecord(
                {}, {'total': float(i), 'breakdown': {},
                     'category': 'good'}, 0,
            ))
        recent = FootprintRecord.get_recent(2)
        assert len(recent) == 2

    def test_max_records_cap(self):
        """Records should be capped at MAX_RECORDS."""
        for i in range(MAX_RECORDS + 10):
            FootprintRecord.save(FootprintRecord(
                {}, {'total': float(i), 'breakdown': {},
                     'category': 'good'}, 0,
            ))
        assert len(FootprintRecord._records) == MAX_RECORDS

    def test_to_dict_format(self):
        """to_dict should contain all expected fields."""
        result = {
            'total': 3.5, 'breakdown': {'transport': 1.0},
            'category': 'good',
        }
        record = FootprintRecord(
            {
                'transport_type': 'bicycle', 'diet': 'vegan',
                'energy': 'renewable', 'consumption': 'minimalist',
            },
            result, 50,
        )
        d = record.to_dict()
        assert d['total'] == 3.5
        assert d['transport_type'] == 'bicycle'
        assert d['transport_distance'] == 50
        assert 'timestamp' in d

    def test_record_timestamp_format(self):
        """Record timestamp should be ISO format string."""
        record = FootprintRecord(
            {'transport_type': 'walk'}, {'total': 1.0,
             'breakdown': {}, 'category': 'good'}, 0,
        )
        assert 'T' in record.timestamp
        assert record.timestamp.endswith('Z') or '-' in record.timestamp
