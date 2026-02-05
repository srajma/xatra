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
from xatra.loaders import gadm, naturalearth, polygon
from xatra.render import export_html_string

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        return {"html": html}
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
            
        # Add elements
        for el in request.elements:
            args = el.args.copy()
            if el.label:
                args["label"] = el.label
                
            if el.type == "flag":
                # Value is expected to be a GADM code string or list of strings
                # For simplicity in this prototype, we'll handle single GADM codes or list of them treated as union
                if isinstance(el.value, str):
                    territory = gadm(el.value)
                elif isinstance(el.value, list):
                    territory = None
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
                # Value is [lat, lon]
                m.Point(position=el.value, **args)
                
            elif el.type == "text":
                m.Text(position=el.value, **args)
            
            elif el.type == "path":
                m.Path(value=el.value, **args)
                
            elif el.type == "admin":
                # Value is gadm code
                m.Admin(gadm=el.value, **args)

        payload = m._export_json()
        html = export_html_string(payload)
        return {"html": html}

    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
