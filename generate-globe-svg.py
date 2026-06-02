"""
Gera SVG dotted-globe Atlantico-centrada para Infizap LP.
Usa Natural Earth low-res land data + projecao orthographic.
"""
import json
import math
import urllib.request
from pathlib import Path
from shapely.geometry import shape, Point

HERE = Path(__file__).parent
GEOJSON_PATH = HERE / "ne_110m_land.geojson"
OUT_SVG = HERE / "globe-atlantic.svg"

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"

CENTER_LAT = 15.0
CENTER_LNG = -25.0
SVG_SIZE = 600
RADIUS = 285
GRID_STEP_DEG = 2.0
DOT_RADIUS = 1.8

CENTER_LAT_RAD = math.radians(CENTER_LAT)
CENTER_LNG_RAD = math.radians(CENTER_LNG)
CX = SVG_SIZE / 2
CY = SVG_SIZE / 2


def download_geojson():
    if GEOJSON_PATH.exists():
        return
    print(f"Downloading {NE_URL} ...")
    urllib.request.urlretrieve(NE_URL, GEOJSON_PATH)


def project(lat_deg, lng_deg):
    """Orthographic projection. Returns (x, y, visible)."""
    lat = math.radians(lat_deg)
    lng = math.radians(lng_deg)
    cos_c = math.sin(CENTER_LAT_RAD) * math.sin(lat) + math.cos(CENTER_LAT_RAD) * math.cos(lat) * math.cos(lng - CENTER_LNG_RAD)
    if cos_c < 0:
        return None
    x = RADIUS * math.cos(lat) * math.sin(lng - CENTER_LNG_RAD)
    y = -RADIUS * (math.cos(CENTER_LAT_RAD) * math.sin(lat) - math.sin(CENTER_LAT_RAD) * math.cos(lat) * math.cos(lng - CENTER_LNG_RAD))
    return (CX + x, CY + y)


def main():
    download_geojson()
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

    dots = []
    lat = -85.0
    while lat <= 85.0:
        step_lng = GRID_STEP_DEG / max(math.cos(math.radians(lat)), 0.1)
        lng = -180.0
        while lng <= 180.0:
            pt = Point(lng, lat)
            for poly in polygons:
                if poly.bounds[0] <= lng <= poly.bounds[2] and poly.bounds[1] <= lat <= poly.bounds[3]:
                    if poly.contains(pt):
                        proj = project(lat, lng)
                        if proj is not None:
                            dots.append(proj)
                        break
            lng += step_lng
        lat += GRID_STEP_DEG

    print(f"Generated {len(dots)} dots")

    svg_parts = []
    svg_parts.append(f'<svg viewBox="0 0 {SVG_SIZE} {SVG_SIZE}" xmlns="http://www.w3.org/2000/svg" class="block h-full w-full select-none" style="border-radius:50%" aria-hidden="true">')
    svg_parts.append('<defs>')
    svg_parts.append('<radialGradient id="globe-glow" cx="50%" cy="50%" r="50%">')
    svg_parts.append('<stop offset="0%" stop-color="hsl(173,76%,48%)" stop-opacity="0.08"/>')
    svg_parts.append('<stop offset="70%" stop-color="hsl(173,76%,48%)" stop-opacity="0.04"/>')
    svg_parts.append('<stop offset="100%" stop-color="transparent"/>')
    svg_parts.append('</radialGradient>')
    svg_parts.append('<radialGradient id="globe-body" cx="40%" cy="35%" r="70%">')
    svg_parts.append('<stop offset="0%" stop-color="#1a2030"/>')
    svg_parts.append('<stop offset="60%" stop-color="#0f1320"/>')
    svg_parts.append('<stop offset="100%" stop-color="#070a12"/>')
    svg_parts.append('</radialGradient>')
    svg_parts.append('</defs>')
    svg_parts.append(f'<circle cx="{CX}" cy="{CY}" r="{RADIUS+10}" fill="url(#globe-glow)"/>')
    svg_parts.append(f'<circle cx="{CX}" cy="{CY}" r="{RADIUS}" fill="url(#globe-body)" stroke="rgba(255,255,255,0.04)"/>')

    svg_parts.append('<g fill="rgba(255,255,255,0.55)">')
    for (x, y) in dots:
        svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_RADIUS}"/>')
    svg_parts.append('</g>')
    svg_parts.append('</svg>')

    OUT_SVG.write_text("".join(svg_parts), encoding="utf-8")
    print(f"Wrote {OUT_SVG} ({OUT_SVG.stat().st_size} bytes)")

    br = project(-15.0, -50.0)
    pt = project(39.5, -8.0)
    print(f"\nCALIBRATION (pixel coords on {SVG_SIZE}x{SVG_SIZE} canvas):")
    if br:
        print(f"  Brasil center -15/-50 -> ({br[0]:.0f}, {br[1]:.0f}) -> top:{br[1]/SVG_SIZE*100:.1f}%; left:{br[0]/SVG_SIZE*100:.1f}%")
    if pt:
        print(f"  Portugal 39.5/-8 -> ({pt[0]:.0f}, {pt[1]:.0f}) -> top:{pt[1]/SVG_SIZE*100:.1f}%; left:{pt[0]/SVG_SIZE*100:.1f}%")


if __name__ == "__main__":
    main()
