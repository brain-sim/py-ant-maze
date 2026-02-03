/**
 * VisualEditor Component
 * 
 * Main visual editing area with the maze grid and element palette.
 * Supports both 2D and 3D mazes with level selection.
 */

import type { MazeData, LayerType, WallType, LevelData } from '../../types/maze';
import { is3DMazeType } from '../../types/maze';
import { MazeGrid } from '../MazeGrid';
import { ElementPalette } from '../controls/ElementPalette';
import { LayerToggle } from '../controls/LayerToggle';
import { LevelSelector } from '../controls/LevelSelector';
import { EmptyState } from './EmptyState';

export interface VisualEditorProps {
    /** Parsed maze data */
    mazeData: MazeData | null;
    /** Callback when a cell is clicked */
    onCellClick: (row: number, col: number) => void;
    /** Callback when a wall is clicked */
    onWallClick: (row: number, col: number, wallType: WallType) => void;
    /** Callback when a radial_arm cell is clicked */
    onRadialCellClick?: (armIndex: number, row: number, col: number) => void;
    /** Callback when a radial_arm wall is clicked */
    onRadialWallClick?: (armIndex: number, row: number, col: number, wallType: WallType) => void;
    /** Currently selected layer */
    selectedLayer: LayerType;
    /** Callback to change selected layer */
    onLayerChange: (layer: LayerType) => void;
    /** Currently selected cell element value */
    selectedElementValue: number;
    /** Callback to select a cell element */
    onSelectElement: (value: number) => void;
    /** Currently selected wall element value */
    selectedWallElementValue: number;
    /** Callback to select a wall element */
    onSelectWallElement: (value: number) => void;
    /** Ref for the grid container (for image export) */
    gridRef: React.RefObject<HTMLDivElement>;
    /** Currently selected level index (for 3D mazes) */
    selectedLevelIndex?: number;
    /** Callback to change selected level */
    onLevelChange?: (index: number) => void;
}

export function VisualEditor({
    mazeData,
    onCellClick,
    onWallClick,
    onRadialCellClick,
    onRadialWallClick,
    selectedLayer,
    onLayerChange,
    selectedElementValue,
    onSelectElement,
    selectedWallElementValue,
    onSelectWallElement,
    gridRef,
    selectedLevelIndex = 0,
    onLevelChange,
}: VisualEditorProps) {
    if (!mazeData) {
        return <EmptyState />;
    }

    const is3D = is3DMazeType(mazeData.maze_type);
    const levels = mazeData.levels || [];
    const currentLevel: LevelData | undefined = is3D ? levels[selectedLevelIndex] : undefined;

    // Create a "virtual" 2D MazeData for the grid from the current level
    // This allows MazeGrid to render the level without knowing about 3D structure
    const mazeDataForGrid: MazeData = is3D && currentLevel
        ? {
            ...mazeData,
            // Flatten level data into top-level fields for grid rendering
            grid: currentLevel.grid,
            cells: currentLevel.cells,
            vertical_walls: currentLevel.vertical_walls,
            horizontal_walls: currentLevel.horizontal_walls,
            arms: currentLevel.arms,
        }
        : mazeData;

    // Compute grid dimensions based on maze type
    let rows: number;
    let cols: number;
    const baseType = is3D ? mazeData.maze_type.replace('_3d', '') : mazeData.maze_type;

    if (baseType === 'radial_arm') {
        const arms = mazeDataForGrid.arms || [];
        rows = arms?.length || 0;  // arm count
        cols = arms?.[0]?.cells?.[0]?.length || 0;
    } else {
        const gridData = mazeDataForGrid.grid || mazeDataForGrid.cells || [];
        rows = gridData.length;
        cols = gridData[0]?.length || 0;
    }

    // Determine if layer toggle should be shown
    const showLayerToggle = baseType === 'edge_grid' || baseType === 'radial_arm';

    const currentElements = selectedLayer === 'cells'
        ? mazeData.elements
        : (mazeData.wall_elements || []);

    const currentSelectedValue = selectedLayer === 'cells'
        ? selectedElementValue
        : selectedWallElementValue;

    const onSelect = selectedLayer === 'cells'
        ? onSelectElement
        : onSelectWallElement;

    return (
        <>
            {/* Toolbar */}
            <div className="shrink-0 p-4 bg-black/20 border-b border-white/10 overflow-x-auto">
                <div className="flex flex-col gap-3">
                    {/* Level Selector (only for 3D mazes) */}
                    {is3D && levels.length > 0 && onLevelChange && (
                        <LevelSelector
                            levels={levels}
                            selectedIndex={selectedLevelIndex}
                            onSelect={onLevelChange}
                        />
                    )}

                    {showLayerToggle && (
                        <LayerToggle
                            selectedLayer={selectedLayer}
                            onChange={onLayerChange}
                        />
                    )}

                    <ElementPalette
                        elements={currentElements}
                        selectedValue={currentSelectedValue}
                        onSelect={onSelect}
                        layer={selectedLayer}
                    />
                </div>
            </div>

            {/* Grid Area */}
            <div className="flex-1 overflow-auto p-4 md:p-8 flex items-center justify-center bg-dot-pattern">
                <div
                    ref={gridRef}
                    className="max-w-full max-h-full overflow-auto bg-slate-800/50 p-2 rounded-2xl shadow-2xl border border-white/10 backdrop-blur-sm"
                >
                    <MazeGrid
                        data={mazeDataForGrid}
                        onCellClick={onCellClick}
                        onWallClick={onWallClick}
                        onRadialCellClick={onRadialCellClick}
                        onRadialWallClick={onRadialWallClick}
                        selectedLayer={selectedLayer}
                    />
                </div>
            </div>

            {/* Footer Hint */}
            <div className="shrink-0 px-4 py-2 text-center text-xs text-slate-500 border-t border-white/5 bg-slate-900/80">
                Click cells/walls to paint • Grid: {rows} × {cols}
                {is3D && currentLevel && <span className="ml-2">• Level: {currentLevel.id}</span>}
            </div>
        </>
    );
}
