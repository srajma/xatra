import pandas as pd
import xatra
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm

# Create test data with a wide range of values
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'IND.20', 'Z01.14'],
    'population': [100, 10000, 1000000, 5000000]  # Wide range for testing log scale
})

df.set_index('GID', inplace=True)

# Test with LogNorm
map_log = xatra.Map()
map_log.BaseOption("OpenStreetMap", default=True)
map_log.DataColormap(plt.cm.viridis, norm=LogNorm())
map_log.Dataframe(df)
map_log.show(out_json="tests/map_log_norm.json", out_html="tests/map_log_norm.html")

# Test with PowerNorm
map_power = xatra.Map()
map_power.BaseOption("OpenStreetMap", default=True)
map_power.DataColormap(plt.cm.plasma, norm=PowerNorm(gamma=0.5))
map_power.Dataframe(df)
map_power.show(out_json="tests/map_power_norm.json", out_html="tests/map_power_norm.html")

# Test with regular linear normalization (for comparison)
map_linear = xatra.Map()
map_linear.BaseOption("OpenStreetMap", default=True)
map_linear.DataColormap(plt.cm.viridis, vmin=100, vmax=5000000)
map_linear.Dataframe(df)
map_linear.show(out_json="tests/map_linear_norm.json", out_html="tests/map_linear_norm.html")

print("Created test maps with different normalization methods:")
print("- map_log_norm.html: LogNorm with viridis colormap")
print("- map_power_norm.html: PowerNorm with plasma colormap") 
print("- map_linear_norm.html: Linear normalization for comparison")
