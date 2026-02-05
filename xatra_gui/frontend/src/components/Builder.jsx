import React from 'react';
import { Plus, Trash2, Map } from 'lucide-react';

const Builder = ({ elements, setElements, options, setOptions }) => {
  const addElement = (type) => {
    const newElement = { 
      type, 
      label: type === 'flag' ? 'New Country' : 'New ' + type, 
      value: type === 'flag' ? 'IND' : '',
      args: {} 
    };
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

  return (
    <div className="space-y-6">
      {/* Global Options */}
      <section className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
           Global Options
        </h3>
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Map Title</label>
            <input
              type="text"
              value={options.title || ''}
              onChange={(e) => setOptions({ ...options, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter map title..."
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Base Map</label>
            <select
              value={options.basemaps?.[0] || 'Esri.WorldTopoMap'}
              onChange={(e) => setOptions({ ...options, basemaps: [e.target.value] })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="Esri.WorldTopoMap">Esri World Topo</option>
              <option value="Esri.WorldImagery">Esri World Imagery</option>
              <option value="OpenTopoMap">Open Topo Map</option>
              <option value="Esri.WorldPhysical">Esri World Physical</option>
            </select>
          </div>
        </div>
      </section>

      {/* Layers */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900">Layers</h3>
          <div className="flex gap-2">
            <button 
              onClick={() => addElement('flag')}
              className="px-2 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded hover:bg-blue-100 flex items-center gap-1"
            >
              <Plus size={12}/> Flag
            </button>
            <button 
              onClick={() => addElement('river')}
              className="px-2 py-1 bg-cyan-50 text-cyan-600 text-xs font-medium rounded hover:bg-cyan-100 flex items-center gap-1"
            >
              <Plus size={12}/> River
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {elements.map((el, index) => (
            <div key={index} className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm relative group hover:border-blue-300 transition-colors">
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => removeElement(index)}
                  className="text-red-400 hover:text-red-600 p-1"
                >
                  <Trash2 size={14} />
                </button>
              </div>

              <div className="flex items-center gap-2 mb-2">
                <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${el.type === 'flag' ? 'bg-orange-100 text-orange-700' : 'bg-cyan-100 text-cyan-700'}`}>
                  {el.type}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-2">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Label</label>
                  <input
                    type="text"
                    value={el.label || ''}
                    onChange={(e) => updateElement(index, 'label', e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                    placeholder="Label"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">
                    {el.type === 'flag' ? 'GADM Code' : 'Value'}
                  </label>
                  <input
                    type="text"
                    value={el.value || ''}
                    onChange={(e) => updateElement(index, 'value', e.target.value)}
                    className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none font-mono"
                    placeholder={el.type === 'flag' ? 'e.g. IND.1' : 'Value'}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-1">Note (Tooltip)</label>
                <input
                  type="text"
                  value={el.args?.note || ''}
                  onChange={(e) => updateArg(index, 'note', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded text-sm focus:border-blue-500 outline-none"
                  placeholder="Optional description..."
                />
              </div>
            </div>
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
