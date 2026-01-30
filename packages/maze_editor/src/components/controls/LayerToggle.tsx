/**
 * LayerToggle Component
 * 
 * Toggle between cells and walls layer for edge_grid mazes.
 */

import clsx from 'clsx';
import type { LayerType } from '../../types/maze';

export interface LayerToggleProps {
    /** Currently selected layer */
    selectedLayer: LayerType;
    /** Callback when layer changes */
    onChange: (layer: LayerType) => void;
}

export function LayerToggle({ selectedLayer, onChange }: LayerToggleProps) {
    return (
        <div className="flex items-center gap-2 border-b border-white/5 pb-2">
            <span className="text-xs text-slate-400 mr-2">Layer:</span>
            <button
                onClick={() => onChange('cells')}
                className={clsx(
                    "px-3 py-1 rounded-full text-xs font-bold transition-all",
                    selectedLayer === 'cells'
                        ? "bg-purple-500 text-white"
                        : "bg-slate-700/50 text-slate-400 hover:bg-slate-700"
                )}
            >
                Cells
            </button>
            <button
                onClick={() => onChange('walls')}
                className={clsx(
                    "px-3 py-1 rounded-full text-xs font-bold transition-all",
                    selectedLayer === 'walls'
                        ? "bg-purple-500 text-white"
                        : "bg-slate-700/50 text-slate-400 hover:bg-slate-700"
                )}
            >
                Walls
            </button>
        </div>
    );
}
