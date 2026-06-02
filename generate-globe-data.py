"""
Gera dataset de (lat, lng) crus para land points do globo, formato JSON compacto
para embed inline no JS. Roda em cima do mesmo ne_110m_land.geojson.
"""
import json
import math
from pathlib import Path
from shapely.geometry import shape, Point

HERE = Path(__file__).parent
GEOJSON_PATH = HERE / "ne_110m_land.geojson"
OUT_JS = HERE / "globe-land-data.js"

GRID_STEP_DEG = 2.0


def main():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    polygons = []
    for feat in data["features"]:
        geom = shape(feat["geometry"])
        if geom.geom_type == "Polygon":
            polygons.append(geom)
        elif geom.geom_type == "MultiPolygon":
            polygons.extend(list(geom.geoms))

    print(f"Loaded {len(polygons)} land polygons")

    points = []
    lat = -85.0
    while lat <= 85.0:
        step_lng = GRID_STEP_DEG / max(math.cos(math.radians(lat)), 0.1)
        lng = -180.0
        while lng <= 180.0:
            pt = Point(lng, lat)
            for poly in polygons:
                if poly.bounds[0] <= lng <= poly.bounds[2] and poly.bounds[1] <= lat <= poly.bounds[3]:
                    if poly.contains(pt):
                        points.append([round(lat, 1), round(lng, 1)])
                        break
            lng += step_lng
        lat += GRID_STEP_DEG

    print(f"Generated {len(points)} land points")

    js_array = "[" + ",".join(f"[{p[0]},{p[1]}]" for p in points) + "]"
    OUT_JS.write_text(f"window.__INFIZAP_LAND_POINTS={js_array};", encoding="utf-8")
    print(f"Wrote {OUT_JS} ({OUT_JS.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
