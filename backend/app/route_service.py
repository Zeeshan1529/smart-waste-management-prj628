from math import atan2, cos, radians, sin, sqrt


PRIORITY_MULTIPLIER = {
    "CRITICAL": 2.50,
    "HIGH": 1.75,
    "MEDIUM": 1.25,
    "LOW": 1.00,
}


def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate great-circle distance between two coordinates.
    """
    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius_km * c


def optimize_route(
    bins,
    start_latitude: float,
    start_longitude: float,
):
    """
    Greedy route heuristic.

    At each step, choose the unvisited bin with the
    lowest urgency-adjusted distance.

    Higher-priority bins receive a larger multiplier,
    making them more likely to be selected earlier.
    """

    remaining = list(bins)

    current_lat = start_latitude
    current_lon = start_longitude

    route = []
    total_distance_km = 0.0

    sequence = 1

    while remaining:
        best_bin = None
        best_distance = None
        best_score = None

        for bin_row in remaining:
            distance = haversine_km(
                current_lat,
                current_lon,
                bin_row.latitude,
                bin_row.longitude,
            )

            priority = getattr(
                bin_row,
                "_route_priority",
                "MEDIUM",
            )

            multiplier = PRIORITY_MULTIPLIER.get(
                priority,
                1.0,
            )

            route_score = distance / multiplier

            if (
                best_score is None
                or route_score < best_score
            ):
                best_score = route_score
                best_bin = bin_row
                best_distance = distance

        priority = getattr(
            best_bin,
            "_route_priority",
            "MEDIUM",
        )

        total_distance_km += best_distance

        route.append(
            {
                "sequence": sequence,
                "bin_id": best_bin.id,
                "code": best_bin.code,
                "ward": best_bin.ward,
                "latitude": best_bin.latitude,
                "longitude": best_bin.longitude,
                "fill_level": round(
                    float(best_bin.fill_level),
                    2,
                ),
                "priority": priority,
                "distance_from_previous_km": round(
                    best_distance,
                    3,
                ),
            }
        )

        current_lat = best_bin.latitude
        current_lon = best_bin.longitude

        remaining.remove(best_bin)

        sequence += 1

    return {
        "route": route,
        "total_distance_km": round(
            total_distance_km,
            3,
        ),
        "number_of_stops": len(route),
    }
