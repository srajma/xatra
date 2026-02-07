import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Trash2, MousePointer2, GripVertical } from 'lucide-react';
import AutocompleteInput from './AutocompleteInput';

const TerritoryBuilder = ({ 
  value, onChange, lastMapClick, activePicker, setActivePicker, draftPoints, setDraftPoints, parentId, predefinedCode, onStartReferencePick, onStartTerritoryLibraryPick
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
  const isReferencePickingThisFlag = !!(activePicker && activePicker.context === 'reference-gadm' && activePicker.target?.flagIndex === parentId);
  const isLibraryPickingThisPart = !!(activePicker && activePicker.context === 'territory-library' && activePicker.target?.flagIndex === parentId && activePicker.target?.partIndex != null);

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
              } catch {
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

  const [draggedIndex, setDraggedIndex] = useState(null);
  const [dragOverIndex, setDragOverIndex] = useState(null);

  const movePart = (fromIndex, toIndex) => {
    if (fromIndex === toIndex) return;
    const newParts = [...parts];
    const [removed] = newParts.splice(fromIndex, 1);
    newParts.splice(toIndex, 0, removed);
    onChange(newParts);
    setActivePicker(null);
  };

  const handleDragStart = (e, index) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', String(index));
  };
  const handleDragOver = (e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };
  const handleDragLeave = () => setDragOverIndex(null);
  const handleDrop = (e, toIndex) => {
    e.preventDefault();
    setDragOverIndex(null);
    setDraggedIndex(null);
    const fromIndex = parseInt(e.dataTransfer.getData('text/plain'), 10);
    if (Number.isNaN(fromIndex)) return;
    movePart(fromIndex, toIndex);
  };
  const handleDragEnd = () => {
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleRowKeyDown = (e, index) => {
    if (!e.altKey) return;
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      movePart(index, Math.max(0, index - 1));
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      movePart(index, Math.min(parts.length - 1, index + 1));
    }
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
        <div
          key={idx}
          draggable
          tabIndex={0}
          onDragStart={(e) => handleDragStart(e, idx)}
          onDragOver={(e) => handleDragOver(e, idx)}
          onDragLeave={handleDragLeave}
          onDrop={(e) => handleDrop(e, idx)}
          onDragEnd={handleDragEnd}
          onKeyDown={(e) => handleRowKeyDown(e, idx)}
          className={`flex gap-2 items-start bg-gray-50 p-2 rounded border transition-colors ${draggedIndex === idx ? 'opacity-50' : ''} ${dragOverIndex === idx ? 'border-blue-400 ring-1 ring-blue-200' : 'border-gray-200'}`}
        >
           <div className="flex items-center cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600 flex-shrink-0" title="Drag to reorder">
             <GripVertical size={14}/>
           </div>
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
             <option value="predefined">Territory library</option>
           </select>

           {/* Value */}
           <div className="flex-1 min-w-0">
               {part.type === 'gadm' ? (
                  <div className="flex gap-1">
                    <AutocompleteInput
                      value={part.value}
                      onChange={(val) => updatePart(idx, 'value', val)}
                      className="w-full text-xs p-1 border rounded bg-white"
                      placeholder="Search GADM..."
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (isReferencePickingThisFlag) {
                          setActivePicker(null);
                          return;
                        }
                        onStartReferencePick({ kind: 'gadm', flagIndex: parentId, partIndex: idx });
                      }}
                      className={`p-1 border rounded flex-shrink-0 transition-colors ${isReferencePickingThisFlag ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'}`}
                      title={isReferencePickingThisFlag ? 'Cancel GADM picking' : 'Pick GADM from Reference Map'}
                    >
                      <MousePointer2 size={12}/>
                    </button>
                  </div>
               ) : part.type === 'predefined' ? (
                   <div className="flex gap-1 items-start">
                       <div className="relative flex-1 min-w-0">
                           <input 
                               type="text"
                               value={part.value}
                               onChange={(e) => updatePart(idx, 'value', e.target.value)}
                               className="w-full text-xs p-1 border rounded bg-white"
                               placeholder="e.g. maurya or NORTH_INDIA (from territory library)"
                               list={`predefined-list-${parentId}-${idx}`}
                           />
                           <datalist id={`predefined-list-${parentId}-${idx}`}>
                               {allPredefinedOptions.map(v => (
                                   <option key={v} value={v} />
                               ))}
                           </datalist>
                       </div>
                       <button
                         type="button"
                         onClick={() => {
                           if (isLibraryPickingThisPart && activePicker?.target?.partIndex === idx) {
                             setActivePicker(null);
                             return;
                           }
                           onStartTerritoryLibraryPick({ kind: 'territory', flagIndex: parentId, partIndex: idx });
                         }}
                         className={`p-1 border rounded flex-shrink-0 transition-colors ${isLibraryPickingThisPart && activePicker?.target?.partIndex === idx ? 'bg-blue-100 text-blue-700 border-blue-300 ring-2 ring-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border-gray-200'}`}
                         title={isLibraryPickingThisPart && activePicker?.target?.partIndex === idx ? 'Cancel territory library picking' : 'Pick from Territory Library map'}
                       >
                         <MousePointer2 size={12}/>
                       </button>
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
