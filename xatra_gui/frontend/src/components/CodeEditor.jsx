import React from 'react';
import { RefreshCw } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';

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
      
      <div className="flex-1 border border-gray-700 rounded-md overflow-hidden bg-[#2d2d2d] relative">
          <div className="absolute inset-0 overflow-auto">
            <Editor
                value={code}
                onValueChange={code => setCode(code)}
                highlight={code => Prism.highlight(code, Prism.languages.python || Prism.languages.extend('clike', {}), 'python')}
                padding={12}
                style={{
                fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                fontSize: 13,
                backgroundColor: '#2d2d2d',
                color: '#f8f8f2',
                minHeight: '100%'
                }}
                textareaClassName="focus:outline-none"
            />
          </div>
      </div>

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