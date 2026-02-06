import React from 'react';
import { Map, Users, MapPin, Type, GitMerge, Table } from 'lucide-react';
import LayerItem from './LayerItem';
import GlobalOptions from './GlobalOptions';

const Builder = ({ 
  elements, setElements, options, setOptions, onGetCurrentView, 
  lastMapClick, activePicker, setActivePicker, draftPoints, setDraftPoints,
  onSaveTerritory, predefinedCode
}) => {
  const addElement = (type) => {
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
      case 'admin_rivers':
        newElement.label = 'All Rivers'; // AdminRivers doesn't really have a label arg in MapElement but useful for UI
        newElement.value = '["naturalearth"]';
        break;
      case 'dataframe':
        newElement.label = 'Data';
        newElement.value = 'GID,value\nIND,100\nPAK,50';
        newElement.args = { data_column: 'value' };
        break;
      default:
        break;
    }

    setElements([...elements, newElement]);
  };

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
        
        {/* Add Buttons Grid */}
        <div className="grid grid-cols-4 gap-2 mb-4">
             <button onClick={() => addElement('flag')} className="flex flex-col items-center justify-center p-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-[10px] gap-1 border border-blue-100">
               <Map size={14}/> Flag
             </button>
             <button onClick={() => addElement('river')} className="flex flex-col items-center justify-center p-2 bg-cyan-50 text-cyan-700 rounded hover:bg-cyan-100 text-[10px] gap-1 border border-cyan-100">
               <span className="text-lg leading-3">~</span> River
             </button>
             <button onClick={() => addElement('point')} className="flex flex-col items-center justify-center p-2 bg-purple-50 text-purple-700 rounded hover:bg-purple-100 text-[10px] gap-1 border border-purple-100">
               <MapPin size={14}/> Point
             </button>
             <button onClick={() => addElement('text')} className="flex flex-col items-center justify-center p-2 bg-gray-50 text-gray-700 rounded hover:bg-gray-100 text-[10px] gap-1 border border-gray-100">
               <Type size={14}/> Text
             </button>
             <button onClick={() => addElement('path')} className="flex flex-col items-center justify-center p-2 bg-orange-50 text-orange-700 rounded hover:bg-orange-100 text-[10px] gap-1 border border-orange-100">
               <GitMerge size={14}/> Path
             </button>
             <button onClick={() => addElement('admin')} className="flex flex-col items-center justify-center p-2 bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100 text-[10px] gap-1 border border-indigo-100">
               <Users size={14}/> Admin
             </button>
             <button onClick={() => addElement('admin_rivers')} className="flex flex-col items-center justify-center p-2 bg-teal-50 text-teal-700 rounded hover:bg-teal-100 text-[10px] gap-1 border border-teal-100">
               <span className="text-lg leading-3">≈</span> All Rivers
             </button>
             <button onClick={() => addElement('dataframe')} className="flex flex-col items-center justify-center p-2 bg-green-50 text-green-700 rounded hover:bg-green-100 text-[10px] gap-1 border border-green-100">
               <Table size={14}/> Data
             </button>
        </div>

        <div className="space-y-3">
          {elements.map((el, index) => (
            <LayerItem 
              key={index} 
              element={el} 
              index={index} 
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
            />
          ))}
          
          {elements.length === 0 && (
            <div className="text-center py-8 border-2 border-dashed border-gray-200 rounded-lg text-gray-400 text-sm">
              No layers added yet. Click above to add one.
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Builder;