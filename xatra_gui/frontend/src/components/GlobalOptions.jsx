import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Plus, Trash2, Crosshair, Info, X } from 'lucide-react';

const GlobalOptions = ({ options, setOptions, elements, onGetCurrentView }) => {
  const [showMore, setShowMore] = useState(false);

  const updateOption = (key, value) => {
    setOptions({ ...options, [key]: value });
  };

  const getAvailableClasses = () => {
      const classes = new Set([
        'flag', 'river', 'path', 'point', 'admin', 'admin-river', 'data',
        'text-label', 'path-label', 'river-label', 'admin-river-label', 'point-label', 'flag-label', 'vassal-label'
      ]);
      elements.forEach(el => {
          if (el.args?.classes) {
              el.args.classes.split(' ').forEach(c => {
                  if (c.trim()) classes.add(c.trim());
              });
          }
      });
      return Array.from(classes).sort();
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

  const ALL_BASE_MAPS = [
      { id: 'Esri.WorldTopoMap', name: 'Esri World Topo' },
      { id: 'Esri.WorldImagery', name: 'Esri World Imagery' },
      { id: 'OpenTopoMap', name: 'Open Topo Map' },
      { id: 'Esri.WorldPhysical', name: 'Esri World Physical' },
      { id: 'Stadia.OSMBright', name: 'Stadia OSM Bright' },
  ];

  // Local state for slider inputs to allow intermediate typing (minus signs etc)
  const [sliderStart, setSliderStart] = useState(options.slider?.start?.toString() || '');
  const [sliderEnd, setSliderEnd] = useState(options.slider?.end?.toString() || '');
  const [sliderSpeed, setSliderSpeed] = useState(options.slider?.speed?.toString() || '5.0');

  useEffect(() => {
      setSliderStart(options.slider?.start?.toString() || '');
      setSliderEnd(options.slider?.end?.toString() || '');
      setSliderSpeed(options.slider?.speed?.toString() || '5.0');
  }, [options.slider]);

  const handleSliderChange = (field, val) => {
      if (field === 'start') setSliderStart(val);
      if (field === 'end') setSliderEnd(val);
      if (field === 'speed') setSliderSpeed(val);

      const parsed = field === 'speed' ? parseFloat(val) : parseInt(val);
      if (val === '') {
          updateOption('slider', { ...options.slider, [field]: null });
      } else if (val === '-') {
          // Do not update global options for intermediate state, keep local state
      } else if (!isNaN(parsed)) {
          updateOption('slider', { ...options.slider, [field]: parsed });
      }
  };

  const FLAG_SEQ_PRESETS = ['Pastel1', 'Set1', 'Set3', 'tab10', 'Accent', 'Dark2', 'Paired'];
  const ADMIN_SEQ_PRESETS = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'tab20'];
  const DATA_CMAP_PRESETS = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'RdYlGn', 'RdYlBu', 'Spectral'];

  const flagColorRows = Array.isArray(options.flag_color_sequences)
    ? options.flag_color_sequences
    : (options.flag_colors ? [{ class_name: '', value: options.flag_colors }] : []);

  const setFlagColorRows = (rows) => {
    const cleaned = rows.filter((r) => (r?.value || '').trim() !== '' || (r?.class_name || '').trim() !== '');
    setOptions({
      ...options,
      flag_color_sequences: cleaned,
      flag_colors: undefined,
    });
  };

  const updateFlagColorRow = (index, field, value) => {
    const rows = [...flagColorRows];
    rows[index] = { ...rows[index], [field]: value };
    setFlagColorRows(rows);
  };

  const addFlagColorRow = () => setFlagColorRows([...flagColorRows, { class_name: '', value: '' }]);

  const removeFlagColorRow = (index) => {
    const rows = [...flagColorRows];
    rows.splice(index, 1);
    setFlagColorRows(rows);
  };

  return (
    <section className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Global Options</h3>
        
        <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">TitleBox (HTML)</label>
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
                    <label className="text-xs font-medium text-gray-700 mb-2 block">Base Layers</label>
                    <div className="space-y-2 max-h-48 overflow-y-auto border rounded p-2 bg-gray-50">
                        {ALL_BASE_MAPS.map(bm => {
                            const isIncluded = (options.basemaps || []).some(b => b.url_or_provider === bm.id);
                            const isDefault = (options.basemaps || []).find(b => b.url_or_provider === bm.id)?.default;
                            
                            return (
                                <div key={bm.id} className="flex items-center justify-between gap-2 p-1 hover:bg-white rounded transition-colors">
                                    <label className="flex items-center gap-2 cursor-pointer flex-1 min-w-0">
                                        <input 
                                            type="checkbox" 
                                            checked={isIncluded}
                                            onChange={(e) => {
                                                const current = options.basemaps || [];
                                                if (e.target.checked) {
                                                    updateOption('basemaps', [...current, { url_or_provider: bm.id, name: bm.name, default: current.length === 0 }]);
                                                } else {
                                                    updateOption('basemaps', current.filter(b => b.url_or_provider !== bm.id));
                                                }
                                            }}
                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-xs truncate">{bm.name}</span>
                                    </label>
                                    {isIncluded && (
                                        <button 
                                            onClick={() => {
                                                const current = (options.basemaps || []).map(b => ({
                                                    ...b,
                                                    default: b.url_or_provider === bm.id
                                                }));
                                                updateOption('basemaps', current);
                                            }}
                                            className={`text-[10px] px-1.5 py-0.5 rounded border transition-colors ${isDefault ? 'bg-blue-600 border-blue-600 text-white' : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'}`}
                                        >
                                            {isDefault ? 'Default' : 'Set Default'}
                                        </button>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* CSS Rules */}
                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-xs font-medium text-gray-700">CSS Styling</label>
                         <button onClick={addCssRule} className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1"><Plus size={12}/> Add Rule</button>
                    </div>
                    <div className="space-y-2">
                        {(options.css_rules || []).map((rule, idx) => {
                             const availableClasses = getAvailableClasses().map(c => c.startsWith('.') ? c : '.' + c);
                             const isCustom = !availableClasses.includes(rule.selector);

                             return (
                             <div key={idx} className="flex gap-2 items-start bg-gray-50 p-2 rounded">
                                 <div className="flex-1 space-y-1">
                                     <div className="flex gap-1">
                                         <div className="w-1/3 relative">
                                            {isCustom ? (
                                                <div className="flex gap-1 items-center">
                                                    <input
                                                        type="text"
                                                        value={rule.selector}
                                                        onChange={(e) => updateCssRule(idx, 'selector', e.target.value)}
                                                        className="w-full text-xs p-1 border rounded font-mono"
                                                        placeholder=".class"
                                                        autoFocus
                                                    />
                                                    <button 
                                                        onClick={() => updateCssRule(idx, 'selector', availableClasses[0] || '.flag')} 
                                                        className="text-gray-400 hover:text-gray-600 p-1"
                                                        title="Back to list"
                                                    >
                                                        <X size={10}/>
                                                    </button>
                                                </div>
                                            ) : (
                                                <select
                                                    value={rule.selector}
                                                    onChange={(e) => {
                                                        if (e.target.value === '__custom__') {
                                                            updateCssRule(idx, 'selector', '');
                                                        } else {
                                                            updateCssRule(idx, 'selector', e.target.value);
                                                        }
                                                    }}
                                                    className="w-full text-xs p-1 border rounded font-mono"
                                                >
                                                    {availableClasses.map(c => (
                                                        <option key={c} value={c}>{c}</option>
                                                    ))}
                                                    <option value="__custom__">Custom...</option>
                                                </select>
                                            )}
                                         </div>
                                          <input 
                                            type="text"
                                            value={rule.style}
                                            onChange={(e) => updateCssRule(idx, 'style', e.target.value)}
                                            className="flex-1 text-xs p-1 border rounded font-mono"
                                            placeholder="fill: red; ..."
                                          />
                                     </div>
                                 </div>
                                 <button onClick={() => removeCssRule(idx)} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={12}/></button>
                             </div>
                             );
                        })}
                    </div>
                </div>

                {/* Slider */}
                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-xs font-medium text-gray-700">Time Slider</label>
                         {(options.slider?.start !== undefined || options.slider?.end !== undefined) && (
                            <button 
                                onClick={() => {
                                    const newOptions = { ...options };
                                    delete newOptions.slider;
                                    setOptions(newOptions);
                                }}
                                className="text-gray-400 hover:text-gray-600 p-1"
                                title="Clear Slider"
                            >
                                <X size={10}/>
                            </button>
                         )}
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                         <div>
                            <label className="block text-[10px] text-gray-500">Start Year</label>
                            <input
                                type="text"
                                value={sliderStart}
                                onChange={(e) => handleSliderChange('start', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded font-mono"
                                placeholder="e.g. -320"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">End Year</label>
                             <input
                                type="text"
                                value={sliderEnd}
                                onChange={(e) => handleSliderChange('end', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded font-mono"
                                placeholder="e.g. 2024"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Speed</label>
                             <input
                                type="text"
                                value={sliderSpeed}
                                onChange={(e) => handleSliderChange('speed', e.target.value)}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                    </div>
                </div>

                {/* Zoom and Focus */}
                <div>
                     <div className="flex justify-between items-center mb-2">
                        <label className="text-xs font-medium text-gray-700">Initial View</label>
                        <div className="flex gap-1">
                            {(options.zoom !== undefined || options.focus) && (
                                <button 
                                    onClick={() => {
                                        const newOptions = { ...options };
                                        delete newOptions.zoom;
                                        delete newOptions.focus;
                                        setOptions(newOptions);
                                    }}
                                    className="text-gray-400 hover:text-gray-600 p-1"
                                    title="Clear View"
                                >
                                    <X size={10}/>
                                </button>
                            )}
                            <button 
                                onClick={onGetCurrentView}
                                className="text-blue-600 hover:text-blue-800 text-[10px] flex items-center gap-1 font-medium bg-blue-50 px-1.5 py-0.5 rounded"
                            >
                                <Crosshair size={10}/> Use Current
                            </button>
                        </div>
                     </div>
                     <div className="grid grid-cols-3 gap-2">
                         <div>
                            <label className="block text-[10px] text-gray-500">Zoom (0-18)</label>
                            <input
                                type="number"
                                value={options.zoom || ''}
                                onChange={(e) => updateOption('zoom', e.target.value === '' ? null : parseInt(e.target.value))}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Focus Lat</label>
                             <input
                                type="number"
                                step="any"
                                value={options.focus?.[0] !== undefined && options.focus?.[0] !== null ? options.focus[0] : ''}
                                onChange={(e) => {
                                    const val = e.target.value === '' ? null : parseFloat(e.target.value);
                                    const currentLon = options.focus?.[1] ?? null;
                                    updateOption('focus', [val, currentLon]);
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                         <div>
                            <label className="block text-[10px] text-gray-500">Focus Lon</label>
                             <input
                                type="number"
                                step="any"
                                value={options.focus?.[1] !== undefined && options.focus?.[1] !== null ? options.focus[1] : ''}
                                onChange={(e) => {
                                    const val = e.target.value === '' ? null : parseFloat(e.target.value);
                                    const currentLat = options.focus?.[0] ?? null;
                                    updateOption('focus', [currentLat, val]);
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-200 rounded"
                            />
                        </div>
                    </div>
                </div>

                {/* Color Sequences */}
                <div className="space-y-4">
                     <label className="text-xs font-medium text-gray-700 block border-b pb-1">Color Options</label>
                     
                     <div className="space-y-3">
                         <div>
                             <label className="block text-[10px] font-bold text-gray-500 mb-1 flex items-center gap-1">
                                Flag Color Sequences
                                <span title="Set one or more rows. Optional class name applies sequence only to flags with that CSS class. Sequence can be a matplotlib palette name or comma-separated colors.">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="space-y-2">
                                {flagColorRows.length === 0 && (
                                  <div className="text-[10px] text-gray-400 italic">No custom rows. Add one below.</div>
                                )}
                                {flagColorRows.map((row, idx) => (
                                  <div key={idx} className="grid grid-cols-[120px_1fr_90px_24px] gap-1 items-center">
                                    <input
                                      type="text"
                                      value={row.class_name || ''}
                                      onChange={(e) => updateFlagColorRow(idx, 'class_name', e.target.value)}
                                      className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                      placeholder="class (optional)"
                                    />
                                    <input
                                      type="text"
                                      value={row.value || ''}
                                      onChange={(e) => updateFlagColorRow(idx, 'value', e.target.value)}
                                      className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                      placeholder="Pastel1 or #f00,#0f0,#00f"
                                    />
                                    <select
                                      className="text-[10px] border rounded px-1 bg-white"
                                      onChange={(e) => updateFlagColorRow(idx, 'value', e.target.value)}
                                      value=""
                                    >
                                      <option value="" disabled>Preset</option>
                                      {FLAG_SEQ_PRESETS.map((preset) => (
                                        <option key={preset} value={preset}>{preset}</option>
                                      ))}
                                    </select>
                                    <button
                                      onClick={() => removeFlagColorRow(idx)}
                                      className="text-red-400 hover:text-red-600 p-1"
                                      title="Remove row"
                                    >
                                      <Trash2 size={12}/>
                                    </button>
                                  </div>
                                ))}
                                <button onClick={addFlagColorRow} className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1">
                                  <Plus size={12}/> Add Sequence
                                </button>
                             </div>
                         </div>
                         <div>
                             <label className="block text-[10px] font-bold text-gray-500 mb-1 flex items-center gap-1">
                                Admin Color Sequence
                                <span title="Matplotlib palette name (e.g. Blues) or comma-separated colors.">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="flex gap-1">
                                <input
                                    type="text"
                                    value={options.admin_colors || ''}
                                    onChange={(e) => updateOption('admin_colors', e.target.value)}
                                    className="flex-1 px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    placeholder="#ff0000, #00ff00..."
                                />
                                <select 
                                    className="text-[10px] border rounded px-1 bg-white"
                                    onChange={(e) => updateOption('admin_colors', e.target.value)}
                                    value=""
                                >
                                    <option value="" disabled>Presets</option>
                                    {ADMIN_SEQ_PRESETS.map((preset) => (
                                      <option key={preset} value={preset}>{preset}</option>
                                    ))}
                                </select>
                             </div>
                         </div>
                         <div>
                             <label className="block text-[10px] font-bold text-gray-500 mb-1 flex items-center gap-1">
                                Data Colormap
                                <span title="Matplotlib colormap name (e.g. viridis, plasma).">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="flex gap-1">
                                <input
                                    type="text"
                                    value={options.data_colormap || ''}
                                    onChange={(e) => updateOption('data_colormap', e.target.value)}
                                    className="flex-1 px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    placeholder="viridis, plasma, or #color1, #color2..."
                                />
                                <select 
                                    className="text-[10px] border rounded px-1 bg-white"
                                    onChange={(e) => updateOption('data_colormap', e.target.value)}
                                    value=""
                                >
                                    <option value="" disabled>Presets</option>
                                    {DATA_CMAP_PRESETS.map((preset) => (
                                      <option key={preset} value={preset}>{preset}</option>
                                    ))}
                                </select>
                             </div>
                         </div>
                     </div>
                </div>
            </div>
        )}
    </section>
  );
};

export default GlobalOptions;
