"""
Xatra Debug Utilities Module

This module provides time debugging utilities for tracking performance
and execution flow throughout the xatra codebase.
"""

import functools
from datetime import datetime
from typing import Any, Callable, Optional

# Global flag to enable/disable time debugging
DEBUG_TIME = False


def get_timestamp() -> str:
    """Get current time formatted as HH:MM:SS.
    
    Returns:
        String timestamp in HH:MM:SS format
    """
    return datetime.now().strftime("%H:%M:%S")


def debug_log(message: str, indent: int = 0):
    """Print a debug message with timestamp if DEBUG_TIME is enabled.
    
    Args:
        message: Debug message to print
        indent: Number of spaces to indent the message
    """
    if DEBUG_TIME:
        timestamp = get_timestamp()
        indent_str = " " * indent
        print(f"[{timestamp}] {indent_str}{message}")


def time_debug(activity_name: Optional[str] = None, indent: int = 0):
    """Decorator to add time debugging to functions.
    
    Logs when a function starts and finishes execution with timestamps.
    
    Args:
        activity_name: Custom name for the activity (defaults to function name)
        indent: Number of spaces to indent the debug messages
        
    Example:
        @time_debug()
        def my_function(x, y):
            return x + y
            
        @time_debug("Loading data")
        def load_data():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not DEBUG_TIME:
                return func(*args, **kwargs)
            
            name = activity_name if activity_name else func.__name__
            
            # Log function start
            debug_log(f"→ START: {name}", indent)
            
            # Get function arguments for debugging context
            if args or kwargs:
                arg_strs = []
                if args:
                    # Only show first few args to avoid clutter
                    arg_reprs = [repr(arg)[:50] for arg in args[:3]]
                    if len(args) > 3:
                        arg_reprs.append("...")
                    arg_strs.extend(arg_reprs)
                if kwargs:
                    # Show first few kwargs
                    kwarg_items = list(kwargs.items())[:3]
                    kwarg_strs = [f"{k}={repr(v)[:50]}" for k, v in kwarg_items]
                    if len(kwargs) > 3:
                        kwarg_strs.append("...")
                    arg_strs.extend(kwarg_strs)
                debug_log(f"  args: {', '.join(arg_strs)}", indent)
            
            try:
                result = func(*args, **kwargs)
                debug_log(f"✓ FINISH: {name}", indent)
                return result
            except Exception as e:
                debug_log(f"✗ ERROR in {name}: {type(e).__name__}: {str(e)[:100]}", indent)
                raise
        
        return wrapper
    return decorator


class DebugSection:
    """Context manager for debugging a section of code.
    
    Example:
        with DebugSection("Processing data"):
            # do work
            pass
    """
    
    def __init__(self, name: str, indent: int = 0):
        self.name = name
        self.indent = indent
    
    def __enter__(self):
        debug_log(f"→ START: {self.name}", self.indent)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            debug_log(f"✓ FINISH: {self.name}", self.indent)
        else:
            debug_log(f"✗ ERROR in {self.name}: {exc_type.__name__}", self.indent)
        return False

