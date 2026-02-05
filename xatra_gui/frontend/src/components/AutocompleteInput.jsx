import React, { useState, useEffect, useRef } from 'react';

const AutocompleteInput = ({ value, onChange, placeholder, className }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  const fetchSuggestions = async (query) => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8088/search/gadm?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setSuggestions(data);
      setShowSuggestions(true);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const val = e.target.value;
    onChange(val);
    
    if (timerRef.current) clearTimeout(timerRef.current);
    
    timerRef.current = setTimeout(() => {
        fetchSuggestions(val);
    }, 300);
  };

  const handleSelect = (item) => {
    onChange(item.gid);
    setShowSuggestions(false);
  };

  return (
    <div className="relative" ref={wrapperRef}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
        className={className}
        placeholder={placeholder}
      />
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((item) => (
            <div
              key={item.gid}
              onClick={() => handleSelect(item)}
              className="px-3 py-2 cursor-pointer hover:bg-gray-100 text-xs border-b border-gray-50 last:border-none"
            >
              <div className="font-semibold">{item.name} <span className="text-gray-400 font-normal">({item.gid})</span></div>
              <div className="text-gray-500 text-[10px]">{item.country} • Level {item.level}</div>
            </div>
          ))}
        </div>
      )}
      {loading && (
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
      )}
    </div>
  );
};

export default AutocompleteInput;