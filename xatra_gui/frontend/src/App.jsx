import React, { useState, useEffect, useRef } from 'react';
import { Layers, Code, Play, RefreshCw, Map as MapIcon, Upload, Save, FileJson, FileCode } from 'lucide-react';

// Components (defined inline for simplicity first, can be split later)
import Builder from './components/Builder';
import CodeEditor from './components/CodeEditor';
import MapPreview from './components/MapPreview';

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

  // Picker State
  const [pickerOptions, setPickerOptions] = useState({
    countries: ['IND'],
    level: 1,
    adminRivers: true
  });

  const iframeRef = useRef(null);
  const pickerIframeRef = useRef(null);

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
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [activePreviewTab]);

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
        : { elements: builderElements, options: builderOptions };

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
    const project = { elements: builderElements, options: builderOptions };
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

  const generatePythonCode = () => {
    let lines = [
        'import xatra',
        'from xatra.loaders import gadm, naturalearth, polygon',
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

    lines.push('');

    // Elements
    builderElements.forEach(el => {
        const args = { ...el.args };
        if (el.label) args.label = el.label;
        
        let argsStr = Object.entries(args)
            .map(([k, v]) => `${k}=${JSON.stringify(v).replace(/"/g, "'").replace(/null/g, 'None').replace(/true/g, 'True').replace(/false/g, 'False')}`)
            .join(', ');
        
        if (argsStr) argsStr = ', ' + argsStr;

        if (el.type === 'flag') {
            let valStr = 'None';
            if (Array.isArray(el.value)) {
                // Complex territory
                const ops = { union: '|', difference: '-', intersection: '&' };
                valStr = el.value.map((part, i) => {
                    let pStr = '';
                    if (part.type === 'gadm') pStr = `gadm("${part.value}")`;
                    else if (part.type === 'polygon') pStr = `polygon(${part.value})`;
                    
                    if (i === 0) return pStr;
                    return ` ${ops[part.op] || '|'} ${pStr}`;
                }).join('');
            } else {
                valStr = `gadm("${el.value}")`;
            }
            lines.push(`xatra.Flag(value=${valStr}${argsStr})`);
        } else if (el.type === 'river') {
            const func = el.args?.source_type === 'overpass' ? 'overpass' : 'naturalearth';
            lines.push(`xatra.River(value=${func}("${el.value}")${argsStr})`);
        } else if (el.type === 'point') {
            lines.push(`xatra.Point(position=${el.value}${argsStr})`);
        } else if (el.type === 'text') {
            lines.push(`xatra.Text(position=${el.value}${argsStr})`);
        } else if (el.type === 'path') {
            lines.push(`xatra.Path(value=${el.value}${argsStr})`);
        } else if (el.type === 'admin') {
            lines.push(`xatra.Admin(gadm="${el.value}"${argsStr})`);
        } else if (el.type === 'admin_rivers') {
            lines.push(`xatra.AdminRivers(sources=${el.value}${argsStr})`);
        }
    });

    setCode(lines.join('\n'));
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
            />
          ) : (
            <CodeEditor code={code} setCode={setCode} onSync={generatePythonCode} />
          )}
        </div>

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={renderMap}
            disabled={loading}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? <RefreshCw className="animate-spin w-5 h-5" /> : <Play className="w-5 h-5 fill-current" />}
            {loading ? 'Rendering...' : 'Render Map'}
          </button>
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
                Picker Map
            </button>
        </div>

        {activePreviewTab === 'picker' && (
            <div className="absolute top-16 right-4 z-20 w-64 bg-white/95 backdrop-blur p-4 rounded-lg shadow-xl border border-gray-200 space-y-4">
                <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2 border-b pb-2">
                    Picker Options
                </h3>
                <div className="space-y-3">
                    <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Countries (GADM)</label>
                        <input 
                            type="text" 
                            value={pickerOptions.countries.join(', ')}
                            onChange={(e) => setPickerOptions({ ...pickerOptions, countries: e.target.value.split(',').map(s => s.trim()) })}
                            className="w-full text-xs p-2 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="IND, PAK..."
                        />
                    </div>
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">Level</label>
                            <input 
                                type="number" 
                                value={pickerOptions.level}
                                onChange={(e) => setPickerOptions({ ...pickerOptions, level: parseInt(e.target.value) })}
                                className="w-full text-xs p-2 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                min="0" max="3"
                            />
                        </div>
                        <div className="flex items-end pb-2">
                            <label className="flex items-center gap-2 text-xs font-medium text-gray-700 cursor-pointer">
                                <input 
                                    type="checkbox"
                                    checked={pickerOptions.adminRivers}
                                    onChange={(e) => setPickerOptions({ ...pickerOptions, adminRivers: e.target.checked })}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                Rivers
                            </label>
                        </div>
                    </div>
                    <button 
                        onClick={renderPickerMap}
                        disabled={loading}
                        className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded shadow transition-colors disabled:opacity-50"
                    >
                        Update Picker Map
                    </button>
                </div>
                <div className="text-[10px] text-gray-400 bg-gray-50 p-2 rounded italic">
                    Tip: Use the picker map to find GADM codes or coordinates. You can still use "Use Current View" in Global Options while this tab is active.
                </div>
            </div>
        )}

        <div className="flex-1 overflow-hidden">
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