import raw_data
import rdviz
import magic
import chronologies

# raw data download
# raw_data.download_loka(raw_data.loka, raw_data.breaks)
# raw_data.download_varuna(raw_data.varuna)

# raw data visualization
# rdviz.rdviz(feature_list = raw_data.indiaish + raw_data.indiaish_rivers, path_out = 'examples/rdviz_indiaish.html')
# rdviz.rdviz(feature_list = raw_data.afghanish + raw_data.afghanish_rivers, path_out = 'examples/rdviz_afghanish.html')
# rdviz.rdviz(feature_list = raw_data.silkrd + raw_data.silkrd_rivers, path_out = 'examples/rdviz_silkrd.html')
# rdviz(feature_list = raw_data.world + raw_data.world_rivers, path_out = 'examples/rdviz_world.html')

# main historical visualizations : standard tracts 
magic.visualize_map(
    features_list = raw_data.indiaish, 
    flags_list = chronologies.tracts.flags, 
    rivers_list = raw_data.indiaish_rivers, 
    custom_colors = chronologies.tracts.custom_colors,
    path_out = 'examples/magic_indiaish.html')
magic.visualize_map(
    features_list = raw_data.silkrd, 
    flags_list = chronologies.tracts.flags, 
    rivers_list = raw_data.silkrd_rivers, 
    custom_colors = chronologies.tracts.custom_colors,
    path_out = 'examples/magic_silkrd.html')
magic.visualize_map(
    features_list = raw_data.world, 
    flags_list = chronologies.tracts.flags, 
    rivers_list = raw_data.world_rivers, 
    custom_colors = chronologies.tracts.custom_colors,
    path_out = 'examples/magic_world.html')