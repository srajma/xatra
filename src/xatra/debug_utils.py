"""
Xatra Debug Utilities Module

This module provides time debugging utilities for tracking performance
and execution flow throughout the xatra codebase.
"""

import functools
import time
import threading
from datetime import datetime
from typing import Any, Callable, Optional, Dict, List
from collections import defaultdict

# Global flag to enable/disable time debugging
DEBUG_TIME = False

# Thread-local storage for timing data
_local = threading.local()

# Global timing statistics
_timing_stats = {
    'exclusive_times': defaultdict(float),  # Function name -> exclusive time
    'total_times': defaultdict(float),      # Function name -> total time
    'call_counts': defaultdict(int),        # Function name -> number of calls
}


def get_timestamp() -> str:
    """Get current time formatted as HH:MM:SS.
    
    Returns:
        String timestamp in HH:MM:SS format
    """
    return datetime.now().strftime("%H:%M:%S")


def _get_current_time():
    """Get current time in seconds with high precision."""
    return time.perf_counter()


def _init_local_data():
    """Initialize thread-local data structures."""
    if not hasattr(_local, 'call_stack'):
        _local.call_stack = []
    if not hasattr(_local, 'child_times'):
        _local.child_times = defaultdict(float)  # Function name -> time spent in children


def reset_timing_stats():
    """Reset all timing statistics."""
    global _timing_stats
    _timing_stats = {
        'exclusive_times': defaultdict(float),
        'total_times': defaultdict(float),
        'call_counts': defaultdict(int),
    }
    _init_local_data()
    _local.call_stack = []
    _local.child_times = defaultdict(float)


def get_timing_stats() -> Dict[str, Any]:
    """Get current timing statistics.
    
    Returns:
        Dictionary containing timing statistics with keys:
        - exclusive_times: Dict[str, float] - Function name -> exclusive time
        - total_times: Dict[str, float] - Function name -> total time  
        - call_counts: Dict[str, int] - Function name -> number of calls
    """
    return {
        'exclusive_times': dict(_timing_stats['exclusive_times']),
        'total_times': dict(_timing_stats['total_times']),
        'call_counts': dict(_timing_stats['call_counts']),
    }


def print_timing_summary():
    """Print a summary of timing statistics."""
    if not DEBUG_TIME:
        print("Time debugging is disabled. Enable with set_debug_time(True)")
        return
    
    stats = get_timing_stats()
    
    if not stats['exclusive_times']:
        print("No timing data available.")
        return
    
    print("\n" + "="*80)
    print("TIMING SUMMARY")
    print("="*80)
    
    # Sort by exclusive time (descending)
    sorted_functions = sorted(
        stats['exclusive_times'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    print(f"{'Function':<40} {'Exclusive':<12} {'Total':<12} {'Calls':<8} {'Avg/Excl':<10}")
    print("-" * 80)
    
    for func_name, excl_time in sorted_functions:
        total_time = stats['total_times'].get(func_name, 0)
        call_count = stats['call_counts'].get(func_name, 1)
        avg_excl = excl_time / call_count if call_count > 0 else 0
        
        print(f"{func_name:<40} {excl_time:<12.4f} {total_time:<12.4f} {call_count:<8} {avg_excl:<10.4f}")
    
    total_exclusive = sum(stats['exclusive_times'].values())
    total_time = sum(stats['total_times'].values())
    
    print("-" * 80)
    print(f"{'TOTAL':<40} {total_exclusive:<12.4f} {total_time:<12.4f}")
    print("="*80)


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
    """Decorator to add time debugging to functions with exclusive timing.
    
    Logs when a function starts and finishes execution with timestamps.
    Tracks both total time and exclusive time (excluding time spent in other tracked functions).
    
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
            
            # Initialize thread-local data
            _init_local_data()
            
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
            
            # Start timing this function
            start_time = _get_current_time()
            _local.call_stack.append((name, start_time, 0.0))  # (name, start_time, child_time)
            _timing_stats['call_counts'][name] += 1
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate timing
                end_time = _get_current_time()
                total_elapsed = end_time - start_time
                
                # Get child time from the call stack entry
                _, _, child_time = _local.call_stack.pop()
                
                # Calculate exclusive time (total time minus time spent in child functions)
                exclusive_time = total_elapsed - child_time
                
                # Update timing statistics
                _timing_stats['total_times'][name] += total_elapsed
                _timing_stats['exclusive_times'][name] += exclusive_time
                
                # Add this function's total time to its parent's child time
                if _local.call_stack:
                    parent_name, parent_start, parent_child_time = _local.call_stack[-1]
                    _local.call_stack[-1] = (parent_name, parent_start, parent_child_time + total_elapsed)
                
                debug_log(f"✓ FINISH: {name}", indent)
                return result
                
            except Exception as e:
                # Calculate timing even on error
                end_time = _get_current_time()
                total_elapsed = end_time - start_time
                
                # Get child time from the call stack entry
                _, _, child_time = _local.call_stack.pop()
                
                # Calculate exclusive time
                exclusive_time = total_elapsed - child_time
                
                # Update timing statistics
                _timing_stats['total_times'][name] += total_elapsed
                _timing_stats['exclusive_times'][name] += exclusive_time
                
                # Add this function's total time to its parent's child time
                if _local.call_stack:
                    parent_name, parent_start, parent_child_time = _local.call_stack[-1]
                    _local.call_stack[-1] = (parent_name, parent_start, parent_child_time + total_elapsed)
                
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


def plot_timing_chart(show_chart: bool = True, save_path: Optional[str] = None):
    """Create a bar chart visualization of timing statistics.
    
    Args:
        show_chart: Whether to display the chart (requires matplotlib)
        save_path: Optional path to save the chart as an image file
        
    Returns:
        matplotlib figure object if matplotlib is available, None otherwise
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("matplotlib not available for plotting. Install with: pip install matplotlib")
        return None
    
    if not DEBUG_TIME:
        print("Time debugging is disabled. Enable with set_debug_time(True)")
        return None
    
    stats = get_timing_stats()
    
    if not stats['exclusive_times']:
        print("No timing data available.")
        return None
    
    # Sort by exclusive time (descending)
    sorted_functions = sorted(
        stats['exclusive_times'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Take top 15 functions to avoid overcrowding
    top_functions = sorted_functions[:15]
    
    if not top_functions:
        print("No timing data to plot.")
        return None
    
    # Extract data
    func_names = [name for name, _ in top_functions]
    exclusive_times = [time for _, time in top_functions]
    total_times = [stats['total_times'].get(name, 0) for name in func_names]
    call_counts = [stats['call_counts'].get(name, 1) for name in func_names]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Truncate long function names for display
    display_names = [name[:30] + "..." if len(name) > 30 else name for name in func_names]
    
    # Plot 1: Exclusive times
    bars1 = ax1.barh(range(len(display_names)), exclusive_times, color='steelblue', alpha=0.7)
    ax1.set_yticks(range(len(display_names)))
    ax1.set_yticklabels(display_names)
    ax1.set_xlabel('Exclusive Time (seconds)')
    ax1.set_title('Function Execution Times - Exclusive (Top 15)', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time) in enumerate(zip(bars1, exclusive_times)):
        width = bar.get_width()
        ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                f'{time:.3f}s', ha='left', va='center', fontsize=9)
    
    # Plot 2: Total vs Exclusive comparison
    x = range(len(display_names))
    width = 0.35
    
    bars2 = ax2.bar([i - width/2 for i in x], exclusive_times, width, 
                   label='Exclusive', color='steelblue', alpha=0.7)
    bars3 = ax2.bar([i + width/2 for i in x], total_times, width, 
                   label='Total', color='orange', alpha=0.7)
    
    ax2.set_xlabel('Functions')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Exclusive vs Total Time Comparison', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(display_names, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, time in zip(bars2, exclusive_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + height*0.01, 
                f'{time:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)
    
    for bar, time in zip(bars3, total_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height + height*0.01, 
                f'{time:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)
    
    plt.tight_layout()
    
    # Add summary statistics as text
    total_exclusive = sum(exclusive_times)
    total_time = sum(total_times)
    
    summary_text = f"Summary:\n"
    summary_text += f"Total Exclusive Time: {total_exclusive:.3f}s\n"
    summary_text += f"Total Time: {total_time:.3f}s\n"
    summary_text += f"Functions Tracked: {len(stats['exclusive_times'])}\n"
    summary_text += f"Total Function Calls: {sum(stats['call_counts'].values())}"
    
    fig.text(0.02, 0.02, summary_text, fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Timing chart saved to: {save_path}")
    
    if show_chart:
        plt.show()
    
    return fig


def show_timing_chart():
    """Convenience function to display the timing chart."""
    return plot_timing_chart(show_chart=True)


def _auto_display_timing_stats():
    """Automatically display timing statistics when debug time is enabled.
    
    This function is registered to run at program exit when DEBUG_TIME is True.
    It displays both the text summary and the chart if timing data exists.
    """
    if not DEBUG_TIME:
        return
    
    stats = get_timing_stats()
    
    # Only display if we have timing data
    if not stats['exclusive_times']:
        return
    
    print("\n" + "="*80)
    print("AUTOMATIC TIMING SUMMARY")
    print("="*80)
    print("Time debugging was enabled. Here's the performance analysis:")
    
    # Print the timing summary
    print_timing_summary()
    
    # Try to show the chart
    print("\nGenerating timing visualization chart...")
    try:
        plot_timing_chart(show_chart=True)
    except ImportError:
        print("Note: matplotlib not available for chart display. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Note: Could not display chart: {e}")
    
    print("\nTo disable automatic timing display, use: xatra.set_debug_time(False)")
    print("="*80)

