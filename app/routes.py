"""Route definitions for the EcoTrack web application.

Handles all HTTP endpoints including the main pages, form submission,
REST API, history display, and CSV export.
"""

from typing import Any, Dict, Tuple
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    Response,
)
from app.calculator import (
    calculate_carbon_footprint,
    validate_inputs,
)
from app.csrf import get_csrf_token, validate_csrf
from app.insights import (
    CATEGORY_MESSAGES,
    estimate_forest_offset,
    get_global_comparison,
    get_personalized_tips,
    TIPS,
)
from app.models import FootprintRecord

__all__ = ['bp', '_process_inputs', '_build_result_data', '_compute_trends']

bp = Blueprint('main', __name__)


def _process_inputs(
    data: Dict[str, Any],
) -> Tuple[str, float, str, str, str]:
    """Extract and normalize form/JSON input fields."""
    transport_type: str = data.get('transport_type', '').strip().lower()
    transport_distance: float = float(data.get('transport_distance', 0))
    diet: str = data.get('diet', '').strip().lower()
    energy: str = data.get('energy', '').strip().lower()
    consumption: str = data.get('consumption', '').strip().lower()
    return transport_type, transport_distance, diet, energy, consumption


def _build_result_data(
    result: Dict[str, Any],
    transport_distance: float,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Persist the calculation and build the template/API result payload."""
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
    """Render the home page."""
    return render_template('index.html')


@bp.route('/calculator')
def calculator() -> str:
    """Render the carbon footprint calculator form."""
    return render_template('calculator.html', csrf_token=get_csrf_token())


@bp.route('/calculate', methods=['POST'])
def calculate() -> str:
    """Process the calculator form submission and show results."""
    validate_csrf()
    data: Dict[str, Any] = request.form
    errors = validate_inputs(data)
    if errors:
        return render_template(
            'calculator.html',
            errors=errors,
            data=data,
            csrf_token=get_csrf_token(),
        )
    transport_type, transport_distance, diet, energy, consumption = (
        _process_inputs(data)
    )
    result = calculate_carbon_footprint(
        transport_type, transport_distance, diet, energy, consumption,
    )
    rd = _build_result_data(result, transport_distance, data)
    return render_template('results.html', **rd)


@bp.route('/api/calculate', methods=['POST'])
def api_calculate() -> Tuple[Response, int]:
    """REST API endpoint for carbon footprint calculation."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    errors = validate_inputs(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    transport_type, transport_distance, diet, energy, consumption = (
        _process_inputs(data)
    )
    result = calculate_carbon_footprint(
        transport_type, transport_distance, diet, energy, consumption,
    )
    rd = _build_result_data(result, transport_distance, data)
    return jsonify({'success': True, **rd}), 200


@bp.route('/tips')
def tips() -> str:
    """Render the full tips and insights library page."""
    return render_template('tips.html', tips=TIPS)


@bp.route('/history')
def history() -> str:
    """Render the calculation history page with trends."""
    records = FootprintRecord.get_all()
    trends = _compute_trends(records)
    return render_template('history.html', records=records, trends=trends)


@bp.route('/history/export')
def history_export() -> Response:
    """Export calculation history as a CSV file."""
    records = FootprintRecord.get_all()
    header = (
        'timestamp,transport_type,transport_distance,'
        'diet,energy,consumption,total,category'
    )
    lines = [header]
    for r in records:
        lines.append(
            f"{r['timestamp']},{r['transport_type']},"
            f"{r['transport_distance']},{r['diet']},"
            f"{r['energy']},{r['consumption']},"
            f"{r['total']},{r['category']}"
        )
    return Response(
        '\n'.join(lines),
        mimetype='text/csv',
        headers={
            'Content-Disposition': (
                'attachment; filename=eco-track-history.csv'
            ),
        },
    )


def _compute_trends(records: list) -> Dict[str, Any]:
    """Compute direction and magnitude between first and last record."""
    if len(records) < 2:
        return {'has_trend': False, 'direction': '', 'change': 0}
    first = records[0]['total']
    last = records[-1]['total']
    change = round(last - first, 2)
    direction = (
        'down' if change < 0 else 'up' if change > 0 else 'flat'
    )
    return {'has_trend': True, 'direction': direction, 'change': abs(change)}
