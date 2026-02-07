import sys
import os
from pathlib import Path
import json
import traceback
import threading
import multiprocessing
import signal

# Set matplotlib backend to Agg before importing anything else
import matplotlib
matplotlib.use('Agg')

# Add src to path so we can import xatra
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Union

import xatra
from xatra.loaders import gadm, naturalearth, polygon, GADM_DIR
from xatra.render import export_html_string
from xatra.colorseq import Color, RotatingColorSequence, color_sequences
from xatra.icon import Icon

# Global variable to track the current rendering process
current_process = None
process_lock = threading.Lock()

# GADM Indexing
GADM_INDEX = []
INDEX_BUILDING = False
COUNTRY_LEVELS_INDEX = {}
COUNTRY_SEARCH_INDEX = []

def rebuild_country_indexes():
    global COUNTRY_LEVELS_INDEX, COUNTRY_SEARCH_INDEX
    levels_map = {}
    names_map = {}

    for item in GADM_INDEX:
        gid = item.get("gid")
        if not gid:
            continue
        country_code = gid.split(".")[0]
        level = item.get("level")
        if level is None:
            continue
        levels_map.setdefault(country_code, set()).add(int(level))
        country_name = (item.get("country") or "").strip()
        if country_name and country_code not in names_map:
            names_map[country_code] = country_name

    COUNTRY_LEVELS_INDEX = {
        code: sorted(list(levels))
        for code, levels in levels_map.items()
    }
    COUNTRY_SEARCH_INDEX = sorted(
        [
            {
                "country_code": code,
                "country": names_map.get(code, code),
                "max_level": max(levels) if levels else 0,
            }
            for code, levels in COUNTRY_LEVELS_INDEX.items()
        ],
        key=lambda x: x["country_code"],
    )

def build_gadm_index():
    global INDEX_BUILDING, GADM_INDEX
    if INDEX_BUILDING: return
    INDEX_BUILDING = True
    print("Building GADM index...")
    
    try:
        index = []
        seen_gids = set()
        if os.path.exists(GADM_DIR):
            files = sorted(os.listdir(GADM_DIR))
            for f in files:
                if not f.endswith(".json") or not f.startswith("gadm41_"): continue
                
                parts = f.replace(".json", "").split("_")
                if len(parts) < 3: continue
                try:
                    level = int(parts[2])
                except:
                    continue
                
                path = os.path.join(GADM_DIR, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        data = json.load(fh)
                        for feat in data.get("features", []):
                            p = feat.get("properties", {})
                            gid = p.get(f"GID_{level}")
                            name = p.get(f"NAME_{level}")
                            country = p.get("COUNTRY")
                            varname = p.get(f"VARNAME_{level}")
                            
                            if gid:
                                if gid.endswith("_1"):
                                    gid = gid[:-2]
                                
                                if gid in seen_gids:
                                    continue
                                seen_gids.add(gid)
                                    
                                entry = {
                                    "gid": gid,
                                    "name": name,
                                    "country": country,
                                    "level": level
                                }
                                if varname and varname != "NA":
                                    entry["varname"] = varname
                                    
                                index.append(entry)
                except Exception as e:
                    pass
        
        GADM_INDEX = index
        rebuild_country_indexes()
        with open("gadm_index.json", "w") as f:
            json.dump(index, f)
        print(f"GADM index built: {len(index)} entries")
            
    except Exception as e:
        print(f"Error building index: {e}")
    finally:
        INDEX_BUILDING = False

if os.path.exists("gadm_index.json"):
    try:
        with open("gadm_index.json", "r") as f:
            GADM_INDEX = json.load(f)
        rebuild_country_indexes()
    except:
        threading.Thread(target=build_gadm_index).start()
else:
    threading.Thread(target=build_gadm_index).start()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search/gadm")
def search_gadm(q: str):
    if not q: return []
    q = q.lower()
    results = []
    limit = 20
    
    for item in GADM_INDEX:
        score = 0
        gid = item["gid"].lower()
        name = item["name"].lower() if item["name"] else ""
        
        if gid == q: score = 100
        elif gid.startswith(q): score = 80
        elif name == q: score = 90
        elif name.startswith(q): score = 70
        elif q in name: score = 50
        elif item.get("varname") and q in item.get("varname").lower(): score = 40
        elif item["country"] and q in item["country"].lower(): score = 30
        
        if score > 0:
            tie_breaker = -len(gid)
            results.append((score, tie_breaker, item))
            
    results.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [r[2] for r in results[:limit]]

@app.get("/search/countries")
def search_countries(q: str):
    if not q:
        return COUNTRY_SEARCH_INDEX[:20]
    q = q.lower().strip()
    results = []

    for item in COUNTRY_SEARCH_INDEX:
        code = item["country_code"].lower()
        name = item["country"].lower()
        score = 0
        if code == q:
            score = 100
        elif code.startswith(q):
            score = 90
        elif name == q:
            score = 80
        elif name.startswith(q):
            score = 70
        elif q in name:
            score = 60
        if score > 0:
            results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:20]]

@app.get("/gadm/levels")
def gadm_levels(country: str):
    if not country:
        return []
    country_code = country.strip().upper().split(".")[0]
    return COUNTRY_LEVELS_INDEX.get(country_code, [0, 1, 2, 3, 4])

class CodeRequest(BaseModel):
    code: str

class MapElement(BaseModel):
    type: str
    label: Optional[str] = None
    value: Any = None
    args: Dict[str, Any] = {}

class BuilderRequest(BaseModel):
    elements: List[MapElement]
    options: Dict[str, Any] = {}
    predefined_code: Optional[str] = None

class PickerEntry(BaseModel):
    country: str
    level: int

class PickerRequest(BaseModel):
    entries: List[PickerEntry]
    adminRivers: bool = False

@app.get("/icons/list")
def list_icons():
    """Return list of built-in icon filenames for Point icon picker."""
    try:
        icons_dir = Path(xatra.__file__).parent / "icons"
        if not icons_dir.exists():
            return []
        return sorted(
            f.name for f in icons_dir.iterdir()
            if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in (".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp")
        )
    except Exception:
        return []

@app.get("/territory_library/names")
def territory_library_names():
    """Return public names from xatra.territory_library for autocomplete in Territory library."""
    try:
        import xatra.territory_library as tl
        return [n for n in dir(tl) if not n.startswith("_")]
    except Exception:
        return []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/stop")
def stop_generation():
    global current_process
    with process_lock:
        if current_process and current_process.is_alive():
            current_process.terminate()
            current_process.join()
            current_process = None
            return {"status": "stopped"}
    return {"status": "no process running"}

def run_rendering_task(task_type, data, result_queue):
    def parse_color_sequence(val):
        if not val or not isinstance(val, str) or not val.strip():
            return None
        if val.replace('_', '').isalnum():
            return val.strip()
        return [c.strip() for c in val.split(',') if c.strip()]

    try:
        # Re-import xatra inside the process just in case, though imports are inherited on fork (mostly)
        # But we need fresh map state
        import xatra
        xatra.new_map()
        m = xatra.get_current_map()
        
        if task_type == 'picker':
            m.BaseOption("Esri.WorldTopoMap", default=True)
            for entry in data.entries:
                m.Admin(gadm=entry.country, level=entry.level)
            if data.adminRivers:
                m.AdminRivers()
                
        elif task_type == 'code':
            exec_globals = {
                "xatra": xatra,
                "gadm": xatra.loaders.gadm,
                "naturalearth": xatra.loaders.naturalearth,
                "polygon": xatra.loaders.polygon,
                "overpass": xatra.loaders.overpass,
                "map": m
            }
            exec(data.code, exec_globals)
            m = xatra.get_current_map() # Refresh in case they used map = xatra.Map()
            
        elif task_type == 'builder':
            # Apply options
            if "basemaps" in data.options:
                for bm in data.options["basemaps"]:
                    if isinstance(bm, dict):
                        m.BaseOption(**bm)
                    else:
                        m.BaseOption(bm)
            
            if "title" in data.options:
                m.TitleBox(data.options["title"])
                
            if "css_rules" in data.options:
                css_str = ""
                for rule in data.options["css_rules"]:
                    selector = rule.get("selector", "")
                    style = rule.get("style", "")
                    if selector and style:
                        css_str += f"{selector} {{ {style} }}\n"
                if css_str:
                    m.CSS(css_str)
            
            if "slider" in data.options:
                sl = data.options["slider"]
                start = sl.get("start")
                end = sl.get("end")
                speed = sl.get("speed")
                if isinstance(start, str) and start.strip():
                     try: start = int(start)
                     except: start = None
                elif isinstance(start, str): start = None
                if isinstance(end, str) and end.strip():
                     try: end = int(end)
                     except: end = None
                elif isinstance(end, str): end = None
                
                if start is not None or end is not None:
                    m.slider(start=start, end=end, speed=speed if speed else 5.0)

            if "zoom" in data.options and data.options["zoom"] is not None:
                 try: m.zoom(int(data.options["zoom"]))
                 except: pass
                 
            if "focus" in data.options and data.options["focus"]:
                 focus = data.options["focus"]
                 if isinstance(focus, list) and len(focus) == 2:
                     try: m.focus(float(focus[0]), float(focus[1]))
                     except: pass

            if "flag_color_sequences" in data.options and isinstance(data.options["flag_color_sequences"], list):
                for row in data.options["flag_color_sequences"]:
                    if not isinstance(row, dict):
                        continue
                    seq = parse_color_sequence(row.get("value"))
                    if not seq:
                        continue
                    class_name = row.get("class_name")
                    if isinstance(class_name, str):
                        class_name = class_name.strip() or None
                    else:
                        class_name = None
                    m.FlagColorSequence(seq, class_name=class_name)
            elif "flag_colors" in data.options:
                seq = parse_color_sequence(data.options["flag_colors"])
                if seq:
                    m.FlagColorSequence(seq)
            
            if "admin_colors" in data.options:
                seq = parse_color_sequence(data.options["admin_colors"])
                if seq:
                    m.AdminColorSequence(seq)
                    
            if "data_colormap" in data.options and data.options["data_colormap"]:
                m.DataColormap(data.options["data_colormap"])

            # Execute predefined territory code so Flag parts of type "predefined" can use them
            predefined_namespace = {}
            if getattr(data, "predefined_code", None) and data.predefined_code.strip():
                try:
                    import xatra.territory_library as territory_library
                    exec_globals = {
                        "gadm": xatra.loaders.gadm,
                        "polygon": xatra.loaders.polygon,
                        "naturalearth": xatra.loaders.naturalearth,
                        "overpass": xatra.loaders.overpass,
                    }
                    for name in dir(territory_library):
                        if not name.startswith("_"):
                            exec_globals[name] = getattr(territory_library, name)
                    exec(data.predefined_code.strip(), exec_globals)
                    predefined_namespace = {k: v for k, v in exec_globals.items() if k not in ("gadm", "polygon", "naturalearth", "overpass") and not k.startswith("_")}
                except Exception:
                    predefined_namespace = {}

            for el in data.elements:
                args = el.args.copy()
                if el.label:
                    args["label"] = el.label
                    
                if el.type == "flag":
                    if isinstance(el.value, str):
                        territory = xatra.loaders.gadm(el.value)
                    elif isinstance(el.value, list):
                        territory = None
                        if len(el.value) > 0 and isinstance(el.value[0], dict):
                             for part in el.value:
                                 op = part.get("op", "union")
                                 ptype = part.get("type", "gadm")
                                 val = part.get("value")
                                 part_terr = None
                                 if ptype == "gadm":
                                     part_terr = xatra.loaders.gadm(val)
                                 elif ptype == "polygon":
                                     try:
                                         coords = json.loads(val) if isinstance(val, str) else val
                                         part_terr = xatra.loaders.polygon(coords)
                                     except: pass
                                 elif ptype == "predefined" and val and predefined_namespace:
                                     part_terr = predefined_namespace.get(val)
                                 else:
                                     part_terr = None
                                 
                                 if part_terr:
                                     if territory is None: territory = part_terr
                                     else:
                                         if op == "union": territory = territory | part_terr
                                         elif op == "difference": territory = territory - part_terr
                                         elif op == "intersection": territory = territory & part_terr
                        else:
                            for code in el.value:
                                t = xatra.loaders.gadm(code)
                                territory = t if territory is None else (territory | t)
                    else:
                        continue
                    m.Flag(value=territory, **args)
                    
                elif el.type == "river":
                    source_type = args.get("source_type", "naturalearth")
                    if "source_type" in args: del args["source_type"]
                    if isinstance(el.value, str):
                        if source_type == "overpass":
                            geom = xatra.loaders.overpass(el.value)
                        else:
                            geom = xatra.loaders.naturalearth(el.value)
                        m.River(value=geom, **args)
                        
                elif el.type == "point":
                    pos = el.value
                    if isinstance(pos, str):
                        try: pos = json.loads(pos)
                        except: continue
                    icon_arg = args.pop("icon", None)
                    if icon_arg is not None and icon_arg != "":
                        try:
                            if isinstance(icon_arg, str):
                                args["icon"] = Icon.builtin(icon_arg)
                            elif isinstance(icon_arg, dict):
                                if "shape" in icon_arg:
                                    args["icon"] = Icon.geometric(
                                        icon_arg.get("shape", "circle"),
                                        color=icon_arg.get("color", "#3388ff"),
                                        size=int(icon_arg.get("size", 24)),
                                        border_color=icon_arg.get("border_color"),
                                        border_width=int(icon_arg.get("border_width", 0)),
                                    )
                                elif "icon_url" in icon_arg or "iconUrl" in icon_arg:
                                    url = icon_arg.get("icon_url") or icon_arg.get("iconUrl")
                                    args["icon"] = Icon(
                                        icon_url=url,
                                        icon_size=tuple(icon_arg.get("icon_size", icon_arg.get("iconSize", (25, 41)))),
                                        icon_anchor=tuple(icon_arg.get("icon_anchor", icon_arg.get("iconAnchor", (12, 41)))),
                                    )
                        except Exception:
                            pass
                    m.Point(position=pos, **args)
                    
                elif el.type == "text":
                    pos = el.value
                    if isinstance(pos, str):
                        try: pos = json.loads(pos)
                        except: continue
                    m.Text(position=pos, **args)
                
                elif el.type == "path":
                    val = el.value
                    if isinstance(val, str):
                        try: val = json.loads(val)
                        except: continue
                    m.Path(value=val, **args)
                    
                elif el.type == "admin":
                    if "label" in args: del args["label"]
                    m.Admin(gadm=el.value, **args)
                
                elif el.type == "admin_rivers":
                    if "label" in args: del args["label"]
                    sources = el.value
                    if isinstance(sources, str):
                        try: sources = json.loads(sources)
                        except: sources = [sources]
                    m.AdminRivers(sources=sources, **args)

                elif el.type == "dataframe":
                    import pandas as pd
                    import io
                    val = el.value
                    if isinstance(val, str):
                        if val.endswith('.csv') and os.path.exists(val):
                             df = pd.read_csv(val)
                        else:
                             df = pd.read_csv(io.StringIO(val))
                        if "label" in args: del args["label"]
                        if args.get("data_column") in (None, ""): args.pop("data_column", None)
                        if args.get("year_columns") in (None, [], ""): args.pop("year_columns", None)
                        m.Dataframe(df, **args)

        payload = m._export_json()
        html = export_html_string(payload)
        result_queue.put({"html": html, "payload": payload})
        
    except Exception as e:
        result_queue.put({"error": str(e), "traceback": traceback.format_exc()})

def run_in_process(task_type, data):
    global current_process
    
    # Ensure previous process is dead
    with process_lock:
        if current_process and current_process.is_alive():
            current_process.terminate()
            current_process.join()
    
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_rendering_task, args=(task_type, data, queue))
    
    with process_lock:
        current_process = p
        
    p.start()
    
    result = {"error": "Rendering process timed out or crashed"}
    try:
        # Get result from queue with a timeout (60s)
        # IMPORTANT: Read from queue BEFORE join() to avoid deadlocks with large data
        result = queue.get(timeout=60)
    except Exception as e:
        result = {"error": f"Rendering failed: {str(e)}"}
    
    p.join(timeout=5)
    if p.is_alive():
        p.terminate()
        p.join()
        
    with process_lock:
        current_process = None
        
    return result

@app.post("/render/picker")
def render_picker(request: PickerRequest):
    result = run_in_process('picker', request)
    if "error" in result:
        return result
    return result

@app.post("/render/code")
def render_code(request: CodeRequest):
    result = run_in_process('code', request)
    if "error" in result:
        return result
    return result

@app.post("/render/builder")
def render_builder(request: BuilderRequest):
    result = run_in_process('builder', request)
    if "error" in result:
        return result
    return result

if __name__ == "__main__":
    import uvicorn
    # Use spawn for multiprocessing compatibility
    multiprocessing.set_start_method('spawn')
    uvicorn.run(app, host="0.0.0.0", port=8088)
