import React from 'react';
import { RefreshCw } from 'lucide-react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';

// Handle potential ESM/CJS mismatch
const SimpleEditor = typeof Editor === 'function' ? Editor : (Editor?.default || null);

const CodeEditor = ({ code, setCode, predefinedCode, setPredefinedCode, onSync }) => {
  const highlight = (code) => {
    const lang = Prism.languages.python || Prism.languages.extend('clike', {});
    return Prism.highlight(code || '', lang, 'python');
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      
      {/* Predefined Library */}
      <div className="flex flex-col flex-1 min-h-[150px]">
        <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">Predefined Territories</label>
        </div>
        <div className="flex-1 border border-gray-700 rounded-md overflow-hidden bg-[#2d2d2d] relative">
            <div className="absolute inset-0 overflow-auto">
                {SimpleEditor ? (
                    <SimpleEditor
                        value={predefinedCode || ''}
                        onValueChange={code => setPredefinedCode(code)}
                        highlight={highlight}
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
                ) : (
                    <textarea
                        value={predefinedCode}
                        onChange={(e) => setPredefinedCode(e.target.value)}
                        className="w-full h-full p-3 font-mono text-sm bg-gray-900 text-gray-100 outline-none resize-none"
                        spellCheck="false"
                    />
                )}
            </div>
        </div>
      </div>

      {/* Main Map Code */}
      <div className="flex flex-col flex-[2] min-h-[200px]">
        <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">Map Code</label>
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
                {SimpleEditor ? (
                    <SimpleEditor
                        value={code || ''}
                        onValueChange={code => setCode(code)}
                        highlight={highlight}
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
                ) : (
                    <textarea
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="w-full h-full p-3 font-mono text-sm bg-gray-900 text-gray-100 outline-none resize-none"
                        spellCheck="false"
                    />
                )}
            </div>
        </div>
      </div>

      <div className="p-2 bg-gray-50 border rounded">
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