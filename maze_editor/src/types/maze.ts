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

/** Hub configuration for radial_arm maze type */
export interface RadialArmHub {
    shape: 'circular' | 'polygon';
    angle_degrees: number;
    radius?: number;        // For circular shape
    side_length?: number;   // For polygon shape
    sides?: number;         // For polygon shape
}

/** Individual arm in radial_arm maze (EdgeGrid-like structure) */
export interface RadialArmArm {
    cells: number[][];           // width × length grid
    vertical_walls: number[][];  // width × (length + 1)
    horizontal_walls: number[][]; // (width + 1) × length
}

/** Parsed maze data from Pyodide */
export interface MazeData {
    maze_type: 'occupancy_grid' | 'edge_grid' | 'radial_arm';
    /** Grid for occupancy_grid type */
    grid?: number[][];
    /** Cells for edge_grid type */
    cells?: number[][];
    /** Vertical walls for edge_grid type */
    vertical_walls?: number[][];
    /** Horizontal walls for edge_grid type */
    horizontal_walls?: number[][];
    /** Arms for radial_arm type (list of EdgeGrid-like structures) */
    arms?: RadialArmArm[];
    /** Hub configuration for radial_arm type */
    hub?: RadialArmHub;
    /** Cell elements configuration */
    elements: MazeElement[];
    /** Wall elements configuration (edge_grid and radial_arm) */
    wall_elements?: MazeElement[];
    /** Raw config object */
    config: Record<string, unknown>;
}

/** Result from parsing or updating maze */
export interface MazeResult {
    text: string;
    data: MazeData;
}

/** Grid types for maze editing */
export type GridType = 'grid' | 'cells' | 'vertical_walls' | 'horizontal_walls';

/** Layer selection for edge_grid/radial_arm editing */
export type LayerType = 'cells' | 'walls';

/** Wall orientation for edge_grid and radial_arm */
export type WallType = 'vertical' | 'horizontal';

/** Element type when adding new elements */
export type ElementType = 'cell' | 'wall';

/** Maze type options */
export type MazeType = 'occupancy_grid' | 'edge_grid' | 'radial_arm';

