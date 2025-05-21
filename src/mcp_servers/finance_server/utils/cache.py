"""
Cache utility for the Finance MCP Server
"""
import time
from typing import Dict, Any, Optional


class DataCache:
    """
    Simple in-memory cache with TTL for financial data
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the cache
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        expiry_time = cache_entry.get("expiry")
        
        # Check if the entry has expired
        if expiry_time and time.time() > expiry_time:
            # Remove expired entry
            del self._cache[key]
            return None
            
        return cache_entry.get("value")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        expiry_time = time.time() + (ttl if ttl is not None else self._default_ttl)
        
        self._cache[key] = {
            "value": value,
            "expiry": expiry_time
        }
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all entries from the cache"""
        self._cache.clear()
    
    def cleanup(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if "expiry" in entry and current_time > entry["expiry"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys) 