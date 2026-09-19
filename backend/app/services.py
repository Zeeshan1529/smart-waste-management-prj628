def priority_score(fill_level: float, hours_since_update: float) -> float:
    """
    Baseline operational priority score.

    Higher fill level and older sensor updates increase collection urgency.
    This rule can later be augmented with the ML prediction module.
    """
    score = fill_level + min(hours_since_update * 2.0, 20.0)
    return round(score, 2)


def collection_priority(fill_level: float, hours_since_update: float) -> str:
    score = priority_score(fill_level, hours_since_update)

    if score >= 90:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 45:
        return "MEDIUM"

    return "LOW"
