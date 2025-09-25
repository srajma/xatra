#!/usr/bin/env python3
"""
GADM Data Downloader for Xatra Map-Making Software
Downloads all GADM 4.1 GeoJSON files for all countries at all administrative levels.
"""

import os
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gadm_download.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base URL for GADM 4.1 data
BASE_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json"

# Complete list of country codes from GADM 4.1
# Based on the GADM website dropdown list
COUNTRY_CODES = [
    'AFG', 'XAD', 'ALA', 'ALB', 'DZA', 'ASM', 'AND', 'AGO', 'AIA', 'ATA', 'ATG', 'ARG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN', 'BOL', 'BES', 'BIH', 'BWA', 'BVT', 'BRA', 'IOT', 'VGB', 'BRN', 'BGR', 'BFA', 'BDI', 'CPV', 'KHM', 'CMR', 'CAN', 'XCA', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'CXR', 'CPT', 'CCK', 'COL', 'COM', 'COG', 'COK', 'CRI', 'CIV', 'HRV', 'CUB', 'CUW', 'CYP', 'CZE', 'COD', 'DNK', 'DJI', 'DMA', 'DOM', 'TLS', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'SWZ', 'ETH', 'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'PYF', 'ATF', 'GAB', 'GMB', 'GEO', 'DEU', 'GHA', 'GIB', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GGY', 'GIN', 'GNB', 'GUY', 'HTI', 'HMD', 'HND', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JAM', 'JPN', 'JEY', 'JOR', 'KAZ', 'KEN', 'KIR', 'XKO', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LIE', 'LTU', 'LUX', 'MKD', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MHL', 'MTQ', 'MRT', 'MUS', 'MYT', 'MEX', 'FSM', 'MDA', 'MCO', 'MNG', 'MNE', 'MSR', 'MAR', 'MOZ', 'MMR', 'NAM', 'NRU', 'NPL', 'NLD', 'NCL', 'NZL', 'NIC', 'NER', 'NGA', 'NIU', 'NFK', 'PRK', 'CYN', 'MNP', 'NOR', 'OMN', 'PAK', 'PLW', 'PSE', 'PAN', 'PNG', 'XPA', 'PRY', 'PER', 'PHL', 'PCN', 'POL', 'PRT', 'PRI', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'BLM', 'MAF', 'SHN', 'KNA', 'LCA', 'SPM', 'VCT', 'WSM', 'SMR', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SXM', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SGS', 'KOR', 'SSD', 'ESP', 'XSP', 'LKA', 'SDN', 'SUR', 'SJM', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'TZA', 'THA', 'TGO', 'TKL', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'TCA', 'TUV', 'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'UMI', 'URY', 'UZB', 'VUT', 'VAT', 'VEN', 'VNM', 'VIR', 'WLF', 'ESH', 'YEM', 'ZMB', 'ZWE'
]

# Maximum administrative levels to check (most countries have 0-3, some have up to 5)
MAX_ADMIN_LEVELS = 5

class GADMDownloader:
    def __init__(self, base_dir: str = "data/gadm"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Xatra-Map-Software/1.0 (Educational/Research Use)'
        })
        
    def get_available_levels(self, country_code: str) -> List[int]:
        """Check which administrative levels are available for a country."""
        available_levels = []
        
        for level in range(MAX_ADMIN_LEVELS + 1):
            url = f"{BASE_URL}/gadm41_{country_code}_{level}.json"
            try:
                response = self.session.head(url, timeout=10)
                if response.status_code == 200:
                    available_levels.append(level)
                    logger.info(f"Found level {level} for {country_code}")
                else:
                    logger.debug(f"Level {level} not available for {country_code}")
            except Exception as e:
                logger.debug(f"Error checking level {level} for {country_code}: {e}")
                
        return available_levels
    
    def download_file(self, country_code: str, level: int) -> bool:
        """Download a single GADM file."""
        url = f"{BASE_URL}/gadm41_{country_code}_{level}.json"
        filename = f"gadm41_{country_code}_{level}.json"
        filepath = self.base_dir / filename
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"File {filename} already exists, skipping")
            return True
            
        try:
            logger.info(f"Downloading {filename}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Verify it's valid JSON
            try:
                data = response.json()
                if 'type' in data and data['type'] == 'FeatureCollection':
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    logger.info(f"Successfully downloaded {filename}")
                    return True
                else:
                    logger.error(f"Invalid GeoJSON format in {filename}")
                    return False
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {filename}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {filename}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {filename}: {e}")
            return False
    
    def download_country(self, country_code: str) -> Dict[str, any]:
        """Download all available levels for a country."""
        logger.info(f"Processing country: {country_code}")
        
        # Check available levels
        available_levels = self.get_available_levels(country_code)
        
        if not available_levels:
            logger.warning(f"No data found for country {country_code}")
            return {
                'country': country_code,
                'levels': [],
                'success': False,
                'error': 'No data available'
            }
        
        # Download all available levels
        results = []
        for level in available_levels:
            success = self.download_file(country_code, level)
            results.append({
                'level': level,
                'success': success
            })
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'country': country_code,
            'levels': available_levels,
            'downloaded': success_count,
            'total': len(available_levels),
            'success': success_count == len(available_levels),
            'results': results
        }
    
    def download_all(self, max_workers: int = 5) -> Dict[str, any]:
        """Download all GADM data for all countries."""
        logger.info(f"Starting download of GADM data for {len(COUNTRY_CODES)} countries")
        logger.info(f"Using {max_workers} concurrent workers")
        
        results = []
        failed_countries = []
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all country downloads
            future_to_country = {
                executor.submit(self.download_country, country): country 
                for country in COUNTRY_CODES
            }
            
            # Process completed downloads
            for future in as_completed(future_to_country):
                country = future_to_country[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result['success']:
                        failed_countries.append(country)
                        logger.error(f"Failed to download all data for {country}")
                    else:
                        logger.info(f"Successfully downloaded {result['downloaded']}/{result['total']} levels for {country}")
                        
                except Exception as e:
                    logger.error(f"Exception processing {country}: {e}")
                    failed_countries.append(country)
                    results.append({
                        'country': country,
                        'success': False,
                        'error': str(e)
                    })
                
                # Small delay to be respectful to the server
                time.sleep(0.1)
        
        # Summary
        total_countries = len(COUNTRY_CODES)
        successful_countries = total_countries - len(failed_countries)
        total_files = sum(r.get('downloaded', 0) for r in results)
        
        logger.info(f"\n=== DOWNLOAD SUMMARY ===")
        logger.info(f"Total countries: {total_countries}")
        logger.info(f"Successful countries: {successful_countries}")
        logger.info(f"Failed countries: {len(failed_countries)}")
        logger.info(f"Total files downloaded: {total_files}")
        
        if failed_countries:
            logger.info(f"Failed countries: {', '.join(failed_countries)}")
        
        return {
            'total_countries': total_countries,
            'successful_countries': successful_countries,
            'failed_countries': failed_countries,
            'total_files': total_files,
            'results': results
        }

def main():
    """Main function to run the GADM downloader."""
    print("🌍 Xatra GADM Data Downloader")
    print("=" * 50)
    
    downloader = GADMDownloader()
    
    try:
        summary = downloader.download_all(max_workers=3)  # Conservative number of workers
        
        # Save summary to file
        summary_file = downloader.base_dir / "download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Download completed!")
        print(f"📁 Data saved to: {downloader.base_dir}")
        print(f"📊 Summary saved to: {summary_file}")
        
        if summary['failed_countries']:
            print(f"⚠️  {len(summary['failed_countries'])} countries failed to download")
            print("Check the log file for details.")
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        print("\n⏹️  Download interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()