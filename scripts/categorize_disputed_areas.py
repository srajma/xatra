#!/usr/bin/env python3
"""
Put all Z-prefixed entries in one place.

This script:
1. Creates backup copies of PAK and CHN files with _original suffix
2. Extracts all Z-prefixed entries from PAK and CHN files by level
3. Removes Z-prefixed entries from original PAK and CHN files
4. Creates backup copies of IND files with _original suffix
5. Appends Z-prefixed entries to corresponding IND files by level
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any

def load_geojson(file_path: str) -> Dict[str, Any]:
    """Load a GeoJSON file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_geojson(data: Dict[str, Any], file_path: str) -> None:
    """Save data as a GeoJSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

def backup_file(file_path: str) -> str:
    """Create a backup copy of a file with _original suffix."""
    backup_path = file_path.replace('.json', '_original.json')
    shutil.copy2(file_path, backup_path)
    print(f"Backed up {file_path} -> {backup_path}")
    return backup_path

def extract_z_entries(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all features with GID_0 starting with 'Z' from GeoJSON data."""
    z_entries = []
    if 'features' in data:
        for feature in data['features']:
            if 'properties' in feature and 'GID_0' in feature['properties']:
                gid_0 = feature['properties']['GID_0']
                if gid_0.startswith('Z'):
                    z_entries.append(feature)
    return z_entries

def remove_z_entries(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove all features with GID_0 starting with 'Z' from GeoJSON data."""
    if 'features' in data:
        data['features'] = [
            feature for feature in data['features']
            if not (feature.get('properties', {}).get('GID_0', '').startswith('Z'))
        ]
    return data

def append_entries(data: Dict[str, Any], entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Append entries to the features list of GeoJSON data."""
    if 'features' not in data:
        data['features'] = []
    data['features'].extend(entries)
    return data

def get_level_from_filename(filename: str) -> int:
    """Extract the level number from a GADM filename."""
    # Extract level from filename like gadm41_PAK_1.json -> 1
    parts = filename.split('_')
    if len(parts) >= 3:
        level_str = parts[2].replace('.json', '')
        try:
            return int(level_str)
        except ValueError:
            return 0
    return 0

def main():
    """Main function to categorize disputed areas."""
    data_dir = Path("data/gadm")
    
    # Countries to process (PAK and CHN for extraction, IND for appending)
    source_countries = ["PAK", "CHN"]
    target_country = "IND"
    
    # Collect Z entries by level
    z_entries_by_level = {}
    
    print("Step 1: Processing PAK and CHN files to extract Z entries...")
    
    for country in source_countries:
        print(f"\nProcessing {country} files...")
        
        # Process all level files (1, 2, 3, etc.)
        for level in range(1, 10):  # Check up to level 9
            filename = f"gadm41_{country}_{level}.json"
            file_path = data_dir / filename
            
            if not file_path.exists():
                print(f"  {filename} not found, skipping...")
                continue
                
            print(f"  Processing {filename}...")
            
            # Load the file
            data = load_geojson(str(file_path))
            
            # Extract Z entries
            z_entries = extract_z_entries(data)
            
            if z_entries:
                print(f"    Found {len(z_entries)} Z entries")
                
                # Store by level
                if level not in z_entries_by_level:
                    z_entries_by_level[level] = []
                z_entries_by_level[level].extend(z_entries)
                
                # Create backup of original file
                backup_file(str(file_path))
                
                # Remove Z entries from original file
                data_cleaned = remove_z_entries(data)
                save_geojson(data_cleaned, str(file_path))
                print(f"    Removed Z entries from {filename}")
            else:
                print(f"    No Z entries found in {filename}")
    
    print(f"\nStep 2: Processing IND files to append Z entries...")
    
    # Process IND files
    for level in range(1, 10):  # Check up to level 9
        filename = f"gadm41_{target_country}_{level}.json"
        file_path = data_dir / filename
        
        if not file_path.exists():
            print(f"  {filename} not found, skipping...")
            continue
            
        print(f"  Processing {filename}...")
        
        # Create backup of original IND file
        backup_file(str(file_path))
        
        # Load the file
        data = load_geojson(str(file_path))
        
        # Append Z entries for this level if any exist
        if level in z_entries_by_level:
            z_entries = z_entries_by_level[level]
            print(f"    Appending {len(z_entries)} Z entries to {filename}")
            data = append_entries(data, z_entries)
            save_geojson(data, str(file_path))
        else:
            print(f"    No Z entries to append to {filename}")
    
    print(f"\nSummary:")
    print(f"  Z entries found by level:")
    for level, entries in z_entries_by_level.items():
        print(f"    Level {level}: {len(entries)} entries")
    
if __name__ == "__main__":
    main()