import React, { useState, useEffect, useRef } from 'react';
import { Layers, Code, Play, Upload, Save, FileJson, FileCode, Plus, Trash2, Keyboard, Copy, Check, Moon, Sun } from 'lucide-react';

// Components (defined inline for simplicity first, can be split later)
import Builder from './components/Builder';
import CodeEditor from './components/CodeEditor';
import MapPreview from './components/MapPreview';
import AutocompleteInput from './components/AutocompleteInput';

const isTerritoryPolygonPicker = (ctx) => /^territory-\d+$/.test(String(ctx || ''));
const isEditableTarget = (target) => (
  !!(target && typeof target.closest === 'function' && target.closest('input, textarea, [contenteditable="true"], [role="textbox"]'))
);

function App() {
  const [activeTab, setActiveTab] = useState('builder'); // 'builder' or 'code'
  const [activePreviewTab, setActivePreviewTab] = useState('main'); // 'main' | 'picker' | 'library'
  const [mapHtml, setMapHtml] = useState('');
  const [mapPayload, setMapPayload] = useState(null);
  const [pickerHtml, setPickerHtml] = useState('');
  const [territoryLibraryHtml, setTerritoryLibraryHtml] = useState('');
  const [territoryLibrarySource, setTerritoryLibrarySource] = useState('builtin'); // builtin | custom
  const [territoryLibraryNames, setTerritoryLibraryNames] = useState([]);
  const [selectedTerritoryNames, setSelectedTerritoryNames] = useState([]);
  const [territorySearchTerm, setTerritorySearchTerm] = useState('');
  const [copyIndexCopied, setCopyIndexCopied] = useState(false);
  const [loadingByView, setLoadingByView] = useState({ main: false, picker: false, library: false });
  const [mainRenderTask, setMainRenderTask] = useState(null); // 'code' | 'builder' | null
  const [error, setError] = useState(null);

  // Builder State
  const [builderElements, setBuilderElements] = useState([
    { type: 'flag', label: 'India', value: [], args: { note: 'Republic of India' } }
  ]);
  const [builderOptions, setBuilderOptions] = useState({
    basemaps: [{ url_or_provider: 'Esri.WorldTopoMap', default: true }],
    flag_color_sequences: [{ class_name: '', colors: '', step_h: 1.6180339887, step_s: 0.0, step_l: 0.0 }],
    admin_color_sequences: [{ colors: '', step_h: 1.6180339887, step_s: 0.0, step_l: 0.0 }],
    data_colormap: { type: 'LinearSegmented', colors: 'yellow,orange,red' },
  });
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      return localStorage.getItem('xatra-theme') === 'dark';
    } catch {
      return false;
    }
  });

  // Code State
  const [code, setCode] = useState(`import xatra
from xatra.loaders import gadm, naturalearth

xatra.BaseOption("Esri.WorldTopoMap", default=True)
xatra.Flag(label="India", value=gadm("IND"), note="Republic of India")
xatra.TitleBox("<b>My Map</b>")
`);

  const [predefinedCode, setPredefinedCode] = useState(`from xatra.territory_library import *  # https://github.com/srajma/xatra/blob/master/src/xatra/territory_library.py

`);

  // Picker State
  const [pickerOptions, setPickerOptions] = useState({
    entries: [
      { country: 'IND', level: 2 },
      { country: 'PAK', level: 3 },
      { country: 'BGD', level: 2 },
      { country: 'NPL', level: 3 },
      { country: 'BTN', level: 1 },
      { country: 'LKA', level: 1 },
      { country: 'AFG', level: 2 },
    ],
    adminRivers: true
  });
  
  const [lastMapClick, setLastMapClick] = useState(null);
  const [activePicker, setActivePicker] = useState(null); // { id, type, context }
  const [draftPoints, setDraftPoints] = useState([]);
  const [freehandModifierPressed, setFreehandModifierPressed] = useState(false);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [pickedGadmSelection, setPickedGadmSelection] = useState([]);
  const [pickedTerritorySelection, setPickedTerritorySelection] = useState([]);
  const [selectionBatches, setSelectionBatches] = useState([]);
  const [referencePickTarget, setReferencePickTarget] = useState(null); // { kind: 'gadm'|'river'|'territory', flagIndex?, layerIndex?, partIndex? }
  const [countryLevelOptions, setCountryLevelOptions] = useState({});
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  const [addLayerSignal, setAddLayerSignal] = useState(null);
  const hoverPickRef = useRef('');
  const didPrefetchReferenceRef = useRef(false);
  const didPrefetchTerritoryRef = useRef(false);

  const iframeRef = useRef(null);
  const pickerIframeRef = useRef(null);
  const territoryLibraryIframeRef = useRef(null);

  useEffect(() => {
    try {
      localStorage.setItem('xatra-theme', isDarkMode ? 'dark' : 'light');
    } catch {
      // Ignore persistence errors (e.g., private mode restrictions)
    }
  }, [isDarkMode]);

  const updateDraft = (points, shapeType) => {
      const ref = activePreviewTab === 'picker'
        ? pickerIframeRef
        : (activePreviewTab === 'library' ? territoryLibraryIframeRef : iframeRef);
      if (ref.current && ref.current.contentWindow) {
          ref.current.contentWindow.postMessage({ type: 'setDraft', points, shapeType }, '*');
      }
  };

  useEffect(() => {
      const isDraftPicker = !!(activePicker && (activePicker.context === 'layer' || isTerritoryPolygonPicker(activePicker.context)));
      if (isDraftPicker) {
          updateDraft(draftPoints, activePicker.type);
      } else {
          updateDraft([], null);
      }
  }, [draftPoints, activePicker, activePreviewTab, pickerHtml, territoryLibraryHtml]);

  useEffect(() => {
    const handleKeyDown = (e) => {
        if (!activePicker) return;
        if (isEditableTarget(e.target)) return;
        const isDraftPicker = activePicker.context === 'layer' || isTerritoryPolygonPicker(activePicker.context);
        if (!isDraftPicker) return;
        if (e.key === 'Control' || e.key === 'Meta') {
            setFreehandModifierPressed(true);
            return;
        }
        if (e.key === 'Backspace') {
            e.preventDefault();
            setDraftPoints(prev => {
                const newPoints = prev.slice(0, -1);
                updateElementFromDraft(newPoints);
                return newPoints;
            });
        } else if (e.key === 'Escape') {
            setActivePicker(null);
            setDraftPoints([]);
            setFreehandModifierPressed(false);
        }
    };
    const handleKeyUp = (e) => {
      if (e.key === 'Control' || e.key === 'Meta') setFreehandModifierPressed(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
        window.removeEventListener('keydown', handleKeyDown);
        window.removeEventListener('keyup', handleKeyUp);
    };
  }, [activePicker]);

  const updateElementFromDraft = (points) => {
      if (!activePicker) return;
      if (activePicker.context === 'layer') {
          const idx = activePicker.id;
          const newElements = [...builderElements];
          newElements[idx].value = JSON.stringify(points);
          setBuilderElements(newElements);
      } else if (isTerritoryPolygonPicker(activePicker.context)) {
          const parentId = parseInt(activePicker.context.replace('territory-', ''), 10);
          if (Number.isNaN(parentId)) return;
          const el = builderElements[parentId];
          if (!el || el.type !== 'flag' || !Array.isArray(el.value)) return;
          const partIndex = activePicker.id;
          const parts = [...el.value];
          if (partIndex < 0 || partIndex >= parts.length) return;
          const part = parts[partIndex];
          if (part && part.type === 'polygon') {
              parts[partIndex] = { ...part, value: JSON.stringify(points) };
              const newElements = [...builderElements];
              newElements[parentId] = { ...el, value: parts };
              setBuilderElements(newElements);
          }
      }
  };

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'mapViewUpdate') {
        const targetSet = activePreviewTab === 'picker' ? null : setBuilderOptions;
        if (targetSet) {
            targetSet(prev => ({
                ...prev,
                focus: [
                    parseFloat(event.data.center[0].toFixed(4)), 
                    parseFloat(event.data.center[1].toFixed(4))
                ],
                zoom: event.data.zoom
            }));
        }
      } else if (event.data && event.data.type === 'mapClick') {
          setLastMapClick({ lat: event.data.lat, lng: event.data.lng, ts: Date.now() });
      } else if (event.data && event.data.type === 'mapMouseDown') {
          setIsMouseDown(true);
          if (event.data.ctrlKey || event.data.metaKey) setFreehandModifierPressed(true);
      } else if (event.data && event.data.type === 'mapMouseUp') {
          setIsMouseDown(false);
          if (!event.data.ctrlKey && !event.data.metaKey) setFreehandModifierPressed(false);
      } else if (event.data && event.data.type === 'mapMouseMove') {
          const modifierPressed = !!(event.data.ctrlKey || event.data.metaKey || freehandModifierPressed);
          if (modifierPressed !== freehandModifierPressed) setFreehandModifierPressed(modifierPressed);
          if (activePicker && modifierPressed && isMouseDown && (activePicker.context === 'layer' || isTerritoryPolygonPicker(activePicker.context))) {
              const point = [parseFloat(event.data.lat.toFixed(4)), parseFloat(event.data.lng.toFixed(4))];
              setDraftPoints(prev => {
                  const last = prev[prev.length - 1];
                  if (last && Math.abs(last[0] - point[0]) < 0.0001 && Math.abs(last[1] - point[1]) < 0.0001) return prev;
                  const newPoints = [...prev, point];
                  updateElementFromDraft(newPoints);
                  return newPoints;
              });
          }
      } else if (event.data && event.data.type === 'mapKeyDown') {
          // Keys forwarded from map iframe (when user clicked map, focus is in iframe)
          const key = event.data.key;
          if (!activePicker) return;
          const isDraftPicker = activePicker.context === 'layer' || isTerritoryPolygonPicker(activePicker.context);
          if (key === 'Backspace' && isDraftPicker) {
            setDraftPoints(prev => {
              const newPoints = prev.slice(0, -1);
              updateElementFromDraft(newPoints);
              return newPoints;
            });
          } else if (key === 'Escape') {
            setActivePicker(null);
            setDraftPoints([]);
            setFreehandModifierPressed(false);
          } else if (key === 'Control' || key === 'Meta') {
            setFreehandModifierPressed(true);
          }
      } else if (event.data && event.data.type === 'mapKeyUp') {
          if (event.data.key === 'Control' || event.data.key === 'Meta') setFreehandModifierPressed(false);
      } else if (event.data && event.data.type === 'mapShortcut') {
          if (event.data.shortcut === 'updatePickerMap') {
            if (activePreviewTab === 'picker') {
              renderPickerMap();
            } else if (activePreviewTab === 'library') {
              renderTerritoryLibrary(territoryLibrarySource);
            }
          }
      } else if (event.data && event.data.type === 'mapFeaturePick') {
          const data = event.data || {};
          if (data.featureType === 'gadm' && data.gid && activePicker?.context === 'reference-gadm') {
              const gid = String(data.gid);
              if (data.hoverMode === 'add' || data.hoverMode === 'remove') {
                const sig = `${data.hoverMode}:${gid}`;
                if (hoverPickRef.current === sig) return;
                hoverPickRef.current = sig;
                setPickedGadmSelection((prev) => {
                  const exists = prev.some((x) => x.gid === gid);
                  if (data.hoverMode === 'add') {
                    return exists ? prev : [...prev, { gid, name: data.name || '' }];
                  }
                  return exists ? prev.filter((x) => x.gid !== gid) : prev;
                });
              } else {
                hoverPickRef.current = '';
                setPickedGadmSelection((prev) => {
                  const exists = prev.some((x) => x.gid === gid);
                  if (exists) return prev.filter((x) => x.gid !== gid);
                  return [...prev, { gid, name: data.name || '' }];
                });
              }
          } else if (data.featureType === 'river' && data.id && activePicker?.context === 'reference-river' && referencePickTarget?.kind === 'river') {
              const idx = referencePickTarget.layerIndex;
              if (idx != null) {
                setBuilderElements((prev) => {
                  const next = [...prev];
                  const el = next[idx];
                  if (!el || el.type !== 'river') return prev;
                  next[idx] = {
                    ...el,
                    value: String(data.id),
                    args: { ...(el.args || {}), source_type: data.source_type || 'naturalearth' }
                  };
                  return next;
                });
              }
              setActivePicker(null);
              setReferencePickTarget(null);
              setActivePreviewTab('main');
          } else if (data.featureType === 'territory' && data.name && activePicker?.context === 'territory-library' && referencePickTarget?.kind === 'territory') {
              const name = String(data.name);
              setPickedTerritorySelection((prev) => {
                const exists = prev.includes(name);
                if (exists) return prev.filter((x) => x !== name);
                return [...prev, name];
              });
          }
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [activePreviewTab, activePicker, freehandModifierPressed, isMouseDown, referencePickTarget, builderElements]);

  useEffect(() => {
    const uniqueCountries = Array.from(
      new Set(
        (pickerOptions.entries || [])
          .map((entry) => String(entry.country || '').trim().toUpperCase().split('.')[0])
          .filter(Boolean)
      )
    );
    if (uniqueCountries.length === 0) {
      setCountryLevelOptions({});
      return;
    }
    Promise.all(
      uniqueCountries.map(async (country) => {
        try {
          const res = await fetch(`http://localhost:8088/gadm/levels?country=${encodeURIComponent(country)}`);
          const levels = await res.json();
          return [country, Array.isArray(levels) && levels.length ? levels : [0, 1, 2, 3, 4]];
        } catch {
          return [country, [0, 1, 2, 3, 4]];
        }
      })
    ).then((pairs) => {
      const next = {};
      pairs.forEach(([country, levels]) => {
        next[country] = levels;
      });
      setCountryLevelOptions(next);
    });
  }, [pickerOptions.entries]);

  useEffect(() => {
    const ref = pickerIframeRef.current;
    if (!ref || !ref.contentWindow) return;
    const groups = [
      ...selectionBatches,
      ...(pickedGadmSelection.length ? [{ op: 'pending', gids: pickedGadmSelection.map((x) => x.gid) }] : []),
    ];
    ref.contentWindow.postMessage({ type: 'setSelectionOverlay', groups }, '*');
  }, [selectionBatches, pickedGadmSelection, pickerHtml]);

  useEffect(() => {
    const ref = territoryLibraryIframeRef.current;
    if (!ref || !ref.contentWindow) return;
    const groups = [
      ...selectionBatches,
      ...(pickedTerritorySelection.length ? [{ op: 'pending', names: pickedTerritorySelection }] : []),
    ];
    ref.contentWindow.postMessage({ type: 'setLabelSelectionOverlay', groups }, '*');
  }, [selectionBatches, pickedTerritorySelection, territoryLibraryHtml]);

  const getFlagOccurrenceInfo = (flagIndex) => {
    const target = builderElements[flagIndex];
    if (!target || target.type !== 'flag') return null;
    const label = target.label || '(unnamed)';
    let occurrence = 0;
    let count = 0;
    builderElements.forEach((el, idx) => {
      if (el.type !== 'flag' || (el.label || '(unnamed)') !== label) return;
      count += 1;
      if (idx <= flagIndex) occurrence = count;
    });
    return { label, occurrence, count };
  };

  const handleStartReferencePick = (target) => {
    if (!target || !target.kind) return;
    setReferencePickTarget(target);
    setPickedGadmSelection([]);
    setPickedTerritorySelection([]);
    setSelectionBatches([]);
    hoverPickRef.current = '';
    setDraftPoints([]);
    const isTerritoryPick = target.kind === 'territory';
    setActivePicker({
      id: target.layerIndex ?? target.flagIndex ?? 0,
      type: target.kind,
      context: isTerritoryPick ? 'territory-library' : (target.kind === 'river' ? 'reference-river' : 'reference-gadm'),
      target,
    });
    setActivePreviewTab(isTerritoryPick ? 'library' : 'picker');
    if (isTerritoryPick && !territoryLibraryHtml) {
      renderTerritoryLibrary(territoryLibrarySource);
    }
  };

  const normalizeFlagPartsForApply = (rawValue) => {
    if (Array.isArray(rawValue)) return [...rawValue];
    if (!rawValue) return [];
    return [{ op: 'union', type: 'gadm', value: rawValue }];
  };

  const isBlankTerritoryPart = (part, type) => (
    !!part &&
    part.type === type &&
    (part.value == null || String(part.value).trim() === '')
  );

  const applyPickedGadmsToTarget = (op) => {
    if (!pickedGadmSelection.length || referencePickTarget?.kind !== 'gadm') return;
    const targetFlagIndex = referencePickTarget.flagIndex;
    if (targetFlagIndex == null) return;
    const picked = pickedGadmSelection.filter((x) => x?.gid);
    if (!picked.length) return;
    setBuilderElements((prev) => {
      const next = [...prev];
      const target = next[targetFlagIndex];
      if (!target || target.type !== 'flag') return prev;
      const currentParts = normalizeFlagPartsForApply(target.value).filter((part) => !isBlankTerritoryPart(part, 'gadm'));
      picked.forEach((item) => {
        const nextOp = currentParts.length === 0 ? 'union' : op;
        currentParts.push({ op: nextOp, type: 'gadm', value: item.gid });
      });
      next[targetFlagIndex] = { ...target, value: currentParts };
      return next;
    });
    setSelectionBatches((prev) => [...prev, { op, gids: picked.map((x) => x.gid) }]);
    setPickedGadmSelection([]);
    hoverPickRef.current = '';
  };

  const applyPickedTerritoriesToTarget = (op) => {
    if (!pickedTerritorySelection.length || referencePickTarget?.kind !== 'territory') return;
    const targetFlagIndex = referencePickTarget.flagIndex;
    if (targetFlagIndex == null) return;
    const picked = pickedTerritorySelection.filter(Boolean);
    if (!picked.length) return;
    setBuilderElements((prev) => {
      const next = [...prev];
      const target = next[targetFlagIndex];
      if (!target || target.type !== 'flag') return prev;
      const currentParts = normalizeFlagPartsForApply(target.value).filter((part) => !isBlankTerritoryPart(part, 'predefined'));
      picked.forEach((name) => {
        const nextOp = currentParts.length === 0 ? 'union' : op;
        currentParts.push({ op: nextOp, type: 'predefined', value: name });
      });
      next[targetFlagIndex] = { ...target, value: currentParts };
      return next;
    });
    setSelectionBatches((prev) => [...prev, { op, names: picked }]);
    setPickedTerritorySelection([]);
  };

  const clearReferenceSelection = () => {
    setPickedGadmSelection([]);
    setPickedTerritorySelection([]);
    setSelectionBatches([]);
    hoverPickRef.current = '';
  };

  const toggleTerritoryName = (name) => {
    setSelectedTerritoryNames((prev) => (
      prev.includes(name) ? prev.filter((x) => x !== name) : [...prev, name]
    ));
  };

  const copySelectedTerritoryIndex = async () => {
    const payload = `__TERRITORY_INDEX__ = ${JSON.stringify(selectedTerritoryNames)}`;
    try {
      await navigator.clipboard.writeText(payload);
      setCopyIndexCopied(true);
      window.setTimeout(() => setCopyIndexCopied(false), 1400);
    } catch (err) {
      setError(`Failed to copy index list: ${err.message}`);
    }
  };

  useEffect(() => {
    if (!activePicker) {
      setReferencePickTarget(null);
      clearReferenceSelection();
      setFreehandModifierPressed(false);
    }
  }, [activePicker]);

  useEffect(() => {
    const onKeyDown = (e) => {
      const editableTarget = isEditableTarget(e.target);
      const lowerKey = String(e.key || '').toLowerCase();
      const isMeta = e.ctrlKey || e.metaKey;
      const allowPickerMapShortcutInInput = activeTab === 'builder' && isMeta && e.code === 'Space';
      if (editableTarget && !allowPickerMapShortcutInInput) return;
      if (e.key === '?') {
        e.preventDefault();
        setShowShortcutHelp((prev) => !prev);
      } else if (isMeta && e.key === '1') {
        e.preventDefault();
        handleTabChange('builder');
      } else if (isMeta && e.key === '2') {
        e.preventDefault();
        handleTabChange('code');
      } else if (isMeta && e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        handleStop(activePreviewTab);
      } else if (isMeta && e.key === 'Enter') {
        e.preventDefault();
        renderMap();
      } else if (isMeta && e.key === '3') {
        e.preventDefault();
        setActivePreviewTab('main');
      } else if (isMeta && e.key === '4') {
        e.preventDefault();
        setActivePreviewTab('picker');
      } else if (isMeta && e.key === '5') {
        e.preventDefault();
        setActivePreviewTab('library');
      } else if (isMeta && e.code === 'Space') {
        e.preventDefault();
        if (activePreviewTab === 'picker') {
          renderPickerMap();
        } else if (activePreviewTab === 'library') {
          renderTerritoryLibrary(territoryLibrarySource);
        }
      } else if (activeTab === 'builder' && isMeta && e.shiftKey) {
        const layerByKey = {
          f: 'flag',
          r: 'river',
          p: 'point',
          t: 'text',
          h: 'path',
          a: 'admin',
          d: 'dataframe',
          b: 'titlebox',
        };
        const layerType = layerByKey[lowerKey];
        if (layerType) {
          e.preventDefault();
          setAddLayerSignal({ type: layerType, nonce: Date.now() });
        }
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [activeTab, code, predefinedCode, builderElements, builderOptions, activePreviewTab, territoryLibrarySource]);

  const handleGetCurrentView = () => {
    const ref = activePreviewTab === 'picker' ? pickerIframeRef : activePreviewTab === 'library' ? territoryLibraryIframeRef : iframeRef;
    if (ref.current && ref.current.contentWindow) {
      ref.current.contentWindow.postMessage('getCurrentView', '*');
    }
  };

  const renderPickerMap = async ({ background = false, showLoading = true } = {}) => {
      if (showLoading) setLoadingByView((prev) => ({ ...prev, picker: true }));
      try {
          const payload = {
            ...pickerOptions,
            basemaps: builderOptions.basemaps || [],
          };
          const response = await fetch(`http://localhost:8088/render/picker`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          });
          const data = await response.json();
          if (data.html) setPickerHtml(data.html);
      } catch (err) {
          setError(err.message);
      } finally {
          if (showLoading) setLoadingByView((prev) => ({ ...prev, picker: false }));
      }
  };

  const loadTerritoryLibraryCatalog = async (source = territoryLibrarySource) => {
      try {
          const response = await fetch('http://localhost:8088/territory_library/catalog', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                source,
                predefined_code: predefinedCode || '',
              }),
          });
          const data = await response.json();
          if (!response.ok || data.error) {
              throw new Error(data.error || 'Failed to load territory catalog');
          }
          const names = Array.isArray(data.names) ? data.names : [];
          const indexNames = Array.isArray(data.index_names) ? data.index_names : [];
          setTerritoryLibraryNames(names);
          setSelectedTerritoryNames((prev) => {
            if (prev.length && prev.some((name) => names.includes(name))) {
              return prev.filter((name) => names.includes(name));
            }
            return indexNames.filter((name) => names.includes(name));
          });
      } catch (err) {
          setError(err.message);
      }
  };

  const renderTerritoryLibrary = async (
    source = territoryLibrarySource,
    { background = false, useDefaultSelection = false, showLoading = true } = {}
  ) => {
      if (showLoading) setLoadingByView((prev) => ({ ...prev, library: true }));
      try {
          const body = {
            source,
            predefined_code: predefinedCode || '',
            basemaps: builderOptions.basemaps || [],
          };
          if (!useDefaultSelection) {
            body.selected_names = selectedTerritoryNames;
          }
          const response = await fetch('http://localhost:8088/render/territory-library', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body),
          });
          const data = await response.json();
          if (data.error) {
              setError(data.error);
          } else if (data.html) {
              setTerritoryLibraryHtml(data.html);
              const names = Array.isArray(data.available_names) ? data.available_names : [];
              if (names.length) setTerritoryLibraryNames(names);
          }
      } catch (err) {
          setError(err.message);
      } finally {
          if (showLoading) setLoadingByView((prev) => ({ ...prev, library: false }));
      }
  };

  const renderMap = async () => {
    const taskType = activeTab === 'code' ? 'code' : 'builder';
    setActivePreviewTab('main');
    setMainRenderTask(taskType);
    setLoadingByView((prev) => ({ ...prev, main: true }));
    setError(null);
    try {
      const endpoint = activeTab === 'code' ? '/render/code' : '/render/builder';
      const body = activeTab === 'code' 
        ? { code } 
        : { elements: builderElements, options: builderOptions, predefined_code: predefinedCode || undefined };

      const response = await fetch(`http://localhost:8088${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        console.error(data.traceback);
      } else {
        setMapHtml(data.html);
        setMapPayload(data.payload);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingByView((prev) => ({ ...prev, main: false }));
      setMainRenderTask(null);
    }
  };

  const downloadFile = (content, filename, contentType) => {
    const a = document.createElement("a");
    const file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = filename;
    a.click();
  };

  const handleExportHtml = () => {
    if (mapHtml) downloadFile(mapHtml, "map.html", "text/html");
  };

  const handleExportJson = () => {
    if (mapPayload) downloadFile(JSON.stringify(mapPayload, null, 2), "map.json", "application/json");
  };

  const handleSaveProject = () => {
    const project = { elements: builderElements, options: builderOptions, predefinedCode };
    downloadFile(JSON.stringify(project, null, 2), "project.json", "application/json");
  };

  const handleLoadProject = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const project = JSON.parse(e.target.result);
          if (project.elements && project.options) {
             setBuilderElements(project.elements);
             setBuilderOptions(project.options);
             if (project.predefinedCode) setPredefinedCode(project.predefinedCode);
          }
        } catch (err) {
          setError("Failed to load project: " + err.message);
        }
      };
      reader.readAsText(file);
    }
    // Reset file input
    e.target.value = null;
  };

  const formatTerritory = (value) => {
      if (value == null || (Array.isArray(value) && value.length === 0)) return 'None';
      if (Array.isArray(value)) {
          const ops = { union: '|', difference: '-', intersection: '&' };
          const emitted = [];
          value.forEach((part) => {
              let pStr = '';
              if (part.type === 'gadm' && part.value != null && part.value !== '') pStr = `gadm("${part.value}")`;
              else if (part.type === 'polygon' && part.value != null && part.value !== '') pStr = `polygon(${part.value})`;
              else if (part.type === 'predefined' && part.value) pStr = part.value;
              else return;
              if (emitted.length === 0) emitted.push(pStr);
              else emitted.push(` ${ops[part.op] || '|'} ${pStr}`);
          });
          if (emitted.length === 0) return 'None';
          return emitted.join('');
      }
      if (value === '') return 'None';
      return `gadm("${value}")`;
  };

  const handleSaveTerritoryToLibrary = (element) => {
      const name = (element.label || '').replace(/\s+/g, '_');
      const terrStr = formatTerritory(element.value);
      setPredefinedCode(prev => prev + `\n${name} = ${terrStr}\n`);
      handleTabChange('code');
  };

  const generatePythonCode = () => {
    const needsIconImport = builderElements.some(el => el.type === 'point' && el.args?.icon);
    const hasFlagColorOptions = Array.isArray(builderOptions.flag_color_sequences) || !!builderOptions.flag_colors;
    const hasAdminColorOptions = Array.isArray(builderOptions.admin_color_sequences) || !!builderOptions.admin_colors;
    const needsColorSeqImport = hasFlagColorOptions || hasAdminColorOptions;
    const dataColormapOpt = (builderOptions.data_colormap && typeof builderOptions.data_colormap === 'object')
      ? builderOptions.data_colormap
      : (typeof builderOptions.data_colormap === 'string' && builderOptions.data_colormap
        ? { type: builderOptions.data_colormap, colors: 'yellow,orange,red' }
        : null);
    const needsPyplotImport = !!(dataColormapOpt && dataColormapOpt.type && dataColormapOpt.type !== 'LinearSegmented');
    const needsLinearSegmentedImport = !!(dataColormapOpt && dataColormapOpt.type === 'LinearSegmented');
    const pyVal = (v) => {
        if (v == null || v === '') return 'None';
        if (typeof v === 'boolean') return v ? 'True' : 'False';
        if (typeof v === 'string') return `"${v.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
        if (Array.isArray(v)) return JSON.stringify(v);
        return JSON.stringify(v).replace(/"/g, "'").replace(/null/g, 'None').replace(/true/g, 'True').replace(/false/g, 'False');
    };
    const colorSequenceExpr = (raw) => {
        if (typeof raw !== 'string') return null;
        const val = raw.trim();
        if (!val) return null;
        const namedColors = new Set(['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'brown', 'gray', 'black', 'white', 'pink', 'cyan', 'magenta', 'lime', 'teal', 'indigo', 'violet']);
        const parts = val
          .split(',')
          .map((p) => p.trim())
          .filter(Boolean)
          .map((p) => (
            p.startsWith('#')
              ? `Color.hex(${pyVal(p)})`
              : (namedColors.has(p.toLowerCase()) ? `Color.named(${pyVal(p.toLowerCase())})` : null)
          ));
        if (parts.length === 0 || parts.some((p) => p == null)) return null;
        return `[${parts.join(', ')}]`;
    };
    let lines = [
        'import xatra',
        'from xatra.loaders import gadm, naturalearth, polygon, overpass',
        ...(needsIconImport ? ['from xatra.icon import Icon', ''] : []),
        ...(needsColorSeqImport ? ['from xatra.colorseq import Color, LinearColorSequence', ''] : []),
        ...(needsPyplotImport ? ['import matplotlib.pyplot as plt', ''] : []),
        ...(needsLinearSegmentedImport ? ['from matplotlib.colors import LinearSegmentedColormap', ''] : []),
        '',
        predefinedCode,
        ''
    ];

    // Options
    if (builderOptions.basemaps) {
        builderOptions.basemaps.forEach(bm => {
            lines.push(`xatra.BaseOption("${bm.url_or_provider}", name="${bm.name || ''}", default=${bm.default ? 'True' : 'False'})`);
        });
    }

    if (builderOptions.zoom !== undefined && builderOptions.zoom !== null) {
        lines.push(`xatra.zoom(${builderOptions.zoom})`);
    }

    if (
      Array.isArray(builderOptions.focus) &&
      builderOptions.focus.length === 2 &&
      builderOptions.focus[0] != null &&
      builderOptions.focus[1] != null
    ) {
        lines.push(`xatra.focus(${builderOptions.focus[0]}, ${builderOptions.focus[1]})`);
    }

    if (builderOptions.css_rules) {
        let css = builderOptions.css_rules.map(r => `${r.selector} { ${r.style} }`).join('\n');
        if (css) lines.push(`xatra.CSS("""${css}""")`);
    }

    if (builderOptions.slider) {
        const { start, end, speed } = builderOptions.slider;
        lines.push(`xatra.slider(start=${start ?? 'None'}, end=${end ?? 'None'}, speed=${speed ?? 5.0})`);
    }

    if (Array.isArray(builderOptions.flag_color_sequences)) {
        builderOptions.flag_color_sequences.forEach((row) => {
            const className = (row?.class_name || '').trim();
            const stepH = Number.isFinite(Number(row?.step_h)) ? Number(row.step_h) : 1.6180339887;
            const stepS = Number.isFinite(Number(row?.step_s)) ? Number(row.step_s) : 0.0;
            const stepL = Number.isFinite(Number(row?.step_l)) ? Number(row.step_l) : 0.0;
            const colorsExpr = colorSequenceExpr(row?.colors || '') || 'None';
            const seqExpr = `LinearColorSequence(colors=${colorsExpr}, step=Color.hsl(${stepH}, ${stepS}, ${stepL}))`;
            if (className) lines.push(`xatra.FlagColorSequence(${seqExpr}, class_name=${pyVal(className)})`);
            else lines.push(`xatra.FlagColorSequence(${seqExpr})`);
        });
    } else if (builderOptions.flag_colors) {
        const colorsExpr = colorSequenceExpr(builderOptions.flag_colors) || 'None';
        lines.push(`xatra.FlagColorSequence(LinearColorSequence(colors=${colorsExpr}, step=Color.hsl(1.6180339887, 0.0, 0.0)))`);
    }

    if (Array.isArray(builderOptions.admin_color_sequences) && builderOptions.admin_color_sequences.length) {
        const row = builderOptions.admin_color_sequences[0];
        const stepH = Number.isFinite(Number(row?.step_h)) ? Number(row.step_h) : 1.6180339887;
        const stepS = Number.isFinite(Number(row?.step_s)) ? Number(row.step_s) : 0.0;
        const stepL = Number.isFinite(Number(row?.step_l)) ? Number(row.step_l) : 0.0;
        const colorsExpr = colorSequenceExpr(row?.colors || '') || 'None';
        const seqExpr = `LinearColorSequence(colors=${colorsExpr}, step=Color.hsl(${stepH}, ${stepS}, ${stepL}))`;
        lines.push(`xatra.AdminColorSequence(${seqExpr})`);
    } else if (builderOptions.admin_colors) {
        const colorsExpr = colorSequenceExpr(builderOptions.admin_colors) || 'None';
        lines.push(`xatra.AdminColorSequence(LinearColorSequence(colors=${colorsExpr}, step=Color.hsl(1.6180339887, 0.0, 0.0)))`);
    }

    if (dataColormapOpt && dataColormapOpt.type) {
        if (dataColormapOpt.type === 'LinearSegmented') {
            const colors = String(dataColormapOpt.colors || 'yellow,orange,red')
              .split(',')
              .map((x) => x.trim())
              .filter(Boolean)
              .map((c) => pyVal(c))
              .join(', ');
            lines.push(`xatra.DataColormap(LinearSegmentedColormap.from_list("custom_cmap", [${colors || '"yellow", "orange", "red"'}]))`);
        } else {
            lines.push(`xatra.DataColormap(plt.cm.${String(dataColormapOpt.type).replace(/[^A-Za-z0-9_]/g, '')})`);
        }
    }

    lines.push('');
    const argsEntries = (obj) => Object.entries(obj || {}).filter(([, v]) => {
        if (v == null || v === '') return false;
        if (Array.isArray(v) && v.length === 0) return false;
        return true;
    });
    const argsToStr = (args) => {
        const parts = argsEntries(args).map(([k, v]) => `${k}=${typeof v === 'string' ? pyVal(v) : pyVal(v)}`);
        return parts.length ? ', ' + parts.join(', ') : '';
    };

    // Elements
    const labelCapableTypes = new Set(['flag', 'river', 'point', 'text', 'path']);
    builderElements.forEach(el => {
        const args = { ...el.args };
        if (el.type === 'flag') delete args.parent;
        if (labelCapableTypes.has(el.type) && el.label != null && el.label !== '') args.label = el.label;
        const argsStr = argsToStr(args);

        if (el.type === 'flag') {
            lines.push(`xatra.Flag(value=${formatTerritory(el.value)}${argsStr})`);
        } else if (el.type === 'river') {
            const func = el.args?.source_type === 'overpass' ? 'overpass' : 'naturalearth';
            const riverArgs = { ...args };
            delete riverArgs.source_type;
            const riverArgsStrFormatted = argsToStr(riverArgs);
            const riverVal = (el.value != null && el.value !== '') ? `${func}("${String(el.value).replace(/"/g, '\\"')}")` : 'None';
            lines.push(`xatra.River(value=${riverVal}${riverArgsStrFormatted})`);
        } else if (el.type === 'point') {
            const pointArgs = { ...args };
            const iconVal = pointArgs.icon;
            delete pointArgs.icon;
            let pointArgsStr = argsToStr(pointArgs);
            let iconPy = '';
            if (iconVal != null && iconVal !== '') {
                if (typeof iconVal === 'string') {
                    iconPy = `icon=Icon.builtin("${iconVal}")`;
                } else if (iconVal.shape) {
                    const c = (iconVal.color || '#3388ff').replace(/'/g, "\\'");
                    iconPy = `icon=Icon.geometric("${iconVal.shape}", color="${c}", size=${iconVal.size ?? 24})`;
                } else if (iconVal.icon_url || iconVal.iconUrl) {
                    const url = (iconVal.icon_url || iconVal.iconUrl).replace(/"/g, '\\"');
                    iconPy = `icon=Icon(icon_url="${url}")`;
                }
            }
            if (iconPy) pointArgsStr = pointArgsStr ? `${pointArgsStr}, ${iconPy}` : `, ${iconPy}`;
            const pos = (el.value != null && el.value !== '') ? (Array.isArray(el.value) ? JSON.stringify(el.value) : el.value) : 'None';
            lines.push(`xatra.Point(position=${pos}${pointArgsStr})`);
        } else if (el.type === 'text') {
            const pos = (el.value != null && el.value !== '') ? (Array.isArray(el.value) ? JSON.stringify(el.value) : el.value) : 'None';
            lines.push(`xatra.Text(position=${pos}${argsStr})`);
        } else if (el.type === 'path') {
            const pathVal = (el.value != null && el.value !== '') ? (typeof el.value === 'string' ? el.value : JSON.stringify(el.value)) : 'None';
            lines.push(`xatra.Path(value=${pathVal}${argsStr})`);
        } else if (el.type === 'admin') {
            const gadmVal = (el.value != null && el.value !== '') ? `"${String(el.value).replace(/"/g, '\\"')}"` : 'None';
            lines.push(`xatra.Admin(gadm=${gadmVal}${argsStr})`);
        } else if (el.type === 'admin_rivers') {
            const sourcesVal = (el.value != null && el.value !== '') ? el.value : 'None';
            lines.push(`xatra.AdminRivers(sources=${typeof sourcesVal === 'object' ? JSON.stringify(sourcesVal) : sourcesVal}${argsStr})`);
        } else if (el.type === 'dataframe') {
            lines.push(`# DataFrame handling requires local CSV file or manual implementation in code mode`);
            lines.push(`import pandas as pd`);
            lines.push(`import io`);
            const csvContent = (el.value != null && el.value !== '') ? String(el.value).replace(/"""/g, '\\"\\"\\"') : '';
            lines.push(`df = pd.read_csv(io.StringIO("""${csvContent}"""))`);
            lines.push(`xatra.Dataframe(df${argsStr})`);
        } else if (el.type === 'titlebox') {
            const titleHtml = (el.value != null && el.value !== '') ? String(el.value).replace(/"""/g, '\\"\\"\\"') : '';
            lines.push(`xatra.TitleBox("""${titleHtml}"""${argsStr})`);
        }
    });

    setCode(lines.join('\n'));
  };

  const parseCodeToBuilder = async () => {
    const response = await fetch('http://localhost:8088/sync/code_to_builder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, predefined_code: predefinedCode }),
    });
    const data = await response.json();
    if (!response.ok || data.error) {
      throw new Error(data.error || 'Failed to parse code into Builder state');
    }
    return data;
  };

  const handleTabChange = async (nextTab) => {
    if (nextTab === activeTab) return;
    if (nextTab === 'code') {
      generatePythonCode();
      setActiveTab('code');
      return;
    }
    if (activeTab === 'code' && nextTab === 'builder') {
      try {
        const parsed = await parseCodeToBuilder();
        if (Array.isArray(parsed.elements)) setBuilderElements(parsed.elements);
        if (parsed.options && typeof parsed.options === 'object') setBuilderOptions(parsed.options);
        if (typeof parsed.predefined_code === 'string') setPredefinedCode(parsed.predefined_code);
      } catch (err) {
        setError(`Code → Builder sync failed: ${err.message}`);
        return;
      }
    }
    setActiveTab(nextTab);
  };

  const handleStop = async (view) => {
      const stopView = view || 'main';
      const mappedTaskTypes = (
        stopView === 'main'
          ? (mainRenderTask ? [mainRenderTask] : ['builder', 'code'])
          : (stopView === 'picker' ? ['picker'] : ['territory_library'])
      );
      setLoadingByView((prev) => ({ ...prev, [stopView]: false }));
      try {
          await fetch('http://localhost:8088/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_types: mappedTaskTypes }),
          });
      } catch (e) { console.error(e); }
      if (stopView === 'main') setMainRenderTask(null);
  };

  // Initial render
  useEffect(() => {
    renderMap();
  }, []);

  useEffect(() => {
    if (didPrefetchReferenceRef.current || !mapHtml) return;
    didPrefetchReferenceRef.current = true;
    renderPickerMap({ background: true, showLoading: true });
  }, [mapHtml]);

  useEffect(() => {
    if (didPrefetchTerritoryRef.current || !mapHtml) return;
    didPrefetchTerritoryRef.current = true;
    (async () => {
      await loadTerritoryLibraryCatalog('builtin');
      await renderTerritoryLibrary('builtin', { background: true, useDefaultSelection: true, showLoading: true });
    })();
  }, [mapHtml]);

  useEffect(() => {
    if (activePreviewTab !== 'library') return;
    loadTerritoryLibraryCatalog(territoryLibrarySource);
  }, [activePreviewTab, territoryLibrarySource, predefinedCode]);

  const filteredTerritoryNames = territoryLibraryNames.filter((name) => (
    !territorySearchTerm.trim() || name.toLowerCase().includes(territorySearchTerm.trim().toLowerCase())
  ));
  const mapTabBarClass = isDarkMode
    ? 'bg-slate-900/90 border-slate-700'
    : 'bg-white/90 border-gray-200';
  const mapTabInactiveClass = isDarkMode
    ? 'text-slate-300 hover:bg-slate-800'
    : 'text-gray-600 hover:bg-gray-100';
  const sidePanelClass = isDarkMode
    ? 'bg-slate-900/95 border-slate-700 text-slate-100'
    : 'bg-white/95 border-gray-200';
  const shortcutsToggleClass = isDarkMode
    ? 'bg-slate-900/95 border-slate-700 text-slate-300 hover:text-blue-300 hover:border-blue-500'
    : 'bg-white/95 border-gray-200 text-gray-600 hover:text-blue-700 hover:border-blue-300';
  const shortcutsPanelClass = isDarkMode
    ? 'bg-slate-900/95 border-slate-700 text-slate-200'
    : 'bg-white/95 border-gray-200 text-gray-700';

  return (
    <div className={`flex h-screen font-sans ${isDarkMode ? 'theme-dark bg-slate-950 text-slate-100' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <div className="w-1/3 min-w-[350px] max-w-[500px] flex flex-col bg-white border-r border-gray-200 shadow-md z-10">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2 lowercase">
                xatra
            </h1>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsDarkMode((prev) => !prev)}
                className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50"
                title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? <Sun size={16} className="text-amber-500" /> : <Moon size={16} className="text-gray-600" />}
              </button>
              <div className="flex bg-white rounded-lg border border-gray-300 p-0.5">
                <button 
                onClick={() => handleTabChange('builder')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'builder' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                <span className="flex items-center gap-1"><Layers size={16}/> Builder</span>
                </button>
                <button 
                onClick={() => handleTabChange('code')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'code' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                >
                <span className="flex items-center gap-1"><Code size={16}/> Code</span>
                </button>
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
             <label className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 cursor-pointer" title="Load Project">
                <Upload size={16} className="text-gray-600"/>
                <input type="file" className="hidden" accept=".json" onChange={handleLoadProject} />
             </label>
             <button onClick={handleSaveProject} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50" title="Save Project"><Save size={16} className="text-gray-600"/></button>
             <div className="h-auto w-px bg-gray-300 mx-1"></div>
             <button onClick={handleExportHtml} disabled={!mapHtml} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50" title="Export HTML"><FileCode size={16} className="text-gray-600"/></button>
             <button onClick={handleExportJson} disabled={!mapPayload} className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50" title="Export Map JSON"><FileJson size={16} className="text-gray-600"/></button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'builder' ? (
            <Builder 
              elements={builderElements} 
              setElements={setBuilderElements}
              options={builderOptions}
              setOptions={setBuilderOptions}
              onGetCurrentView={handleGetCurrentView}
              lastMapClick={lastMapClick}
              activePicker={activePicker}
              setActivePicker={setActivePicker}
              draftPoints={draftPoints}
              setDraftPoints={setDraftPoints}
              onSaveTerritory={handleSaveTerritoryToLibrary}
              predefinedCode={predefinedCode}
              onStartReferencePick={handleStartReferencePick}
              addLayerSignal={addLayerSignal}
            />
          ) : (
            <CodeEditor 
                code={code} setCode={setCode} 
                predefinedCode={predefinedCode} setPredefinedCode={setPredefinedCode}
                onSync={generatePythonCode}
            />
          )}
        </div>

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={renderMap}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2 transition-all"
          >
            <Play className="w-5 h-5 fill-current" /> Render Map
          </button>
          {error && (
            <div className="mt-3 p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200 overflow-auto max-h-32">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>
      </div>

      {/* Main Preview Area */}
      <div className={`flex-1 flex flex-col relative ${isDarkMode ? 'bg-slate-900' : 'bg-gray-200'}`}>
        <div className={`absolute top-4 left-1/2 transform -translate-x-1/2 z-20 flex backdrop-blur shadow-md rounded-full p-1 border ${mapTabBarClass}`}>
            <button 
                onClick={() => setActivePreviewTab('main')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${activePreviewTab === 'main' ? 'bg-blue-600 text-white shadow-sm' : mapTabInactiveClass}`}
            >
                Map Preview
            </button>
            <button 
                onClick={() => setActivePreviewTab('picker')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${activePreviewTab === 'picker' ? 'bg-blue-600 text-white shadow-sm' : mapTabInactiveClass}`}
            >
                Reference Map
            </button>
            <button 
                onClick={() => setActivePreviewTab('library')}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${activePreviewTab === 'library' ? 'bg-blue-600 text-white shadow-sm' : mapTabInactiveClass}`}
            >
                Territory Library
            </button>
        </div>

        {activePreviewTab === 'picker' && (
            <div className={`absolute top-16 right-4 z-20 w-72 backdrop-blur p-4 rounded-lg shadow-xl border space-y-4 max-h-[calc(100vh-100px)] overflow-y-auto overflow-x-hidden ${sidePanelClass}`}>
                <h3 className="text-sm font-bold text-gray-800 flex items-center gap-2 border-b pb-2">
                    Reference Map Options
                </h3>
                <div className="space-y-3">
                    <div className="space-y-2">
                         <div className="grid grid-cols-[1fr_64px_24px] gap-1.5 items-center">
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Countries</label>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider">Admin Level</label>
                            <div />
                         </div>
                         {pickerOptions.entries.map((entry, idx) => (
                             <div key={idx} className="flex gap-1.5 items-center">
                                 <AutocompleteInput 
                                     value={entry.country}
                                     endpoint="http://localhost:8088/search/gadm"
                                     onChange={(val) => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries[idx].country = val;
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     onSelectSuggestion={(item) => {
                                         const code = String(item.gid || item.country_code || item.country || '');
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries[idx].country = code;
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="w-32 text-xs p-1.5 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none font-mono"
                                     placeholder="e.g. IND.20"
                                 />
                                 <select
                                     value={entry.level}
                                     onChange={(e) => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries[idx].level = parseInt(e.target.value);
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="w-16 text-xs p-1.5 border rounded bg-white shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                 >
                                     {(countryLevelOptions[String(entry.country || '').toUpperCase().split('.')[0]] || [0, 1, 2, 3, 4]).map((level) => (
                                       <option key={level} value={level}>{level}</option>
                                     ))}
                                 </select>
                                 <button 
                                     onClick={() => {
                                         const newEntries = [...pickerOptions.entries];
                                         newEntries.splice(idx, 1);
                                         setPickerOptions({...pickerOptions, entries: newEntries});
                                     }}
                                     className="p-1.5 text-red-500 hover:bg-red-50 rounded flex-shrink-0"
                                 >
                                     <Trash2 size={12}/>
                                 </button>
                             </div>
                         ))}
                         <button 
                             onClick={() => setPickerOptions({...pickerOptions, entries: [...pickerOptions.entries, {country: '', level: 1}]})}
                             className="text-xs text-blue-600 flex items-center gap-1 font-medium hover:text-blue-800"
                         >
                             <Plus size={12}/> Add Country
                         </button>
                    </div>

                    <div className="flex items-center pb-2 pt-2 border-t border-gray-100">
                        <label className="flex items-center gap-2 text-xs font-medium text-gray-700 cursor-pointer">
                            <input 
                                type="checkbox"
                                checked={pickerOptions.adminRivers}
                                onChange={(e) => setPickerOptions({ ...pickerOptions, adminRivers: e.target.checked })}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            Show Admin Rivers
                        </label>
                    </div>

                    <button 
                        onClick={renderPickerMap}
                        disabled={loadingByView.picker}
                        className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded shadow transition-colors disabled:opacity-50"
                    >
                        Update Reference Map
                    </button>
                    <div className="space-y-2 border-t border-gray-100 pt-2 text-[11px]">
                        <div className="font-semibold text-gray-600">Reference Picker Target</div>
                        {referencePickTarget?.kind === 'gadm' && referencePickTarget.flagIndex != null ? (
                          <div className="text-[11px] text-gray-500">
                            {(() => {
                              const info = getFlagOccurrenceInfo(referencePickTarget.flagIndex);
                              if (!info) return 'No flag selected.';
                              return `Flag "${info.label}" #${info.occurrence}${info.count > 1 ? ` of ${info.count}` : ''}`;
                            })()}
                          </div>
                        ) : referencePickTarget?.kind === 'river' ? (
                          <div className="text-[11px] text-gray-500">
                            Picking river for layer #{(referencePickTarget.layerIndex ?? 0) + 1}
                          </div>
                        ) : (
                          <div className="text-gray-400 italic">Activate a pick button in Builder to target a layer.</div>
                        )}
                    </div>
                    <div className="space-y-2 border-t border-gray-100 pt-2 text-[11px]">
                        <div className="font-semibold text-gray-600">Selected GADM</div>
                        {pickedGadmSelection.length === 0 ? (
                          <div className="text-gray-400 italic">No selections yet.</div>
                        ) : (
                          <div className="flex flex-wrap gap-1">
                            {pickedGadmSelection.map((picked) => (
                              <span key={picked.gid} className="px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-700 font-mono">
                                {picked.gid}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className="flex gap-1.5">
                          <button
                            onClick={() => applyPickedGadmsToTarget('union')}
                            disabled={!pickedGadmSelection.length || referencePickTarget?.kind !== 'gadm'}
                            className="flex-1 py-1 px-2 text-[11px] bg-green-600 hover:bg-green-700 text-white rounded disabled:opacity-50"
                          >
                            + Add
                          </button>
                          <button
                            onClick={() => applyPickedGadmsToTarget('difference')}
                            disabled={!pickedGadmSelection.length || referencePickTarget?.kind !== 'gadm'}
                            className="flex-1 py-1 px-2 text-[11px] bg-rose-600 hover:bg-rose-700 text-white rounded disabled:opacity-50"
                          >
                            - Subtract
                          </button>
                          <button
                            onClick={() => applyPickedGadmsToTarget('intersection')}
                            disabled={!pickedGadmSelection.length || referencePickTarget?.kind !== 'gadm'}
                            className="flex-1 py-1 px-2 text-[11px] bg-indigo-600 hover:bg-indigo-700 text-white rounded disabled:opacity-50"
                          >
                            & Intersect
                          </button>
                          <button
                            onClick={clearReferenceSelection}
                            disabled={!pickedGadmSelection.length && selectionBatches.length === 0}
                            className="py-1 px-2 text-[11px] border rounded bg-white hover:bg-gray-50 disabled:opacity-50"
                          >
                            Clear
                          </button>
                        </div>
                    </div>
                </div>
                <div className="text-[10px] text-gray-400 bg-gray-50 p-2 rounded italic">
                    Tip: Click regions to toggle selection. Hold Ctrl/Cmd and move to paint-select, hold Alt and move to paint-unselect.
                </div>
            </div>
        )}
        {activePreviewTab === 'library' && (
            <div className={`absolute top-16 right-4 z-20 w-72 backdrop-blur p-4 rounded-lg shadow-xl border space-y-3 max-h-[calc(100vh-100px)] overflow-y-auto overflow-x-hidden ${sidePanelClass}`}>
                <h3 className="text-sm font-bold text-gray-800 border-b pb-2">Territory Library</h3>
                <div className="grid grid-cols-2 gap-1">
                    <button
                        onClick={() => {
                          setTerritoryLibrarySource('builtin');
                          setSelectedTerritoryNames([]);
                        }}
                        className={`py-1.5 px-2 text-xs rounded border ${territoryLibrarySource === 'builtin' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                    >
                        xatra.territory_library
                    </button>
                    <button
                        onClick={() => {
                          setTerritoryLibrarySource('custom');
                          setSelectedTerritoryNames([]);
                        }}
                        className={`py-1.5 px-2 text-xs rounded border ${territoryLibrarySource === 'custom' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                    >
                        Custom Library
                    </button>
                </div>
                <div className="space-y-2 border border-gray-200 rounded p-2 bg-gray-50">
                    <div className="flex items-center justify-between">
                        <div className="text-[11px] font-semibold text-gray-700">Territories to Render</div>
                        <button
                          onClick={copySelectedTerritoryIndex}
                          className={`p-1 border rounded bg-white transition-colors ${copyIndexCopied ? 'text-green-700 border-green-300 bg-green-50' : 'text-gray-600 hover:bg-gray-50'}`}
                          disabled={!selectedTerritoryNames.length}
                          title="Copy selected names as __TERRITORY_INDEX__"
                        >
                          {copyIndexCopied ? <Check size={12}/> : <Copy size={12}/>}
                        </button>
                    </div>
                    <div className="space-y-1">
                        <input
                          type="text"
                          value={territorySearchTerm}
                          onChange={(e) => setTerritorySearchTerm(e.target.value)}
                          className="w-full text-[11px] p-1.5 border rounded bg-white"
                          placeholder="Filter territories..."
                        />
                    </div>
                    <div className="max-h-40 overflow-y-auto space-y-1">
                        {territoryLibraryNames.length === 0 ? (
                          <div className="text-[10px] text-gray-400 italic">No territories found.</div>
                        ) : filteredTerritoryNames.length === 0 ? (
                          <div className="text-[10px] text-gray-400 italic">No matches for this search.</div>
                        ) : (
                          filteredTerritoryNames.map((name) => (
                            <label key={name} className="flex items-center gap-2 text-[11px] text-gray-700 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={selectedTerritoryNames.includes(name)}
                                onChange={() => toggleTerritoryName(name)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="font-mono">{name}</span>
                            </label>
                          ))
                        )}
                    </div>
                </div>
                <div className="space-y-2 border-t border-gray-100 pt-2 text-[11px]">
                    <div className="font-semibold text-gray-600">Picker Target</div>
                    {referencePickTarget?.kind === 'territory' && referencePickTarget.flagIndex != null ? (
                      <div className="text-gray-500">
                        {(() => {
                          const info = getFlagOccurrenceInfo(referencePickTarget.flagIndex);
                          if (!info) return 'No flag selected.';
                          return `Flag "${info.label}" #${info.occurrence}${info.count > 1 ? ` of ${info.count}` : ''}`;
                        })()}
                      </div>
                    ) : (
                      <div className="text-gray-400 italic">Activate a Territory Library pick button in Builder.</div>
                    )}
                    <div className="font-semibold text-gray-600">Picked Territories</div>
                    {pickedTerritorySelection.length === 0 ? (
                      <div className="text-gray-400 italic">No selections yet.</div>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {pickedTerritorySelection.map((name) => (
                          <span key={name} className="px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-700 font-mono">
                            {name}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="flex gap-1.5">
                      <button
                        onClick={() => applyPickedTerritoriesToTarget('union')}
                        disabled={!pickedTerritorySelection.length || referencePickTarget?.kind !== 'territory'}
                        className="flex-1 py-1 px-2 text-[11px] bg-green-600 hover:bg-green-700 text-white rounded disabled:opacity-50"
                      >
                        + Add
                      </button>
                      <button
                        onClick={() => applyPickedTerritoriesToTarget('difference')}
                        disabled={!pickedTerritorySelection.length || referencePickTarget?.kind !== 'territory'}
                        className="flex-1 py-1 px-2 text-[11px] bg-rose-600 hover:bg-rose-700 text-white rounded disabled:opacity-50"
                      >
                        - Subtract
                      </button>
                      <button
                        onClick={() => applyPickedTerritoriesToTarget('intersection')}
                        disabled={!pickedTerritorySelection.length || referencePickTarget?.kind !== 'territory'}
                        className="flex-1 py-1 px-2 text-[11px] bg-indigo-600 hover:bg-indigo-700 text-white rounded disabled:opacity-50"
                      >
                        & Intersect
                      </button>
                      <button
                        onClick={clearReferenceSelection}
                        disabled={!pickedTerritorySelection.length && selectionBatches.length === 0}
                        className="py-1 px-2 text-[11px] border rounded bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Clear
                      </button>
                    </div>
                </div>
                <button 
                    onClick={() => renderTerritoryLibrary(territoryLibrarySource)}
                    disabled={loadingByView.library}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded shadow transition-colors disabled:opacity-50"
                >
                    Update Territory Library Map
                </button>
            </div>
        )}

        <div className="flex-1 overflow-hidden relative">
            <button
                type="button"
                onClick={() => setShowShortcutHelp((prev) => !prev)}
                className={`absolute top-4 right-4 z-40 rounded-full shadow p-2 border ${shortcutsToggleClass}`}
                title="Toggle keyboard shortcuts"
            >
                <Keyboard size={16} />
            </button>
            {showShortcutHelp && (
                <div className={`absolute top-16 right-4 z-40 rounded-lg shadow-lg p-3 text-xs w-64 border ${shortcutsPanelClass}`}>
                    <div className="font-semibold text-gray-800 mb-2">Shortcuts</div>
                    <div>`?` toggle this panel</div>
                    <div>`Ctrl/Cmd+1` Builder tab</div>
                    <div>`Ctrl/Cmd+2` Code tab</div>
                    <div>`Ctrl/Cmd+3` Map Preview</div>
                    <div>`Ctrl/Cmd+4` Reference Map</div>
                    <div>`Ctrl/Cmd+5` Territory Library</div>
                    <div>`Ctrl/Cmd+Enter` Render map</div>
                    <div>`Ctrl/Cmd+Shift+Enter` Stop active preview generation</div>
                    <div>`Ctrl/Cmd+Space` Update active picker map tab</div>
                    <div className="mt-2 pt-2 border-t border-gray-200">`Ctrl/Cmd+Shift+F` add Flag</div>
                    <div>`Ctrl/Cmd+Shift+R` add River</div>
                    <div>`Ctrl/Cmd+Shift+P` add Point</div>
                    <div>`Ctrl/Cmd+Shift+T` add Text</div>
                    <div>`Ctrl/Cmd+Shift+H` add Path</div>
                    <div>`Ctrl/Cmd+Shift+A` add Admin</div>
                    <div>`Ctrl/Cmd+Shift+D` add Data</div>
                    <div>`Ctrl/Cmd+Shift+B` add TitleBox</div>
                </div>
            )}
            {activePicker && (activePicker.context === 'layer' || isTerritoryPolygonPicker(activePicker.context)) && (
                <div className="absolute inset-0 z-30 pointer-events-none flex items-center justify-center">
                    <div className="bg-amber-500 text-white px-6 py-4 rounded-lg shadow-2xl border-2 border-amber-600 font-semibold text-center max-w-md animate-pulse">
                        <div className="text-sm mb-1">Click map to add points</div>
                        <div className="text-xs font-normal opacity-95">
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Backspace</kbd> undo last point
                            {' · '}
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Ctrl/Cmd</kbd> hold + drag for freehand
                            {' · '}
                            <kbd className="bg-amber-600 px-1.5 py-0.5 rounded">Esc</kbd> cancel
                        </div>
                    </div>
                </div>
            )}
            {activePreviewTab === 'main' ? (
                <MapPreview html={mapHtml} loading={loadingByView.main} iframeRef={iframeRef} onStop={() => handleStop('main')} />
            ) : activePreviewTab === 'picker' ? (
                <MapPreview html={pickerHtml} loading={loadingByView.picker} iframeRef={pickerIframeRef} onStop={() => handleStop('picker')} />
            ) : (
                <MapPreview html={territoryLibraryHtml} loading={loadingByView.library} iframeRef={territoryLibraryIframeRef} onStop={() => handleStop('library')} />
            )}
        </div>
      </div>
    </div>
  );
}

export default App;
