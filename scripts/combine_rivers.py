#!/usr/bin/env python3
"""
Combine Natural Earth rivers with specific Overpass river data for xatra map-making software.
Only includes selected rivers that are not already in Natural Earth data.
"""

import json
import os
import glob
from pathlib import Path

def load_geojson(filepath):
    """Load a GeoJSON file and return the data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def process_overpass_river(filepath):
    """Process a single Overpass river file and standardize its format."""
    data = load_geojson(filepath)
    if not data or 'features' not in data:
        return None
    
    # Extract river name from filename
    filename = Path(filepath).stem
    river_name = filename.split('_')[-1]  # Get the last part after underscores
    
    processed_features = []
    
    for feature in data['features']:
        if feature.get('geometry', {}).get('type') == 'LineString':
            # Create a standardized feature
            processed_feature = {
                "type": "Feature",
                "properties": {
                    "name": river_name.title(),
                    "name_en": river_name.title(),
                    "featurecla": "River",
                    "scalerank": 1,  # High importance for Overpass rivers
                    "source": "Overpass",
                    "original_id": feature.get('properties', {}).get('id', ''),
                    "river_name": river_name
                },
                "geometry": feature['geometry']
            }
            processed_features.append(processed_feature)
    
    return processed_features

def combine_selected_rivers():
    """Combine Natural Earth and selected Overpass river data."""
    print("🌊 Combining selected river data for xatra...")
    
    # Load Natural Earth rivers
    ne_rivers_path = "data/rivers/ne_10m_rivers.geojson"
    ne_data = load_geojson(ne_rivers_path)
    
    if not ne_data:
        print("❌ Could not load Natural Earth rivers!")
        return None
    
    print(f"✅ Loaded {len(ne_data['features'])} Natural Earth rivers")
    
    # Define the specific rivers to include from Overpass
    selected_rivers = [
        "river_relation_6722174_ramaganga.json",
        "river_way_247787304_campa.json", 
        "river_relation_12559166_suvarnanadi.json",
        "river_relation_11117634_kshipra.json",
        "river_relation_5388381_sarasvati (ghaggar).json",
        "river_relation_1676476_kubha (kabul).json",
        "river_relation_6608825_kama (kunar).json",
        "river_relation_8623883_haraxvati (arghandab).json"
    ]
    
    # Process only the selected Overpass rivers
    overpass_dir = "data/rivers_overpass_india"
    all_overpass_features = []
    processed_count = 0
    
    for filename in selected_rivers:
        filepath = os.path.join(overpass_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}...")
            features = process_overpass_river(filepath)
            if features:
                all_overpass_features.extend(features)
                processed_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"✅ Processed {processed_count} selected Overpass river files")
    print(f"✅ Added {len(all_overpass_features)} Overpass river features")
    
    # Combine all features
    combined_features = ne_data['features'] + all_overpass_features
    
    # Create combined GeoJSON
    combined_data = {
        "type": "FeatureCollection",
        "features": combined_features
    }
    
    # Save combined data
    output_path = "data/rivers/combined_rivers.geojson"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Combined data saved to {output_path}")
    print(f"📊 Total rivers: {len(combined_features)}")
    print(f"   - Natural Earth: {len(ne_data['features'])}")
    print(f"   - Selected Overpass: {len(all_overpass_features)}")
    
    # List the selected rivers
    print("\n🎯 Selected Overpass rivers:")
    for filename in selected_rivers:
        if os.path.exists(os.path.join(overpass_dir, filename)):
            river_name = filename.split('_')[-1].replace('.json', '')
            print(f"   - {river_name}")
    
    return combined_data

if __name__ == "__main__":
    combine_selected_rivers()