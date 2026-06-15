from flask import Blueprint, render_template, request, jsonify, Response
from app.calculator import validate_inputs, calculate_carbon_footprint
from app.insights import get_personalized_tips, get_global_comparison, estimate_forest_offset, CATEGORY_MESSAGES, TIPS
from app.models import FootprintRecord
from app.csrf import get_csrf_token, validate_csrf
from typing import Dict, Any, Tuple


bp = Blueprint('main', __name__)


@bp.context_processor
def inject_csrf() -> Dict[str, str]:
    return {'csrf_token': get_csrf_token()}


def _process_inputs(data: Dict[str, Any]) -> Tuple[str, float, str, str, str]:
    transport_type: str = data.get('transport_type', '').strip().lower()
    transport_distance: float = float(data.get('transport_distance', 0))
    diet: str = data.get('diet', '').strip().lower()
    energy: str = data.get('energy', '').strip().lower()
    consumption: str = data.get('consumption', '').strip().lower()
    return transport_type, transport_distance, diet, energy, consumption


def _build_result_data(result: Dict[str, Any], transport_distance: float, data: Dict[str, Any]) -> Dict[str, Any]:
    record = FootprintRecord(data, result, transport_distance)
    FootprintRecord.save(record)
    return {
        'result': result,
        'category': result['category'],
        'tips': get_personalized_tips(result['breakdown']),
        'comparison': get_global_comparison(result['total']),
        'offset': estimate_forest_offset(result['total']),
        'message': CATEGORY_MESSAGES.get(result['category'], ''),
    }


@bp.route('/')
def index() -> str:
    return render_template('index.html')


@bp.route('/calculator')
def calculator() -> str:
    return render_template('calculator.html', csrf_token=get_csrf_token())


@bp.route('/calculate', methods=['POST'])
def calculate() -> str:
    validate_csrf()
    data: Dict[str, Any] = request.form
    errors = validate_inputs(data)
    if errors:
        return render_template('calculator.html', errors=errors, data=data, csrf_token=get_csrf_token())
    transport_type, transport_distance, diet, energy, consumption = _process_inputs(data)
    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)
    rd = _build_result_data(result, transport_distance, data)
    return render_template('results.html', **rd)


@bp.route('/api/calculate', methods=['POST'])
def api_calculate() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    errors = validate_inputs(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    transport_type, transport_distance, diet, energy, consumption = _process_inputs(data)
    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)
    rd = _build_result_data(result, transport_distance, data)
    return jsonify({'success': True, **rd}), 200


@bp.route('/tips')
def tips() -> str:
    return render_template('tips.html', tips=TIPS)


@bp.route('/history')
def history() -> str:
    records = FootprintRecord.get_all()
    trends = _compute_trends(records)
    return render_template('history.html', records=records, trends=trends)


@bp.route('/history/export')
def history_export() -> Response:
    records = FootprintRecord.get_all()
    lines = ['timestamp,transport_type,transport_distance,diet,energy,consumption,total,category']
    for r in records:
        lines.append(
            f"{r['timestamp']},{r['transport_type']},{r['transport_distance']},"
            f"{r['diet']},{r['energy']},{r['consumption']},{r['total']},{r['category']}"
        )
    return Response(
        '\n'.join(lines),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=eco-track-history.csv'},
    )


def _compute_trends(records: list) -> Dict[str, Any]:
    if len(records) < 2:
        return {'has_trend': False, 'direction': '', 'change': 0}
    first = records[0]['total']
    last = records[-1]['total']
    change = round(last - first, 2)
    direction = 'down' if change < 0 else 'up' if change > 0 else 'flat'
    return {'has_trend': True, 'direction': direction, 'change': abs(change)}
