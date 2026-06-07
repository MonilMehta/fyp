"""
Aggregate geolocated records into map marker clusters.
"""
from typing import Dict, Iterable, List, Tuple


def aggregate_geo_points(records: Iterable[Dict], point_type: str) -> List[Dict]:
    """
    Group records by rounded lat/lng into dots with event counts.
    """
    buckets: Dict[Tuple[float, float, str], Dict] = {}

    for record in records:
        lat = record.get('latitude')
        lng = record.get('longitude')
        if lat is None or lng is None:
            continue

        rounded_lat = round(float(lat), 2)
        rounded_lng = round(float(lng), 2)
        key = (rounded_lat, rounded_lng, point_type)

        if key not in buckets:
            location = ', '.join(
                part for part in (record.get('city', ''), record.get('country', '')) if part
            )
            buckets[key] = {
                'lat': rounded_lat,
                'lng': rounded_lng,
                'type': point_type,
                'count': 0,
                'label': location or f'{rounded_lat}, {rounded_lng}',
            }

        buckets[key]['count'] += 1

    return sorted(buckets.values(), key=lambda point: point['count'], reverse=True)
