import React, { useRef, useEffect } from 'react';
import { Map, Users, MapPin, Type, GitMerge, Table, Heading } from 'lucide-react';
import LayerItem from './LayerItem';
import GlobalOptions from './GlobalOptions';

const Builder = ({ 
  elements, setElements, options, setOptions, onGetCurrentView, 
  lastMapClick, activePicker, setActivePicker, draftPoints, setDraftPoints,
  onSaveTerritory, predefinedCode, onStartReferencePick, addLayerSignal
}) => {
  const layersEndRef = useRef(null);
  const prevElementsLengthRef = useRef(elements.length);
  const pendingFocusNewLayerRef = useRef(false);

  const addElement = (type, opts = { focusFirstField: true }) => {
    let newElement = { 
      type, 
      label: 'New ' + type, 
      value: '',
      args: {} 
    };

    switch (type) {
      case 'flag':
        newElement.label = 'New Country';
        newElement.value = [];
        break;
      case 'river':
        newElement.value = '1159122643';
        newElement.args = { source_type: 'naturalearth' };
        break;
      case 'point':
        newElement.value = '[28.6, 77.2]';
        break;
      case 'text':
        newElement.value = '[28.6, 77.2]';
        break;
      case 'path':
        newElement.value = '[]';
        break;
      case 'admin':
        newElement.value = 'IND';
        newElement.args = { level: 1 };
        break;
      case 'dataframe':
        newElement.label = 'Data';
        newElement.value = 'GID,value\nIND,100\nPAK,50';
        newElement.args = { data_column: 'value' };
        break;
      case 'titlebox':
        newElement.label = 'TitleBox';
        newElement.value = '<b>My Map</b>';
        newElement.args = {};
        break;
      default:
        break;
    }

    if (opts.focusFirstField) pendingFocusNewLayerRef.current = true;
    setElements([...elements, newElement]);
  };

  useEffect(() => {
    if (elements.length > prevElementsLengthRef.current && layersEndRef.current) {
      layersEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
      if (pendingFocusNewLayerRef.current) {
        [0, 40, 120, 240].forEach((delay) => {
          window.setTimeout(() => {
            const cards = document.querySelectorAll('#layers-container .xatra-layer-card');
            const lastCard = cards[cards.length - 1];
            if (!lastCard) return;
            const firstField = lastCard.querySelector('[data-focus-primary="true"], input, textarea, select');
            if (firstField && typeof firstField.focus === 'function') {
              firstField.focus();
              if (typeof firstField.select === 'function' && (firstField.tagName === 'INPUT' || firstField.tagName === 'TEXTAREA')) {
                firstField.select();
              }
            }
          }, delay);
        });
        pendingFocusNewLayerRef.current = false;
      }
    }
    prevElementsLengthRef.current = elements.length;
  }, [elements.length]);

  useEffect(() => {
    if (!addLayerSignal || !addLayerSignal.type) return;
    addElement(addLayerSignal.type, { focusFirstField: true });
  }, [addLayerSignal]);

  const removeElement = (index) => {
    const newElements = [...elements];
    newElements.splice(index, 1);
    setElements(newElements);
  };

  const updateElement = (index, field, value) => {
    const newElements = [...elements];
    newElements[index][field] = value;
    setElements(newElements);
  };

  const updateArg = (index, key, value) => {
    const newElements = [...elements];
    newElements[index].args = { ...newElements[index].args, [key]: value };
    setElements(newElements);
  };

  const replaceElement = (index, newElement) => {
    const newElements = [...elements];
    newElements[index] = newElement;
    setElements(newElements);
  };

  return (
    <div className="space-y-6">
      {/* Global Options */}
      <GlobalOptions 
        options={options} 
        setOptions={setOptions} 
        elements={elements} 
        onGetCurrentView={onGetCurrentView}
      />

      {/* Layers */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900">Layers</h3>
        </div>

        <div className="space-y-3 overflow-auto max-h-[70vh]" id="layers-container">
          {elements.map((el, index) => (
            <LayerItem 
              key={index} 
              element={el} 
              index={index} 
              elements={elements}
              updateElement={updateElement} 
              updateArg={updateArg}
              replaceElement={replaceElement}
              removeElement={removeElement}
              lastMapClick={lastMapClick}
              activePicker={activePicker}
              setActivePicker={setActivePicker}
              draftPoints={draftPoints}
              setDraftPoints={setDraftPoints}
              onSaveTerritory={onSaveTerritory}
              predefinedCode={predefinedCode}
              onStartReferencePick={onStartReferencePick}
            />
          ))}
          
          {elements.length === 0 && (
            <div className="text-center py-8 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 text-sm">
              No layers added yet. Add one below.
            </div>
          )}

          {/* Add layer panel at bottom so new layers appear above it */}
          <div ref={layersEndRef} className="grid grid-cols-3 gap-2 pt-2 sm:grid-cols-4">
             <button data-kind="flag" onClick={() => addElement('flag', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-[10px] gap-1 border border-blue-100">
               <Map size={14}/> Flag
             </button>
             <button data-kind="river" onClick={() => addElement('river', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-cyan-50 text-cyan-700 rounded hover:bg-cyan-100 text-[10px] gap-1 border border-cyan-100">
               <span className="text-lg leading-3">~</span> River
             </button>
             <button data-kind="point" onClick={() => addElement('point', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-purple-50 text-purple-700 rounded hover:bg-purple-100 text-[10px] gap-1 border border-purple-100">
               <MapPin size={14}/> Point
             </button>
             <button data-kind="text" onClick={() => addElement('text', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-gray-50 text-gray-700 rounded hover:bg-gray-100 text-[10px] gap-1 border border-gray-100">
               <Type size={14}/> Text
             </button>
             <button data-kind="path" onClick={() => addElement('path', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-orange-50 text-orange-700 rounded hover:bg-orange-100 text-[10px] gap-1 border border-orange-100">
               <GitMerge size={14}/> Path
             </button>
             <button data-kind="admin" onClick={() => addElement('admin', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 text-[10px] gap-1 border border-indigo-100">
               <Users size={14}/> Admin
             </button>
             <button data-kind="data" onClick={() => addElement('dataframe', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-green-50 text-green-700 rounded hover:bg-green-100 text-[10px] gap-1 border border-green-100">
               <Table size={14}/> Data
             </button>
             <button data-kind="titlebox" onClick={() => addElement('titlebox', { focusFirstField: true })} className="xatra-add-layer-btn flex flex-col items-center justify-center p-2 bg-fuchsia-50 text-fuchsia-700 rounded hover:bg-fuchsia-100 text-[10px] gap-1 border border-fuchsia-100">
               <Heading size={14}/> TitleBox
             </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Builder;
