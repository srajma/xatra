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

  const getCustomFlagClasses = () => {
      const classes = new Set();
      elements.forEach((el) => {
          if (el.type !== 'flag') return;
          const raw = el.args?.classes;
          if (!raw || typeof raw !== 'string') return;
          raw.split(' ').forEach((cls) => {
              const trimmed = cls.trim();
              if (trimmed) classes.add(trimmed);
          });
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

  const DEFAULT_FLAG_SEQUENCE_ROW = {
    class_name: '',
    colors: '',
    step_h: 1.6180339887,
    step_s: 0.0,
    step_l: 0.0,
  };
  const DEFAULT_ADMIN_SEQUENCE_ROW = {
    colors: '',
    step_h: 1.6180339887,
    step_s: 0.0,
    step_l: 0.0,
  };
  const DATA_CMAP_PRESETS = ['LinearSegmented', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'RdYlGn', 'RdYlBu', 'Spectral'];

  const flagColorRows = Array.isArray(options.flag_color_sequences)
    ? options.flag_color_sequences
    : (options.flag_colors ? [{ ...DEFAULT_FLAG_SEQUENCE_ROW, colors: options.flag_colors }] : [DEFAULT_FLAG_SEQUENCE_ROW]);

  const setFlagColorRows = (rows) => {
    setOptions({
      ...options,
      flag_color_sequences: rows,
      flag_colors: undefined,
    });
  };

  const updateFlagColorRow = (index, field, value) => {
    const rows = [...flagColorRows];
    rows[index] = { ...rows[index], [field]: value };
    setFlagColorRows(rows);
  };

  const addFlagColorRow = () => setFlagColorRows([...flagColorRows, { ...DEFAULT_FLAG_SEQUENCE_ROW }]);

  const removeFlagColorRow = (index) => {
    const rows = [...flagColorRows];
    rows.splice(index, 1);
    setFlagColorRows(rows.length ? rows : [{ ...DEFAULT_FLAG_SEQUENCE_ROW }]);
  };

  const adminColorRow = (Array.isArray(options.admin_color_sequences) && options.admin_color_sequences.length > 0)
    ? options.admin_color_sequences[0]
    : (options.admin_colors ? { ...DEFAULT_ADMIN_SEQUENCE_ROW, colors: options.admin_colors } : { ...DEFAULT_ADMIN_SEQUENCE_ROW });

  const updateAdminColorRow = (field, value) => {
    const nextRow = { ...(adminColorRow || DEFAULT_ADMIN_SEQUENCE_ROW), [field]: value };
    setOptions({
      ...options,
      admin_color_sequences: [nextRow],
      admin_colors: undefined,
    });
  };

  const DEFAULT_DATA_COLORMAP = { type: 'LinearSegmented', colors: 'yellow,orange,red' };
  const dataColormap = typeof options.data_colormap === 'object' && options.data_colormap !== null
    ? { ...DEFAULT_DATA_COLORMAP, ...options.data_colormap }
    : (typeof options.data_colormap === 'string' && options.data_colormap.trim()
      ? { type: options.data_colormap, colors: 'yellow,orange,red' }
      : DEFAULT_DATA_COLORMAP);

  return (
    <section className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-semibold text-gray-900">Global Options</h3>
            <button 
                onClick={() => setShowMore(!showMore)}
                className="p-1 text-gray-500 hover:text-blue-700 rounded hover:bg-gray-100 transition-colors"
                title={showMore ? 'Collapse global options' : 'Expand global options'}
            >
                {showMore ? <ChevronUp size={14}/> : <ChevronDown size={14}/>}
            </button>
        </div>

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
                                <span title="Build a LinearColorSequence. Set H/S/L step and optionally seed colors (comma-separated CSS names or hex).">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="space-y-2">
                                {flagColorRows.map((row, idx) => (
                                  <div key={idx} className="bg-gray-50 border border-gray-200 rounded p-2 space-y-2">
                                    <div className="grid grid-cols-1 sm:grid-cols-[130px_1fr_24px] gap-1 items-center">
                                      <select
                                        value={row.class_name || ''}
                                        onChange={(e) => updateFlagColorRow(idx, 'class_name', e.target.value)}
                                        className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono bg-white"
                                      >
                                        <option value="">(all flags)</option>
                                        {getCustomFlagClasses().map((cls) => (
                                          <option key={cls} value={cls}>{cls}</option>
                                        ))}
                                      </select>
                                      <input
                                        type="text"
                                        value={row.colors || ''}
                                        onChange={(e) => updateFlagColorRow(idx, 'colors', e.target.value)}
                                        className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                        placeholder="#1f77b4,#ff7f0e or red,blue"
                                      />
                                      <button
                                        onClick={() => removeFlagColorRow(idx)}
                                        className="text-red-400 hover:text-red-600 p-1 justify-self-end"
                                        title="Remove row"
                                      >
                                        <Trash2 size={12}/>
                                      </button>
                                    </div>
                                    <div className="grid grid-cols-3 gap-1">
                                      <input
                                        type="number"
                                        step="any"
                                        value={row.step_h ?? DEFAULT_FLAG_SEQUENCE_ROW.step_h}
                                        onChange={(e) => updateFlagColorRow(idx, 'step_h', e.target.value)}
                                        className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                        title="Hue step"
                                        placeholder="Step H"
                                      />
                                      <input
                                        type="number"
                                        step="any"
                                        value={row.step_s ?? DEFAULT_FLAG_SEQUENCE_ROW.step_s}
                                        onChange={(e) => updateFlagColorRow(idx, 'step_s', e.target.value)}
                                        className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                        title="Saturation step"
                                        placeholder="Step S"
                                      />
                                      <input
                                        type="number"
                                        step="any"
                                        value={row.step_l ?? DEFAULT_FLAG_SEQUENCE_ROW.step_l}
                                        onChange={(e) => updateFlagColorRow(idx, 'step_l', e.target.value)}
                                        className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                        title="Lightness step"
                                        placeholder="Step L"
                                      />
                                    </div>
                                  </div>
                                ))}
                                <div className="text-[10px] text-gray-500">Each row: class filter (optional), seed colors (optional), then H/S/L step.</div>
                                <button onClick={addFlagColorRow} className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1">
                                  <Plus size={12}/> Add Sequence
                                </button>
                             </div>
                         </div>
                         <div>
                             <label className="block text-[10px] font-bold text-gray-500 mb-1 flex items-center gap-1">
                                Admin Color Sequence
                                <span title="Same LinearColorSequence controls as flags.">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="bg-gray-50 border border-gray-200 rounded p-2 space-y-2">
                                <input
                                  type="text"
                                  value={adminColorRow.colors || ''}
                                  onChange={(e) => updateAdminColorRow('colors', e.target.value)}
                                  className="w-full px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                  placeholder="#bbbbbb,#666666 or lightgray,gray"
                                />
                                <div className="grid grid-cols-3 gap-1">
                                  <input
                                    type="number"
                                    step="any"
                                    value={adminColorRow.step_h ?? DEFAULT_ADMIN_SEQUENCE_ROW.step_h}
                                    onChange={(e) => updateAdminColorRow('step_h', e.target.value)}
                                    className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    title="Hue step"
                                    placeholder="Step H"
                                  />
                                  <input
                                    type="number"
                                    step="any"
                                    value={adminColorRow.step_s ?? DEFAULT_ADMIN_SEQUENCE_ROW.step_s}
                                    onChange={(e) => updateAdminColorRow('step_s', e.target.value)}
                                    className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    title="Saturation step"
                                    placeholder="Step S"
                                  />
                                  <input
                                    type="number"
                                    step="any"
                                    value={adminColorRow.step_l ?? DEFAULT_ADMIN_SEQUENCE_ROW.step_l}
                                    onChange={(e) => updateAdminColorRow('step_l', e.target.value)}
                                    className="px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    title="Lightness step"
                                    placeholder="Step L"
                                  />
                                </div>
                             </div>
                         </div>
                         <div>
                             <label className="block text-[10px] font-bold text-gray-500 mb-1 flex items-center gap-1">
                                Data Colormap
                                <span title="Choose a matplotlib colormap, or LinearSegmented with custom colors.">
                                    <Info size={10} className="text-blue-500 cursor-help"/>
                                </span>
                             </label>
                             <div className="space-y-2">
                                <select
                                  value={dataColormap.type}
                                  onChange={(e) => updateOption('data_colormap', { ...dataColormap, type: e.target.value })}
                                  className="w-full px-2 py-1 border border-gray-200 rounded text-[11px] bg-white"
                                >
                                  {DATA_CMAP_PRESETS.map((preset) => (
                                    <option key={preset} value={preset}>{preset}</option>
                                  ))}
                                </select>
                                {dataColormap.type === 'LinearSegmented' && (
                                  <input
                                    type="text"
                                    value={dataColormap.colors}
                                    onChange={(e) => updateOption('data_colormap', { ...dataColormap, colors: e.target.value })}
                                    className="w-full px-2 py-1 border border-gray-200 rounded text-[11px] font-mono"
                                    placeholder="yellow,orange,red"
                                  />
                                )}
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
