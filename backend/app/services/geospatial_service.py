from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from app.models.properties import Property


def search_properties_nearby(db: Session, lon: float, lat: float, radius_km: float) -> List[Property]:
    """Find properties within radius_km using PostGIS ST_DWithin.
    
    Note: ST_DWithin with geography uses meters, with geometry uses units of the CRS.
    For WGS84 geometry, we use geography cast for accurate distance.
    """
    point_wkt = f"SRID=4326;POINT({lon} {lat})"
    radius_meters = radius_km * 1000

    query = db.query(Property).filter(
        func.ST_DWithin(
            func.ST_GeogFromWKB(Property.geom),
            func.ST_GeogFromText(point_wkt),
            radius_meters
        )
    )
    return query.all()


def properties_to_geojson(properties: List[Property]) -> dict:
    """Convert list of Property objects to GeoJSON FeatureCollection."""
    features = []
    for prop in properties:
        geom = None
        if prop.geom is not None:
            shape = to_shape(prop.geom)
            geom = mapping(shape)

        feature = {
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "property_id": str(prop.property_id),
                "property_code": prop.property_code,
                "property_name": prop.property_name,
                "property_type": prop.property_type,
                "address": prop.address,
                "city": prop.city,
                "suburb": prop.suburb,
                "status": prop.status,
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }
