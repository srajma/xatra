#!/usr/bin/env python3
"""
GADM Data Verification Script
Verifies that all downloaded GeoJSON files are valid and contain the expected structure.
"""

import json
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_geojson_file(filepath: Path) -> dict:
    """Verify a single GeoJSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check basic GeoJSON structure
        if not isinstance(data, dict):
            return {"valid": False, "error": "Not a JSON object"}
        
        if data.get("type") != "FeatureCollection":
            return {"valid": False, "error": "Not a FeatureCollection"}
        
        if "features" not in data:
            return {"valid": False, "error": "Missing features array"}
        
        features = data.get("features", [])
        if not isinstance(features, list):
            return {"valid": False, "error": "Features is not an array"}
        
        # Count features and check for geometry
        feature_count = len(features)
        valid_geometries = 0
        
        for feature in features:
            if isinstance(feature, dict) and "geometry" in feature:
                valid_geometries += 1
        
        return {
            "valid": True,
            "feature_count": feature_count,
            "valid_geometries": valid_geometries,
            "has_crs": "crs" in data,
            "name": data.get("name", "unknown")
        }
        
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "error": f"Error reading file: {e}"}

def main():
    """Main verification function."""
    data_dir = Path("data/gadm")
    
    if not data_dir.exists():
        logger.error("Data directory not found!")
        return
    
    # Get all JSON files
    json_files = list(data_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "download_summary.json"]
    
    logger.info(f"Found {len(json_files)} GeoJSON files to verify")
    
    valid_files = 0
    invalid_files = []
    total_features = 0
    total_valid_geometries = 0
    
    for filepath in json_files:
        result = verify_geojson_file(filepath)
        
        if result["valid"]:
            valid_files += 1
            total_features += result["feature_count"]
            total_valid_geometries += result["valid_geometries"]
            logger.info(f"✅ {filepath.name}: {result['feature_count']} features, {result['valid_geometries']} valid geometries")
        else:
            invalid_files.append({
                "file": filepath.name,
                "error": result["error"]
            })
            logger.error(f"❌ {filepath.name}: {result['error']}")
    
    # Summary
    logger.info(f"\n=== VERIFICATION SUMMARY ===")
    logger.info(f"Total files: {len(json_files)}")
    logger.info(f"Valid files: {valid_files}")
    logger.info(f"Invalid files: {len(invalid_files)}")
    logger.info(f"Total features: {total_features:,}")
    logger.info(f"Total valid geometries: {total_valid_geometries:,}")
    
    if invalid_files:
        logger.info(f"\nInvalid files:")
        for item in invalid_files:
            logger.info(f"  - {item['file']}: {item['error']}")
    
    # Calculate success rate
    success_rate = (valid_files / len(json_files)) * 100 if json_files else 0
    logger.info(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        logger.info("🎉 Excellent! Over 95% of files are valid.")
    elif success_rate >= 90:
        logger.info("✅ Good! Over 90% of files are valid.")
    else:
        logger.warning("⚠️  Some files have issues. Check the errors above.")

if __name__ == "__main__":
    main()