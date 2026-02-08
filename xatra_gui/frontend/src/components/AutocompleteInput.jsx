import React, { useState, useEffect, useRef } from 'react';

const AutocompleteInput = ({
  value,
  onChange,
  placeholder,
  className,
  endpoint = 'http://localhost:8088/search/gadm',
  minChars = 2,
  onSelectSuggestion,
  inputProps = {},
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef(null);
  const timerRef = useRef(null);
  const listRef = useRef(null);
  const itemRefs = useRef([]);

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
    if (!query || query.length < minChars) {
      setSuggestions([]);
      setActiveIndex(-1);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setSuggestions(data);
      setShowSuggestions(true);
      setActiveIndex(data.length > 0 ? 0 : -1);
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
    if (typeof onSelectSuggestion === 'function') {
      onSelectSuggestion(item);
    } else {
      onChange(item.gid || item.country_code || item.country || '');
    }
    setShowSuggestions(false);
    setActiveIndex(-1);
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Escape') setShowSuggestions(false);
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1) % suggestions.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => (prev <= 0 ? suggestions.length - 1 : prev - 1));
    } else if (e.key === 'Enter') {
      if (activeIndex >= 0 && activeIndex < suggestions.length) {
        e.preventDefault();
        handleSelect(suggestions[activeIndex]);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setShowSuggestions(false);
      setActiveIndex(-1);
    }
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  useEffect(() => {
    const listEl = listRef.current;
    const activeEl = itemRefs.current[activeIndex];
    if (!listEl || !activeEl) return;
    activeEl.scrollIntoView({ block: 'nearest' });
  }, [activeIndex]);

  return (
    <div className="relative" ref={wrapperRef}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
        className={className}
        placeholder={placeholder}
        {...inputProps}
      />
      {showSuggestions && suggestions.length > 0 && (
        <div ref={listRef} className="xatra-autocomplete-menu absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((item, idx) => (
            <div
              key={`${item.gid || item.country_code || item.country || 'item'}-${idx}`}
              ref={(el) => { itemRefs.current[idx] = el; }}
              onClick={() => handleSelect(item)}
              onMouseEnter={() => setActiveIndex(idx)}
              className={`xatra-autocomplete-item px-3 py-2 cursor-pointer text-xs border-b border-gray-50 last:border-none ${
                idx === activeIndex ? 'bg-blue-50 xatra-autocomplete-item-active' : 'hover:bg-gray-100'
              }`}
            >
              <div className="font-semibold">
                {item.name || item.country || item.country_code || 'Unknown'}
                {(item.gid || item.country_code) && (
                  <span className="text-gray-400 font-normal"> ({item.gid || item.country_code})</span>
                )}
              </div>
              {(item.country || item.level != null || item.max_level != null) && (
                <div className="xatra-autocomplete-meta text-gray-500 text-[10px]">
                  {item.country || item.country_code}
                  {item.level != null ? ` • Level ${item.level}` : ''}
                  {item.max_level != null ? ` • Max ${item.max_level}` : ''}
                </div>
              )}
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
