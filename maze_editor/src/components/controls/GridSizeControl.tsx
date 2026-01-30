/**
 * GridSizeControl Component
 * 
 * Controls for resizing the maze grid dimensions.
 */

export interface GridSizeControlProps {
    /** Current number of rows */
    rows: number;
    /** Current number of columns */
    cols: number;
    /** Callback when size changes */
    onResize: (rows: number, cols: number) => void;
}

export function GridSizeControl({ rows, cols, onResize }: GridSizeControlProps) {
    return (
        <div className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2 border border-white/5">
            <span className="text-xs text-slate-400">Grid Size:</span>
            <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">Rows</span>
                    <input
                        type="number"
                        min="1"
                        max="100"
                        value={rows}
                        onChange={(e) => {
                            const val = parseInt(e.target.value);
                            if (val > 0) onResize(val, cols);
                        }}
                        className="w-12 bg-black/40 border border-white/10 rounded px-1.5 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors"
                    />
                </div>
                <span className="text-slate-600">×</span>
                <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">Cols</span>
                    <input
                        type="number"
                        min="1"
                        max="100"
                        value={cols}
                        onChange={(e) => {
                            const val = parseInt(e.target.value);
                            if (val > 0) onResize(rows, val);
                        }}
                        className="w-12 bg-black/40 border border-white/10 rounded px-1.5 py-1 text-xs text-center focus:outline-none focus:border-purple-500 transition-colors"
                    />
                </div>
            </div>
        </div>
    );
}
