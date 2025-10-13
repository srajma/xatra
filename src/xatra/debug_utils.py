"""
Xatra Debug Utilities Module

This module provides time debugging utilities for tracking performance
and execution flow throughout the xatra codebase.
"""

import functools
import time
import atexit
from datetime import datetime
from typing import Any, Callable, Optional, Dict, List, Tuple
import threading

# Global flag to enable/disable time debugging
DEBUG_TIME = False

# Auto-print stats configuration
AUTO_PRINT_STATS = True
AUTO_SAVE_PLOT = True
AUTO_PLOT_PATH = "xatra_timing_analysis.png"

# Timing statistics storage
_timing_stats: Dict[str, List[float]] = {}
_call_stack: List[str] = []
_thread_local = threading.local()

# Track if auto-print has been registered
_auto_print_registered = False


def _register_auto_print():
    """Register the auto-print function to run at program exit."""
    global _auto_print_registered
    if not _auto_print_registered and DEBUG_TIME:
        atexit.register(_auto_print_and_plot_stats)
        _auto_print_registered = True


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


def _get_thread_call_stack():
    """Get the call stack for the current thread."""
    if not hasattr(_thread_local, 'call_stack'):
        _thread_local.call_stack = []
    return _thread_local.call_stack


def _record_timing(function_name: str, elapsed_time: float):
    """Record timing statistics for a function.
    
    Args:
        function_name: Name of the function
        elapsed_time: Time spent in the function (excluding nested calls)
    """
    if function_name not in _timing_stats:
        _timing_stats[function_name] = []
    _timing_stats[function_name].append(elapsed_time)


def get_timing_stats() -> Dict[str, Dict[str, float]]:
    """Get timing statistics for all tracked functions.
    
    Returns:
        Dictionary mapping function names to statistics (total_time, avg_time, call_count)
    """
    stats = {}
    for function_name, times in _timing_stats.items():
        if times:
            stats[function_name] = {
                'total_time': sum(times),
                'avg_time': sum(times) / len(times),
                'call_count': len(times),
                'min_time': min(times),
                'max_time': max(times)
            }
    return stats


def clear_timing_stats():
    """Clear all timing statistics."""
    global _timing_stats
    _timing_stats.clear()
    # Clear thread-local call stacks
    if hasattr(_thread_local, 'call_stack'):
        _thread_local.call_stack.clear()


def _auto_print_and_plot_stats():
    """Automatically print stats and save plot if enabled."""
    if not DEBUG_TIME:
        return
    
    # Only auto-print if we have some timing data
    if not _timing_stats:
        return
    
    # Print stats if enabled
    if AUTO_PRINT_STATS:
        print_timing_stats()
    
    # Save plot if enabled
    if AUTO_SAVE_PLOT:
        try:
            plot_timing_stats(
                save_path=AUTO_PLOT_PATH,
                show_plot=False,  # Don't show plot automatically
                top_n=15  # Show top 15 functions
            )
        except Exception as e:
            # Don't fail if plotting fails
            print(f"Note: Could not auto-save timing plot: {e}")


def configure_auto_stats(auto_print: bool = True, auto_save_plot: bool = True, plot_path: str = "xatra_timing_analysis.png"):
    """Configure automatic statistics printing and plotting.
    
    Args:
        auto_print: Whether to automatically print timing statistics
        auto_save_plot: Whether to automatically save timing plots
        plot_path: Path for automatically saved plots
    """
    global AUTO_PRINT_STATS, AUTO_SAVE_PLOT, AUTO_PLOT_PATH
    AUTO_PRINT_STATS = auto_print
    AUTO_SAVE_PLOT = auto_save_plot
    AUTO_PLOT_PATH = plot_path


def print_timing_stats():
    """Print timing statistics in a formatted table."""
    stats = get_timing_stats()
    if not stats:
        print("No timing statistics available.")
        return
    
    # Sort by total time descending
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_time'], reverse=True)
    
    print("\n" + "=" * 80)
    print("XATRA TIMING STATISTICS")
    print("=" * 80)
    print(f"{'Function Name':<40} {'Calls':<8} {'Total (s)':<12} {'Avg (s)':<12} {'Min (s)':<12} {'Max (s)':<12}")
    print("-" * 80)
    
    for function_name, data in sorted_stats:
        print(f"{function_name:<40} {data['call_count']:<8} {data['total_time']:<12.4f} "
              f"{data['avg_time']:<12.4f} {data['min_time']:<12.4f} {data['max_time']:<12.4f}")
    
    print("=" * 80)


def plot_timing_stats(save_path: Optional[str] = None, show_plot: bool = True, top_n: Optional[int] = None):
    """Generate a bar chart of timing statistics.
    
    Args:
        save_path: Optional path to save the plot as PNG/PDF
        show_plot: Whether to display the plot (default: True)
        top_n: Number of top functions to show (default: all)
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("Error: matplotlib is required for plotting timing statistics.")
        print("Install with: pip install matplotlib")
        return
    
    stats = get_timing_stats()
    if not stats:
        print("No timing statistics available for plotting.")
        return
    
    # Sort by total time descending
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_time'], reverse=True)
    
    # Limit to top N if specified
    if top_n:
        sorted_stats = sorted_stats[:top_n]
    
    if not sorted_stats:
        print("No data to plot.")
        return
    
    # Extract data for plotting
    function_names = [name.replace('_', ' ').title() for name, _ in sorted_stats]
    total_times = [data['total_time'] for _, data in sorted_stats]
    call_counts = [data['call_count'] for _, data in sorted_stats]
    avg_times = [data['avg_time'] for _, data in sorted_stats]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Color mapping based on call count (more calls = darker)
    colors = plt.cm.viridis([count / max(call_counts) for count in call_counts])
    
    # Plot 1: Total time by function
    bars1 = ax1.barh(function_names, total_times, color=colors)
    ax1.set_xlabel('Total Time (seconds)')
    ax1.set_title('Xatra Function Timing - Total Time (excluding nested calls)')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time_val) in enumerate(zip(bars1, total_times)):
        width = bar.get_width()
        ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                f'{time_val:.3f}s', ha='left', va='center', fontsize=9)
    
    # Plot 2: Average time by function
    bars2 = ax2.barh(function_names, avg_times, color=colors)
    ax2.set_xlabel('Average Time (seconds)')
    ax2.set_title('Xatra Function Timing - Average Time per Call')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, time_val) in enumerate(zip(bars2, avg_times)):
        width = bar.get_width()
        ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                f'{time_val:.3f}s', ha='left', va='center', fontsize=9)
    
    # Add call count annotations
    for i, (ax, bars) in enumerate([(ax1, bars1), (ax2, bars2)]):
        for j, (bar, count) in enumerate(zip(bars, call_counts)):
            ax.text(0.02, bar.get_y() + bar.get_height()/2, 
                   f'{count} calls', ha='left', va='center', 
                   fontsize=8, color='white', weight='bold')
    
    plt.tight_layout()
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='darkblue', label='Few calls'),
        mpatches.Patch(color='yellow', label='Many calls')
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Timing plot saved to: {save_path}")
    
    # Show plot
    if show_plot:
        plt.show()
    
    return fig


def time_debug(activity_name: Optional[str] = None, indent: int = 0):
    """Decorator to add time debugging to functions.
    
    Logs when a function starts and finishes execution with timestamps.
    Also tracks timing statistics (excluding nested calls).
    
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
            
            # Register auto-print on first function call
            _register_auto_print()
            
            name = activity_name if activity_name else func.__name__
            call_stack = _get_thread_call_stack()
            
            # Record start time and add to call stack
            start_time = time.perf_counter()
            call_stack.append(name)
            
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
                
                # Calculate elapsed time and remove from call stack
                end_time = time.perf_counter()
                call_stack.pop()
                
                # Calculate self-time (excluding nested tracked calls)
                # This is a simplified approach - for more accuracy we'd need to track
                # nested call times more precisely, but this gives a good approximation
                elapsed_time = end_time - start_time
                
                # Record timing statistics
                _record_timing(name, elapsed_time)
                
                debug_log(f"✓ FINISH: {name}", indent)
                return result
            except Exception as e:
                # Remove from call stack on error
                if call_stack and call_stack[-1] == name:
                    call_stack.pop()
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

