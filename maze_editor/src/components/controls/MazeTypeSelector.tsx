/**
 * MazeTypeSelector Component
 * 
 * Toggle between occupancy_grid, edge_grid, and radial_arm maze types.
 * For radial_arm, shows sub-options for circular or polygon hub.
 */

import clsx from 'clsx';
import type { MazeType } from '../../types/maze';

export interface MazeTypeSelectorProps {
    /** Current maze type */
    currentType?: MazeType;
    /** Current hub shape (for radial_arm) */
    currentHubShape?: 'circular' | 'polygon';
    /** Callback when maze type is changed */
    onChange: (type: MazeType, hubType?: 'circular' | 'polygon') => void;
}

export function MazeTypeSelector({ currentType, currentHubShape, onChange }: MazeTypeSelectorProps) {
    const isRadialArm = currentType === 'radial_arm';

    return (
        <div className="space-y-2">
            {/* Primary Type Row */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Maze Type:</span>
                <div className="flex gap-1">
                    <button
                        onClick={() => onChange('occupancy_grid')}
                        className={clsx(
                            "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                            currentType === 'occupancy_grid'
                                ? "bg-purple-500 text-white"
                                : "bg-black/40 text-slate-500 hover:text-white"
                        )}
                    >
                        Occupancy
                    </button>
                    <button
                        onClick={() => onChange('edge_grid')}
                        className={clsx(
                            "px-2 py-1 text-[10px] uppercase font-bold rounded transition-colors",
                            currentType === 'edge_grid'
                                ? "bg-purple-500 text-white"
                                : "bg-black/40 text-slate-500 hover:text-white"
                        )}
                    >
                        Edge
                    </button>
                    <button
                        onClick={() => onChange('radial_arm', currentHubShape || 'circular')}
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
                            onClick={() => onChange('radial_arm', 'circular')}
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
                            onClick={() => onChange('radial_arm', 'polygon')}
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
