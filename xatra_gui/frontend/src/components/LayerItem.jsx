import React, { useState } from 'react';
import { Trash2, ChevronDown, ChevronUp, Info } from 'lucide-react';
import AutocompleteInput from './AutocompleteInput';
import TerritoryBuilder from './TerritoryBuilder';

const LayerItem = ({ element, index, updateElement, updateArg, replaceElement, removeElement }) => {
  const [showMore, setShowMore] = useState(false);

  const renderSpecificFields = () => {
    switch (element.type) {
      case 'flag':
        return (
          <div className="grid grid-cols-1 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Label</label>
              <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Name"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Territory</label>
              <TerritoryBuilder
                value={element.value}
                onChange={(val) => updateElement(index, 'value', val)}
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
              <input
                type="text"
                value={element.value || ''}
                onChange={(e) => updateElement(index, 'value', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                placeholder={element.args?.source_type === 'overpass' ? 'e.g. 1159122643' : 'e.g. Ganges'}
              />
              <div className="text-[10px] text-gray-400 mt-1 flex items-center gap-1">
                  <Info size={10}/> 
                  {element.args?.source_type === 'overpass' ? 'OSM Way/Relation ID' : 'Natural Earth ID or Name'}
              </div>
            </div>
          </div>
        );
      case 'point':
      case 'text':
         return (
           <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Label</label>
              <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Label"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Position [lat, lon]</label>
              <input
                type="text"
                value={element.value || ''}
                onChange={(e) => updateElement(index, 'value', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                placeholder="[28.6, 77.2]"
              />
            </div>
          </div>
        );
       case 'path':
         return (
           <div className="grid grid-cols-2 gap-3 mb-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Label</label>
              <input
                type="text"
                value={element.label || ''}
                onChange={(e) => updateElement(index, 'label', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                placeholder="Route Name"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Coords [[lat,lon]...]</label>
              <textarea
                value={element.value || ''}
                onChange={(e) => updateElement(index, 'value', e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono h-20"
                placeholder="[[28.6, 77.2], [19.0, 72.8]]"
              />
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
                className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                placeholder='["naturalearth"]'
              />
          </div>
        );
      default:
        return null;
    }
  };

  const renderMoreOptions = () => {
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
                    <label className="block text-xs text-gray-500 mb-1">Parent (Label)</label>
                    <input
                        type="text"
                        value={element.args?.parent || ''}
                        onChange={(e) => updateArg(index, 'parent', e.target.value)}
                        className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                        placeholder="e.g. British Empire"
                    />
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

         {element.type === 'point' && (
             <div className="col-span-2">
                <label className="block text-xs text-gray-500 mb-1 flex items-center gap-1">
                    Icon Options (JSON) 
                    <span title='Supports xatra.Icon() args: e.g. {"iconUrl": "...", "iconSize": [32, 32]}. Built-in icons: "city", "fort", "port", "temple", etc. Geometric: {"shape": "circle", "color": "red"}'>
                        <Info size={12} className="text-blue-500 cursor-help"/>
                    </span>
                </label>
                 <input
                    type="text"
                    value={element.args?.icon ? (typeof element.args.icon === 'string' ? element.args.icon : JSON.stringify(element.args.icon)) : ''}
                    onChange={(e) => {
                         const val = e.target.value;
                         try {
                                                 updateArg(index, 'icon', JSON.parse(val));
                                              } catch {
                                                  updateArg(index, 'icon', val);
                                              }
                                         }}
                                         className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                                         placeholder='e.g. "city" or {"shape": "star"}'
                                     />
                                 </div>
                              )}
                             </div>
                             );
                             };
                             
                             const [periodText, setPeriodText] = useState(element.args?.period ? element.args.period.join(', ') : '');
                             
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

  return (
    <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm relative group hover:border-blue-300 transition-colors">
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

      {/* Note */}
      <div>
        <label className="block text-xs text-gray-500 mb-1">Note (Tooltip)</label>
        <input
          type="text"
          value={element.args?.note || ''}
          onChange={(e) => updateArg(index, 'note', e.target.value)}
          className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
          placeholder="Optional description..."
        />
      </div>

      <button 
        onClick={() => setShowMore(!showMore)}
        className="mt-2 text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium"
      >
        {showMore ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
        {showMore ? 'Less Options' : 'More Options'}
      </button>
      
      {showMore && renderMoreOptions()}
    </div>
  );
};

export default LayerItem;