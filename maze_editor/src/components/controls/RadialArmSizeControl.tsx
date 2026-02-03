/**
 * RadialArmSizeControl Component
 * 
 * Controls for resizing individual arms in a radial arm maze.
 * Displays width × length for each arm with editable inputs.
 * Also allows adding/removing arms and adjusting hub angle.
 */

import { Minus, Plus } from 'lucide-react';
import type { RadialArmArm } from '../../types/maze';

export interface RadialArmSizeControlProps {
    /** Arms data */
    arms: RadialArmArm[];
    /** Hub angle degrees */
    angleDegrees?: number;
    /** Hub shape */
    hubShape?: 'circular' | 'polygon';
    /** Hub radius (for circular) */
    hubRadius?: number;
    /** Hub side length (for polygon) */
    hubSideLength?: number;
    /** Callback when an arm is resized */
    onResizeArm: (armIndex: number, width: number, length: number) => void;
    /** Callback when arm count changes */
    onSetArmCount?: (count: number) => void;
    /** Callback when angle degrees changes */
    onSetAngle?: (degrees: number) => void;
    /** Callback when hub size changes */
    onSetHubSize?: (size: number) => void;
}

export function RadialArmSizeControl({
    arms,
    angleDegrees = 360,
    hubShape = 'circular',
    hubRadius,
    hubSideLength,
    onResizeArm,
    onSetArmCount,
    onSetAngle,
    onSetHubSize
}: RadialArmSizeControlProps) {
    const armCount = arms.length;
    const currentHubSize = hubShape === 'circular' ? hubRadius : hubSideLength;

    return (
        <div className="space-y-2">
            {/* Arm Count Control */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Arms:</span>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => onSetArmCount?.(armCount - 1)}
                        disabled={armCount <= 1}
                        className="p-1 rounded bg-black/40 border border-white/10 hover:bg-purple-500/20 hover:border-purple-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        title="Remove last arm"
                    >
                        <Minus className="w-3 h-3" />
                    </button>
                    <span className="text-sm font-medium min-w-[2ch] text-center">{armCount}</span>
                    <button
                        onClick={() => onSetArmCount?.(armCount + 1)}
                        disabled={armCount >= 30}
                        className="p-1 rounded bg-black/40 border border-white/10 hover:bg-purple-500/20 hover:border-purple-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        title="Add new arm"
                    >
                        <Plus className="w-3 h-3" />
                    </button>
                </div>
            </div>

            {/* Angle Degrees Control */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Angle:</span>
                <div className="flex items-center gap-2">
                    <input
                        type="range"
                        min="30"
                        max="360"
                        step="5"
                        value={angleDegrees}
                        onChange={(e) => onSetAngle?.(parseInt(e.target.value))}
                        className="w-20 h-1 bg-black/40 rounded-lg appearance-none cursor-pointer accent-purple-500"
                        title="Hub angle degrees"
                    />
                    <input
                        type="number"
                        min="1"
                        max="360"
                        value={angleDegrees}
                        onChange={(e) => {
                            const val = parseInt(e.target.value);
                            if (val >= 1 && val <= 360) onSetAngle?.(val);
                        }}
                        className="w-12 bg-black/40 border border-white/10 rounded px-1 py-0.5 text-[10px] text-center focus:outline-none focus:border-purple-500 transition-colors"
                        title="Hub angle degrees"
                    />
                    <span className="text-[10px] text-slate-500">°</span>
                </div>
            </div>

            {/* Hub Size Control - Radius for circular, Side Length for polygon */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">
                    {hubShape === 'circular' ? 'Radius:' : 'Side:'}
                </span>
                <div className="flex items-center gap-2">
                    <input
                        type="number"
                        min="0.1"
                        step="0.1"
                        value={currentHubSize?.toFixed(2) ?? ''}
                        onChange={(e) => {
                            const val = parseFloat(e.target.value);
                            if (val > 0) onSetHubSize?.(val);
                        }}
                        className="w-16 bg-black/40 border border-white/10 rounded px-1 py-0.5 text-[10px] text-center focus:outline-none focus:border-purple-500 transition-colors"
                        title={hubShape === 'circular' ? 'Hub radius' : 'Hub side length'}
                    />
                    <span className="text-[10px] text-slate-500">cells</span>
                </div>
            </div>

            {/* Arm Sizes Header */}
            <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
                <span className="text-xs text-slate-400">Arm Sizes:</span>
                <span className="text-[10px] text-slate-500 uppercase">Width × Length</span>
            </div>

            <div className="space-y-1 ml-4">
                {arms.map((arm, index) => {
                    const width = arm.cells.length;
                    const length = arm.cells[0]?.length || 0;

                    return (
                        <div
                            key={index}
                            className="flex items-center justify-between bg-slate-800/20 rounded-lg px-2 py-1.5 border border-white/5"
                        >
                            <span className="text-xs text-slate-400">Arm {index + 1}:</span>
                            <div className="flex items-center gap-2">
                                <input
                                    type="number"
                                    min="1"
                                    max="20"
                                    value={width}
                                    onChange={(e) => {
                                        const val = parseInt(e.target.value);
                                        if (val > 0) onResizeArm(index, val, length);
                                    }}
                                    className="w-10 bg-black/40 border border-white/10 rounded px-1 py-0.5 text-[10px] text-center focus:outline-none focus:border-purple-500 transition-colors"
                                    title="Width (rows)"
                                />
                                <span className="text-slate-600 text-xs">×</span>
                                <input
                                    type="number"
                                    min="1"
                                    max="50"
                                    value={length}
                                    onChange={(e) => {
                                        const val = parseInt(e.target.value);
                                        if (val > 0) onResizeArm(index, width, val);
                                    }}
                                    className="w-10 bg-black/40 border border-white/10 rounded px-1 py-0.5 text-[10px] text-center focus:outline-none focus:border-purple-500 transition-colors"
                                    title="Length (columns)"
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
