/**
 * VisualEditor Component
 * 
 * Main visual editing area with the maze grid and element palette.
 */

import type { MazeData, LayerType, WallType } from '../../types/maze';
import { MazeGrid } from '../MazeGrid';
import { ElementPalette } from '../controls/ElementPalette';
import { LayerToggle } from '../controls/LayerToggle';
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
}: VisualEditorProps) {
    if (!mazeData) {
        return <EmptyState />;
    }

    // Compute grid dimensions based on maze type
    let rows: number;
    let cols: number;
    if (mazeData.maze_type === 'radial_arm') {
        rows = mazeData.arms?.length || 0;  // arm count
        // For radial_arm, cols is the max arm length (first arm's cell row length)
        cols = mazeData.arms?.[0]?.cells?.[0]?.length || 0;
    } else {
        const gridData = mazeData.grid || mazeData.cells || [];
        rows = gridData.length;
        cols = gridData[0]?.length || 0;
    }

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
                    {(mazeData.maze_type === 'edge_grid' || mazeData.maze_type === 'radial_arm') && (
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
                        data={mazeData}
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
            </div>
        </>
    );
}
