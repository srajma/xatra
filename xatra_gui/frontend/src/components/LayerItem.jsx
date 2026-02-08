import React, { useState, useEffect } from 'react';
import { Trash2, ChevronDown, ChevronUp, Info, MousePointer2, Save } from 'lucide-react';
import AutocompleteInput from './AutocompleteInput';
import TerritoryBuilder from './TerritoryBuilder';

const BUILTIN_ICON_SHAPES = ['circle', 'square', 'triangle', 'diamond', 'cross', 'plus', 'star', 'hexagon', 'pentagon', 'octagon'];

const LayerItem = ({ 
  element, index, elements, updateElement, updateArg, replaceElement, removeElement, 
  lastMapClick, activePicker, setActivePicker, draftPoints, setDraftPoints,
  onSaveTerritory, predefinedCode, onStartReferencePick
}) => {
  const [showMore, setShowMore] = useState(false);
  const [builtinIconsList, setBuiltinIconsList] = useState([]);
  
  const isPicking = activePicker && activePicker.id === index && activePicker.context === 'layer';
  const isRiverReferencePicking = activePicker && activePicker.id === index && activePicker.context === 'reference-river';

  const [periodText, setPeriodText] = useState(element.args?.period ? element.args.period.join(', ') : '');

  // Sync periodText when element changes (e.g. project load)
  useEffect(() => {
      setPeriodText(element.args?.period ? element.args.period.join(', ') : '');
  }, [element.args?.period]);

  useEffect(() => {
    if (element.type === 'point') {
      fetch('http://localhost:8088/icons/list')
        .then(r => r.json())
        .then(setBuiltinIconsList)
        .catch(() => setBuiltinIconsList([]));
    }
  }, [element.type]);

  useEffect(() => {
      if (isPicking && lastMapClick) {
        const lat = parseFloat(lastMapClick.lat.toFixed(4));
        const lng = parseFloat(lastMapClick.lng.toFixed(4));
        const point = [lat, lng];

        if (element.type === 'point' || element.type === 'text') {
            updateElement(index, 'value', JSON.stringify(point));
            setDraftPoints([point]);
            // Keep cue visible briefly so the click location is perceptible after picker turns off.
            window.setTimeout(() => {
              setActivePicker(null);
              setDraftPoints([]);
            }, 240);
        } else if (element.type === 'path') {
            const newPoints = [...draftPoints, point];
            setDraftPoints(newPoints);
            updateElement(index, 'value', JSON.stringify(newPoints));
        }
      }
  }, [lastMapClick]);

  // Sync draftPoints when entering picking mode for path
  useEffect(() => {
      if (isPicking && element.type === 'path') {
          try {
              const current = JSON.parse(element.value || '[]');
              setDraftPoints(Array.isArray(current) ? current : []);
          } catch {
              setDraftPoints([]);
          }
      }
  }, [isPicking]);

  const togglePicking = () => {
      if (isPicking) {
          setActivePicker(null);
          setDraftPoints([]);
      } else {
          setActivePicker({ id: index, type: element.type, context: 'layer' });
          // For point/text, show existing position as dot when entering picker mode
          if (element.type === 'point' || element.type === 'text') {
              try {
                  const pos = typeof element.value === 'string' ? JSON.parse(element.value || '[]') : element.value;
                  if (Array.isArray(pos) && pos.length >= 2 && typeof pos[0] === 'number' && typeof pos[1] === 'number') {
                      setDraftPoints([pos]);
                      return;
                  }
              } catch {
                // ignore malformed coordinates while entering picker mode
              }
          }
          setDraftPoints([]);
      }
  };

  const handlePeriodChange = (val) => {
    setPeriodText(val);
    if (val === "") {
      updateArg(index, 'period', null);
      return;
    }
    
    // Support [-320, -180] or -320, -180
    let clean = val.split('[').join('').split(']').join('');
    const parts = clean.split(',').map(s => s.trim());      
    if (parts.length === 2) {
        const start = parseInt(parts[0]);
        const end = parseInt(parts[1]);
        if (!isNaN(start) && !isNaN(end)) {
            updateArg(index, 'period', [start, end]);
        }
    }
  };

  const renderSpecificFields = () => {
    switch (element.type) {
      case 'flag':
        return (
          <div className="grid grid-cols-1 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">State name</label>
              <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                data-focus-primary="true"
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Name"
              />
              <div className="mt-1 text-[10px] text-gray-500 leading-snug">
                A <b>Flag</b> asserts the reign of a State over a Territory (perhaps for a particular period of time). Flag layers with the same State name are rendered as the same geometry.
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs text-gray-500">Territory</label>
                  <button 
                    onClick={() => onSaveTerritory(element)}
                    className="text-[10px] text-blue-600 hover:text-blue-800 flex items-center gap-1 font-bold"
                    title="Save territory to Territory library"
                  >
                    <Save size={10}/> Save to Library
                  </button>
              </div>
              <TerritoryBuilder
                value={element.value}
                onChange={(val) => updateElement(index, 'value', val)}
                lastMapClick={lastMapClick}
                activePicker={activePicker}
                setActivePicker={setActivePicker}
                draftPoints={draftPoints}
                setDraftPoints={setDraftPoints}
                parentId={index}
                predefinedCode={predefinedCode}
                onStartReferencePick={onStartReferencePick}
                onStartTerritoryLibraryPick={onStartReferencePick}
              />
            </div>
          </div>
        );
      case 'river':
        return (
           <div className="space-y-3 mb-2">
            <div className="grid grid-cols-2 gap-3">
                <div>
                <label className="block text-xs text-gray-500 mb-1">Label</label>
                <input
                    type="text"
                    value={element.label || ''}
                    onChange={(e) => updateElement(index, 'label', e.target.value)}
                    data-focus-primary="true"
                    className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                    placeholder="River Name"
                />
                </div>
                <div>
                    <label className="block text-xs text-gray-500 mb-1">Source</label>
                    <select
                        value={element.args?.source_type || 'naturalearth'}
                        onChange={(e) => {
                             const newType = e.target.value;
                             const newValue = newType === 'overpass' ? '1159233' : '1159122643';
                             replaceElement(index, {
                                 ...element,
                                 value: newValue,
                                 args: { ...element.args, source_type: newType }
                             });
                        }}
                        className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                    >
                        <option value="naturalearth">Natural Earth</option>
                        <option value="overpass">Overpass (OSM)</option>
                    </select>
                </div>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">ID</label>
              <div className="flex gap-1">
                <input
                  type="text"
                  value={element.value || ''}
                  onChange={(e) => updateElement(index, 'value', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                  placeholder={element.args?.source_type === 'overpass' ? 'e.g. 1159233' : 'e.g. 1159122643'}
                />
                <button
                  type="button"
                  onClick={() => {
                    if (isRiverReferencePicking) {
                      setActivePicker(null);
                      return;
                    }
                    onStartReferencePick({ kind: 'river', layerIndex: index, label: element.label || '' });
                  }}
                  className={`p-1.5 border rounded flex-shrink-0 transition-colors ${isRiverReferencePicking ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'}`}
                  title={isRiverReferencePicking ? 'Cancel river picking' : 'Pick river from Reference Map'}
                >
                  <MousePointer2 size={14} />
                </button>
              </div>
              <div className="text-[10px] text-gray-400 mt-1 flex items-center gap-1">
                  <Info size={10}/> 
                  {element.args?.source_type === 'overpass' ? 'OSM Way/Relation ID' : 'Natural Earth ID'}
              </div>
            </div>
          </div>
        );
      case 'point':
      case 'text': {
        const iconArg = element.args?.icon;
        const iconMode = !iconArg ? 'default' : typeof iconArg === 'string' ? 'builtin' : iconArg.shape ? 'geometric' : 'custom';
        return (
           <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Label</label>
                <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                data-focus-primary="true"
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Label"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Position [lat, lon]</label>
              <div className="flex gap-1">
                  <input
                    type="text"
                    value={element.value || ''}
                    onChange={(e) => updateElement(index, 'value', e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                    placeholder="[28.6, 77.2]"
                  />
                  <button 
                    onClick={togglePicking}
                    className={`p-1.5 border rounded flex-shrink-0 transition-colors ${isPicking ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'}`}
                    title={isPicking ? "Click on map to pick location (Esc to cancel)" : "Pick from map"}
                  >
                    <MousePointer2 size={16}/>
                  </button>
              </div>
            </div>
            {element.type === 'point' && (
              <div className="col-span-2 space-y-2 pt-1 border-t border-gray-100">
                <label className="block text-xs text-gray-500 mb-1 flex items-center gap-1">
                  Icon
                  <span title="Built-in: package icons. Geometric: circle, star, etc. Custom: any image URL.">
                    <Info size={12} className="text-blue-500 cursor-help"/>
                  </span>
                </label>
                <div className="flex flex-wrap gap-2 items-end">
                  <select
                    value={iconMode}
                    onChange={(e) => {
                      const m = e.target.value;
                      if (m === 'default') updateArg(index, 'icon', null);
                      else if (m === 'builtin') updateArg(index, 'icon', builtinIconsList[0] || 'star.svg');
                      else if (m === 'geometric') updateArg(index, 'icon', { shape: 'circle', color: '#3388ff', size: 24 });
                      else updateArg(index, 'icon', { icon_url: '' });
                    }}
                    className="text-xs px-2 py-1.5 border border-gray-200 rounded bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="default">Default marker</option>
                    <option value="builtin">Built-in icon</option>
                    <option value="geometric">Geometric shape</option>
                    <option value="custom">Custom URL</option>
                  </select>
                  {iconMode === 'builtin' && (
                    <select
                      value={typeof iconArg === 'string' ? iconArg : ''}
                      onChange={(e) => updateArg(index, 'icon', e.target.value || null)}
                      className="text-xs px-2 py-1.5 border border-gray-200 rounded bg-white focus:ring-2 focus:ring-blue-500 outline-none max-w-[180px]"
                    >
                      <option value="">—</option>
                      {builtinIconsList.map(f => (
                        <option key={f} value={f}>{f}</option>
                      ))}
                    </select>
                  )}
                  {iconMode === 'geometric' && (
                    <>
                      <select
                        value={iconArg?.shape || 'circle'}
                        onChange={(e) => updateArg(index, 'icon', { ...iconArg, shape: e.target.value })}
                        className="text-xs px-2 py-1.5 border border-gray-200 rounded bg-white focus:ring-2 focus:ring-blue-500 outline-none"
                      >
                        {BUILTIN_ICON_SHAPES.map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                      <input
                        type="text"
                        value={iconArg?.color || '#3388ff'}
                        onChange={(e) => updateArg(index, 'icon', { ...iconArg, color: e.target.value })}
                        placeholder="Color"
                        className="w-20 text-xs px-2 py-1.5 border border-gray-200 rounded font-mono"
                        title="CSS color, e.g. red or #ff0000"
                      />
                      <input
                        type="number"
                        min={8}
                        max={64}
                        value={iconArg?.size ?? 24}
                        onChange={(e) => updateArg(index, 'icon', { ...iconArg, size: parseInt(e.target.value) || 24 })}
                        className="w-14 text-xs px-2 py-1.5 border border-gray-200 rounded"
                        title="Size in pixels"
                      />
                    </>
                  )}
                  {iconMode === 'custom' && (
                    <input
                      type="text"
                      value={iconArg?.icon_url || iconArg?.iconUrl || ''}
                      onChange={(e) => updateArg(index, 'icon', { ...iconArg, icon_url: e.target.value })}
                      placeholder="https://... or data:..."
                      className="flex-1 min-w-[160px] text-xs px-2 py-1.5 border border-gray-200 rounded font-mono"
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        );
      }
       case 'path':
         return (
           <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Label</label>
              <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                data-focus-primary="true"
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Route Name"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Coords [[lat,lon]...]</label>
              <div className="flex gap-1 items-start">
                  <textarea
                    value={element.value || ''}
                    onChange={(e) => updateElement(index, 'value', e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono h-20 resize-none"
                    placeholder="[[28.6, 77.2], [19.0, 72.8]]"
                  />
                  <button 
                    onClick={togglePicking}
                    className={`p-1.5 border rounded flex-shrink-0 transition-colors ${isPicking ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'}`}
                    title={isPicking ? "Click on map to append points (Backspace to undo, Esc to stop)" : "Draw path on map"}
                  >
                    <MousePointer2 size={16}/>
                  </button>
              </div>
              {isPicking && (
                  <div className="text-[10px] text-gray-500 mt-1 italic flex gap-2">
                      <span>Hold Ctrl/Cmd + drag for freehand</span>
                      <span>⌫ Backspace to undo</span>
                  </div>
              )}
            </div>
          </div>
        );
      case 'dataframe':
        return (
          <div className="space-y-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">CSV Content or File Path</label>
              <textarea
                value={element.value || ''}
                onChange={(e) => updateElement(index, 'value', e.target.value)}
                data-focus-primary="true"
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono h-24 resize-y text-xs"
                placeholder="GID,value\nIND,100"
              />
              <div className="mt-1">
                 <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                            const reader = new FileReader();
                            reader.onload = (ev) => {
                                updateElement(index, 'value', ev.target.result);
                            };
                            reader.readAsText(file);
                        }
                    }}
                    className="text-xs text-gray-500"
                 />
              </div>
            </div>
            <div className="text-[10px] text-gray-500 italic">
              `GID` and data/year columns are auto-detected from CSV.
            </div>
          </div>
        );
      case 'admin':
         return (
           <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
               <label className="block text-xs text-gray-500 mb-1">GADM Code</label>
              <AutocompleteInput
                value={element.value || ''}
                onChange={(val) => updateElement(index, 'value', val)}
                inputProps={{ 'data-focus-primary': 'true' }}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                placeholder="e.g. IND"
              />
            </div>
             <div>
              <label className="block text-xs text-gray-500 mb-1">Level</label>
              <input
                type="number"
                value={element.args?.level || 1}
                onChange={(e) => updateArg(index, 'level', parseInt(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
              />
            </div>
          </div>
        );
      case 'admin_rivers':
         return (
           <div className="mb-2">
              <label className="block text-xs text-gray-500 mb-1">Sources (JSON list)</label>
              <input
                type="text"
                value={element.value || '["naturalearth"]'}
                onChange={(e) => updateElement(index, 'value', e.target.value)}
                data-focus-primary="true"
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
              placeholder='["naturalearth"]'
              />
          </div>
        );
      case 'titlebox':
        return (
          <div className="mb-2">
            <label className="block text-xs text-gray-500 mb-1">TitleBox (HTML)</label>
            <textarea
              value={element.value || ''}
              onChange={(e) => updateElement(index, 'value', e.target.value)}
              data-focus-primary="true"
              className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono h-20 resize-y"
              placeholder="<b>My Map</b>"
            />
          </div>
        );
      default:
        return null;
    }
  };

  const renderMoreOptions = () => {
    if (element.type === 'titlebox') {
      return null;
    }
    const inheritOptions = (elements || [])
      .filter((el, idx) => idx !== index && el?.type === 'flag')
      .map((el) => String(el?.label || '').trim())
      .filter(Boolean)
      .filter((label, idx, arr) => arr.indexOf(label) === idx);

    return (
      <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-3">
        {/* Classes */}
        <div>
           <label className="block text-xs text-gray-500 mb-1">CSS Classes</label>
           <input
            type="text"
            value={element.args?.classes || ''}
            onChange={(e) => updateArg(index, 'classes', e.target.value)}
            className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
            placeholder="e.g. my-style"
          />
        </div>

        {/* Type specific extra args */}
        {element.type === 'flag' && (
            <>
                 <div>
                    <label className="block text-xs text-gray-500 mb-1">Color (Hex)</label>
                    <input
                        type="text"
                        value={element.args?.color || ''}
                        onChange={(e) => updateArg(index, 'color', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                        placeholder="#ff0000"
                    />
                </div>
                 <div>
                    <label className="block text-xs text-gray-500 mb-1">Inherit Color From</label>
                    <select
                      value={element.args?.inherit || ''}
                      onChange={(e) => updateArg(index, 'inherit', e.target.value)}
                      className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                    >
                      <option value="">None</option>
                      {inheritOptions.map((label) => (
                        <option key={label} value={label}>
                          {label}
                        </option>
                      ))}
                    </select>
                </div>
            </>
        )}
        
        {(element.type === 'river' || element.type === 'path' || element.type === 'point') && (
             <div className="flex items-center pt-4">
                <label className="flex items-center gap-2 text-xs text-gray-700 cursor-pointer select-none">
                    <input
                        type="checkbox"
                        checked={element.args?.show_label || false}
                        onChange={(e) => updateArg(index, 'show_label', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    Show Label
                </label>
            </div>
        )}

         {/* Point icon is configured in the main form */}
        </div>
    );
  };

  return (
    <div className="xatra-layer-card bg-white p-3 rounded-lg border border-gray-200 shadow-sm relative group hover:border-blue-300 transition-colors">
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          onClick={() => removeElement(index)}
          className="text-red-400 hover:text-red-600 p-1"
        >
          <Trash2 size={14} />
        </button>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-gray-100 text-gray-700`}>
          {element.type}
        </span>
      </div>

      {renderSpecificFields()}

      {/* Period - Now visible by default */}
      <div className="mb-2">
          <label className="block text-xs text-gray-500 mb-1">Period [start, end]</label>
          <input
            type="text"
            value={periodText}
            onChange={(e) => handlePeriodChange(e.target.value)}
            className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
            placeholder="e.g. -320, -180"
          />
           <div className="text-[10px] text-gray-400 mt-0.5 flex items-center gap-1">
               <Info size={10}/> Use negative numbers for BC years (e.g. -320, -180)
           </div>
      </div>

      {element.type !== 'titlebox' && (
        <div>
          <label className="block text-xs text-gray-500 mb-1">Note (Tooltip)</label>
          <input
            type="text"
            value={element.args?.note || ''}
            onChange={(e) => updateArg(index, 'note', e.target.value)}
            className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
            placeholder="Optional description..."
          />
        </div>
      )}

      {element.type !== 'titlebox' && (
        <>
          <button 
            onClick={() => setShowMore(!showMore)}
            className="mt-2 text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium"
          >
            {showMore ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
            {showMore ? 'Less Options' : 'More Options'}
          </button>
          
          {showMore && renderMoreOptions()}
        </>
      )}
    </div>
  );
};

export default LayerItem;
