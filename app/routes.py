from flask import Blueprint, render_template, request, jsonify, session
from app.calculator import validate_inputs, calculate_carbon_footprint
from app.insights import get_personalized_tips, get_global_comparison, estimate_forest_offset, CATEGORY_MESSAGES, TIPS
from app.models import FootprintRecord
from app.csrf import get_csrf_token, validate_csrf
from typing import Dict, Any

bp = Blueprint('main', __name__)


@bp.context_processor
def inject_csrf() -> Dict[str, str]:
    return {'csrf_token': get_csrf_token()}


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

    transport_type: str = data.get('transport_type', '').strip().lower()
    transport_distance: float = float(data.get('transport_distance', 0))
    diet: str = data.get('diet', '').strip().lower()
    energy: str = data.get('energy', '').strip().lower()
    consumption: str = data.get('consumption', '').strip().lower()

    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)

    record = FootprintRecord(data, result, transport_distance)
    FootprintRecord.save(record)

    tips = get_personalized_tips(result['breakdown'])
    comparison = get_global_comparison(result['total'])
    offset = estimate_forest_offset(result['total'])
    message = CATEGORY_MESSAGES.get(result['category'], '')

    return render_template(
        'results.html',
        result=result,
        category=result['category'],
        tips=tips,
        comparison=comparison,
        offset=offset,
        message=message,
    )


@bp.route('/api/calculate', methods=['POST'])
def api_calculate() -> str:
    data: Dict[str, Any] = request.get_json(silent=True) or {}

    errors = validate_inputs(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    transport_type: str = data.get('transport_type', '').strip().lower()
    transport_distance: float = float(data.get('transport_distance', 0))
    diet: str = data.get('diet', '').strip().lower()
    energy: str = data.get('energy', '').strip().lower()
    consumption: str = data.get('consumption', '').strip().lower()

    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)

    tips = get_personalized_tips(result['breakdown'])
    comparison = get_global_comparison(result['total'])
    offset = estimate_forest_offset(result['total'])

    return jsonify({
        'success': True,
        'result': result,
        'category': result['category'],
        'tips': tips,
        'comparison': comparison,
        'offset': offset,
    })


@bp.route('/tips')
def tips() -> str:
    return render_template('tips.html', tips=TIPS)


@bp.route('/history')
def history() -> str:
    records = FootprintRecord.get_all()
    return render_template('history.html', records=records)
