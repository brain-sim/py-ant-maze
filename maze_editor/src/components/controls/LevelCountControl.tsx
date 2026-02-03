/**
 * LevelCountControl Component
 * 
 * Control for adjusting the number of levels in 3D mazes.
 */

import { Minus, Plus, Layers } from 'lucide-react';

export interface LevelCountControlProps {
    /** Current number of levels */
    levelCount: number;
    /** Callback when level count changes */
    onSetLevelCount: (count: number) => void;
}

export function LevelCountControl({
    levelCount,
    onSetLevelCount,
}: LevelCountControlProps) {
    return (
        <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
            <div className="flex items-center gap-1 text-slate-400">
                <Layers size={14} />
                <span className="text-xs font-medium">Levels:</span>
            </div>
            <div className="flex items-center gap-2">
                <button
                    onClick={() => onSetLevelCount(levelCount - 1)}
                    disabled={levelCount <= 2}
                    className="p-1 rounded bg-black/40 border border-white/10 hover:bg-purple-500/20 hover:border-purple-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Remove last level"
                >
                    <Minus className="w-3 h-3" />
                </button>
                <span className="text-sm font-medium min-w-[2ch] text-center">{levelCount}</span>
                <button
                    onClick={() => onSetLevelCount(levelCount + 1)}
                    disabled={levelCount >= 10}
                    className="p-1 rounded bg-black/40 border border-white/10 hover:bg-purple-500/20 hover:border-purple-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Add new level"
                >
                    <Plus className="w-3 h-3" />
                </button>
            </div>
        </div>
    );
}
