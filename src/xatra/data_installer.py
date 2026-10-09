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


def _list_repo_files(repo_id: str) -> list[tuple[str, int]]:
    """List (path, size) of every file in the dataset repo (one paginated API listing)."""
    from huggingface_hub import HfApi

    files = []
    for entry in HfApi().list_repo_tree(repo_id, repo_type="dataset", recursive=True):
        size = getattr(entry, "size", None)
        if size is not None and not entry.path.startswith("."):
            files.append((entry.path, int(size)))
    return files


def _download_file(url: str, dest: Path, expected_size: int, max_attempts: int = 12) -> None:
    """Download one file with retries; backs off on rate limiting (HTTP 429) and server errors."""
    import time
    import requests

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    for attempt in range(max_attempts):
        try:
            with requests.get(url, stream=True, timeout=120, headers={"User-Agent": "xatra-install-data"}) as resp:
                if resp.status_code == 429 or resp.status_code >= 500:
                    wait = min(300, int(resp.headers.get("Retry-After", 0) or 0) or 20 * (attempt + 1))
                    print(f"  … server busy ({resp.status_code}); retrying in {wait}s", flush=True)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                with open(tmp, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
            if expected_size and tmp.stat().st_size != expected_size:
                raise IOError(f"size mismatch for {dest.name}")
            tmp.replace(dest)
            return
        except (requests.RequestException, IOError) as exc:
            wait = min(120, 10 * (attempt + 1))
            print(f"  … {exc}; retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Could not download {url}")


def download_from_huggingface(repo_id: str, target_dir: Path, force: bool = False):
    """
    Download data from Hugging Face Hub.

    Files are fetched one at a time from the CDN with retries, so the install
    survives Hugging Face's anonymous rate limits, and re-running it resumes
    where it stopped (files already present with the right size are skipped).

    Args:
        repo_id: HuggingFace repository ID (e.g., "username/xatra-data")
        target_dir: Local directory to download to
        force: If True, re-download even if data exists
    """
    from urllib.parse import quote

    try:
        import huggingface_hub  # noqa: F401
    except ImportError:
        print("ERROR: huggingface_hub is required for data installation.")
        print("Install it with: pip install huggingface_hub")
        sys.exit(1)

    print(f"Downloading Xatra data from Hugging Face: {repo_id}")
    print(f"Target directory: {target_dir}")
    print("This may take several minutes depending on your connection...")

    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        files = _list_repo_files(repo_id)
        # Geographic data first (needed to render anything), then the optional geometry cache.
        files.sort(key=lambda item: (not item[0].startswith("data/"), item[0]))
        total = len(files)
        pending = [
            (path, size) for path, size in files
            if force or not ((target_dir / path).exists() and (target_dir / path).stat().st_size == size)
        ]
        print(f"{total - len(pending)} of {total} files already present; fetching {len(pending)}.", flush=True)

        def fetch(item):
            path, size = item
            url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/{quote(path)}"
            _download_file(url, target_dir / path, size)
            return path

        done = total - len(pending)
        with ThreadPoolExecutor(max_workers=4) as pool:
            for future in as_completed([pool.submit(fetch, item) for item in pending]):
                done += 1
                print(f"  [{done}/{total}] {future.result()}", flush=True)
        print(f"✓ {total} files present in {target_dir}", flush=True)
    except Exception as e:
        print(f"ERROR: Failed to download data from Hugging Face: {e}")
        print("Re-run the installer to resume, or download manually:")
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

