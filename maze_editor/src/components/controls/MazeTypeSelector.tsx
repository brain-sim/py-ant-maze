/**
 * MazeTypeSelector Component
 * 
 * Toggle between occupancy_grid and edge_grid maze types.
 */

import clsx from 'clsx';
import type { MazeType } from '../../types/maze';

export interface MazeTypeSelectorProps {
    /** Current maze type */
    currentType?: MazeType;
    /** Callback when maze type is changed */
    onChange: (type: MazeType) => void;
}

export function MazeTypeSelector({ currentType, onChange }: MazeTypeSelectorProps) {
    return (
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
            </div>
        </div>
    );
}
