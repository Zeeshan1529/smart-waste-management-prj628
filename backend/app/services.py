def collection_priority(fill_level: float, hours_since_update: float) -> str:
    """Baseline prioritization rule. Replace/augment with ML later."""
    score = fill_level + min(hours_since_update * 2.0, 20.0)
    if score >= 90:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"
