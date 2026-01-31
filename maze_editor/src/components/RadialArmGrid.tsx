/**
 * RadialArmGrid Component
 * 
 * Renders a radial_arm maze using SVG.
 * - Center hub is open space (circular or polygon)
 * - Arms are straight rectangular grids connecting to the hub edge
 * - Each arm's base connects to the hub perimeter and extends outward
 */

import React from 'react';
import clsx from 'clsx';
import type { MazeData, WallType, RadialArmArm } from '../types/maze';
import { generateColorStyle } from './MazeGrid';

interface RadialArmGridProps {
    data: MazeData;
    onCellClick: (armIndex: number, row: number, col: number) => void;
    onWallClick?: (armIndex: number, row: number, col: number, wallType: WallType) => void;
    selectedLayer?: 'cells' | 'walls';
    className?: string;
}

export function RadialArmGrid({
    data,
    onCellClick,
    onWallClick,
    selectedLayer = 'cells',
    className,
}: RadialArmGridProps) {
    const { arms, hub, elements, wall_elements } = data;
    const [isDrawing, setIsDrawing] = React.useState(false);

    React.useEffect(() => {
        const handleGlobalMouseUp = () => setIsDrawing(false);
        window.addEventListener('mouseup', handleGlobalMouseUp);
        return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
    }, []);

    const cellElementMap = React.useMemo(() => {
        const map = new Map<number, { name: string; token: string; value: number }>();
        elements.forEach((e) => map.set(e.value, e));
        return map;
    }, [elements]);

    const wallElementMap = React.useMemo(() => {
        const map = new Map<number, { name: string; token: string; value: number }>();
        wall_elements?.forEach((e) => map.set(e.value, e));
        return map;
    }, [wall_elements]);

    if (!arms || !hub || arms.length === 0) {
        return null;
    }

    const armCount = arms.length;
    const angleSpan = (hub.angle_degrees * Math.PI) / 180;
    const startAngle = -Math.PI / 2; // Start from top

    // Cell and wall dimensions (matching EdgeGrid - wall thickness is 1/4 of cell size)
    const cellSize = 48;  // S in EdgeGrid
    const wallThickness = Math.floor(cellSize / 4);  // T in EdgeGrid

    // Get max arm length for canvas sizing
    const maxArmLength = Math.max(...arms.map(arm => arm.cells[0]?.length || 0));

    // Hub radius calculation (in cell units, convert to pixels)
    let hubRadius: number;
    if (hub.shape === 'circular') {
        hubRadius = (hub.radius || 2) * cellSize;
    } else {
        const sideLength = (hub.side_length || 2) * cellSize;
        const sides = hub.sides || armCount;
        hubRadius = sideLength / (2 * Math.sin(Math.PI / sides));
    }

    // Total size: hub + largest arm extending outward + padding
    const totalRadius = hubRadius + maxArmLength * cellSize + cellSize;
    const size = totalRadius * 2 + 80;
    const center = size / 2;
    // SVG color map - since Tailwind classes don't work in SVG fill, use hex values
    // These match the Tailwind colors used in EdgeGrid
    const svgColors = {
        cell: {
            wall: '#334155',    // slate-700
            open: '#f8fafc',    // slate-50
            start: '#10b981',   // emerald-500
            goal: '#f43f5e',    // rose-500
        },
        wall: {
            wall: '#475569',    // slate-600
            open: '#e2e8f0',    // slate-200
            empty: '#e2e8f0',   // slate-200
        },
    } as const;

    // Get color for an element - matching EdgeGrid color scheme
    const getElementColor = (value: number, layer: 'cell' | 'wall') => {
        const map = layer === 'cell' ? cellElementMap : wallElementMap;
        const el = map.get(value);
        const name = el?.name || 'unknown';

        // Check SVG color map first
        const colorMap = layer === 'cell' ? svgColors.cell : svgColors.wall;
        if (name in colorMap) {
            return colorMap[name as keyof typeof colorMap];
        }

        // Fallback: check if generateColorStyle returns a backgroundColor
        const { style } = generateColorStyle(name, layer);
        if (style?.backgroundColor) {
            return style.backgroundColor;
        }

        // Final fallback
        return layer === 'cell' ? '#f8fafc' : '#475569';
    };

    // Open space color for hub (same as 'open' cells)
    const openSpaceColor = '#f8fafc'; // slate-50

    const handleCellAction = (armIdx: number, row: number, col: number) => {
        if (selectedLayer !== 'cells') return;
        onCellClick(armIdx, row, col);
    };

    const handleWallAction = (armIdx: number, row: number, col: number, type: WallType) => {
        if (selectedLayer !== 'walls') return;
        onWallClick?.(armIdx, row, col, type);
    };

    const handleMouseDown = (armIdx: number, row: number, col: number, type: 'cell' | WallType) => {
        setIsDrawing(true);
        if (type === 'cell') handleCellAction(armIdx, row, col);
        else handleWallAction(armIdx, row, col, type);
    };

    const handleMouseEnter = (armIdx: number, row: number, col: number, type: 'cell' | WallType) => {
        if (isDrawing) {
            if (type === 'cell') handleCellAction(armIdx, row, col);
            else handleWallAction(armIdx, row, col, type);
        }
    };

    // Calculate angle per arm
    const anglePerArm = angleSpan / armCount;

    // Render hub as open space
    const renderHub = () => {
        if (hub.shape === 'circular') {
            if (hub.angle_degrees >= 360) {
                return (
                    <circle
                        cx={center}
                        cy={center}
                        r={hubRadius}
                        fill={openSpaceColor}
                        stroke="#cbd5e1"
                        strokeWidth={1}
                    />
                );
            } else {
                // Partial arc hub
                const endAngle = startAngle + angleSpan;
                const start = {
                    x: center + hubRadius * Math.cos(startAngle),
                    y: center + hubRadius * Math.sin(startAngle),
                };
                const end = {
                    x: center + hubRadius * Math.cos(endAngle),
                    y: center + hubRadius * Math.sin(endAngle),
                };
                const largeArc = angleSpan > Math.PI ? 1 : 0;
                const path = [
                    `M ${center} ${center}`,
                    `L ${start.x} ${start.y}`,
                    `A ${hubRadius} ${hubRadius} 0 ${largeArc} 1 ${end.x} ${end.y}`,
                    'Z'
                ].join(' ');
                return (
                    <path d={path} fill={openSpaceColor} stroke="#cbd5e1" strokeWidth={1} />
                );
            }
        } else {
            // Polygon hub
            const sides = hub.sides || armCount;
            const polygonAngleStep = (2 * Math.PI) / sides;
            const points: string[] = [];
            for (let i = 0; i < sides; i++) {
                const angle = startAngle + i * polygonAngleStep + polygonAngleStep / 2;
                const x = center + hubRadius * Math.cos(angle);
                const y = center + hubRadius * Math.sin(angle);
                points.push(`${x},${y}`);
            }
            return (
                <polygon
                    points={points.join(' ')}
                    fill={openSpaceColor}
                    stroke="#cbd5e1"
                    strokeWidth={1}
                />
            );
        }
    };

    // Render a single arm as a straight rectangular grid
    // The arm connects at the hub edge and extends outward
    const renderArm = (arm: RadialArmArm, armIdx: number) => {
        // Arm angle (center of the arm's angular position)
        const armAngle = startAngle + (armIdx + 0.5) * anglePerArm;

        // Arm dimensions
        const armWidth = arm.cells.length; // rows = width of arm (perpendicular to direction)
        const armLength = arm.cells[0]?.length || 0; // cols = length extending from hub

        const allElements: React.ReactNode[] = [];

        // Render cells as rectangles
        // Local coordinate system: 
        // - X axis: perpendicular to arm direction (across arm width)
        // - Y axis: along arm direction (outward from hub)
        // Origin (0, 0) is at the center of the arm's connection point to hub
        for (let row = 0; row < armWidth; row++) {
            for (let col = 0; col < armLength; col++) {
                const value = arm.cells[row][col];
                const fill = getElementColor(value, 'cell');
                const el = cellElementMap.get(value);

                // Position relative to arm's local origin
                // X: offset from center of arm width
                // Y: distance along arm from hub (col 0 is closest to hub)
                const localX = (row - (armWidth - 1) / 2) * cellSize;
                const localY = col * cellSize;

                allElements.push(
                    <rect
                        key={`cell-${armIdx}-${row}-${col}`}
                        x={localX - cellSize / 2}
                        y={localY}
                        width={cellSize}
                        height={cellSize}
                        fill={fill}
                        stroke="#cbd5e1"
                        strokeWidth={1}
                        style={{ pointerEvents: selectedLayer === 'cells' ? 'auto' : 'none' }}
                        className={clsx(
                            'cursor-pointer transition-all',
                            selectedLayer === 'cells' && 'hover:brightness-110'
                        )}
                        onMouseDown={() => handleMouseDown(armIdx, row, col, 'cell')}
                        onMouseEnter={() => handleMouseEnter(armIdx, row, col, 'cell')}
                    >
                        <title>Arm {armIdx} Cell ({row}, {col}) {el?.name}</title>
                    </rect>
                );
            }
        }

        // Render vertical walls (perpendicular to arm direction, at column boundaries)
        // vertical_walls: armWidth × (armLength + 1)
        for (let row = 0; row < arm.vertical_walls.length; row++) {
            for (let col = 0; col < arm.vertical_walls[row].length; col++) {
                const value = arm.vertical_walls[row][col];
                const fill = getElementColor(value, 'wall');
                const el = wallElementMap.get(value);

                const localX = (row - (armWidth - 1) / 2) * cellSize;
                const localY = col * cellSize;

                // Rectangle across the cell at this column boundary
                allElements.push(
                    <rect
                        key={`vwall-${armIdx}-${row}-${col}`}
                        x={localX - cellSize / 2}
                        y={localY - wallThickness / 2}
                        width={cellSize}
                        height={wallThickness}
                        fill={fill}
                        style={{ pointerEvents: selectedLayer === 'walls' ? 'auto' : 'none' }}
                        className={clsx(
                            'cursor-pointer transition-all',
                            selectedLayer === 'walls' && 'hover:brightness-125'
                        )}
                        onMouseDown={() => handleMouseDown(armIdx, row, col, 'vertical')}
                        onMouseEnter={() => handleMouseEnter(armIdx, row, col, 'vertical')}
                    >
                        <title>Arm {armIdx} V-Wall ({row}, {col}) {el?.name}</title>
                    </rect>
                );
            }
        }

        // Render horizontal walls (along arm sides, at row boundaries)
        // horizontal_walls: (armWidth + 1) × armLength
        for (let row = 0; row < arm.horizontal_walls.length; row++) {
            for (let col = 0; col < arm.horizontal_walls[row].length; col++) {
                const value = arm.horizontal_walls[row][col];
                const fill = getElementColor(value, 'wall');
                const el = wallElementMap.get(value);

                // Row boundary position
                const localX = (row - armWidth / 2) * cellSize;
                const localY = col * cellSize;

                // Rectangle along the arm at this row boundary
                allElements.push(
                    <rect
                        key={`hwall-${armIdx}-${row}-${col}`}
                        x={localX - wallThickness / 2}
                        y={localY}
                        width={wallThickness}
                        height={cellSize}
                        fill={fill}
                        style={{ pointerEvents: selectedLayer === 'walls' ? 'auto' : 'none' }}
                        className={clsx(
                            'cursor-pointer transition-all',
                            selectedLayer === 'walls' && 'hover:brightness-125'
                        )}
                        onMouseDown={() => handleMouseDown(armIdx, row, col, 'horizontal')}
                        onMouseEnter={() => handleMouseEnter(armIdx, row, col, 'horizontal')}
                    >
                        <title>Arm {armIdx} H-Wall ({row}, {col}) {el?.name}</title>
                    </rect>
                );
            }
        }

        // Transform: position at hub edge, rotate to point outward
        // The arm's origin (0,0) should be at the hub edge
        const hubEdgeX = center + hubRadius * Math.cos(armAngle);
        const hubEdgeY = center + hubRadius * Math.sin(armAngle);

        // Rotation: arm's local +Y axis should point OUTWARD from hub center
        // In SVG default, +Y points down. We need +Y to point in armAngle direction (away from center).
        // To rotate (0,1) to (cos θ, sin θ), we use rotation = θ - 90°
        const rotationDeg = (armAngle * 180 / Math.PI) - 90;

        return (
            <g
                key={`arm-${armIdx}`}
                transform={`translate(${hubEdgeX}, ${hubEdgeY}) rotate(${rotationDeg})`}
            >
                {allElements}
            </g>
        );
    };

    return (
        <div
            className={clsx('inline-block', className)}
            onMouseLeave={() => setIsDrawing(false)}
        >
            <svg
                width={size}
                height={size}
                viewBox={`0 0 ${size} ${size}`}
                className="bg-slate-900/50 rounded-xl"
            >
                {renderHub()}
                {arms.map((arm, idx) => renderArm(arm, idx))}
            </svg>
        </div>
    );
}
