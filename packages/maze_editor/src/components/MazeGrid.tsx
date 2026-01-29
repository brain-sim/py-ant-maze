import React from 'react';
import clsx from 'clsx';
import { type MazeData } from '../lib/pyodide';

interface MazeGridProps {
    data: MazeData;
    onCellClick: (row: number, col: number) => void;
    onWallClick?: (row: number, col: number, wallType: 'vertical' | 'horizontal') => void;
    className?: string;
}

const ELEMENT_COLORS: Record<string, string> = {
    wall: 'bg-slate-700 hover:bg-slate-600',
    open: 'bg-slate-100 hover:bg-white',
    empty: 'bg-slate-100 hover:bg-white',
    start: 'bg-emerald-500 hover:bg-emerald-400',
    goal: 'bg-rose-500 hover:bg-rose-400',
};

// Simple string hash function
const hashString = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
};

// Helper to determine text color (black/white) based on background luminance
const getContrastColor = (hexOrHsl: string) => {
    // For hardcoded classes, we use a lookup (simplified for this context)
    if (hexOrHsl.includes('bg-slate-700')) return '#ffffff'; // Dark slate
    if (hexOrHsl.includes('bg-slate-100')) return '#0f172a'; // Light slate (slate-900 text)
    if (hexOrHsl.includes('bg-emerald-500')) return '#ffffff';
    if (hexOrHsl.includes('bg-rose-500')) return '#ffffff';

    // For HSL strings: hsl(h, s%, l%)
    const hslMatch = hexOrHsl.match(/hsl\((\d+(?:\.\d+)?),\s*(\d+)%,\s*(\d+)%\)/);
    if (hslMatch) {
        const l = parseInt(hslMatch[3]);
        return l > 65 ? '#0f172a' : '#ffffff';
    }

    return '#ffffff';
};

// Generate consistent HSL color from name
export const generateColorStyle = (name: string) => {
    if (ELEMENT_COLORS[name]) {
        const textColor = getContrastColor(ELEMENT_COLORS[name]);
        return { className: ELEMENT_COLORS[name], style: { color: textColor } as React.CSSProperties };
    }

    const hash = hashString(name);
    // Use good saturation/lightness for vibrant but readable colors
    const hue = Math.abs(hash % 360);
    // Adjusted range: 40-60% lightness for better saturation
    const bg = `hsl(${hue}, 70%, 50%)`;
    const hover = `hsl(${hue}, 70%, 60%)`;

    // Determine contrast
    const textColor = '#ffffff'; // With L=50% and S=70%, white is usually good for most hues here.

    return { style: { backgroundColor: bg, color: textColor, '--hover-color': hover } as React.CSSProperties };
};

export function MazeGrid({ data, onCellClick, onWallClick, className }: MazeGridProps) {
    const { maze_type, grid, cells, vertical_walls, horizontal_walls, elements, wall_elements } = data;
    const [isDrawing, setIsDrawing] = React.useState(false);

    React.useEffect(() => {
        const handleGlobalMouseUp = () => setIsDrawing(false);
        window.addEventListener('mouseup', handleGlobalMouseUp);
        return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
    }, []);

    const cellElementMap = React.useMemo(() => {
        const map = new Map<number, typeof elements[0]>();
        elements.forEach((e) => map.set(e.value, e));
        return map;
    }, [elements]);

    const wallElementMap = React.useMemo(() => {
        const map = new Map<number, { name: string; token: string; value: number }>();
        wall_elements?.forEach((e) => map.set(e.value, e));
        return map;
    }, [wall_elements]);

    const handleCellAction = (r: number, c: number) => {
        onCellClick(r, c);
    };

    const handleWallAction = (r: number, c: number, type: 'vertical' | 'horizontal') => {
        onWallClick?.(r, c, type);
    };

    const handleMouseDown = (r: number, c: number, type: 'cell' | 'vertical' | 'horizontal') => {
        setIsDrawing(true);
        if (type === 'cell') handleCellAction(r, c);
        else handleWallAction(r, c, type);
    };

    const handleMouseEnter = (r: number, c: number, type: 'cell' | 'vertical' | 'horizontal') => {
        if (isDrawing) {
            if (type === 'cell') handleCellAction(r, c);
            else handleWallAction(r, c, type);
        }
    };

    if (maze_type === 'occupancy_grid' && grid) {
        const rows = grid.length;
        const cols = grid[0]?.length || 0;
        const cellSize = Math.max(24, Math.min(48, Math.floor(600 / Math.max(rows, cols))));

        return (
            <div
                className={clsx('inline-grid gap-0.5 bg-slate-900/50 p-0.5 rounded-xl', className)}
                style={{ gridTemplateColumns: `repeat(${cols}, ${cellSize}px)` }}
                onMouseLeave={() => setIsDrawing(false)}
            >
                {grid.map((row, rIndex) =>
                    row.map((cellValue, cIndex) => {
                        const element = cellElementMap.get(cellValue);
                        const name = element?.name || 'unknown';
                        const { className: colorClass, style: colorStyle } = generateColorStyle(name);

                        return (
                            <div
                                key={`${rIndex}-${cIndex}`}
                                onMouseDown={() => handleMouseDown(rIndex, cIndex, 'cell')}
                                onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'cell')}
                                className={clsx(
                                    'rounded-sm transition-all duration-100 transform active:scale-95 cursor-pointer',
                                    colorClass,
                                    !colorClass && 'hover:brightness-110'
                                )}
                                style={{ width: cellSize, height: cellSize, ...colorStyle }}
                                title={`(${rIndex}, ${cIndex}) ${name}`}
                            />
                        );
                    })
                )}
            </div>
        );
    }

    if (maze_type === 'edge_grid' && cells && vertical_walls && horizontal_walls) {
        const h = cells.length;
        const w = cells[0]?.length || 0;
        const S = Math.max(24, Math.min(48, Math.floor(600 / Math.max(h, w))));
        const T = Math.floor(S / 4);

        return (
            <div
                className={clsx('inline-flex flex-col bg-slate-900/50 p-2 rounded-xl transition-all', className)}
                onMouseLeave={() => setIsDrawing(false)}
            >
                {Array.from({ length: h * 2 + 1 }).map((_, r) => {
                    const isWallRow = r % 2 === 0;
                    const rIndex = Math.floor(r / 2);

                    return (
                        <div key={r} className="flex">
                            {Array.from({ length: w * 2 + 1 }).map((_, c) => {
                                const isWallCol = c % 2 === 0;
                                const cIndex = Math.floor(c / 2);

                                if (isWallRow && isWallCol) {
                                    // Corner/Intersection
                                    return <div key={c} style={{ width: T, height: T }} className="bg-slate-700/30" />;
                                }

                                if (isWallRow) {
                                    // Horizontal Wall
                                    const val = horizontal_walls[rIndex][cIndex];
                                    const el = wallElementMap.get(val);
                                    const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown');
                                    return (
                                        <div
                                            key={c}
                                            onMouseDown={() => handleMouseDown(rIndex, cIndex, 'horizontal')}
                                            onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'horizontal')}
                                            style={{ width: S, height: T, ...colorStyle }}
                                            className={clsx('cursor-pointer transition-all hover:brightness-125', colorClass)}
                                            title={`H-Wall (${rIndex}, ${cIndex})`}
                                        />
                                    );
                                }

                                if (isWallCol) {
                                    // Vertical Wall
                                    const val = vertical_walls[rIndex][cIndex];
                                    const el = wallElementMap.get(val);
                                    const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown');
                                    return (
                                        <div
                                            key={c}
                                            onMouseDown={() => handleMouseDown(rIndex, cIndex, 'vertical')}
                                            onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'vertical')}
                                            style={{ width: T, height: S, ...colorStyle }}
                                            className={clsx('cursor-pointer transition-all hover:brightness-125', colorClass)}
                                            title={`V-Wall (${rIndex}, ${cIndex})`}
                                        />
                                    );
                                }

                                // Cell
                                const val = cells[rIndex][cIndex];
                                const el = cellElementMap.get(val);
                                const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown');
                                return (
                                    <div
                                        key={c}
                                        onMouseDown={() => handleMouseDown(rIndex, cIndex, 'cell')}
                                        onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'cell')}
                                        style={{ width: S, height: S, ...colorStyle }}
                                        className={clsx('cursor-pointer transition-all flex items-center justify-center font-mono text-[10px] opacity-80 hover:opacity-100', colorClass)}
                                        title={`Cell (${rIndex}, ${cIndex})`}
                                    >
                                        {el?.token}
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>
        );
    }

    return null;
}
