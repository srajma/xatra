import xatra
import xatra.maps.tracts as tracts
import xatra.raw_data as raw_data

# raw data download
#loka.download("examples/rd/", overwrite = True)
#varuna.download("examples/rd/")

# raw data visualization
xatra.rdviz(feature_list = raw_data.subcont + raw_data.indiaish_rivers, path_out = 'examples/rdviz/subcont.html')
# xatra.rdviz(feature_list = raw_data.indiaish + raw_data.indiaish_rivers, path_out = 'examples/rdviz/indiaish.html')
# xatra.rdviz(feature_list = raw_data.silkrd + raw_data.silkrd_rivers, path_out = 'examples/rdviz/silkrd.html')
# xatra.rdviz(feature_list = raw_data.world + raw_data.world_rivers, path_out = 'examples/rdviz/world.html')
# ^ i recommend you don't run this last one as the file it generates is close to Github's 75 MB limit

# main historical visualizations : standard tracts 
xatra.magic(
    features_list = raw_data.indiaish, 
    flags_list = tracts.flags, 
    rivers_list = raw_data.indiaish_rivers, 
    custom_colors = tracts.custom_colors,
    path_out = 'examples/tracts_indiaish.html')
# xatra.magic(
#     features_list = raw_data.silkrd, 
#     flags_list = tracts.flags, 
#     rivers_list = raw_data.silkrd_rivers, 
#     custom_colors = tracts.custom_colors,
#     path_out = 'examples/tracts_silkrd.html')
# xatra.magic(
#     features_list = raw_data.world, 
#     flags_list = tracts.flags, 
#     rivers_list = raw_data.world_rivers, 
#     custom_colors = tracts.custom_colors,
#     path_out = 'examples/tracts_world.html')

#flags_test = [dict(flag, period = [-1000,1000]) for flag in maps.tracts.flags]
