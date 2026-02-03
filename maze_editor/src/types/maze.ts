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

/** Level definition for 3D mazes */
export interface LevelDefinition {
    id: string;
    index: number;
}

/** Location reference for a connector endpoint */
export interface ConnectorLocation {
    level: string;  // level id
    row: number;
    col: number;
    arm?: number;  // for radial_arm_3d
}

/** Level connector (elevator or escalator) */
export interface LevelConnector {
    type: 'elevator' | 'escalator';
    from: ConnectorLocation;
    to: ConnectorLocation;
}

/** Level data for 3D mazes - contains layout for a single level */
export interface LevelData {
    id: string;
    index: number;
    /** Grid for occupancy_grid_3d type */
    grid?: number[][];
    /** Cells for edge_grid_3d type */
    cells?: number[][];
    /** Vertical walls for edge_grid_3d type */
    vertical_walls?: number[][];
    /** Horizontal walls for edge_grid_3d type */
    horizontal_walls?: number[][];
    /** Arms for radial_arm_3d type */
    arms?: RadialArmArm[];
}

/** Parsed maze data from Pyodide */
export interface MazeData {
    maze_type: MazeType;
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
    /** Levels for 3D maze types */
    levels?: LevelData[];
    /** Connectors for 3D maze types (elevators/escalators) */
    connectors?: LevelConnector[];
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

/** 2D Maze type options */
export type MazeType2D = 'occupancy_grid' | 'edge_grid' | 'radial_arm';

/** 3D Maze type options */
export type MazeType3D = 'occupancy_grid_3d' | 'edge_grid_3d' | 'radial_arm_3d';

/** All maze type options */
export type MazeType = MazeType2D | MazeType3D;

/** Helper to check if a maze type is 3D */
export function is3DMazeType(type: MazeType): type is MazeType3D {
    return type.endsWith('_3d');
}

/** Get the base 2D type for a 3D maze type */
export function getBase2DType(type: MazeType3D): MazeType2D {
    return type.replace('_3d', '') as MazeType2D;
}
