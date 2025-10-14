"""
Xatra Geometry Cache Module

This module provides a global caching system for Territory geometries with both
in-memory and on-disk caching layers. This significantly improves performance
for repeated geometry calculations.

The cache uses a hash of the Territory's string representation as the key,
avoiding redundant computations for identical territory expressions.
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry

from .debug_utils import time_debug


class GeometryCache:
    """Global geometry cache with in-memory and on-disk layers."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the geometry cache.
        
        Args:
            cache_dir: Directory for on-disk cache. If None, uses ~/.xatra/cache/
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".xatra" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache: hash -> geometry
        self._memory_cache: Dict[str, BaseGeometry] = {}
        
        # Cache statistics
        self._hits = 0
        self._misses = 0
        self._disk_hits = 0
        self._disk_misses = 0
    
    def _compute_hash(self, strrepr: str) -> str:
        """Compute a hash for the territory string representation.
        
        Args:
            strrepr: Territory string representation
            
        Returns:
            Hash string for use as cache key
        """
        return hashlib.sha256(strrepr.encode('utf-8')).hexdigest()[:16]
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.pkl"
    
    @time_debug("Get geometry from cache")
    def get(self, strrepr: str) -> Optional[BaseGeometry]:
        """Get geometry from cache.
        
        First checks in-memory cache, then on-disk cache.
        
        Args:
            strrepr: Territory string representation
            
        Returns:
            Cached geometry or None if not found
        """
        cache_key = self._compute_hash(strrepr)
        
        # Check in-memory cache first
        if cache_key in self._memory_cache:
            self._hits += 1
            return self._memory_cache[cache_key]
        
        # Check on-disk cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    geometry = pickle.load(f)
                # Store in memory cache for future access
                self._memory_cache[cache_key] = geometry
                self._disk_hits += 1
                self._hits += 1
                return geometry
            except (pickle.PickleError, EOFError, FileNotFoundError):
                # Cache file is corrupted, remove it
                cache_path.unlink(missing_ok=True)
        
        self._misses += 1
        self._disk_misses += 1
        return None
    
    @time_debug("Store geometry in cache")
    def put(self, strrepr: str, geometry: BaseGeometry) -> None:
        """Store geometry in cache.
        
        Stores in both in-memory and on-disk cache.
        
        Args:
            strrepr: Territory string representation
            geometry: Geometry to cache
        """
        cache_key = self._compute_hash(strrepr)
        
        # Store in memory cache
        self._memory_cache[cache_key] = geometry
        
        # Store in disk cache
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(geometry, f, protocol=pickle.HIGHEST_PROTOCOL)
        except (OSError, pickle.PickleError):
            # If disk write fails, continue with memory-only caching
            pass
    
    def clear_memory_cache(self) -> None:
        """Clear the in-memory cache."""
        self._memory_cache.clear()
    
    def clear_disk_cache(self) -> None:
        """Clear the on-disk cache."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink(missing_ok=True)
    
    def clear_all_cache(self) -> None:
        """Clear both in-memory and on-disk cache."""
        self.clear_memory_cache()
        self.clear_disk_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache hit/miss statistics
        """
        total_requests = self._hits + self._misses
        memory_size = len(self._memory_cache)
        
        # Count disk cache files
        disk_size = len(list(self.cache_dir.glob("*.pkl")))
        
        stats = {
            "total_requests": total_requests,
            "memory_hits": self._hits,
            "memory_misses": self._misses,
            "disk_hits": self._disk_hits,
            "disk_misses": self._disk_misses,
            "memory_cache_size": memory_size,
            "disk_cache_size": disk_size,
            "hit_rate": self._hits / total_requests if total_requests > 0 else 0.0,
            "cache_dir": str(self.cache_dir)
        }
        
        return stats


# Global cache instance
_global_cache: Optional[GeometryCache] = None


def get_global_cache() -> GeometryCache:
    """Get the global geometry cache instance.
    
    Returns:
        Global GeometryCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = GeometryCache()
    return _global_cache


def clear_geometry_cache(memory_only: bool = False, disk_only: bool = False) -> None:
    """Clear the global geometry cache.
    
    Args:
        memory_only: If True, only clear in-memory cache
        disk_only: If True, only clear on-disk cache
    """
    cache = get_global_cache()
    if memory_only:
        cache.clear_memory_cache()
    elif disk_only:
        cache.clear_disk_cache()
    else:
        cache.clear_all_cache()


def get_geometry_cache_stats() -> Dict[str, Any]:
    """Get statistics for the global geometry cache.
    
    Returns:
        Dictionary with cache statistics
    """
    return get_global_cache().get_cache_stats()
