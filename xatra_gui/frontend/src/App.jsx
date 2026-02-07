import React, { useState, useEffect, useRef } from 'react';
import { Layers, Code, Play, RefreshCw, Map as MapIcon, Upload, Save, FileJson, FileCode, Plus, Trash2, X } from 'lucide-react';

// Components (defined inline for simplicity first, can be split later)
import Builder from './components/Builder';
import CodeEditor from './components/CodeEditor';
import MapPreview from './components/MapPreview';
import AutocompleteInput from './components/AutocompleteInput';

function App() {
  const [activeTab, setActiveTab] = useState('builder'); // 'builder' or 'code'
  const [activePreviewTab, setActivePreviewTab] = useState('main'); // 'main' or 'picker'
  const [mapHtml, setMapHtml] = useState('');
  const [mapPayload, setMapPayload] = useState(null);
  const [pickerHtml, setPickerHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Builder State
  const [builderElements, setBuilderElements] = useState([
    { type: 'flag', label: 'India', value: [], args: { note: 'Republic of India' } }
  ]);
  const [builderOptions, setBuilderOptions] = useState({
    title: '<b>My Interactive Map</b>',
    basemaps: [{ url_or_provider: 'Esri.WorldTopoMap', default: true }]
  });

  // Code State
  const [code, setCode] = useState(`import xatra
from xatra.loaders import gadm, naturalearth

xatra.BaseOption("Esri.WorldTopoMap", default=True)
xatra.Flag(label="India", value=gadm("IND"), note="Republic of India")
xatra.TitleBox("<b>My Map</b>")
`);

  const [predefinedCode, setPredefinedCode] = useState(`from xatra.territory_library import *  # https://github.com/srajma/xatra/blob/master/src/xatra/territory_library.py

`);

  // Picker State
  const [pickerOptions, setPickerOptions] = useState({
    entries: [{ country: 'IND', level: 1 }],
    adminRivers: true
  });
  
  const [lastMapClick, setLastMapClick] = useState(null);
  const [lastPickedGadm, setLastPickedGadm] = useState(null);
  const [lastPickedRiver, setLastPickedRiver] = useState(null);
  const [activePicker, setActivePicker] = useState(null); // { id, type, context }
  const [draftPoints, setDraftPoints] = useState([]);
  const [isFreehand, setIsFreehand] = useState(false);
  const [isMouseDown, setIsMouseDown] = useState(false);

  const iframeRef = useRef(null);
  const pickerIframeRef = useRef(null);

  const updateDraft = (points, shapeType) => {
      const ref = activePreviewTab === 'main' ? iframeRef : pickerIframeRef;
      if (ref.current && ref.current.contentWindow) {
          ref.current.contentWindow.postMessage({ type: 'setDraft', points, shapeType }, '*');
      }
  };

  useEffect(() => {
      if (activePicker) {
          updateDraft(draftPoints, activePicker.type);
      } else {
          updateDraft([], null);
      }
  }, [draftPoints, activePicker, activePreviewTab]);

  useEffect(() => {
    const handleKeyDown = (e) => {
        if (!activePicker) return;
        if (e.target.matches('input, textarea, [contenteditable="true"]')) return;
        if (e.key === 'Backspace') {
            e.preventDefault();
            setDraftPoints(prev => {
                const newPoints = prev.slice(0, -1);
                updateElementFromDraft(newPoints);
                return newPoints;
            });
        } else if (e.key === ' ' && !e.repeat) {
            e.preventDefault();
            setIsFreehand(prev => !prev);
        } else if (e.key === 'Escape') {
            setActivePicker(null);
            setDraftPoints([]);
            setIsFreehand(false);
        }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
        window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activePicker]);

  const updateElementFromDraft = (points) => {
      if (!activePicker) return;
      if (activePicker.context === 'layer') {
          const idx = activePicker.id;
          const newElements = [...builderElements];
          newElements[idx].value = JSON.stringify(points);
          setBuilderElements(newElements);
      } else if (typeof activePicker.context === 'string' && activePicker.context.startsWith('territory-')) {
          const parentId = parseInt(activePicker.context.replace('territory-', ''), 10);
          if (Number.isNaN(parentId)) return;
          const el = builderElements[parentId];
          if (!el || el.type !== 'flag' || !Array.isArray(el.value)) return;
          const partIndex = activePicker.id;
          const parts = [...el.value];
          if (partIndex < 0 || partIndex >= parts.length) return;
          const part = parts[partIndex];
          if (part && part.type === 'polygon') {
              parts[partIndex] = { ...part, value: JSON.stringify(points) };
              const newElements = [...builderElements];
              newElements[parentId] = { ...el, value: parts };
              setBuilderElements(newElements);
          }
      }
  };

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'mapViewUpdate') {
        const targetSet = activePreviewTab === 'picker' ? null : setBuilderOptions;
        if (targetSet) {
            targetSet(prev => ({
                ...prev,
                focus: [
                    parseFloat(event.data.center[0].toFixed(4)), 
                    parseFloat(event.data.center[1].toFixed(4))
                ],
                zoom: event.data.zoom
            }));
        }
      } else if (event.data && event.data.type === 'mapClick') {
          setLastMapClick({ lat: event.data.lat, lng: event.data.lng, ts: Date.now() });
      } else if (event.data && event.data.type === 'mapMouseDown') {
          setIsMouseDown(true);
      } else if (event.data && event.data.type === 'mapMouseUp') {
          setIsMouseDown(false);
      } else if (event.data && event.data.type === 'mapMouseMove') {
          if (activePicker && isFreehand && isMouseDown) {
              const point = [parseFloat(event.data.lat.toFixed(4)), parseFloat(event.data.lng.toFixed(4))];
              setDraftPoints(prev => {
                  const last = prev[prev.length - 1];
                  if (last && Math.abs(last[0] - point[0]) < 0.0001 && Math.abs(last[1] - point[1]) < 0.0001) return prev;
                  const newPoints = [...prev, point];
                  updateElementFromDraft(newPoints);
                  return newPoints;
              });
          }
      } else if (event.data && event.data.type === 'mapKeyDown') {
          // Keys forwarded from map iframe (when user clicked map, focus is in iframe)
          const key = event.data.key;
          if (!activePicker) return;
          if (key === 'Backspace') {
            setDraftPoints(prev => {
              const newPoints = prev.slice(0, -1);
              updateElementFromDraft(newPoints);
              return newPoints;
            });
          } else if (key === 'Escape') {
            setActivePicker(null);
            setDraftPoints([]);
            setIsFreehand(false);
          } else if (key === ' ' && !event.data.repeat) {
            setIsFreehand(prev => !prev);
          }
      } else if (event.data && event.data.type === 'mapFeaturePick') {
          const data = event.data || {};
          if (data.featureType === 'gadm' && data.gid) {
              setLastPickedGadm({ gid: data.gid, name: data.name || '', ts: Date.now() });
          } else if (data.featureType === 'river' && data.id) {
              setLastPickedRiver({
                  id: String(data.id),
                  source_type: data.source_type || 'naturalearth',
                  name: data.name || '',
                  ts: Date.now()
              });
          }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [activePreviewTab, activePicker, isFreehand, isMouseDown, builderElements]);

  const handleGetCurrentView = () => {
    const ref = activePreviewTab === 'picker' ? pickerIframeRef : iframeRef;
    if (ref.current && ref.current.contentWindow) {
      ref.current.contentWindow.postMessage('getCurrentView', '*');
    }
  };

  const renderPickerMap = async () => {
      setLoading(true);
      try {
          const response = await fetch(`http://localhost:8088/render/picker`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(pickerOptions)
          });
          const data = await response.json();
          if (data.html) setPickerHtml(data.html);
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  const renderMap = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = activeTab === 'code' ? '/render/code' : '/render/builder';
      const body = activeTab === 'code' 
        ? { code } 
        : { elements: builderElements, options: builderOptions, predefined_code: predefinedCode || undefined };

      const response = await fetch(`http://localhost:8088${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        console.error(data.traceback);
      } else {
        setMapHtml(data.html);
        setMapPayload(data.payload);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (content, filename, contentType) => {
    const a = document.createElement("a");
    const file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = filename;
    a.click();
  };

  const handleExportHtml = () => {
    if (mapHtml) downloadFile(mapHtml, "map.html", "text/html");
  };

  const handleExportJson = () => {
    if (mapPayload) downloadFile(JSON.stringify(mapPayload, null, 2), "map.json", "application/json");
  };

  const handleSaveProject = () => {
    const project = { elements: builderElements, options: builderOptions, predefinedCode };
    downloadFile(JSON.stringify(project, null, 2), "project.json", "application/json");
  };

  const handleLoadProject = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const project = JSON.parse(e.target.result);
          if (project.elements && project.options) {
             setBuilderElements(project.elements);
             setBuilderOptions(project.options);
             if (project.predefinedCode) setPredefinedCode(project.predefinedCode);
          }
        } catch (err) {
          setError("Failed to load project: " + err.message);
        }
      };
      reader.readAsText(file);
    }
    // Reset file input
    e.target.value = null;
  };

  const formatTerritory = (value) => {
      if (value == null || (Array.isArray(value) && value.length === 0)) return 'None';
      if (Array.isArray(value)) {
          const ops = { union: '|', difference: '-', intersection: '&' };
          const parts = value.map((part, i) => {
              let pStr = '';
              if (part.type === 'gadm' && part.value != null && part.value !== '') pStr = `gadm("${part.value}")`;
              else if (part.type === 'polygon' && part.value != null && part.value !== '') pStr = `polygon(${part.value})`;
              else if (part.type === 'predefined' && part.value) pStr = part.value;
              else return null;
              if (i === 0) return pStr;
              return ` ${ops[part.op] || '|'} ${pStr}`;
          }).filter(Boolean);
          if (parts.length === 0) return 'None';
          return parts.join('');
      }
      if (value === '') return 'None';
      return `gadm("${value}")`;
  };

  const handleSaveTerritoryToLibrary = (element) => {
      const name = (element.label || '').replace(/\s+/g, '_');
      const terrStr = formatTerritory(element.value);
      setPredefinedCode(prev => prev + `\n${name} = ${terrStr}\n`);
      setActiveTab('code');
  };

  const generatePythonCode = () => {
    const needsIconImport = builderElements.some(el => el.type === 'point' && el.args?.icon);
    const hasFlagColorOptions =
      (Array.isArray(builderOptions.flag_color_sequences) && builderOptions.flag_color_sequences.some((row) => (row?.value || '').trim() !== '')) ||
      !!builderOptions.flag_colors;
    const hasAdminColorOptions = !!builderOptions.admin_colors;
    const needsColorSeqImport = hasFlagColorOptions || hasAdminColorOptions;
    const pyVal = (v) => {
        if (v == null || v === '') return 'None';
        if (typeof v === 'boolean') return v ? 'True' : 'False';
        if (typeof v === 'string') return `"${v.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
        if (Array.isArray(v)) return JSON.stringify(v);
        return JSON.stringify(v).replace(/"/g, "'").replace(/null/g, 'None').replace(/true/g, 'True').replace(/false/g, 'False');
    };
    const colorSequenceExpr = (raw) => {
        if (typeof raw !== 'string') return null;
        const val = raw.trim();
        if (!val) return null;
        if (!val.includes(',')) {
            return `RotatingColorSequence().from_matplotlib_color_sequence(${pyVal(val)})`;
        }
        const parts = val
          .split(',')
          .map((p) => p.trim())
          .filter(Boolean)
          .map((p) => (
            p.startsWith('#')
              ? `Color.hex(${pyVal(p)})`
              : `Color.named(${pyVal(p.toLowerCase())})`
          ));
        if (parts.length === 0) return null;
        return `RotatingColorSequence([${parts.join(', ')}])`;
    };
    let lines = [
        'import xatra',
        'from xatra.loaders import gadm, naturalearth, polygon, overpass',
        ...(needsIconImport ? ['from xatra.icon import Icon', ''] : []),
        ...(needsColorSeqImport ? ['from xatra.colorseq import Color, RotatingColorSequence', ''] : []),
        '',
        predefinedCode,
        ''
    ];

    // Options
    if (builderOptions.basemaps) {
        builderOptions.basemaps.forEach(bm => {
            lines.push(`xatra.BaseOption("${bm.url_or_provider}", name="${bm.name || ''}", default=${bm.default ? 'True' : 'False'})`);
        });
    }

    if (builderOptions.title) {
        lines.push(`xatra.TitleBox("""${builderOptions.title}""")`);
    }

    if (builderOptions.zoom) {
        lines.push(`xatra.zoom(${builderOptions.zoom})`);
    }

    if (builderOptions.focus) {
        lines.push(`xatra.focus(${builderOptions.focus[0]}, ${builderOptions.focus[1]})`);
    }

    if (builderOptions.css_rules) {
        let css = builderOptions.css_rules.map(r => `${r.selector} { ${r.style} }`).join('\n');
        if (css) lines.push(`xatra.CSS("""${css}""")`);
    }

    if (builderOptions.slider) {
        const { start, end, speed } = builderOptions.slider;
        lines.push(`xatra.slider(start=${start ?? 'None'}, end=${end ?? 'None'}, speed=${speed ?? 5.0})`);
    }

    if (Array.isArray(builderOptions.flag_color_sequences)) {
        builderOptions.flag_color_sequences.forEach((row) => {
            const val = (row?.value || '').trim();
            if (!val) return;
            const className = (row?.class_name || '').trim();
            const seqExpr = colorSequenceExpr(val);
            if (!seqExpr) return;
            if (className) lines.push(`xatra.FlagColorSequence(${seqExpr}, class_name=${pyVal(className)})`);
            else lines.push(`xatra.FlagColorSequence(${seqExpr})`);
        });
    } else if (builderOptions.flag_colors) {
        const seqExpr = colorSequenceExpr(builderOptions.flag_colors);
        if (seqExpr) lines.push(`xatra.FlagColorSequence(${seqExpr})`);
    }

    if (builderOptions.admin_colors) {
        const seqExpr = colorSequenceExpr(builderOptions.admin_colors);
        if (seqExpr) lines.push(`xatra.AdminColorSequence(${seqExpr})`);
    }

    if (builderOptions.data_colormap) {
        lines.push(`xatra.DataColormap(${pyVal(builderOptions.data_colormap)})`);
    }

    lines.push('');
    const argsEntries = (obj) => Object.entries(obj || {}).filter(([, v]) => {
        if (v == null || v === '') return false;
        if (Array.isArray(v) && v.length === 0) return false;
        return true;
    });
    const argsToStr = (args) => {
        const parts = argsEntries(args).map(([k, v]) => `${k}=${typeof v === 'string' ? pyVal(v) : pyVal(v)}`);
        return parts.length ? ', ' + parts.join(', ') : '';
    };

    // Elements
    builderElements.forEach(el => {
        const args = { ...el.args };
        if (el.label != null && el.label !== '') args.label = el.label;
        const argsStr = argsToStr(args);

        if (el.type === 'flag') {
            lines.push(`xatra.Flag(value=${formatTerritory(el.value)}${argsStr})`);
        } else if (el.type === 'river') {
            const func = el.args?.source_type === 'overpass' ? 'overpass' : 'naturalearth';
            const riverArgs = { ...args };
            delete riverArgs.source_type;
            const riverArgsStrFormatted = argsToStr(riverArgs);
            const riverVal = (el.value != null && el.value !== '') ? `${func}("${String(el.value).replace(/"/g, '\\"')}")` : 'None';
            lines.push(`xatra.River(value=${riverVal}${riverArgsStrFormatted})`);
        } else if (el.type === 'point') {
            const pointArgs = { ...args };
            const iconVal = pointArgs.icon;
            delete pointArgs.icon;
            let pointArgsStr = argsToStr(pointArgs);
            let iconPy = '';
            if (iconVal != null && iconVal !== '') {
                if (typeof iconVal === 'string') {
                    iconPy = `icon=Icon.builtin("${iconVal}")`;
                } else if (iconVal.shape) {
                    const c = (iconVal.color || '#3388ff').replace(/'/g, "\\'");
                    iconPy = `icon=Icon.geometric("${iconVal.shape}", color="${c}", size=${iconVal.size ?? 24})`;
                } else if (iconVal.icon_url || iconVal.iconUrl) {
                    const url = (iconVal.icon_url || iconVal.iconUrl).replace(/"/g, '\\"');
                    iconPy = `icon=Icon(icon_url="${url}")`;
                }
            }
            if (iconPy) pointArgsStr = pointArgsStr ? `${pointArgsStr}, ${iconPy}` : `, ${iconPy}`;
            const pos = (el.value != null && el.value !== '') ? (Array.isArray(el.value) ? JSON.stringify(el.value) : el.value) : 'None';
            lines.push(`xatra.Point(position=${pos}${pointArgsStr})`);
        } else if (el.type === 'text') {
            const pos = (el.value != null && el.value !== '') ? (Array.isArray(el.value) ? JSON.stringify(el.value) : el.value) : 'None';
            lines.push(`xatra.Text(position=${pos}${argsStr})`);
        } else if (el.type === 'path') {
            const pathVal = (el.value != null && el.value !== '') ? (typeof el.value === 'string' ? el.value : JSON.stringify(el.value)) : 'None';
            lines.push(`xatra.Path(value=${pathVal}${argsStr})`);
        } else if (el.type === 'admin') {
            const gadmVal = (el.value != null && el.value !== '') ? `"${String(el.value).replace(/"/g, '\\"')}"` : 'None';
            lines.push(`xatra.Admin(gadm=${gadmVal}${argsStr})`);
        } else if (el.type === 'admin_rivers') {
            const sourcesVal = (el.value != null && el.value !== '') ? el.value : 'None';
            lines.push(`xatra.AdminRivers(sources=${typeof sourcesVal === 'object' ? JSON.stringify(sourcesVal) : sourcesVal}${argsStr})`);
        } else if (el.type === 'dataframe') {
            lines.push(`# DataFrame handling requires local CSV file or manual implementation in code mode`);
            lines.push(`import pandas as pd`);
            lines.push(`import io`);
            const csvContent = (el.value != null && el.value !== '') ? String(el.value).replace(/"""/g, '\\"\\"\\"') : '';
            lines.push(`df = pd.read_csv(io.StringIO("""${csvContent}"""))`);
            lines.push(`xatra.Dataframe(df${argsStr})`);
        }
    });

    setCode(lines.join('\n'));
  };

  const handleStop = async () => {
      // Force stop loading on frontend
      setLoading(false);
      try {
          await fetch('http://localhost:8088/stop', { method: 'POST' });
      } catch (e) { console.error(e); }
  };

  // Initial render
  useEffect(() => {
    renderMap();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-1/3 min-w-[350px] max-w-[500px] flex flex-col bg-white border-r border-gray-200 shadow-md z-10">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                <MapIcon className="w-6 h-6 text-blue-600" />
                Xatra Studio
            </h1>
            <div className="flex bg-white rounded-lg border border-gray-300 p-0.5">
                <button 
                onClick={() => setActiveTab('builder')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'builder' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                <span className="flex items-center gap-1"><Layers size={16}/> Builder</span>
                </button>
                <button 
                onClick={() => setActiveTab('code')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'code' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                <span className="flex items-center gap-1"><Code size={16}/> Code</span>
                </button>
            </div>
          </div>
          
          <div className="flex gap-2">
             <label className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 cursor-pointer" title="Load Project">
                <Upload size={16} className="text-gray-600"/>
                <input type="file" className="hidden" accept=".json" onChange={handleLoadProject} />
             </label>
             <button onClick={handleSaveProject} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50" title="Save Project"><Save size={16} className="text-gray-600"/></button>
             <div className="h-auto w-px bg-gray-300 mx-1"></div>
             <button onClick={handleExportHtml} disabled={!mapHtml} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50" title="Export HTML"><FileCode size={16} className="text-gray-600"/></button>
             <button onClick={handleExportJson} disabled={!mapPayload} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50" title="Export Map JSON"><FileJson size={16} className="text-gray-600"/></button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'builder' ? (
            <Builder 
              elements={builderElements} 
              setElements={setBuilderElements}
              options={builderOptions}
              setOptions={setBuilderOptions}
              onGetCurrentView={handleGetCurrentView}
              lastMapClick={lastMapClick}
              activePicker={activePicker}
              setActivePicker={setActivePicker}
              draftPoints={draftPoints}
              setDraftPoints={setDraftPoints}
              onSaveTerritory={handleSaveTerritoryToLibrary}
              predefinedCode={predefinedCode}
              lastPickedGadm={lastPickedGadm}
              lastPickedRiver={lastPickedRiver}
            />
          ) : (
            <CodeEditor 
                code={code} setCode={setCode} 
                predefinedCode={predefinedCode} setPredefinedCode={setPredefinedCode}
                onSync={generatePythonCode} 
            />
          )}
        </div>

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          {loading ? (
              <button
                onClick={handleStop}
                className="w-full py-2.5 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 transition-all"
              >
                <X size={20} /> Stop Generation
              </button>
          ) : (
              <button
                onClick={renderMap}
                className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 transition-all"
              >
                <Play className="w-5 h-5 fill-current" /> Render Map
              </button>
          )}
          {error && (
            <div className="mt-3 p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200 overflow-auto max-h-32">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>
      </div>

      {/* Main Preview Area */}
      <div className="flex-1 flex flex-col relative bg-gray-200">
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 flex bg-white/90 backdrop-blur shadow-md rounded-full p-1 border border-gray-200">
            <button 
                onClick={() => setActivePreviewTab('main')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${activePreviewTab === 'main' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-100'}`}
            >
                Map Preview
            </button>
            <button 
                onClick={() => setActivePreviewTab('picker')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${activePreviewTab === 'picker' ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-100'}`}
            >
                Reference Map
            </button>
        </div>

        {activePreviewTab === 'picker' && (
            <div className="absolute top-16 right-4 z-20 w-72 bg-white/95 backdrop-blur p-4 rounded-lg shadow-xl border border-gray-200 space-y-4 max-h-[calc(100vh-100px)] overflow-y-auto overflow-x-hidden">
                <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2 border-b pb-2">
                    Reference Map Options
                </h3>
                <div className="space-y-3">
                    <div className="space-y-2">
                         <div className="grid grid-cols-[1fr_64px_24px] gap-1.5 items-center">
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Countries</label>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Admin Level</label>
                            <div />
                         </div>
                         {pickerOptions.entries.map((entry, idx) => (
                             <div key={idx} className="flex gap-1.5 items-center">
                                 <AutocompleteInput 
                                     value={entry.country}
                                     onChange={(val) => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries[idx].country = val;
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="w-20 text-xs p-1.5 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none font-mono uppercase"
                                     placeholder="IND"
                                 />
                                 <input 
                                     type="number" 
                                     value={entry.level}
                                     onChange={(e) => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries[idx].level = parseInt(e.target.value);
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="w-12 text-xs p-1.5 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                     min="0" max="4"
                                 />
                                 <button 
                                     onClick={() => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries.splice(idx, 1);
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="p-1.5 text-red-500 hover:bg-red-50 rounded flex-shrink-0"
                                 >
                                     <Trash2 size={12}/>
                                 </button>
                             </div>
                         ))}
                         <button 
                             onClick={() => setPickerOptions({...pickerOptions, entries: [...pickerOptions.entries, {country: '', level: 1}]})}
                             className="text-xs text-blue-600 flex items-center gap-1 font-medium hover:text-blue-800"
                         >
                             <Plus size={12}/> Add Country
                         </button>
                    </div>

                    <div className="flex items-center pb-2 pt-2 border-t border-gray-100">
                        <label className="flex items-center gap-2 text-xs font-medium text-gray-700 cursor-pointer">
                            <input 
                                type="checkbox"
                                checked={pickerOptions.adminRivers}
                                onChange={(e) => setPickerOptions({ ...pickerOptions, adminRivers: e.target.checked })}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            Show Admin Rivers
                        </label>
                    </div>

                    <button 
                        onClick={renderPickerMap}
                        disabled={loading}
                        className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded shadow transition-colors disabled:opacity-50"
                    >
                        Update Reference Map
                    </button>
                    {(lastPickedGadm || lastPickedRiver) && (
                        <div className="space-y-1 border-t border-gray-100 pt-2 text-[11px]">
                            <div className="font-semibold text-gray-600">Last Picked From Reference Map</div>
                            {lastPickedGadm && (
                                <div className="font-mono text-gray-700">
                                    GADM: {lastPickedGadm.gid}{lastPickedGadm.name ? ` (${lastPickedGadm.name})` : ''}
                                </div>
                            )}
                            {lastPickedRiver && (
                                <div className="font-mono text-gray-700">
                                    River: {lastPickedRiver.source_type}:{lastPickedRiver.id}{lastPickedRiver.name ? ` (${lastPickedRiver.name})` : ''}
                                </div>
                            )}
                        </div>
                    )}
                </div>
                <div className="text-[10px] text-gray-400 bg-gray-50 p-2 rounded italic">
                    Tip: Use the reference map to find GADM codes or coordinates.
                </div>
            </div>
        )}

        <div className="flex-1 overflow-hidden relative">
            {activePicker && (
                <div className="absolute inset-0 z-30 pointer-events-none flex items-center justify-center">
                    <div className="bg-amber-500 text-white px-6 py-4 rounded-lg shadow-2xl border-2 border-amber-600 font-semibold text-center max-w-md animate-pulse">
                        <div className="text-sm mb-1">Click map to add points</div>
                        <div className="text-xs font-normal opacity-95">
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Backspace</kbd> undo last point
                            {' · '}
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Space</kbd> toggle freehand, then drag
                            {' · '}
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Esc</kbd> cancel
                        </div>
                    </div>
                </div>
            )}
            {activePreviewTab === 'main' ? (
                <MapPreview html={mapHtml} loading={loading} iframeRef={iframeRef} />
            ) : (
                <MapPreview html={pickerHtml} loading={loading} iframeRef={pickerIframeRef} />
            )}
        </div>
      </div>
    </div>
  );
}

export default App;
