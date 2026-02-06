import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Trash2, MousePointer2 } from 'lucide-react';
import AutocompleteInput from './AutocompleteInput';

const TerritoryBuilder = ({ 
  value, onChange, lastMapClick, activePicker, setActivePicker, draftPoints, setDraftPoints, parentId, predefinedCode 
}) => {
  // Normalize value to list of objects
  let parts = [];
  if (Array.isArray(value)) {
      if (value.length > 0 && typeof value[0] === 'object') {
          parts = value;
      } else {
          parts = value.map(v => ({ op: 'union', type: 'gadm', value: v }));
      }
  } else if (typeof value === 'string' && value) {
      parts = [{ op: 'union', type: 'gadm', value: value }];
  }

  const getPickingIndex = () => {
      if (activePicker && activePicker.context === `territory-${parentId}`) {
          return activePicker.id;
      }
      return -1;
  };

  const pickingIndex = getPickingIndex();

  useEffect(() => {
      if (pickingIndex >= 0 && lastMapClick) {
        const idx = pickingIndex;
        const lat = parseFloat(lastMapClick.lat.toFixed(4));
        const lng = parseFloat(lastMapClick.lng.toFixed(4));
        const point = [lat, lng];

        const part = parts[idx];
        if (part && part.type === 'polygon') {
            const newPoints = [...draftPoints, point];
            setDraftPoints(newPoints);
            
            const newParts = [...parts];
            newParts[idx] = { ...part, value: JSON.stringify(newPoints) };
            onChange(newParts);
        }
      }
  }, [lastMapClick]);

  // Sync draftPoints when entering picking mode
  useEffect(() => {
      if (pickingIndex >= 0) {
          const part = parts[pickingIndex];
          if (part && part.type === 'polygon') {
              try {
                  const current = JSON.parse(part.value || '[]');
                  setDraftPoints(Array.isArray(current) ? current : []);
              } catch(e) {
                  setDraftPoints([]);
              }
          }
      }
  }, [pickingIndex]);

  const togglePicking = (index) => {
      if (pickingIndex === index) {
          setActivePicker(null);
          setDraftPoints([]);
      } else {
          setActivePicker({ id: index, type: 'polygon', context: `territory-${parentId}` });
          setDraftPoints([]);
      }
  };

  const updatePart = (index, field, val) => {
    const newParts = [...parts];
    newParts[index] = { ...newParts[index], [field]: val };
    onChange(newParts);
  };

  const addPart = () => {
    onChange([...parts, { op: 'union', type: 'gadm', value: '' }]);
  };

  const removePart = (index) => {
    const newParts = [...parts];
    newParts.splice(index, 1);
    onChange(newParts);
  };

  const [territoryLibraryNames, setTerritoryLibraryNames] = useState([]);
  useEffect(() => {
    fetch('http://localhost:8088/territory_library/names')
      .then(r => r.json())
      .then(setTerritoryLibraryNames)
      .catch(() => setTerritoryLibraryNames([]));
  }, []);

  const predefinedVariables = useMemo(() => {
      if (!predefinedCode) return [];
      const regex = /^(\w+)\s*=/gm;
      const matches = [];
      let match;
      while ((match = regex.exec(predefinedCode)) !== null) {
          matches.push(match[1]);
      }
      return matches;
  }, [predefinedCode]);

  const allPredefinedOptions = useMemo(() => {
    const fromCode = predefinedVariables;
    const fromLib = territoryLibraryNames.filter(n => !fromCode.includes(n));
    return [...fromCode, ...fromLib];
  }, [predefinedVariables, territoryLibraryNames]);

  if (parts.length === 0) {
      return (
          <div className="border border-dashed border-gray-300 rounded p-2 text-center bg-gray-50">
              <button onClick={addPart} className="text-xs text-blue-600 flex items-center justify-center gap-1 w-full font-medium">
                  <Plus size={12}/> Define Territory
              </button>
          </div>
      )
  }

  return (
    <div className="space-y-2">
      {parts.map((part, idx) => (
        <div key={idx} className="flex gap-2 items-start bg-gray-50 p-2 rounded border border-gray-200">
           {/* Operator */}
           {idx > 0 ? (
               <select
                 value={part.op}
                 onChange={(e) => updatePart(idx, 'op', e.target.value)}
                 className="text-xs p-1 border rounded bg-white w-16 flex-shrink-0"
               >
                 <option value="union">∪ (+)</option>
                 <option value="difference">∖ (-)</option>
                 <option value="intersection">∩ (&)</option>
               </select>
           ) : (
               <div className="w-16 text-xs p-1 text-center font-bold text-gray-500 bg-gray-100 rounded flex-shrink-0 border border-gray-200">Base</div>
           )}

           {/* Type */}
           <select
             value={part.type}
             onChange={(e) => updatePart(idx, 'type', e.target.value)}
             className="text-xs p-1 border rounded bg-white w-20 flex-shrink-0"
           >
             <option value="gadm">GADM</option>
             <option value="polygon">Polygon</option>
             <option value="predefined">Predefined</option>
           </select>

           {/* Value */}
           <div className="flex-1 min-w-0">
               {part.type === 'gadm' ? (
                   <AutocompleteInput
                     value={part.value}
                     onChange={(val) => updatePart(idx, 'value', val)}
                     className="w-full text-xs p-1 border rounded bg-white"
                     placeholder="Search GADM..."
                   />
               ) : part.type === 'predefined' ? (
                   <div className="relative">
                       <input 
                           type="text"
                           value={part.value}
                           onChange={(e) => updatePart(idx, 'value', e.target.value)}
                           className="w-full text-xs p-1 border rounded bg-white"
                           placeholder="e.g. maurya or NORTH_INDIA"
                           list={`predefined-list-${parentId}-${idx}`}
                       />
                       <datalist id={`predefined-list-${parentId}-${idx}`}>
                           {allPredefinedOptions.map(v => (
                               <option key={v} value={v} />
                           ))}
                       </datalist>
                   </div>
               ) : (
                   <div className="flex gap-1 items-start">
                       <textarea
                         value={part.value}
                         onChange={(e) => updatePart(idx, 'value', e.target.value)}
                         className="w-full text-xs p-1 border rounded font-mono h-8 resize-none bg-white"
                         placeholder="[[lat,lon],...]"
                       />
                       <button 
                            onClick={() => togglePicking(idx)}
                            className={`p-1 border rounded flex-shrink-0 transition-colors ${pickingIndex === idx ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-white text-gray-600 hover:bg-gray-100 border-gray-300'}`}
                            title={pickingIndex === idx ? "Click on map to append points (Backspace to undo, Esc to stop)" : "Draw polygon on map"}
                        >
                            <MousePointer2 size={12}/>
                        </button>
                   </div>
               )}
           </div>

           <button onClick={() => removePart(idx)} className="text-red-400 hover:text-red-600 p-1 flex-shrink-0">
               <Trash2 size={12}/>
           </button>
        </div>
      ))}
      <button onClick={addPart} className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium mt-1">
          <Plus size={12}/> Add Operation
      </button>
    </div>
  );
};

export default TerritoryBuilder;