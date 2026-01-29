import React from 'react';
import clsx from 'clsx';
import { type MazeData } from '../lib/pyodide';

interface MazeGridProps {
    data: MazeData;
    onCellClick: (row: number, col: number) => void;
    className?: string;
}

const ELEMENT_COLORS: Record<string, string> = {
    wall: 'bg-slate-700 hover:bg-slate-600',
    open: 'bg-slate-100 hover:bg-white',
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
        // Simple threshold: if lightness > 50%, use black text, else white
        // This is a heuristic for HSL. For strict accessibility, luminance would be better calculated from RGB,
        // but for dynamic vibrant generation (sat=70%), L is a decent proxy.
        // HSL L=50% with S=70% is usually quite perceptible, but let's check.
        // Pure yellow at 50% L is bright, blue at 50% L is dark.
        // To be safer, we can default to white unless it's very light.
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

export function MazeGrid({ data, onCellClick, className }: MazeGridProps) {
    const { grid, elements } = data;
    const [isDrawing, setIsDrawing] = React.useState(false);

    React.useEffect(() => {
        const handleGlobalMouseUp = () => setIsDrawing(false);
        window.addEventListener('mouseup', handleGlobalMouseUp);
        return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
    }, []);

    const handleMouseDown = (r: number, c: number) => {
        setIsDrawing(true);
        onCellClick(r, c);
    };

    const handleMouseEnter = (r: number, c: number) => {
        if (isDrawing) {
            onCellClick(r, c);
        }
    };

    const elementMap = React.useMemo(() => {
        const map = new Map<number, typeof elements[0]>();
        elements.forEach((e) => map.set(e.value, e));
        return map;
    }, [elements]);

    // Calculate cell size based on grid dimensions for responsive sizing
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
                    const element = elementMap.get(cellValue);
                    const name = element?.name || 'unknown';
                    const { className: colorClass, style: colorStyle } = generateColorStyle(name);

                    return (
                        <div
                            key={`${rIndex}-${cIndex}`}
                            onMouseDown={() => handleMouseDown(rIndex, cIndex)}
                            onMouseEnter={() => handleMouseEnter(rIndex, cIndex)}
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
