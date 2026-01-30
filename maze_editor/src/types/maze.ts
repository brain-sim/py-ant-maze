/**
 * Maze Editor Type Definitions
 * 
 * Centralized TypeScript types for the maze editor application.
 */

/** Element definition for cells or walls */
export interface MazeElement {
    name: string;
    token: string;
    value: number;
}

/** Parsed maze data from Pyodide */
export interface MazeData {
    maze_type: 'occupancy_grid' | 'edge_grid';
    /** Grid for occupancy_grid type */
    grid?: number[][];
    /** Cells for edge_grid type */
    cells?: number[][];
    /** Vertical walls for edge_grid type */
    vertical_walls?: number[][];
    /** Horizontal walls for edge_grid type */
    horizontal_walls?: number[][];
    /** Cell elements configuration */
    elements: MazeElement[];
    /** Wall elements configuration (edge_grid only) */
    wall_elements?: MazeElement[];
    /** Raw config object */
    config: Record<string, unknown>;
}

/** Result from parsing or updating maze */
export interface MazeResult {
    text: string;
    data: MazeData;
}

/** Grid types for edge_grid maze */
export type GridType = 'grid' | 'cells' | 'vertical_walls' | 'horizontal_walls';

/** Layer selection for edge_grid editing */
export type LayerType = 'cells' | 'walls';

/** Wall orientation for edge_grid */
export type WallType = 'vertical' | 'horizontal';

/** Element type when adding new elements */
export type ElementType = 'cell' | 'wall';

/** Maze type options */
export type MazeType = 'occupancy_grid' | 'edge_grid';
