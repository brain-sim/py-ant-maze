/**
 * Default Values and Constants
 * 
 * Centralized constants for the maze editor application.
 */

/** Default YAML for a new occupancy grid maze */
export const DEFAULT_OCCUPANCY_YAML = `maze_type: occupancy_grid
config:
  cell_elements:
    - name: wall
      token: "#"
    - name: open
      token: "."
layout:
  grid: |
    ___ 0 1 2 3 4 5 6 7
    0 | # # # # # # # #
    1 | # . . . . . . #
    2 | # . # # # # . #
    3 | # . # . . # . #
    4 | # . # . . # . #
    5 | # . # # # # . #
    6 | # . . . . . . #
    7 | # # # # # # # #
`;

/** Default YAML for a new edge grid maze */
export const DEFAULT_EDGE_YAML = `maze_type: edge_grid
config:
  cell_elements:
    - {name: open, token: "."}
  wall_elements:
    - {name: wall, token: "#"}
    - {name: empty, token: "-"}
layout:
  cells: |
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
    . . . . . . . .
  walls:
    vertical: |
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
      # - - - - - - - #
    horizontal: |
      # # # # # # # #
      - - - - - - - -
      - - - - - - - -
      - - - - - - - -
      - - - - - - - -
      - - - - - - - -
      - - - - - - - -
      - - - - - - - -
      # # # # # # # #
`;

/** Cell element colors - slightly warmer/brighter */
export const CELL_ELEMENT_COLORS: Record<string, string> = {
    wall: 'bg-slate-700 hover:bg-slate-600',
    open: 'bg-slate-50 hover:bg-white',
    start: 'bg-emerald-500 hover:bg-emerald-400',
    goal: 'bg-rose-500 hover:bg-rose-400',
};

/** Wall element colors - slightly cooler/muted */
export const WALL_ELEMENT_COLORS: Record<string, string> = {
    wall: 'bg-slate-600 hover:bg-slate-500',
    open: 'bg-slate-200 hover:bg-slate-100',
    empty: 'bg-slate-200 hover:bg-slate-100',
};

/** Legacy/compatibility - used when layer is not specified */
export const ELEMENT_COLORS: Record<string, string> = {
    ...CELL_ELEMENT_COLORS,
    empty: 'bg-slate-200 hover:bg-slate-100',
};

/** Grid calculation constants */
export const GRID_CONFIG = {
    MIN_CELL_SIZE: 24,
    MAX_CELL_SIZE: 48,
    TARGET_DIMENSION: 600,
} as const;

/** Export image configuration */
export const IMAGE_EXPORT_CONFIG = {
    backgroundColor: '#1e293b', // slate-800
} as const;
