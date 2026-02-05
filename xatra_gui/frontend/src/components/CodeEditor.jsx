import React from 'react';
import { RefreshCw } from 'lucide-react';

const CodeEditor = ({ code, setCode, onSync }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">Python Code</label>
        <button 
            onClick={onSync}
            className="flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded hover:bg-blue-100 transition-colors"
            title="Generate code from Builder state"
        >
            <RefreshCw size={12}/> Sync from Builder
        </button>
      </div>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="flex-1 w-full p-3 font-mono text-sm bg-gray-900 text-gray-100 rounded-md border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
        spellCheck="false"
      />
      <div className="mt-2 p-2 bg-gray-50 border rounded">
          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Available globals</p>
          <div className="flex flex-wrap gap-2">
              {['xatra', 'gadm', 'naturalearth', 'overpass', 'polygon'].map(g => (
                  <code key={g} className="text-[10px] px-1 bg-gray-200 rounded">{g}</code>
              ))}
          </div>
      </div>
    </div>
  );
};

export default CodeEditor;