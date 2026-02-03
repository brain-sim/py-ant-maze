/**
 * LevelSelector Component
 * 
 * Tab-like component for switching between levels in 3D mazes.
 */

import clsx from 'clsx';
import { Layers, ChevronUp, ChevronDown } from 'lucide-react';
import type { LevelData } from '../../types/maze';

export interface LevelSelectorProps {
    /** List of levels in the maze */
    levels: LevelData[];
    /** Currently selected level index */
    selectedIndex: number;
    /** Callback when a level is selected */
    onSelect: (index: number) => void;
}

export function LevelSelector({ levels, selectedIndex, onSelect }: LevelSelectorProps) {
    if (levels.length === 0) return null;

    return (
        <div className="flex items-center gap-2 bg-slate-800/30 rounded-lg p-2 border border-white/5">
            <div className="flex items-center gap-1 text-slate-400">
                <Layers size={14} />
                <span className="text-xs font-medium">Level:</span>
            </div>

            <div className="flex gap-1">
                {levels.map((level, index) => (
                    <button
                        key={level.id}
                        onClick={() => onSelect(index)}
                        className={clsx(
                            "px-3 py-1.5 text-xs font-bold rounded transition-all duration-150",
                            "flex items-center gap-1",
                            selectedIndex === index
                                ? "bg-amber-500 text-white shadow-lg shadow-amber-500/20"
                                : "bg-black/40 text-slate-400 hover:text-white hover:bg-slate-700/50"
                        )}
                    >
                        {/* Level indicator with position context */}
                        {index === 0 && <ChevronDown size={12} className="opacity-60" />}
                        {index === levels.length - 1 && index !== 0 && <ChevronUp size={12} className="opacity-60" />}
                        <span className="capitalize">{level.id}</span>
                    </button>
                ))}
            </div>

            {/* Level count indicator */}
            <span className="text-[10px] text-slate-500 ml-1">
                ({selectedIndex + 1}/{levels.length})
            </span>
        </div>
    );
}
