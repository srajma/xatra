import React, { useState, useEffect } from 'react';
import { Layers, Code, Play, RefreshCw, Map as MapIcon } from 'lucide-react';

// Components (defined inline for simplicity first, can be split later)
import Builder from './components/Builder';
import CodeEditor from './components/CodeEditor';
import MapPreview from './components/MapPreview';

function App() {
  const [activeTab, setActiveTab] = useState('builder'); // 'builder' or 'code'
  const [mapHtml, setMapHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Builder State
  const [builderElements, setBuilderElements] = useState([
    { type: 'flag', label: 'India', value: 'IND', args: { note: 'Republic of India' } }
  ]);
  const [builderOptions, setBuilderOptions] = useState({
    title: 'My Interactive Map',
    basemaps: ['Esri.WorldTopoMap']
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
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Initial render
  useEffect(() => {
    renderMap();
  }, []);

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-1/3 min-w-[350px] max-w-[500px] flex flex-col bg-white border-r border-gray-200 shadow-md z-10">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
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