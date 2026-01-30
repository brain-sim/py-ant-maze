/**
 * AddElementForm Component
 * 
 * Form for adding new cell or wall elements to the maze configuration.
 */

import { useState } from 'react';
import clsx from 'clsx';
import { Plus } from 'lucide-react';
import type { LayerType, ElementType } from '../../types/maze';

export interface AddElementFormProps {
    /** Whether this is an edge_grid maze (shows layer toggle) */
    isEdgeGrid: boolean;
    /** Currently selected layer */
    selectedLayer: LayerType;
    /** Callback to change selected layer */
    onLayerChange: (layer: LayerType) => void;
    /** Callback when element is added */
    onAdd: (name: string, token: string, type: ElementType) => void;
}

export function AddElementForm({
    isEdgeGrid,
    selectedLayer,
    onLayerChange,
    onAdd,
}: AddElementFormProps) {
    const [name, setName] = useState("");
    const [token, setToken] = useState("");

    const handleSubmit = () => {
        if (name && token.length === 1) {
            onAdd(name, token, selectedLayer === 'walls' ? 'wall' : 'cell');
            setName("");
            setToken("");
        }
    };

    return (
        <div className="flex flex-col gap-2 bg-slate-800/30 rounded-lg p-2 border border-white/5">
            <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Add Element:</span>
                {isEdgeGrid && (
                    <div className="flex gap-1">
                        <button
                            onClick={() => onLayerChange('cells')}
                            className={clsx(
                                "px-2 py-0.5 text-[9px] uppercase font-bold rounded",
                                selectedLayer === 'cells'
                                    ? "bg-purple-500 text-white"
                                    : "bg-black/20 text-slate-500"
                            )}
                        >
                            Cell
                        </button>
                        <button
                            onClick={() => onLayerChange('walls')}
                            className={clsx(
                                "px-2 py-0.5 text-[9px] uppercase font-bold rounded",
                                selectedLayer === 'walls'
                                    ? "bg-purple-500 text-white"
                                    : "bg-black/20 text-slate-500"
                            )}
                        >
                            Wall
                        </button>
                    </div>
                )}
            </div>
            <div className="flex items-center gap-2">
                <div className="flex-1 min-w-0">
                    <input
                        type="text"
                        placeholder="Name (e.g. Water)"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-black/40 border border-white/10 rounded px-2 py-1 text-xs focus:outline-none focus:border-purple-500 transition-colors placeholder:text-slate-600"
                    />
                </div>
                <div className="w-12 shrink-0">
                    <input
                        type="text"
                        placeholder="Char"
                        maxLength={1}
                        value={token}
                        onChange={(e) => setToken(e.target.value)}
                        className="w-full bg-black/40 border border-white/10 rounded px-2 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors placeholder:text-slate-600"
                    />
                </div>
                <button
                    onClick={handleSubmit}
                    disabled={!name || token.length !== 1}
                    className="shrink-0 p-1 rounded bg-purple-500/20 text-purple-400 hover:bg-purple-500 hover:text-white border border-purple-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Add Element"
                >
                    <Plus size={14} />
                </button>
            </div>
        </div>
    );
}
