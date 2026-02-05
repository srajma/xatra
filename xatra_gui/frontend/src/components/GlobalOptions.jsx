import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react';

const GlobalOptions = ({ options, setOptions, elements }) => {
  const [showMore, setShowMore] = useState(false);

  // Helper to update top-level options
  const updateOption = (key, value) => {
    setOptions({ ...options, [key]: value });
  };

  // Helper for Base Maps (list of objects)
  const addBaseMap = () => {
    const current = options.basemaps || [];
    // If it was just a string/object, normalize to array
    // But App.jsx initializes it as array.
    setOptions({
        ...options,
        basemaps: [...current, { url_or_provider: 'Esri.WorldTopoMap', name: 'New Base Layer', default: current.length === 0 }]
    });
  };

  const removeBaseMap = (index) => {
      const current = [...(options.basemaps || [])];
      current.splice(index, 1);
      setOptions({ ...options, basemaps: current });
  };

  const updateBaseMap = (index, field, value) => {
      const current = [...(options.basemaps || [])];
      current[index] = { ...current[index], [field]: value };
      // If setting default to true, unset others?
      // xatra might support multiple defaults? No, typically one.
      if (field === 'default' && value === true) {
          current.forEach((bm, i) => {
              if (i !== index) bm.default = false;
          });
      }
      setOptions({ ...options, basemaps: current });
  };

  // Helper for CSS (custom CSS string generation from UI)
  // The roadmap asks for a UI: pair of (class dropdown, style text).
  // We need to store this structured data in options, then generate .CSS() string.
  // Or just store raw CSS string if simpler?
  // Roadmap: "The interface for this should be as follows: we have a list of classes... each row is a pair..."
  // So we need a new option field `css_rules` which is a list of { selector: string, style: string }.
  // And we gather available classes from `elements`.
  
  const getAvailableClasses = () => {
      const classes = new Set(['flag', 'river', 'point', 'text', 'path', 'admin']);
      elements.forEach(el => {
          if (el.args?.classes) {
              el.args.classes.split(' ').forEach(c => classes.add(c));
          }
      });
      return Array.from(classes);
  };

  const addCssRule = () => {
      const current = options.css_rules || [];
      setOptions({ ...options, css_rules: [...current, { selector: '.flag', style: '' }] });
  };
  
  const updateCssRule = (index, field, value) => {
      const current = [...(options.css_rules || [])];
      current[index] = { ...current[index], [field]: value };
      setOptions({ ...options, css_rules: current });
  };

  const removeCssRule = (index) => {
       const current = [...(options.css_rules || [])];
       current.splice(index, 1);
       setOptions({ ...options, css_rules: current });
  };

  return (
    <section className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Global Options</h3>
        
        {/* Prominent Title */}
        <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">Title (HTML)</label>
            <textarea
              value={options.title || ''}
              onChange={(e) => updateOption('title', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 font-mono h-16"
              placeholder="<b>My Map</b>"
            />
        </div>

        <button 
            onClick={() => setShowMore(!showMore)}
            className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium mb-2"
        >
            {showMore ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
            {showMore ? 'Hide Advanced Options' : 'Show Advanced Options'}
        </button>

        {showMore && (
            <div className="space-y-6 pt-2 border-t border-gray-100">
                
                {/* Base Maps */}
                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-xs font-medium text-gray-700">Base Layers</label>
                        <button onClick={addBaseMap} className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1"><Plus size={12}/> Add</button>
                    </div>
                    <div className="space-y-2">
                        {(options.basemaps || []).map((bm, idx) => (
                            <div key={idx} className="flex gap-2 items-start bg-gray-50 p-2 rounded">
                                <div className="flex-1 space-y-1">
                                    <select 
                                        value={bm.url_or_provider}
                                        onChange={(e) => updateBaseMap(idx, 'url_or_provider', e.target.value)}
                                        className="w-full text-xs p-1 border rounded"
                                    >
                                        <option value="Esri.WorldTopoMap">Esri World Topo</option>
                                        <option value="Esri.WorldImagery">Esri World Imagery</option>
                                        <option value="OpenTopoMap">Open Topo Map</option>
                                        <option value="Esri.WorldPhysical">Esri World Physical</option>
                                        <option value="Stadia.OSMBright">Stadia OSM Bright</option>
                                        {/* Allow custom URL? maybe later */}
                                    </select>
                                    <div className="flex items-center gap-2">
                                        <label className="flex items-center gap-1 text-[10px] text-gray-600 cursor-pointer">
                                            <input 
                                                type="checkbox" 
                                                checked={bm.default || false} 
                                                onChange={(e) => updateBaseMap(idx, 'default', e.target.checked)}
                                            />
                                            Default
                                        </label>
                                         <input
                                            type="text"
                                            value={bm.name || ''}
                                            onChange={(e) => updateBaseMap(idx, 'name', e.target.value)}
                                            className="flex-1 text-[10px] p-1 border rounded"
                                            placeholder="Display Name"
                                        />
                                    </div>
                                </div>
                                <button onClick={() => removeBaseMap(idx)} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={12}/></button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* CSS Rules */}
                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-xs font-medium text-gray-700">CSS Styling</label>
                         <button onClick={addCssRule} className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1"><Plus size={12}/> Add Rule</button>
                    </div>
                    <div className="space-y-2">
                        {(options.css_rules || []).map((rule, idx) => (
                             <div key={idx} className="flex gap-2 items-start bg-gray-50 p-2 rounded">
                                 <div className="flex-1 space-y-1">
                                     <div className="flex gap-1">
                                         <select
                                            value={rule.selector}
                                            onChange={(e) => updateCssRule(idx, 'selector', e.target.value)}
                                            className="w-1/3 text-xs p-1 border rounded font-mono"
                                         >
                                             {getAvailableClasses().map(c => (
                                                 <option key={c} value={c.startsWith('.') ? c : '.' + c}>{c.startsWith('.') ? c : '.' + c}</option>
                                             ))}
                                         </select>
                                          <input 
                                            type="text"
                                            value={rule.style}
                                            onChange={(e) => updateCssRule(idx, 'style', e.target.value)}
                                            className="flex-1 text-xs p-1 border rounded font-mono"
                                            placeholder="fill: red; stroke-width: 2px;"
                                          />
                                     </div>
                                 </div>
                                 <button onClick={() => removeCssRule(idx)} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={12}/></button>
                             </div>
                        ))}
                    </div>
                </div>

                {/* Slider */}
                <div>
                    <label className="text-xs font-medium text-gray-700 mb-2 block">Time Slider</label>
                    <div className="grid grid-cols-3 gap-2">
                         <div>
                            <label className="block text-[10px] text-gray-500">Start Year</label>
                            <input
                                type="number"
                                value={options.slider?.start || ''}
                                onChange={(e) => updateOption('slider', { ...options.slider, start: parseInt(e.target.value) })}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">End Year</label>
                             <input
                                type="number"
                                value={options.slider?.end || ''}
                                onChange={(e) => updateOption('slider', { ...options.slider, end: parseInt(e.target.value) })}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Speed</label>
                             <input
                                type="number"
                                step="0.1"
                                value={options.slider?.speed || 5.0}
                                onChange={(e) => updateOption('slider', { ...options.slider, speed: parseFloat(e.target.value) })}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                    </div>
                </div>

                {/* Zoom and Focus */}
                <div>
                     <label className="text-xs font-medium text-gray-700 mb-2 block">Initial View</label>
                     <div className="grid grid-cols-3 gap-2">
                         <div>
                            <label className="block text-[10px] text-gray-500">Zoom (0-18)</label>
                            <input
                                type="number"
                                value={options.zoom || ''}
                                onChange={(e) => updateOption('zoom', parseInt(e.target.value))}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Focus Lat</label>
                             <input
                                type="number"
                                step="any"
                                value={options.focus?.[0] !== undefined ? options.focus[0] : ''}
                                onChange={(e) => updateOption('focus', [parseFloat(e.target.value), options.focus?.[1] || 0])}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Focus Lon</label>
                             <input
                                type="number"
                                step="any"
                                value={options.focus?.[1] !== undefined ? options.focus[1] : ''}
                                onChange={(e) => updateOption('focus', [options.focus?.[0] || 0, parseFloat(e.target.value)])}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                    </div>
                </div>

                {/* Color Sequences */}
                <div>
                     <label className="text-xs font-medium text-gray-700 mb-2 block">Colors</label>
                     <div className="space-y-2">
                         <div>
                             <label className="block text-[10px] text-gray-500">Flag Color Sequence (Hex list or Palette Name)</label>
                             <input
                                type="text"
                                value={options.flag_colors || ''}
                                onChange={(e) => updateOption('flag_colors', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                                placeholder="#ff0000, #00ff00... or 'Pastel1'"
                             />
                         </div>
                         <div>
                             <label className="block text-[10px] text-gray-500">Admin Color Sequence</label>
                             <input
                                type="text"
                                value={options.admin_colors || ''}
                                onChange={(e) => updateOption('admin_colors', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                                placeholder="#ff0000, #00ff00..."
                             />
                         </div>
                         <div>
                             <label className="block text-[10px] text-gray-500">Data Colormap</label>
                             <input
                                type="text"
                                value={options.data_colormap || ''}
                                onChange={(e) => updateOption('data_colormap', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                                placeholder="viridis, plasma, or #color1, #color2..."
                             />
                         </div>
                     </div>
                </div>
            </div>
        )}
    </section>
  );
};

export default GlobalOptions;