import React from 'react';

const MapPreview = ({ html, loading, iframeRef, onStop }) => {
  return (
    <div className="w-full h-full relative">
      {loading && (
        <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center">
          <div className="bg-white p-4 rounded-lg shadow-lg flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-2"></div>
            <span className="text-gray-700 font-medium">Generating Map...</span>
            {typeof onStop === 'function' && (
              <button
                type="button"
                onClick={onStop}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold rounded transition-colors"
              >
                Stop Generation
              </button>
            )}
          </div>
        </div>
      )}
      
      {html ? (
        <iframe
          ref={iframeRef}
          srcDoc={html}
          title="Map Preview"
          className="w-full h-full border-none bg-white"
          sandbox="allow-scripts allow-popups allow-forms"
        />
      ) : (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <p className="text-lg">No map rendered yet</p>
            <p className="text-sm">Click "Render Map" to start</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapPreview;
