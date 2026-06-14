from flask import Blueprint, render_template, request, jsonify
from app.calculator import validate_inputs, calculate_carbon_footprint, get_category
from app.insights import get_personalized_tips, get_global_comparison, estimate_forest_offset, CATEGORY_MESSAGES
from app.models import FootprintRecord

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/calculator')
def calculator():
    return render_template('calculator.html')


@bp.route('/calculate', methods=['POST'])
def calculate():
    data = request.form

    errors = validate_inputs(data)
    if errors:
        return render_template('calculator.html', errors=errors, data=data)

    transport_type = data.get('transport_type', '').strip().lower()
    transport_distance = float(data.get('transport_distance', 0))
    diet = data.get('diet', '').strip().lower()
    energy = data.get('energy', '').strip().lower()
    consumption = data.get('consumption', '').strip().lower()

    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)
    category = get_category(result['total'])
    result['category'] = category

    record = FootprintRecord(data, result)
    FootprintRecord.save(record)

    tips = get_personalized_tips(result['breakdown'])
    comparison = get_global_comparison(result['total'])
    offset = estimate_forest_offset(result['total'])
    message = CATEGORY_MESSAGES.get(category, '')

    return render_template(
        'results.html',
        result=result,
        category=category,
        tips=tips,
        comparison=comparison,
        offset=offset,
        message=message,
    )


@bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    data = request.get_json(silent=True) or {}

    errors = validate_inputs(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    transport_type = data.get('transport_type', '').strip().lower()
    transport_distance = float(data.get('transport_distance', 0))
    diet = data.get('diet', '').strip().lower()
    energy = data.get('energy', '').strip().lower()
    consumption = data.get('consumption', '').strip().lower()

    result = calculate_carbon_footprint(transport_type, transport_distance, diet, energy, consumption)
    category = get_category(result['total'])
    result['category'] = category

    tips = get_personalized_tips(result['breakdown'])
    comparison = get_global_comparison(result['total'])
    offset = estimate_forest_offset(result['total'])

    return jsonify({
        'success': True,
        'result': result,
        'category': category,
        'tips': tips,
        'comparison': comparison,
        'offset': offset,
    })


@bp.route('/tips')
def tips():
    from app.insights import TIPS
    return render_template('tips.html', tips=TIPS)


@bp.route('/history')
def history():
    records = FootprintRecord.get_all()
    return render_template('history.html', records=records)
