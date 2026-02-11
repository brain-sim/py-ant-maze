/**
 * CodePanel Component
 * 
 * Left sidebar containing the YAML editor and maze configuration controls.
 */

import { RefreshCw, Play, Upload, Download, Image as ImageIcon, FileText, AlertCircle } from 'lucide-react';
import type { MazeData, MazeType, LayerType, ElementType } from '../../types/maze';
import { is3DMazeType, getBase2DType } from '../../types/maze';
import { MazeTypeSelector } from '../controls/MazeTypeSelector';
import { GridSizeControl } from '../controls/GridSizeControl';
import { RadialArmSizeControl } from '../controls/RadialArmSizeControl';
import { LevelCountControl } from '../controls/LevelCountControl';
import { AddElementForm } from '../controls/AddElementForm';

export interface CodePanelProps {
    /** Current YAML input */
    input: string;
    /** Callback when input changes */
    onInputChange: (value: string) => void;
    /** Current maze data */
    mazeData: MazeData | null;
    /** Callback to format YAML */
    onFormat: () => void;
    /** Callback to sync YAML to grid */
    onParse: () => void;
    /** Callback to create new maze */
    onCreate: (type: MazeType, hubType?: 'circular' | 'polygon') => void;
    /** Callback to resize maze (occupancy_grid and edge_grid) */
    onResize: (rows: number, cols: number) => void;
    /** Callback to resize a specific arm (radial_arm only) */
    onResizeArm: (armIndex: number, width: number, length: number) => void;
    /** Callback to set number of arms (radial_arm only) */
    onSetArmCount?: (count: number) => void;
    /** Callback to set hub angle degrees (radial_arm only) */
    onSetAngle?: (degrees: number) => void;
    /** Callback to set hub size (radial_arm only) */
    onSetHubSize?: (size: number) => void;
    /** Callback to set level count (3D mazes only) */
    onSetLevelCount?: (count: number) => void;
    /** Callback to add element */
    onAddElement: (name: string, token: string, type: ElementType) => void;
    /** Current layer selection */
    selectedLayer: LayerType;
    /** Callback to change layer */
    onLayerChange: (layer: LayerType) => void;
    /** Current error message */
    error: string | null;
    /** File input ref */
    fileInputRef: React.RefObject<HTMLInputElement>;
    /** Callback when file is selected */
    onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    /** Callback to trigger upload */
    onUploadClick: () => void;
    /** Callback to download YAML */
    onDownload: () => void;
    /** Callback to export image */
    onExportImage: () => void;
}

export function CodePanel({
    input,
    onInputChange,
    mazeData,
    onFormat,
    onParse,
    onCreate,
    onResize,
    onResizeArm,
    onSetArmCount,
    onSetAngle,
    onSetHubSize,
    onSetLevelCount,
    onAddElement,
    selectedLayer,
    onLayerChange,
    error,
    fileInputRef,
    onFileChange,
    onUploadClick,
    onDownload,
    onExportImage,
}: CodePanelProps) {
    // Determine base type for conditional rendering
    const is3D = mazeData ? is3DMazeType(mazeData.maze_type) : false;
    const baseType = mazeData
        ? (is3D ? getBase2DType(mazeData.maze_type as import('../../types/maze').MazeType3D) : mazeData.maze_type)
        : null;

    // Compute grid dimensions - for 3D mazes, use first level's data
    let gridData: number[][] = [];
    if (mazeData) {
        if (is3D && mazeData.levels && mazeData.levels.length > 0) {
            // For 3D mazes, get grid from first level
            const firstLevel = mazeData.levels[0];
            gridData = firstLevel.grid || firstLevel.cells || [];
        } else {
            // For 2D mazes, use top-level grid
            gridData = mazeData.grid || mazeData.cells || [];
        }
    }
    const rows = gridData.length;
    const cols = gridData[0]?.length || 0;

    // Extract arms for radial_arm mazes (2D uses mazeData.arms, 3D uses levels[0].arms)
    const radialArms = mazeData?.arms || mazeData?.levels?.[0]?.arms;

    return (
        <div className="h-full flex flex-col">
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
                            onChange={onFileChange}
                        />
                        <button
                            onClick={onUploadClick}
                            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                            title="Import YAML"
                        >
                            <Upload size={16} />
                        </button>
                        <button
                            onClick={onDownload}
                            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                            title="Export YAML"
                        >
                            <Download size={16} />
                        </button>
                        <button
                            onClick={onExportImage}
                            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                            title="Export as Image"
                        >
                            <ImageIcon size={16} />
                        </button>
                    </div>
                </div>

                {/* Maze Type Selector */}
                <MazeTypeSelector
                    currentType={mazeData?.maze_type}
                    currentHubShape={mazeData?.hub?.shape as 'circular' | 'polygon' | undefined}
                    onChange={onCreate}
                />

                {/* Level Count Control - 3D mazes only */}
                {mazeData && is3D && mazeData.levels && onSetLevelCount && (
                    <LevelCountControl
                        levelCount={mazeData.levels.length}
                        onSetLevelCount={onSetLevelCount}
                    />
                )}

                {/* Resize Controls - conditional based on base maze type */}
                {mazeData && baseType !== 'radial_arm' && (
                    <GridSizeControl
                        rows={rows}
                        cols={cols}
                        onResize={onResize}
                        is3D={is3D}
                    />
                )}
                {mazeData && baseType === 'radial_arm' && radialArms && (
                    <RadialArmSizeControl
                        arms={radialArms}
                        angleDegrees={mazeData.hub?.angle_degrees}
                        hubShape={mazeData.hub?.shape}
                        hubRadius={mazeData.hub?.radius}
                        hubSideLength={mazeData.hub?.side_length}
                        onResizeArm={onResizeArm}
                        onSetArmCount={onSetArmCount}
                        onSetAngle={onSetAngle}
                        onSetHubSize={onSetHubSize}
                    />
                )}

                {/* Add Element Controls */}
                {mazeData && (
                    <AddElementForm
                        isEdgeGrid={!!(mazeData.wall_elements && mazeData.wall_elements.length > 0)}
                        selectedLayer={selectedLayer}
                        onLayerChange={onLayerChange}
                        onAdd={onAddElement}
                    />
                )}
            </div>

            {/* Code Editor */}
            <div className="flex-1 relative min-h-0">
                <textarea
                    className="absolute inset-0 w-full h-full p-4 resize-none bg-transparent text-slate-300 font-mono text-xs leading-relaxed focus:outline-none"
                    value={input}
                    onChange={(e) => onInputChange(e.target.value)}
                    spellCheck={false}
                    style={{ tabSize: 2 }}
                />
            </div>

            {/* Code Footer */}
            <div className="shrink-0 p-4 border-t border-white/10 bg-black/20 z-10">
                <div className="flex gap-2">
                    <button
                        onClick={onFormat}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 border border-slate-600/50 text-sm font-medium transition-colors"
                    >
                        <RefreshCw size={14} />
                        Format
                    </button>
                    <button
                        onClick={onParse}
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
    );
}
