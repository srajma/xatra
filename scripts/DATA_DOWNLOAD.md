**GADM administrative boundaries:** see the `download_gadm.py` script. Everything's from [here](https://gadm.org/download_country.html)

**Natural Earth rivers:** https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-rivers-lake-centerlines/ 

**Overpass rivers:** I had downloaded the data earlier with this script: https://github.com/srajma/xatra1/blob/master/xatra/data/data.py but it no longer seems to be working. The data is still there, you can see it on the OpenStreetMap website: https://www.openstreetmap.org/relation/5388381#map=6/31.10/78.27 

## Post-processing

### Disputed territories categorizing

```bash
uv run scripts/categorize_disputed_areas.py
```

### Disputed territories mapping

We generate a table mapping disputed GADM roots (e.g. `Z01`, `Z06`, etc.) and any other GIDs that appear in a different country's file (e.g. `Z09.*` found inside an `IND` file) to the country files in which they occur. This helps set sensible defaults for `find_in_gadm`.

```bash
uv run scripts/build_disputed_mapping.py
```