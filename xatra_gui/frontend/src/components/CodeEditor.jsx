import React from 'react';

const CodeEditor = ({ code, setCode }) => {
  return (
    <div className="h-full flex flex-col">
      <label className="block text-sm font-medium text-gray-700 mb-2">Python Code</label>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="flex-1 w-full p-3 font-mono text-sm bg-gray-900 text-gray-100 rounded-md border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
        spellCheck="false"
      />
      <p className="mt-2 text-xs text-gray-500">
        Available globals: <code>xatra</code>, <code>gadm</code>, <code>naturalearth</code>, <code>polygon</code>
      </p>
    </div>
  );
};

export default CodeEditor;
