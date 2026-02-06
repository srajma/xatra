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

# Global variable to track the current rendering process
current_process = None
process_lock = threading.Lock()

# GADM Indexing
GADM_INDEX = []
INDEX_BUILDING = False

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

class PickerEntry(BaseModel):
    country: str
    level: int

class PickerRequest(BaseModel):
    entries: List[PickerEntry]
    adminRivers: bool = False

def parse_color_sequence(val):
    if not val or not isinstance(val, str) or not val.strip():
        return None
    if val.replace('_', '').isalnum():
        return val.strip()
    return [c.strip() for c in val.split(',') if c.strip()]

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

            if "flag_colors" in data.options:
                seq = parse_color_sequence(data.options["flag_colors"])
                if seq:
                    m.FlagColorSequence(seq)
            
            if "admin_colors" in data.options:
                seq = parse_color_sequence(data.options["admin_colors"])
                if seq:
                    m.AdminColorSequence(seq)
                    
            if "data_colormap" in data.options and data.options["data_colormap"]:
                m.DataColormap(data.options["data_colormap"])
                
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