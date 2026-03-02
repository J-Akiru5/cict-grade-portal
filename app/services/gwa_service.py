from app.models.grade import Grade
from app.models.enrollment import Enrollment


# Philippine GWA Grade → Descriptive Equivalent mapping
GRADE_EQUIVALENTS = {
    1.00: 'Excellent',
    1.25: 'Excellent',
    1.50: 'Superior',
    1.75: 'Superior',
    2.00: 'Very Good',
    2.25: 'Very Good',
    2.50: 'Good',
    2.75: 'Good',
    3.00: 'Satisfactory',
    5.00: 'Failed',
}


def compute_gwa(grades: list) -> float | None:
    """
    Compute the General Weighted Average (GWA) using the Philippine standard.
    Formula: GWA = Σ(grade_value × units) / Σ(units)
    Returns None if no grades are encoded yet.
    """
    # Only include grades that have a numeric value (not INC/DRP/None)
    encoded = [
        g for g in grades
        if g.grade_value is not None and g.remarks not in ('INC', 'DRP')
    ]
    if not encoded:
        return None

    total_weighted = sum(
        g.grade_value * g.enrollment.subject.units
        for g in encoded
    )
    total_units = sum(g.enrollment.subject.units for g in encoded)

    if total_units == 0:
        return None

    return round(total_weighted / total_units, 4)


def get_gwa_status(gwa: float | None) -> dict:
    """
    Return display metadata for a given GWA value.
    Color coding:
      - 1.00–1.75 → green (Excellent/Superior)
      - 1.76–2.50 → blue (Good range)
      - 2.51–3.00 → yellow (Satisfactory)
      - > 3.00    → red (Failed)
    """
    if gwa is None:
        return {'label': 'N/A', 'color': 'text-slate-400', 'badge': 'bg-slate-100 text-slate-500'}

    if gwa <= 1.75:
        return {'label': 'Excellent/Superior', 'color': 'text-status-pass', 'badge': 'bg-green-100 text-green-700'}
    elif gwa <= 2.50:
        return {'label': 'Good', 'color': 'text-blue-500', 'badge': 'bg-blue-100 text-blue-700'}
    elif gwa <= 3.00:
        return {'label': 'Satisfactory', 'color': 'text-accent-gold', 'badge': 'bg-yellow-100 text-yellow-700'}
    else:
        return {'label': 'Failed', 'color': 'text-status-fail', 'badge': 'bg-red-100 text-red-700'}


def get_grade_color(grade_value: float | None) -> str:
    """Return a Tailwind text color class based on Philippine grade value."""
    if grade_value is None:
        return 'text-slate-400'
    if grade_value <= 1.75:
        return 'text-status-pass font-semibold'
    elif grade_value <= 3.00:
        return 'text-slate-800 font-semibold'
    else:
        return 'text-status-fail font-semibold'
