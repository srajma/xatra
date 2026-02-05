import sys
import os
from pathlib import Path
import json
import traceback

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
import threading

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
        if os.path.exists(GADM_DIR):
            for f in os.listdir(GADM_DIR):
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
                    # print(f"Error processing {f}: {e}")
                    pass
        
        GADM_INDEX = index
        with open("gadm_index.json", "w") as f:
            json.dump(index, f)
        print(f"GADM index built: {len(index)} entries")
            
    except Exception as e:
        print(f"Error building index: {e}")
    finally:
        INDEX_BUILDING = False

# Load cache if exists
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
    
    # Priority: Exact GID match, Start GID match, Exact Name match, Start Name match, Contains Name
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
            results.append((score, item))
            
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:limit]]

class CodeRequest(BaseModel):
    code: str

class MapElement(BaseModel):
    type: str # flag, river, point, text, path, admin
    label: Optional[str] = None
    value: Any = None # gadm code, ne_id, coords, etc.
    args: Dict[str, Any] = {}

class BuilderRequest(BaseModel):
    elements: List[MapElement]
    options: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/render/code")
def render_code(request: CodeRequest):
    try:
        # Reset the current map
        xatra.new_map()
        
        # execution context
        exec_globals = {
            "xatra": xatra,
            "gadm": gadm,
            "naturalearth": naturalearth,
            "polygon": polygon,
            "map": xatra.get_current_map() # Provide a 'map' variable initially
        }
        
        # Execute the code
        exec(request.code, exec_globals)
        
        # Get the map state
        current_map = xatra.get_current_map()
        
        # Export
        payload = current_map._export_json()
        html = export_html_string(payload)
        
        return {"html": html, "payload": payload}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.post("/render/builder")
def render_builder(request: BuilderRequest):
    try:
        xatra.new_map()
        m = xatra.get_current_map()
        
        # Apply options
        if "basemaps" in request.options:
            for bm in request.options["basemaps"]:
                 # Check if dict or string
                if isinstance(bm, dict):
                    m.BaseOption(**bm)
                else:
                    m.BaseOption(bm)
        
        if "title" in request.options:
            m.TitleBox(request.options["title"])
            
        # CSS Rules
        if "css_rules" in request.options:
            css_str = ""
            for rule in request.options["css_rules"]:
                selector = rule.get("selector", "")
                style = rule.get("style", "")
                if selector and style:
                    css_str += f"{selector} {{ {style} }}\n"
            if css_str:
                m.CSS(css_str)
        
        # Slider
        if "slider" in request.options:
            sl = request.options["slider"]
            start = sl.get("start")
            end = sl.get("end")
            speed = sl.get("speed")
            
            # Ensure types if they come as strings
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

        # Zoom and Focus
        if "zoom" in request.options and request.options["zoom"] is not None:
             try: m.zoom(int(request.options["zoom"]))
             except: pass
             
        if "focus" in request.options and request.options["focus"]:
             focus = request.options["focus"]
             if isinstance(focus, list) and len(focus) == 2:
                 try: m.focus(float(focus[0]), float(focus[1]))
                 except: pass

        # Colors
        if "flag_colors" in request.options:
            seq = parse_color_sequence(request.options["flag_colors"])
            if seq:
                m.FlagColorSequence(seq)
        
        if "admin_colors" in request.options:
            seq = parse_color_sequence(request.options["admin_colors"])
            if seq:
                m.AdminColorSequence(seq)
                
        if "data_colormap" in request.options and request.options["data_colormap"]:
            # DataColormap takes string or list?
            # xatra.pyplot.DataColormap(colormap, ...)
            # If colormap is None, it sets default?
            # If it's a string, it might be a matplotlib colormap name.
            # If it's a list, it might be custom.
            # Let's assume user passes string or parse it if comma separated?
            # DataColormap usually takes a name.
            m.DataColormap(request.options["data_colormap"])
            
        # Add elements
        for el in request.elements:
            args = el.args.copy()
            if el.label:
                args["label"] = el.label
                
            if el.type == "flag":
                # Value is expected to be a GADM code string or list
                if isinstance(el.value, str):
                    territory = gadm(el.value)
                elif isinstance(el.value, list):
                    territory = None
                    if len(el.value) > 0 and isinstance(el.value[0], dict):
                         # Complex builder structure: list of {op, type, value}
                         for part in el.value:
                             op = part.get("op", "union")
                             ptype = part.get("type", "gadm")
                             val = part.get("value")
                             
                             part_terr = None
                             if ptype == "gadm":
                                 part_terr = gadm(val)
                             elif ptype == "polygon":
                                 try:
                                     coords = json.loads(val) if isinstance(val, str) else val
                                     part_terr = polygon(coords)
                                 except: pass
                             
                             if part_terr:
                                 if territory is None:
                                     territory = part_terr
                                 else:
                                     if op == "union": territory = territory | part_terr
                                     elif op == "difference": territory = territory - part_terr
                                     elif op == "intersection": territory = territory & part_terr
                    else:
                        # List of strings (union)
                        for code in el.value:
                            t = gadm(code)
                            territory = t if territory is None else (territory | t)
                else:
                    continue # Skip invalid
                
                m.Flag(value=territory, **args)
                
            elif el.type == "river":
                # Value is ne_id
                if isinstance(el.value, str):
                    geom = naturalearth(el.value)
                    m.River(value=geom, **args)
                    
            elif el.type == "point":
                # Value is [lat, lon] or string "[lat, lon]"
                pos = el.value
                if isinstance(pos, str):
                    try:
                        pos = json.loads(pos)
                    except:
                        continue
                m.Point(position=pos, **args)
                
            elif el.type == "text":
                pos = el.value
                if isinstance(pos, str):
                    try:
                        pos = json.loads(pos)
                    except:
                        continue
                m.Text(position=pos, **args)
            
            elif el.type == "path":
                val = el.value
                if isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except:
                        continue
                m.Path(value=val, **args)
                
            elif el.type == "admin":
                # Value is gadm code
                m.Admin(gadm=el.value, **args)
            
            elif el.type == "admin_rivers":
                # Value could be sources list
                sources = el.value
                if isinstance(sources, str):
                    try:
                        sources = json.loads(sources)
                    except:
                        sources = [sources] # treat as single source string
                m.AdminRivers(sources=sources, **args)

        payload = m._export_json()
        html = export_html_string(payload)
        return {"html": html, "payload": payload}

    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
