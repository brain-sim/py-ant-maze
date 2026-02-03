/**
 * MazeTypeSelector Component
 * 
 * Toggle between occupancy_grid, edge_grid, and radial_arm maze types.
 * Supports both 2D and 3D variants. For radial_arm, shows sub-options for circular or polygon hub.
 */

import clsx from 'clsx';
import { Square, Layers } from 'lucide-react';
import type { MazeType, MazeType2D, MazeType3D } from '../../types/maze';
import { is3DMazeType, getBase2DType } from '../../types/maze';

export interface MazeTypeSelectorProps {
    /** Current maze type */
    currentType?: MazeType;
    /** Current hub shape (for radial_arm) */
    currentHubShape?: 'circular' | 'polygon';
    /** Callback when maze type is changed */
    onChange: (type: MazeType, hubType?: 'circular' | 'polygon') => void;
}

type BaseType = 'occupancy_grid' | 'edge_grid' | 'radial_arm';

export function MazeTypeSelector({ currentType, currentHubShape, onChange }: MazeTypeSelectorProps) {
    // Determine if current type is 3D
    const is3D = currentType ? is3DMazeType(currentType) : false;

    // Get base type (without _3d suffix)
    const getBaseType = (type?: MazeType): BaseType => {
        if (!type) return 'occupancy_grid';
        if (is3DMazeType(type)) return getBase2DType(type) as BaseType;
        return type as BaseType;
    };

    const baseType = getBaseType(currentType);
    const isRadialArm = baseType === 'radial_arm';

    // Handle base type change (preserves 3D state)
    const handleBaseTypeChange = (newBase: BaseType, hubType?: 'circular' | 'polygon') => {
        const fullType: MazeType = is3D ? `${newBase}_3d` as MazeType3D : newBase;
        onChange(fullType, hubType);
    };

    // Handle 3D toggle (preserves base type)
    const handle3DToggle = (enable3D: boolean) => {
        const fullType: MazeType = enable3D ? `${baseType}_3d` as MazeType3D : baseType as MazeType2D;
        onChange(fullType, baseType === 'radial_arm' ? (currentHubShape || 'circular') : undefined);
    };

    return (
        <div className="space-y-2">
            {/* Primary Type Row with 3D Toggle */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Maze Type:</span>
                <div className="flex gap-1 items-center">
                    {/* 2D/3D Toggle */}
                    <div className="flex gap-0.5 bg-black/40 rounded p-0.5 mr-2">
                        <button
                            onClick={() => handle3DToggle(false)}
                            title="2D Maze"
                            className={clsx(
                                "p-1 rounded transition-colors",
                                !is3D
                                    ? "bg-slate-600 text-white"
                                    : "text-slate-500 hover:text-white"
                            )}
                        >
                            <Square size={12} />
                        </button>
                        <button
                            onClick={() => handle3DToggle(true)}
                            title="3D Maze (Multi-Level)"
                            className={clsx(
                                "p-1 rounded transition-colors",
                                is3D
                                    ? "bg-amber-500 text-white"
                                    : "text-slate-500 hover:text-white"
                            )}
                        >
                            <Layers size={12} />
                        </button>
                    </div>

                    <button
                        onClick={() => handleBaseTypeChange('occupancy_grid')}
                        className={clsx(
                            "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                            baseType === 'occupancy_grid'
                                ? "bg-purple-500 text-white"
                                : "bg-black/40 text-slate-500 hover:text-white"
                        )}
                    >
                        Occupancy
                    </button>
                    <button
                        onClick={() => handleBaseTypeChange('edge_grid')}
                        className={clsx(
                            "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                            baseType === 'edge_grid'
                                ? "bg-purple-500 text-white"
                                : "bg-black/40 text-slate-500 hover:text-white"
                        )}
                    >
                        Edge
                    </button>
                    <button
                        onClick={() => handleBaseTypeChange('radial_arm', currentHubShape || 'circular')}
                        className={clsx(
                            "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                            isRadialArm
                                ? "bg-purple-500 text-white"
                                : "bg-black/40 text-slate-500 hover:text-white"
                        )}
                    >
                        Radial Arm
                    </button>
                </div>
            </div>

            {/* Hub Shape Sub-options (only shown for radial_arm) */}
            {isRadialArm && (
                <div className="flex items-center justify-between bg-slate-800/20 rounded-lg p-2 border border-white/5 ml-4">
                    <span className="text-xs text-slate-500">Hub Shape:</span>
                    <div className="flex gap-1">
                        <button
                            onClick={() => handleBaseTypeChange('radial_arm', 'circular')}
                            className={clsx(
                                "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                                currentHubShape === 'circular'
                                    ? "bg-indigo-500 text-white"
                                    : "bg-black/40 text-slate-500 hover:text-white"
                            )}
                        >
                            ○ Circular
                        </button>
                        <button
                            onClick={() => handleBaseTypeChange('radial_arm', 'polygon')}
                            className={clsx(
                                "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                                currentHubShape === 'polygon'
                                    ? "bg-indigo-500 text-white"
                                    : "bg-black/40 text-slate-500 hover:text-white"
                            )}
                        >
                            ◇ Polygon
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
