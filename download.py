from xatra.data import Loka, Varuna, DataItem, DataCollection
#Loka.WORLD.download("xatra/data/", overwrite = True)
#Varuna.WORLD.download("xatra/data/", overwrite = True)
# ^ basically only run this if you're a developer contributing to
# ^ the the package, or if you want to use the project for some
# ^ other region of the world not included in the package by default
# ^ the data included in the package is in "xatra/data"

Loka.SEA_MAINLAND.download("xatra/data/", overwrite = True)
Loka.SEA_MARITIME.download("xatra/data/", overwrite = True)