import React, { useState, useEffect } from 'react';
import { Layers, Code, Play, RefreshCw, Map as MapIcon, Upload, Save, FileJson, FileCode } from 'lucide-react';

// Components (defined inline for simplicity first, can be split later)
import Builder from './components/Builder';
import CodeEditor from './components/CodeEditor';
import MapPreview from './components/MapPreview';

function App() {
  const [activeTab, setActiveTab] = useState('builder'); // 'builder' or 'code'
  const [mapHtml, setMapHtml] = useState('');
  const [mapPayload, setMapPayload] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Builder State
  const [builderElements, setBuilderElements] = useState([
    { type: 'flag', label: 'India', value: 'IND', args: { note: 'Republic of India' } }
  ]);
  const [builderOptions, setBuilderOptions] = useState({
    title: 'My Interactive Map',
    basemaps: [{ url_or_provider: 'Esri.WorldTopoMap', default: true }]
  });

  // Code State
  const [code, setCode] = useState(`import xatra
from xatra.loaders import gadm, naturalearth

xatra.BaseOption("Esri.WorldTopoMap", default=True)
xatra.Flag(label="India", value=gadm("IND"), note="Republic of India")
xatra.TitleBox("<b>My Map</b>")
`);

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
            />
          ) : (
            <CodeEditor code={code} setCode={setCode} />
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
      <div className="flex-1 relative bg-gray-200">
        <MapPreview html={mapHtml} loading={loading} />
      </div>
    </div>
  );
}

export default App;