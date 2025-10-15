#!/usr/bin/env python3
"""
Xatra Data Installer

Downloads and installs Xatra data files from Hugging Face to ~/.xatra/data
This script is run automatically during package installation.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

# Hugging Face repository containing the data
HUGGINGFACE_REPO = "srajma/xatra-data"  

# Local data directory
XATRA_DATA_DIR = Path.home() / ".xatra"

REQUIRED_PATHS = [
    XATRA_DATA_DIR / "data" / "gadm",
    XATRA_DATA_DIR / "data" / "disputed_territories",
    XATRA_DATA_DIR / "data" / "ne_10m_rivers.geojson",
    XATRA_DATA_DIR / "data" / "rivers_overpass_india",
    XATRA_DATA_DIR / "cache",
]
def get_xatra_dir() -> Path:
    """Get the Xatra data directory path."""
    return XATRA_DATA_DIR

def get_data_dir() -> Path:
    """Get ~/.xatra/data"""
    return XATRA_DATA_DIR / "data"


def ensure_xatra_dir() -> Path:
    """Ensure the data directory exists."""
    XATRA_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return XATRA_DATA_DIR


def is_data_installed() -> bool:
    """Check if data is already installed."""
    return all(p.exists() for p in REQUIRED_PATHS)


def download_from_huggingface(repo_id: str, target_dir: Path, force: bool = False):
    """
    Download data from Hugging Face Hub.
    
    Args:
        repo_id: HuggingFace repository ID (e.g., "username/xatra-data")
        target_dir: Local directory to download to
        force: If True, re-download even if data exists
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("ERROR: huggingface_hub is required for data installation.")
        print("Install it with: pip install huggingface_hub")
        sys.exit(1)
    
    print(f"Downloading Xatra data from Hugging Face: {repo_id}")
    print(f"Target directory: {target_dir}")
    print("This may take several minutes depending on your connection...")
    
    try:
        # Download the entire repository
        snapshot_dir = snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=target_dir,
            local_dir_use_symlinks=False,
        )
        
        print(f"✓ Following files were downloaded to {target_dir}:")
        print(f"Contents of {target_dir}:")
        for item in target_dir.iterdir():
            print(f"  - {item.name}{'/' if item.is_dir() else ''}")
        
    except Exception as e:
        print(f"ERROR: Failed to download data from Hugging Face: {e}")
        print(f"\nYou can manually download the data:")
        print(f"1. Visit: https://huggingface.co/datasets/{repo_id}")
        print(f"2. Download and extract the data to: {target_dir}")
        sys.exit(1)


def verify_data_integrity() -> bool:
    """Verify that all required data files are present and valid."""
    print("Verifying data integrity...")

    
    all_valid = True
    
    for file_path in REQUIRED_PATHS:
        if not file_path.exists():
            print(f"  ✗ Missing {'file' if file_path.is_file() else 'directory'}: {file_path}")
            all_valid = False
        
        elif file_path.is_file() and file_path.stat().st_size == 0:
            print(f"  ✗ Empty file: {file_path}")
            all_valid = False
        elif file_path.is_dir() and not any(file_path.iterdir()):
            print(f"  ✗ Empty directory: {file_path}")
            all_valid = False
        elif file_path.is_file():
            print(f"  ✓ Found: {file_path}")
        elif file_path.is_dir():
            # Count files
            file_count = sum(1 for _ in file_path.rglob("*") if _.is_file())
            print(f"  ✓ Found: {file_path}/ ({file_count} files)")
    
    return all_valid


def install_data(force: bool = False, skip_verify: bool = False):
    """
    Main installation function.
    
    Args:
        force: If True, re-download even if data exists
        skip_verify: If True, skip data integrity verification
    """
    print("=" * 70)
    print("Xatra Data Installer")
    print("=" * 70)
    
    # Check if data is already installed
    if is_data_installed() and not force:
        print(f"\nData already installed at: {XATRA_DATA_DIR}")
        if not skip_verify:
            if verify_data_integrity():
                print("\n✓ All data files verified successfully!")
                return
            else:
                print("\n⚠ Data verification failed. Re-downloading...")
                force = True
        else:
            return
    
    # Ensure directory exists
    ensure_xatra_dir()
    
    # Download from Hugging Face
    download_from_huggingface(HUGGINGFACE_REPO, XATRA_DATA_DIR, force=force)
    
    # Verify installation
    if not skip_verify:
        if verify_data_integrity():
            print("\n✓ Data installation complete!")
        else:
            print("\n⚠ Data installation completed with warnings.")
            print("Some files may be missing. Please check manually.")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print(f"Data installed to: {XATRA_DATA_DIR}")
    print("=" * 70)


def print_data_info():
    """Print information about data location and status."""
    print("=" * 70)
    print("Xatra Data Information")
    print("=" * 70)
    print(f"Data directory: {XATRA_DATA_DIR}")
    print(f"Data installed: {'Yes' if is_data_installed() else 'No'}")
    print(f"Hugging Face repo: {HUGGINGFACE_REPO}")
    print("=" * 70)


def main():
    """CLI entry point for manual data installation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Install Xatra data files from Hugging Face",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  xatra-install-data              # Install data
  xatra-install-data --check      # Check if data is installed
  xatra-install-data --force      # Force re-download
  xatra-install-data --info       # Show data location info
        """
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if data exists",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip data integrity verification",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check if data is installed (no download)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show data location and status information",
    )
    
    args = parser.parse_args()
    
    if args.info:
        print_data_info()
        sys.exit(0)
    
    if args.check:
        if is_data_installed():
            print(f"✓ Data is installed at: {XATRA_DATA_DIR}")
            verify_data_integrity()
            sys.exit(0)
        else:
            print(f"✗ Data is not installed at: {XATRA_DATA_DIR}")
            print("Run 'xatra-install-data' to install.")
            sys.exit(1)
    
    try:
        install_data(force=args.force, skip_verify=args.skip_verify)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()

