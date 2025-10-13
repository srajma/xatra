"""
Xatra Debug Utilities Module

This module provides time debugging utilities for tracking performance
and execution flow throughout the xatra codebase. It supports exclusive
timing (excluding time spent in other tracked functions) and generates
performance analysis charts.
"""

import functools
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global flag to enable/disable time debugging
DEBUG_TIME = False

# Thread-local storage for timing context
_thread_local = threading.local()

# Global timing statistics
_timing_stats = defaultdict(lambda: {'total_time': 0.0, 'exclusive_time': 0.0, 'call_count': 0})


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


def _get_timing_stack():
    """Get the current timing stack for this thread."""
    if not hasattr(_thread_local, 'timing_stack'):
        _thread_local.timing_stack = []
    return _thread_local.timing_stack


def _get_timing_context():
    """Get the current timing context for this thread."""
    if not hasattr(_thread_local, 'timing_context'):
        _thread_local.timing_context = {
            'start_time': None,
            'exclusive_time': 0.0,
            'nested_start_time': None
        }
    return _thread_local.timing_context


def time_debug(activity_name: Optional[str] = None, indent: int = 0):
    """Decorator to add time debugging to functions with exclusive timing.
    
    Tracks both total execution time and exclusive time (excluding time spent
    in other tracked functions called within this function).
    
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
            stack = _get_timing_stack()
            context = _get_timing_context()
            
            # Record start time
            start_time = time.time()
            
            # Pause exclusive timing for any parent function
            if stack:
                parent_context = stack[-1]
                if parent_context['nested_start_time'] is None:
                    parent_context['nested_start_time'] = start_time
            
            # Add this function to the stack
            function_context = {
                'name': name,
                'start_time': start_time,
                'exclusive_time': 0.0,
                'nested_start_time': None
            }
            stack.append(function_context)
            
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
                
                # Calculate timing
                end_time = time.time()
                total_time = end_time - start_time
                
                # Calculate exclusive time
                # Start with total time, subtract time spent in nested tracked functions
                exclusive_time = total_time
                if function_context['nested_start_time'] is not None:
                    nested_duration = end_time - function_context['nested_start_time']
                    exclusive_time = total_time - nested_duration
                
                # Update global stats
                _timing_stats[name]['total_time'] += total_time
                _timing_stats[name]['exclusive_time'] += exclusive_time
                _timing_stats[name]['call_count'] += 1
                
                # Resume exclusive timing for parent function
                stack.pop()  # Remove this function from stack
                if stack:
                    parent_context = stack[-1]
                    if parent_context['nested_start_time'] is not None:
                        # Resume parent's exclusive timing
                        parent_context['nested_start_time'] = None
                
                debug_log(f"✓ FINISH: {name} (total: {total_time:.3f}s, exclusive: {exclusive_time:.3f}s)", indent)
                return result
                
            except Exception as e:
                # Handle error case - still need to clean up timing
                end_time = time.time()
                total_time = end_time - start_time
                exclusive_time = total_time
                
                if function_context['nested_start_time'] is not None:
                    nested_duration = end_time - function_context['nested_start_time']
                    exclusive_time = total_time - nested_duration
                
                # Update global stats even for errors
                _timing_stats[name]['total_time'] += total_time
                _timing_stats[name]['exclusive_time'] += exclusive_time
                _timing_stats[name]['call_count'] += 1
                
                # Clean up stack
                stack.pop()
                if stack:
                    parent_context = stack[-1]
                    if parent_context['nested_start_time'] is not None:
                        parent_context['nested_start_time'] = None
                
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
        self.start_time = None
        self.function_context = None
    
    def __enter__(self):
        if DEBUG_TIME:
            self.start_time = time.time()
            stack = _get_timing_stack()
            
            # Pause exclusive timing for any parent function
            if stack:
                parent_context = stack[-1]
                if parent_context['nested_start_time'] is None:
                    parent_context['nested_start_time'] = self.start_time
            
            # Add this section to the stack
            self.function_context = {
                'name': self.name,
                'start_time': self.start_time,
                'exclusive_time': 0.0,
                'nested_start_time': None
            }
            stack.append(self.function_context)
            
            debug_log(f"→ START: {self.name}", self.indent)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if DEBUG_TIME and self.start_time is not None:
            end_time = time.time()
            total_time = end_time - self.start_time
            
            # Calculate exclusive time
            exclusive_time = total_time
            if self.function_context['nested_start_time'] is not None:
                nested_duration = end_time - self.function_context['nested_start_time']
                exclusive_time = total_time - nested_duration
            
            # Update global stats
            _timing_stats[self.name]['total_time'] += total_time
            _timing_stats[self.name]['exclusive_time'] += exclusive_time
            _timing_stats[self.name]['call_count'] += 1
            
            # Clean up stack
            stack = _get_timing_stack()
            stack.pop()
            if stack:
                parent_context = stack[-1]
                if parent_context['nested_start_time'] is not None:
                    parent_context['nested_start_time'] = None
            
            if exc_type is None:
                debug_log(f"✓ FINISH: {self.name} (total: {total_time:.3f}s, exclusive: {exclusive_time:.3f}s)", self.indent)
            else:
                debug_log(f"✗ ERROR in {self.name}: {exc_type.__name__}", self.indent)
        return False


def get_timing_stats() -> Dict[str, Dict[str, float]]:
    """Get current timing statistics.
    
    Returns:
        Dictionary mapping function names to their timing statistics
    """
    return dict(_timing_stats)


def clear_timing_stats():
    """Clear all timing statistics."""
    global _timing_stats
    _timing_stats.clear()


def generate_timing_chart(save_path: Optional[str] = None, show_chart: bool = True) -> str:
    """Generate a bar chart showing function timing statistics.
    
    Args:
        save_path: Optional path to save the chart. If None, saves to 'xatra_timing_analysis.png'
        show_chart: Whether to display the chart (default: True)
        
    Returns:
        Path to the saved chart file
    """
    if not _timing_stats:
        print("No timing data available. Make sure DEBUG_TIME is enabled and functions have been called.")
        return ""
    
    # Prepare data
    functions = list(_timing_stats.keys())
    exclusive_times = [_timing_stats[f]['exclusive_time'] for f in functions]
    total_times = [_timing_stats[f]['total_time'] for f in functions]
    call_counts = [_timing_stats[f]['call_count'] for f in functions]
    
    # Sort by exclusive time (descending)
    sorted_data = sorted(zip(functions, exclusive_times, total_times, call_counts), 
                        key=lambda x: x[1], reverse=True)
    functions, exclusive_times, total_times, call_counts = zip(*sorted_data)
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Top chart: Exclusive times
    bars1 = ax1.barh(range(len(functions)), exclusive_times, color='skyblue', alpha=0.7)
    ax1.set_yticks(range(len(functions)))
    ax1.set_yticklabels([f"{f} ({c} calls)" for f, c in zip(functions, call_counts)], fontsize=9)
    ax1.set_xlabel('Exclusive Time (seconds)')
    ax1.set_title('Function Execution Times (Exclusive - excluding nested tracked functions)', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time_val) in enumerate(zip(bars1, exclusive_times)):
        if time_val > 0:
            ax1.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, 
                    f'{time_val:.3f}s', va='center', ha='left', fontsize=8)
    
    # Bottom chart: Total times
    bars2 = ax2.barh(range(len(functions)), total_times, color='lightcoral', alpha=0.7)
    ax2.set_yticks(range(len(functions)))
    ax2.set_yticklabels([f"{f} ({c} calls)" for f, c in zip(functions, call_counts)], fontsize=9)
    ax2.set_xlabel('Total Time (seconds)')
    ax2.set_title('Function Execution Times (Total - including all nested function calls)', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time_val) in enumerate(zip(bars2, total_times)):
        if time_val > 0:
            ax2.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, 
                    f'{time_val:.3f}s', va='center', ha='left', fontsize=8)
    
    plt.tight_layout()
    
    # Save the chart
    if save_path is None:
        save_path = "xatra_timing_analysis.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show_chart:
        plt.show()
    else:
        plt.close()
    
    print(f"Timing analysis chart saved to: {save_path}")
    return save_path


def print_timing_summary():
    """Print a summary of timing statistics."""
    if not _timing_stats:
        print("No timing data available.")
        return
    
    print("\n" + "="*80)
    print("XATRA TIMING ANALYSIS SUMMARY")
    print("="*80)
    
    # Sort by exclusive time
    sorted_functions = sorted(_timing_stats.items(), key=lambda x: x[1]['exclusive_time'], reverse=True)
    
    print(f"{'Function':<40} {'Calls':<8} {'Total(s)':<10} {'Exclusive(s)':<12} {'Avg Total':<10} {'Avg Exclusive':<12}")
    print("-" * 80)
    
    for name, stats in sorted_functions:
        calls = stats['call_count']
        total = stats['total_time']
        exclusive = stats['exclusive_time']
        avg_total = total / calls if calls > 0 else 0
        avg_exclusive = exclusive / calls if calls > 0 else 0
        
        print(f"{name:<40} {calls:<8} {total:<10.3f} {exclusive:<12.3f} {avg_total:<10.3f} {avg_exclusive:<12.3f}")
    
    print("="*80)
    print(f"Total functions tracked: {len(_timing_stats)}")
    print("="*80)

