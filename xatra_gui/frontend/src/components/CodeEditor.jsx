import React, { useRef, useCallback, useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import Editor from '@monaco-editor/react';

const XATRA_COMPLETIONS = {
  globals: [
    { label: 'xatra', kind: 'module', insertText: 'xatra', detail: 'Main map library' },
    { label: 'gadm', kind: 'function', insertText: 'gadm("${1:IND}")', insertTextRules: 4, detail: 'GADM territory by code' },
    { label: 'naturalearth', kind: 'function', insertText: 'naturalearth("${1:id}")', insertTextRules: 4, detail: 'Natural Earth river/feature' },
    { label: 'overpass', kind: 'function', insertText: 'overpass("${1:id}")', insertTextRules: 4, detail: 'Overpass/OSM feature' },
    { label: 'polygon', kind: 'function', insertText: 'polygon(${1:[[lat,lon],...]})', insertTextRules: 4, detail: 'Polygon from coordinates' },
    { label: 'Icon', kind: 'class', insertText: 'Icon', detail: 'from xatra.icon import Icon' },
  ],
  xatraMethods: [
    { label: 'Flag', insertText: 'Flag(label="${1:}", value=${2:gadm("IND")})', insertTextRules: 4 },
    { label: 'River', insertText: 'River(value=${1:naturalearth("id")})', insertTextRules: 4 },
    { label: 'Path', insertText: 'Path(label="${1:}", value=${2:[[28,77],[19,73]]})', insertTextRules: 4 },
    { label: 'Point', insertText: 'Point(label="${1:}", position=${2:[28.6, 77.2]})', insertTextRules: 4 },
    { label: 'Text', insertText: 'Text(label="${1:}", position=${2:[28.6, 77.2]})', insertTextRules: 4 },
    { label: 'Admin', insertText: 'Admin(gadm="${1:IND}", level=${2:1})', insertTextRules: 4 },
    { label: 'AdminRivers', insertText: 'AdminRivers(sources=${1:["naturalearth"]})', insertTextRules: 4 },
    { label: 'Dataframe', insertText: 'Dataframe(${1:df})', insertTextRules: 4 },
    { label: 'BaseOption', insertText: 'BaseOption("${1:Esri.WorldTopoMap}", default=${2:True})', insertTextRules: 4 },
    { label: 'TitleBox', insertText: 'TitleBox("${1:<b>Title</b>}")', insertTextRules: 4 },
    { label: 'CSS', insertText: 'CSS("""${1:.flag { } }""")', insertTextRules: 4 },
    { label: 'zoom', insertText: 'zoom(${1:4})', insertTextRules: 4 },
    { label: 'focus', insertText: 'focus(${1:20}, ${2:78})', insertTextRules: 4 },
    { label: 'slider', insertText: 'slider(${1:-500}, ${2:500})', insertTextRules: 4 },
    { label: 'FlagColorSequence', insertText: 'FlagColorSequence(${1:})', insertTextRules: 4 },
    { label: 'AdminColorSequence', insertText: 'AdminColorSequence(${1:})', insertTextRules: 4 },
    { label: 'DataColormap', insertText: 'DataColormap(${1:})', insertTextRules: 4 },
    { label: 'show', insertText: 'show()', insertTextRules: 4 },
  ],
};

const CodeEditor = ({ code, setCode, predefinedCode, setPredefinedCode, onSync }) => {
  const editorRef = useRef(null);
  const predefinedEditorRef = useRef(null);
  const activeEditorRef = useRef('map');
  const completionDisposableRef = useRef(null);

  const handleEditorDidMount = useCallback((editor, monaco) => {
    editorRef.current = editor;
    editor.onDidFocusEditorText(() => {
      activeEditorRef.current = 'map';
    });
    monaco.editor.defineTheme('xatra-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: { 'editor.background': '#2d2d2d' },
    });
    monaco.editor.setTheme('xatra-dark');

    // Dispose any previous provider so tab switching doesn't duplicate suggestions
    if (completionDisposableRef.current) {
      completionDisposableRef.current.dispose();
      completionDisposableRef.current = null;
    }

    completionDisposableRef.current = monaco.languages.registerCompletionItemProvider('python', {
      triggerCharacters: ['.', '('],
      provideCompletionItems: (model, position) => {
        const textUntilPosition = model.getValueInRange({ startLineNumber: 1, startColumn: 1, endLineNumber: position.lineNumber, endColumn: position.column });
        const word = model.getWordUntilPosition(position);
        const linePrefix = textUntilPosition.slice(-80);

        const items = [];
        if (linePrefix.endsWith('xatra.')) {
          XATRA_COMPLETIONS.xatraMethods.forEach((m) => {
            items.push({
              label: m.label,
              kind: monaco.languages.CompletionItemKind.Method,
              insertText: m.insertText,
              insertTextRules: m.insertTextRules ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
            });
          });
        } else {
          XATRA_COMPLETIONS.globals.forEach((g) => {
            if (!word.word || g.label.toLowerCase().startsWith(word.word.toLowerCase())) {
              items.push({
                label: g.label,
                kind: g.kind === 'module' ? monaco.languages.CompletionItemKind.Module : monaco.languages.CompletionItemKind.Function,
                insertText: g.insertText,
                insertTextRules: g.insertTextRules ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
                detail: g.detail,
              });
            }
          });
        }
        return { suggestions: items };
      },
    });
  }, []);

  // Dispose completion provider on unmount to avoid duplicate registrations when switching tabs
  React.useEffect(() => {
    return () => {
      if (completionDisposableRef.current) {
        completionDisposableRef.current.dispose();
        completionDisposableRef.current = null;
      }
    };
  }, []);

  const handlePredefinedMount = useCallback((editor) => {
    predefinedEditorRef.current = editor;
    editor.onDidFocusEditorText(() => {
      activeEditorRef.current = 'predefined';
    });
  }, []);

  const mapCodeContainerRef = useRef(null);
  const predefinedCodeContainerRef = useRef(null);
  const [mapCodeHeight, setMapCodeHeight] = useState(420);
  const [predefinedCodeHeight, setPredefinedCodeHeight] = useState(200);

  useEffect(() => {
    const el = mapCodeContainerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const h = el.clientHeight;
      if (h > 100) setMapCodeHeight(h);
    });
    ro.observe(el);
    setMapCodeHeight(el.clientHeight > 100 ? el.clientHeight : 420);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const el = predefinedCodeContainerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const h = el.clientHeight;
      if (h > 80) setPredefinedCodeHeight(h);
    });
    ro.observe(el);
    setPredefinedCodeHeight(el.clientHeight > 80 ? el.clientHeight : 200);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const onKeyDown = (e) => {
      const isMac = navigator.platform.toUpperCase().includes('MAC');
      const mod = isMac ? e.metaKey : e.ctrlKey;
      if (!mod || !e.altKey || String(e.key).toLowerCase() !== 'i') return;
      e.preventDefault();
      if (activeEditorRef.current === 'predefined' && predefinedEditorRef.current) {
        predefinedEditorRef.current.focus();
      } else if (editorRef.current) {
        editorRef.current.focus();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  return (
    <div className="h-full flex flex-col space-y-4 min-h-0">
      <div className="bg-red-600 text-white border border-red-700 rounded-md px-3 py-2 text-xs font-semibold">
        If you are using <b>Vimium</b>, please DISABLE it on this website.
      </div>
      <div className="flex flex-col flex-1 min-h-[120px] min-h-0 overflow-hidden">
        <div className="flex justify-between items-center mb-2 flex-shrink-0">
          <label className="block text-sm font-medium text-gray-700">Territory library</label>
        </div>
        <div ref={predefinedCodeContainerRef} className="flex-1 border border-gray-700 rounded-md overflow-hidden min-h-[120px] flex flex-col">
          <Editor
            height={predefinedCodeHeight}
            defaultLanguage="python"
            value={predefinedCode || ''}
            onChange={(v) => setPredefinedCode(v ?? '')}
            onMount={handlePredefinedMount}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              wordWrap: 'on',
            }}
          />
        </div>
      </div>

      <div className="flex flex-col flex-[2] min-h-[200px] flex-1 min-h-0 overflow-hidden">
        <div className="flex justify-between items-center mb-2 flex-shrink-0">
          <label className="block text-sm font-medium text-gray-700">Map Code</label>
          <button
            onClick={onSync}
            className="flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded hover:bg-blue-100 transition-colors"
            title="Generate code from Builder state"
          >
            <RefreshCw size={12} /> Sync from Builder
          </button>
        </div>
        <div ref={mapCodeContainerRef} className="flex-1 border border-gray-700 rounded-md overflow-hidden min-h-[320px] flex flex-col">
          <Editor
            height={mapCodeHeight}
            defaultLanguage="python"
            value={code || ''}
            onChange={(v) => setCode(v ?? '')}
            onMount={handleEditorDidMount}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              wordWrap: 'on',
            }}
          />
        </div>
      </div>

      <div className="p-2 bg-gray-50 border rounded space-y-1">
        <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Editor</p>
        <p className="text-xs text-gray-600">
          Type <kbd className="px-1 bg-gray-200 rounded">xatra.</kbd> for map methods. Use <kbd className="px-1 bg-gray-200 rounded">Ctrl+Space</kbd> for suggestions.
        </p>
        <p className="text-xs text-gray-600">
          Focus active editor: <kbd className="px-1 bg-gray-200 rounded">Ctrl/Cmd+Alt+I</kbd>
        </p>
      </div>
    </div>
  );
};

export default CodeEditor;
