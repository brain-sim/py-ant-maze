import { useState, useEffect, useRef } from "react";
import { getPyodide, parseMaze, formatMaze, updateMaze, resizeMaze, addElement, type MazeData } from "./lib/pyodide";
import { MazeGrid, generateColorStyle } from "./components/MazeGrid";
import { Download, Upload, Play, FileText, AlertCircle, RefreshCw, Grid3X3, Code, Plus, Image as ImageIcon } from "lucide-react";
import { toPng } from 'html-to-image';

const DEFAULT_YAML = `maze_type: occupancy_grid
config:
  cell_elements:
    - name: wall
      token: "#"
    - name: open
      token: "."
layout:
  grid: |
    ___ 0 1 2 3 4 5 6 7
    0 | # # # # # # # #
    1 | # . . . . . . #
    2 | # . # # # # . #
    3 | # . # . . # . #
    4 | # . # . . # . #
    5 | # . # # # # . #
    6 | # . . . . . . #
    7 | # # # # # # # #
`;

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState(DEFAULT_YAML);
  const [mazeData, setMazeData] = useState<MazeData | null>(null);
  const [selectedElementValue, setSelectedElementValue] = useState<number>(1);
  const [showCode, setShowCode] = useState(true);
  const [newElementName, setNewElementName] = useState("");
  const [newElementToken, setNewElementToken] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getPyodide()
      .then(() => {
        setLoading(false);
        handleParse(DEFAULT_YAML);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load Pyodide: " + err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore typing in input fields
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return;
      }

      if (mazeData) {
        // Find element matching the key
        const element = mazeData.elements.find(el => el.token === e.key);
        if (element) {
          setSelectedElementValue(element.value);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mazeData]);

  const handleParse = async (yaml: string) => {
    try {
      const { data } = await parseMaze(yaml);
      setMazeData(data);
      setError(null);
    } catch (err: any) {
      setError(err.toString());
      setMazeData(null);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const handleParseClick = () => handleParse(input);

  const handleFormat = async () => {
    try {
      const result = await formatMaze(input);
      setInput(result);
      await handleParse(result);
      setError(null);
    } catch (err: any) {
      setError(err.toString());
    }
  };

  const handleCellClick = async (row: number, col: number) => {
    if (!mazeData) return;
    // Optimization: Skip if value is already the same
    if (mazeData.grid[row][col] === selectedElementValue) return;

    try {
      const { text, data } = await updateMaze(input, row, col, selectedElementValue);
      setInput(text);
      setMazeData(data);
      setError(null);
    } catch (err: any) {
      setError(err.toString());
    }
  };

  const handleResize = async (rows: number, cols: number) => {
    if (!mazeData) return;
    try {
      const { text, data } = await resizeMaze(input, rows, cols, selectedElementValue);
      setInput(text);
      setMazeData(data);
      setError(null);
    } catch (err: any) {
      setError(err.toString());
    }
  };

  const handleAddElement = async () => {
    if (!mazeData || !newElementName || !newElementToken) return;
    if (newElementToken.length !== 1) {
      setError("Token must be a single character");
      return;
    }

    try {
      const { text, data } = await addElement(input, newElementName, newElementToken);
      setInput(text);
      setMazeData(data);
      setNewElementName("");
      setNewElementToken("");
      setError(null);
    } catch (err: any) {
      setError(err.toString());
    }
  };

  const handleDownload = () => {
    const blob = new Blob([input], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "maze.yaml";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportImage = async () => {
    if (!gridRef.current) return;
    try {
      const dataUrl = await toPng(gridRef.current, { cacheBust: true, backgroundColor: '#1e293b' }); // slate-800
      const link = document.createElement('a');
      link.download = 'maze-layout.png';
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Failed to export image:', err);
      setError("Failed to export image");
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const content = ev.target?.result as string;
      setInput(content);
      handleParse(content);
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  if (loading)
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-6 text-white">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-purple-500/30 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-purple-400 rounded-full animate-spin"></div>
          </div>
          <div className="text-lg font-medium">Loading Maze Editor...</div>
          <div className="text-sm text-purple-300/70">Initializing Python runtime</div>
        </div>
      </div>
    );

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
      {/* Header */}
      <header className="shrink-0 bg-black/30 backdrop-blur-sm border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
              <Grid3X3 size={20} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Maze Editor</h1>
              <p className="text-xs text-slate-400">Visual maze configuration tool</p>
            </div>
          </div>

          <div className="flex items-center gap-4">


            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span className="text-xs font-medium text-emerald-300">Pyodide Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden min-h-0">
        {/* Code Panel - Collapsible */}
        <div
          className={`shrink-0 flex flex-col bg-slate-900/50 border-r border-white/10 transition-all duration-300 ${showCode ? "w-1/3 min-w-0" : "w-0"
            } overflow-hidden`}
        >
          {/* Code Header */}
          <div className="shrink-0 p-4 border-b border-white/10 bg-black/20 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-300">
                <FileText size={16} />
                <span className="font-medium text-sm">YAML Configuration</span>
              </div>
              <div className="flex items-center gap-1">
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".yaml,.yml"
                  onChange={handleFileChange}
                />
                <button
                  onClick={handleUploadClick}
                  className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  title="Import YAML"
                >
                  <Upload size={16} />
                </button>
                <button
                  onClick={handleDownload}
                  className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  title="Export YAML"
                >
                  <Download size={16} />
                </button>
                <button
                  onClick={handleExportImage}
                  className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                  title="Export as Image"
                >
                  <ImageIcon size={16} />
                </button>
              </div>
            </div>

            {/* Resize Controls */}
            {mazeData && (
              <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Grid Size:</span>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">Rows</span>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={mazeData.grid.length}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (val > 0) handleResize(val, mazeData.grid[0]?.length || 0);
                      }}
                      className="w-12 bg-black/40 border border-white/10 rounded px-1.5 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors"
                    />
                  </div>
                  <span className="text-slate-600">×</span>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">Cols</span>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={mazeData.grid[0]?.length || 0}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (val > 0) handleResize(mazeData.grid.length, val);
                      }}
                      className="w-12 bg-black/40 border border-white/10 rounded px-1.5 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Add Element Controls */}
            {mazeData && (
              <div className="flex flex-col gap-2 bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Add Element:</span>
                <div className="flex items-center gap-2">
                  <div className="flex-1 min-w-0">
                    <input
                      type="text"
                      placeholder="Name (e.g. Water)"
                      value={newElementName}
                      onChange={(e) => setNewElementName(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded px-2 py-1 text-xs focus:outline-none focus:border-purple-500 transition-colors placeholder:text-slate-600"
                    />
                  </div>
                  <div className="w-12 shrink-0">
                    <input
                      type="text"
                      placeholder="Char"
                      maxLength={1}
                      value={newElementToken}
                      onChange={(e) => setNewElementToken(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded px-2 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors placeholder:text-slate-600"
                    />
                  </div>
                  <button
                    onClick={handleAddElement}
                    disabled={!newElementName || newElementToken.length !== 1}
                    className="shrink-0 p-1 rounded bg-purple-500/20 text-purple-400 hover:bg-purple-500 hover:text-white border border-purple-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Add Element"
                  >
                    <Plus size={14} />
                  </button>
                </div>
              </div>
            )}


          </div>

          {/* Code Editor */}
          <div className="flex-1 relative min-h-0">
            <textarea
              className="absolute inset-0 w-full h-full p-4 resize-none bg-transparent text-slate-300 font-mono text-xs leading-relaxed focus:outline-none"
              value={input}
              onChange={handleInputChange}
              spellCheck={false}
              style={{ tabSize: 2 }}
            />
          </div>



          {/* Code Footer */}
          <div className="shrink-0 p-4 border-t border-white/10 bg-black/20 z-10">
            <div className="flex gap-2">
              <button
                onClick={handleFormat}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 border border-slate-600/50 text-sm font-medium transition-colors"
              >
                <RefreshCw size={14} />
                Format
              </button>
              <button
                onClick={handleParseClick}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-sm font-medium transition-all shadow-lg shadow-purple-500/25"
              >
                <Play size={14} />
                Sync to Grid
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="shrink-0 p-3 bg-red-500/10 border-t border-red-500/30 max-h-32 overflow-auto">
              <div className="flex gap-2 text-red-400 text-xs">
                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                <pre className="whitespace-pre-wrap font-mono">{error}</pre>
              </div>
            </div>
          )}
        </div>

        {/* Toggle Code Panel Button */}
        <button
          onClick={() => setShowCode(!showCode)}
          className="shrink-0 w-6 flex items-center justify-center bg-slate-800/50 hover:bg-slate-700/50 border-r border-white/10 transition-colors group z-10"
          title={showCode ? "Hide code" : "Show code"}
        >
          <Code size={14} className={`text-slate-500 group-hover:text-white transition-all ${showCode ? "" : "rotate-180"}`} />
        </button>

        {/* Visual Editor */}
        <div className="flex-1 flex flex-col min-w-0 bg-slate-900 overflow-hidden relative">
          {mazeData ? (
            <>
              {/* Toolbar */}
              <div className="shrink-0 p-4 bg-black/20 border-b border-white/10 overflow-x-auto">
                <div className="flex items-center gap-2 flex-nowrap min-w-max">
                  <span className="text-xs text-slate-400 mr-2">Elements:</span>
                  {mazeData.elements.map((el) => {
                    const { className: colorClass, style: colorStyle } = generateColorStyle(el.name);
                    const isSelected = selectedElementValue === el.value;

                    return (
                      <button
                        key={el.value}
                        onClick={() => setSelectedElementValue(el.value)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 shrink-0 border ${isSelected
                          ? "ring-2 ring-white ring-offset-2 ring-offset-slate-900 border-transparent text-white"
                          : "border-slate-600/50 text-slate-300 hover:border-slate-500 opacity-80 hover:opacity-100"
                          } ${colorClass || ''}`}
                        style={{
                          ...(!colorClass ? colorStyle : undefined),
                          ...(colorStyle?.color ? { color: colorStyle.color } : {})
                        }}
                      >
                        <span className="w-5 h-5 rounded bg-black/20 flex items-center justify-center font-mono text-xs shadow-inner">
                          {el.token}
                        </span>
                        <span className="font-bold">{el.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Grid Area */}
              <div className="flex-1 overflow-auto p-4 md:p-8 flex items-center justify-center bg-dot-pattern">
                <div
                  ref={gridRef}
                  className="max-w-full max-h-full overflow-auto bg-slate-800/50 p-2 rounded-2xl shadow-2xl border border-white/10 backdrop-blur-sm"
                >
                  <MazeGrid data={mazeData} onCellClick={handleCellClick} />
                </div>
              </div>

              {/* Footer Hint */}
              <div className="shrink-0 px-4 py-2 text-center text-xs text-slate-500 border-t border-white/5 bg-slate-900/80">
                Click cells to paint • Grid: {mazeData.grid.length} × {mazeData.grid[0]?.length || 0}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-4 p-4 text-center">
              <AlertCircle size={48} className="opacity-30" />
              <p>Parse a valid YAML configuration to enable the visual editor</p>
            </div>
          )}
        </div>
      </main >
    </div >
  );
}

export default App;
