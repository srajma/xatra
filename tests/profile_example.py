
import xatra
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

xatra.set_debug_time(True)

# Import the example logic
import example

# print_timing_summary is automatically called at exit if set_debug_time is True
