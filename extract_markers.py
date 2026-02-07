#!/usr/bin/env python3
"""Extract building marker data from osu_eui_map.html"""

import re
import json

# Read the HTML file
with open('osu_eui_map.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract all circle markers - simpler approach
marker_blocks = re.findall(
    r'L\.circleMarker\(\s*\[([0-9.\-]+),\s*([0-9.\-]+)\],\s*\{[^}]*"fillColor":\s*"([^"]+)"[^}]*"radius":\s*([\d.]+)[^}]*"weight":\s*(\d+)[^}]*(?:"color":\s*"([^"]+)")?',
    html_content,
    re.DOTALL
)

markers = []
for match in marker_blocks:
    lat = float(match[0])
    lng = float(match[1])
    fill_color = match[2]
    radius = float(match[3])
    weight = int(match[4])
    stroke_color = match[5] if len(match) > 5 and match[5] else None

    markers.append({
        'lat': lat,
        'lng': lng,
        'fillColor': fill_color,
        'radius': radius,
        'weight': weight,
        'strokeColor': stroke_color
    })

# Extract popup data
popup_pattern = r'<b>(.+?)\s*\((\d+)\)</b><br>EUI:\s*([\d.]+)\s*kWh/sqft/yr(?:\s*<b>\(HIGHEST\)</b>)?<br>Area:\s*([\d,]+)\s*sqft'
popups = []
for match in re.finditer(popup_pattern, html_content):
    building_name = match.group(1).strip()
    building_id = match.group(2)
    eui = float(match.group(3))
    area = match.group(4).replace(',', '')

    # Check if it's the highest EUI
    is_highest = '(HIGHEST)' in match.group(0)

    popups.append({
        'name': building_name,
        'id': building_id,
        'eui': eui,
        'area': int(area),
        'is_highest': is_highest
    })

# Combine markers and popups
buildings = []
min_len = min(len(markers), len(popups))
for i in range(min_len):
    buildings.append({
        **markers[i],
        **popups[i]
    })

print(f"Extracted {len(markers)} markers and {len(popups)} popups")
print(f"Combined {len(buildings)} buildings")

# Save to JSON
output = {
    'center': [40.00160797506397, -83.02065110905887],
    'zoom': 15,
    'buildings': buildings
}

with open('building_markers.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved to building_markers.json")
if buildings:
    print(f"\nSample building: {buildings[0]}")
