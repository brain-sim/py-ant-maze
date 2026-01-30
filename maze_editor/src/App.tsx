/**
 * Main App Component
 * 
 * Orchestrates the maze editor application using modular components and hooks.
 */

import { useState, useCallback } from 'react';
import { Code } from 'lucide-react';
import { useMaze, useFileOperations, useKeyboardShortcuts } from './hooks';
import { Header, LoadingScreen } from './components/layout';
import { CodePanel, VisualEditor } from './components/editor';

function App() {
  const [showCode, setShowCode] = useState(true);

  // Maze state and operations
  const maze = useMaze();

  // File operations
  const handleFileLoaded = useCallback((content: string) => {
    maze.setInput(content);
    // Parse will be triggered by the next user action or can be called explicitly
    maze.parse();
  }, [maze]);

  const fileOps = useFileOperations({
    input: maze.input,
    onFileLoaded: handleFileLoaded,
    onError: (err) => console.error(err),
  });

  // Keyboard shortcuts for element selection
  useKeyboardShortcuts({
    cellElements: maze.mazeData?.elements || [],
    wallElements: maze.mazeData?.wall_elements || [],
    selectedLayer: maze.selectedLayer,
    onCellElementSelect: maze.setSelectedElementValue,
    onWallElementSelect: maze.setSelectedWallElementValue,
    enabled: !!maze.mazeData,
  });

  // Loading state
  if (maze.loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white overflow-hidden">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden min-h-0">
        {/* Code Panel - Collapsible */}
        <div
          className={`shrink-0 flex flex-col bg-slate-900/50 border-r border-white/10 transition-all duration-300 ${showCode ? "w-1/3 min-w-0" : "w-0"
            } overflow-hidden`}
        >
          <CodePanel
            input={maze.input}
            onInputChange={maze.setInput}
            mazeData={maze.mazeData}
            onFormat={maze.format}
            onParse={maze.parse}
            onCreate={maze.create}
            onResize={maze.resize}
            onAddElement={maze.addNewElement}
            selectedLayer={maze.selectedLayer}
            onLayerChange={maze.setSelectedLayer}
            error={maze.error}
            fileInputRef={fileOps.fileInputRef}
            onFileChange={fileOps.handleFileChange}
            onUploadClick={fileOps.triggerUpload}
            onDownload={fileOps.downloadYaml}
            onExportImage={fileOps.exportImage}
          />
        </div>

        {/* Toggle Code Panel Button */}
        <button
          onClick={() => setShowCode(!showCode)}
          className="shrink-0 w-6 flex items-center justify-center bg-slate-800/50 hover:bg-slate-700/50 border-r border-white/10 transition-colors group z-10"
          title={showCode ? "Hide code" : "Show code"}
        >
          <Code
            size={14}
            className={`text-slate-500 group-hover:text-white transition-all ${showCode ? "" : "rotate-180"
              }`}
          />
        </button>

        {/* Visual Editor */}
        <div className="flex-1 flex flex-col min-w-0 bg-slate-900 overflow-hidden relative">
          <VisualEditor
            mazeData={maze.mazeData}
            onCellClick={maze.updateCell}
            onWallClick={maze.updateWall}
            selectedLayer={maze.selectedLayer}
            onLayerChange={maze.setSelectedLayer}
            selectedElementValue={maze.selectedElementValue}
            onSelectElement={maze.setSelectedElementValue}
            selectedWallElementValue={maze.selectedWallElementValue}
            onSelectWallElement={maze.setSelectedWallElementValue}
            gridRef={fileOps.gridRef}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
