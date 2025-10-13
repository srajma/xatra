## Download and process GADM data.

Everything's from here: https://gadm.org/download_country.html

```python
uv run download_gadm.py 
uv run verify_gadm.py
uv run categorize_disputed_areas.py
uv run scripts/build_disputed_mapping.py # generate a table mapping disputed GADM roots (e.g. `Z01`, `Z06`, etc.) and any other GIDs that appear in a different country's file (e.g. `Z09.*` found inside an `IND` file) to the country files in which they occur. This helps set sensible defaults for `find_in_gadm`.
```

## Natural earth rivers
Go here: https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-rivers-lake-centerlines/

And manually download: "Download rivers and lake centerlines (1.98 MB) version 5.0.0". [Direct link](https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_rivers_lake_centerlines.zip) does not work.

Then:

```bash
unzip -o "~/Downloads/ne_10m_rivers_lake_centerlines.zip" # or wherever you've downloaded it to
ogr2ogr -f GeoJSON "data/ne_10m_rivers.geojson" ne_10m_rivers_lake_centerlines.shp
rm -f ne_10m_rivers_lake_centerlines.* # cleanup extra files
```

## Overpass rivers

I had downloaded the data earlier with this code: https://github.com/srajma/xatra1/blob/master/xatra/data/data.py but it no longer seems to be working. The data is still there, you can see it on the OpenStreetMap website: https://www.openstreetmap.org/relation/5388381#map=6/31.10/78.27 

I have copied the data here manually from the earlier download.
