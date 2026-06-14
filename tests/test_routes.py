"""Integration tests for Flask routes and the FootprintRecord model."""

import json
import os
from app.models import FootprintRecord, MAX_RECORDS, DATA_FILE


# -------- Page rendering tests --------

def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'EcoTrack' in response.data


def test_calculator_returns_200(client):
    response = client.get('/calculator')
    assert response.status_code == 200
    assert b'Carbon Footprint Calculator' in response.data


def test_tips_returns_200(client):
    response = client.get('/tips')
    assert response.status_code == 200
    assert b'Tips' in response.data


def test_history_returns_200(client):
    response = client.get('/history')
    assert response.status_code == 200


def test_history_empty_state(client):
    response = client.get('/history')
    assert b'No calculations yet' in response.data


# -------- Form submission tests --------

def test_calculate_post_valid(client):
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
    response = client.post('/api/calculate', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


# -------- History integration test --------

def test_history_after_calculation(client):
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
    for _ in range(3):
        client.post('/calculate', data={
            'transport_type': 'car', 'transport_distance': '50',
            'diet': 'vegan', 'energy': 'renewable', 'consumption': 'moderate',
            'csrf_token': 'test',
        }, follow_redirects=True)
    response = client.get('/history')
    html = response.data.decode('utf-8')
    assert html.count('<tr>') >= 3


# -------- Security tests --------

def test_security_headers(client):
    response = client.get('/')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert 'Content-Security-Policy' in response.headers


def test_security_cookie_attributes(client):
    with client:
        client.get('/')
        cookie_headers = [v for v in client.get('/').headers if v[0] == 'Set-Cookie']
        for header_val in cookie_headers:
            assert 'HttpOnly' in str(header_val)
            assert 'SameSite=Lax' in str(header_val)


# -------- HTTP method tests --------

def test_get_on_calculate_post_returns_405(client):
    response = client.get('/calculate')
    assert response.status_code == 405


def test_api_calculate_form_encoded_fallback(client):
    response = client.post('/api/calculate', data={
        'transport_type': 'car', 'transport_distance': '100',
        'diet': 'omnivore_medium', 'energy': 'mixed', 'consumption': 'moderate',
    })
    assert response.status_code == 400


# -------- Persistence tests --------

def test_records_persist_to_disk(client):
    client.post('/calculate', data={
        'transport_type': 'train', 'transport_distance': '200',
        'diet': 'vegetarian', 'energy': 'renewable', 'consumption': 'minimalist',
        'csrf_token': 'test',
    }, follow_redirects=True)
    assert os.path.exists(DATA_FILE)
    with open(DATA_FILE, 'r') as f:
        saved = json.load(f)
    assert len(saved) >= 1
    assert saved[-1]['transport_type'] == 'train'


def test_records_load_from_disk_on_start(client):
    client.post('/calculate', data={
        'transport_type': 'bus', 'transport_distance': '30',
        'diet': 'vegan', 'energy': 'mixed', 'consumption': 'moderate',
        'csrf_token': 'test',
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
        record_data = {
            'transport_type': 'car', 'diet': 'omnivore_low',
            'energy': 'mixed', 'consumption': 'moderate',
        }
        result = {'total': 5.0, 'breakdown': {'transport': 2.0}, 'category': 'average'}
        record = FootprintRecord(record_data, result, 100)
        FootprintRecord.save(record)
        all_records = FootprintRecord.get_all()
        assert len(all_records) == 1
        assert all_records[0]['total'] == 5.0
        assert all_records[0]['category'] == 'average'

    def test_get_recent(self):
        for i in range(5):
            FootprintRecord.save(FootprintRecord(
                {}, {'total': float(i), 'breakdown': {}, 'category': 'good'}, 0,
            ))
        recent = FootprintRecord.get_recent(2)
        assert len(recent) == 2

    def test_max_records_cap(self):
        for i in range(MAX_RECORDS + 10):
            FootprintRecord.save(FootprintRecord(
                {}, {'total': float(i), 'breakdown': {}, 'category': 'good'}, 0,
            ))
        assert len(FootprintRecord._records) == MAX_RECORDS

    def test_to_dict_format(self):
        result = {'total': 3.5, 'breakdown': {'transport': 1.0}, 'category': 'good'}
        record = FootprintRecord(
            {'transport_type': 'bicycle', 'diet': 'vegan',
             'energy': 'renewable', 'consumption': 'minimalist'},
            result, 50,
        )
        d = record.to_dict()
        assert d['total'] == 3.5
        assert d['transport_type'] == 'bicycle'
        assert d['transport_distance'] == 50
        assert 'timestamp' in d
