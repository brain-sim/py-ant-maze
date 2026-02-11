import React from 'react';
import clsx from 'clsx';
import type { MazeData, WallType } from '../types/maze';
import { is3DMazeType, getBase2DType } from '../types/maze';
import { CELL_ELEMENT_COLORS, WALL_ELEMENT_COLORS, ELEMENT_COLORS } from '../constants/defaults';
import { RadialArmGrid } from './RadialArmGrid';

interface MazeGridProps {
    data: MazeData;
    onCellClick: (row: number, col: number) => void;
    onWallClick?: (row: number, col: number, wallType: WallType) => void;
    onRadialCellClick?: (armIndex: number, row: number, col: number) => void;
    onRadialWallClick?: (armIndex: number, row: number, col: number, wallType: WallType) => void;
    selectedLayer?: 'cells' | 'walls';
    className?: string;
}

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
    // Light backgrounds - use dark text
    if (hexOrHsl.includes('bg-slate-50')) return '#0f172a';
    if (hexOrHsl.includes('bg-slate-100')) return '#0f172a';
    if (hexOrHsl.includes('bg-slate-200')) return '#0f172a';
    if (hexOrHsl.includes('bg-white')) return '#0f172a';
    // Dark backgrounds - use white text
    if (hexOrHsl.includes('bg-slate-600')) return '#ffffff';
    if (hexOrHsl.includes('bg-slate-700')) return '#ffffff';
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
export const generateColorStyle = (name: string, layer: 'cell' | 'wall' | 'corner' = 'cell') => {
    // Select the appropriate color map based on layer
    const colorMap = layer === 'wall' ? WALL_ELEMENT_COLORS :
        layer === 'corner' ? WALL_ELEMENT_COLORS :
            CELL_ELEMENT_COLORS;

    if (colorMap[name]) {
        const textColor = getContrastColor(colorMap[name]);
        return { className: colorMap[name], style: { color: textColor } as React.CSSProperties };
    }

    // Fallback to ELEMENT_COLORS for legacy compatibility
    if (ELEMENT_COLORS[name]) {
        const textColor = getContrastColor(ELEMENT_COLORS[name]);
        return { className: ELEMENT_COLORS[name], style: { color: textColor } as React.CSSProperties };
    }

    const hash = hashString(name);
    // Use slightly different saturation/lightness based on layer
    const hue = (Math.abs(hash) * 137.508) % 360;
    const saturation = layer === 'wall' ? 60 : 70;
    const lightness = layer === 'wall' ? 45 : 50;
    const bg = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    const hover = `hsl(${hue}, ${saturation}%, ${lightness + 10}%)`;

    // Determine contrast
    const textColor = '#ffffff';

    return { style: { backgroundColor: bg, color: textColor, '--hover-color': hover } as React.CSSProperties };
};

export function MazeGrid({
    data,
    onCellClick,
    onWallClick,
    onRadialCellClick,
    onRadialWallClick,
    selectedLayer = 'cells',
    className
}: MazeGridProps) {
    const { maze_type, grid, cells, vertical_walls, horizontal_walls, elements, wall_elements } = data;
    const [isDrawing, setIsDrawing] = React.useState(false);

    // Get the base type (occupancy_grid, edge_grid, radial_arm) for rendering decisions
    const baseType = is3DMazeType(maze_type) ? getBase2DType(maze_type) : maze_type;

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
        if (baseType === 'edge_grid' && selectedLayer !== 'cells') return;
        onCellClick(r, c);
    };

    const handleWallAction = (r: number, c: number, type: 'vertical' | 'horizontal') => {
        if (selectedLayer !== 'walls') return;
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

    if (baseType === 'occupancy_grid' && grid) {
        const rows = grid.length;
        const cols = grid[0]?.length || 0;
        const cellSize = Math.max(24, Math.min(48, Math.floor(600 / Math.max(rows, cols))));

        return (
            <div
                className={clsx('inline-grid p-0.5 rounded-xl', className)}
                style={{
                    gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`,
                    gap: '2px',
                    backgroundColor: 'rgba(148, 163, 184, 0.15)'
                }}
                onMouseLeave={() => setIsDrawing(false)}
            >
                {grid.map((row, rIndex) =>
                    row.map((cellValue, cIndex) => {
                        const cellEl = cellElementMap.get(cellValue);
                        const wallEl = wallElementMap.get(cellValue);
                        const element = cellEl || wallEl;
                        const layer: 'cell' | 'wall' = wallEl && !cellEl ? 'wall' : 'cell';
                        const name = element?.name || 'unknown';
                        const { className: colorClass, style: colorStyle } = generateColorStyle(name, layer);

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

    if (baseType === 'edge_grid' && cells && vertical_walls && horizontal_walls) {
        const h = cells.length;
        const w = cells[0]?.length || 0;
        const S = Math.max(24, Math.min(48, Math.floor(600 / Math.max(h, w))));
        const T = Math.floor(S / 4);

        return (
            <div
                className={clsx('inline-block bg-slate-900/50 p-2 rounded-xl transition-all', className)}
                onMouseLeave={() => setIsDrawing(false)}
                style={{ display: 'grid', gridTemplateColumns: `repeat(${w}, ${T}px ${S}px) ${T}px`, gridTemplateRows: `repeat(${h}, ${T}px ${S}px) ${T}px`, overflow: 'visible' }}
            >
                {Array.from({ length: h * 2 + 1 }).map((_, r) => {
                    const isWallRow = r % 2 === 0;
                    const rIndex = Math.floor(r / 2);

                    return Array.from({ length: w * 2 + 1 }).map((_, c) => {
                        const isWallCol = c % 2 === 0;
                        const cIndex = Math.floor(c / 2);

                        if (isWallRow && isWallCol) {
                            // Corner - use wall color to blend with wall areas
                            const { className: colorClass, style: colorStyle } = generateColorStyle('empty', 'corner');
                            return <div key={`${r}-${c}`} className={colorClass} style={{ ...colorStyle }} />;
                        }

                        if (isWallRow) {
                            // Horizontal Wall - extend solid walls to cover corners
                            const val = horizontal_walls[rIndex][cIndex];
                            const el = wallElementMap.get(val);
                            const isSolid = val > 0;
                            const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown', 'wall');
                            return (
                                <div
                                    key={`${r}-${c}`}
                                    onMouseDown={() => handleMouseDown(rIndex, cIndex, 'horizontal')}
                                    onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'horizontal')}
                                    style={{
                                        ...colorStyle,
                                        ...(isSolid ? { width: S + 2 * T, marginLeft: -T, marginRight: -T, zIndex: 1 } : {})
                                    }}
                                    className={clsx('cursor-pointer transition-all hover:brightness-125 relative', colorClass)}
                                    title={`H-Wall (${rIndex}, ${cIndex})`}
                                />
                            );
                        }

                        if (isWallCol) {
                            // Vertical Wall - extend solid walls to cover corners
                            const val = vertical_walls[rIndex][cIndex];
                            const el = wallElementMap.get(val);
                            const isSolid = val > 0;
                            const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown', 'wall');
                            return (
                                <div
                                    key={`${r}-${c}`}
                                    onMouseDown={() => handleMouseDown(rIndex, cIndex, 'vertical')}
                                    onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'vertical')}
                                    style={{
                                        ...colorStyle,
                                        ...(isSolid ? { height: S + 2 * T, alignSelf: 'center', zIndex: 1 } : {})
                                    }}
                                    className={clsx('cursor-pointer transition-all hover:brightness-125 relative', colorClass)}
                                    title={`V-Wall (${rIndex}, ${cIndex})`}
                                />
                            );
                        }

                        // Cell
                        const val = cells[rIndex][cIndex];
                        const el = cellElementMap.get(val);
                        const { className: colorClass, style: colorStyle } = generateColorStyle(el?.name || 'unknown', 'cell');
                        return (
                            <div
                                key={`${r}-${c}`}
                                onMouseDown={() => handleMouseDown(rIndex, cIndex, 'cell')}
                                onMouseEnter={() => handleMouseEnter(rIndex, cIndex, 'cell')}
                                style={{ ...colorStyle }}
                                className={clsx('cursor-pointer transition-all hover:opacity-90', colorClass)}
                                title={`Cell (${rIndex}, ${cIndex})`}
                            />
                        );
                    });
                })}
            </div>
        );
    }

    if (baseType === 'radial_arm') {
        return (
            <RadialArmGrid
                data={data}
                onCellClick={onRadialCellClick || (() => { })}
                onWallClick={onRadialWallClick}
                selectedLayer={selectedLayer}
                className={className}
            />
        );
    }

    return null;
}
