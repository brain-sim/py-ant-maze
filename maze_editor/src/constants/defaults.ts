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

/** Default YAML for a new radial arm maze with circular hub */
export const DEFAULT_RADIAL_ARM_YAML = `maze_type: radial_arm
config:
  cell_elements:
    - name: open
      token: "."
  wall_elements:
    - name: wall
      token: "#"
    - name: open
      token: "-"
layout:
  center_hub:
    shape: circular
    angle_degrees: 360
    radius: 2.0
  arms:
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
`;

/** Default YAML for a new radial arm maze with polygon hub */
export const DEFAULT_RADIAL_ARM_POLYGON_YAML = `maze_type: radial_arm
config:
  cell_elements:
    - name: open
      token: "."
  wall_elements:
    - name: wall
      token: "#"
    - name: open
      token: "-"
layout:
  center_hub:
    shape: polygon
    angle_degrees: 360
    side_length: 2.0
  arms:
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
`;

/** Default YAML for a new 3D occupancy grid maze */
export const DEFAULT_OCCUPANCY_GRID_3D_YAML = `maze_type: occupancy_grid_3d
config:
  cell_elements:
    - name: open
      token: '.'
    - name: wall
      token: '#'
    - name: elevator
      token: 'E'
    - name: escalator
      token: 'S'
layout:
  levels:
    - id: ground
      layout:
        grid: |
          # # # # #
          # . E . #
          # . . . #
          # S . . #
          # # # # #
    - id: upper
      layout:
        grid: |
          # # # # #
          # . E . #
          # . . . #
          # . . S #
          # # # # #
  connectors:
    - type: elevator
      from: {level: ground, row: 1, col: 2}
      to: {level: upper, row: 1, col: 2}
    - type: escalator
      from: {level: ground, row: 3, col: 1}
      to: {level: upper, row: 3, col: 3}
`;

/** Default YAML for a new 3D edge grid maze */
export const DEFAULT_EDGE_GRID_3D_YAML = `maze_type: edge_grid_3d
config:
  cell_elements:
    - name: open
      token: '.'
    - name: elevator
      token: 'E'
    - name: escalator
      token: 'S'
  wall_elements:
    - name: wall
      token: '#'
    - name: open
      token: '-'
layout:
  levels:
    - id: ground
      layout:
        cells: |
          E S . .
          . . . .
          . . . .
        walls:
          vertical: |
            # # # # #
            # # # # #
            # # # # #
          horizontal: |
            # # # #
            # # # #
            # # # #
            # # # #
    - id: upper
      layout:
        cells: |
          E . . .
          S . . .
          . . . .
        walls:
          vertical: |
            # # # # #
            # # # # #
            # # # # #
          horizontal: |
            # # # #
            # # # #
            # # # #
            # # # #
  connectors:
    - type: elevator
      from: {level: ground, row: 0, col: 0}
      to: {level: upper, row: 0, col: 0}
    - type: escalator
      from: {level: ground, row: 0, col: 1}
      to: {level: upper, row: 1, col: 0}
`;

/** Default YAML for a new 3D radial arm maze */
export const DEFAULT_RADIAL_ARM_3D_YAML = `maze_type: radial_arm_3d
config:
  cell_elements:
    - name: open
      token: '.'
    - name: elevator
      token: 'E'
    - name: escalator
      token: 'S'
  wall_elements:
    - name: wall
      token: '#'
    - name: open
      token: '-'
layout:
  center_hub:
    shape: polygon
    angle_degrees: 360
    side_length: 2.0
  levels:
    - id: ground
      layout:
        arms:
          - layout:
              cells: |
                E . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                . . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                . S . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                . . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
    - id: upper
      layout:
        arms:
          - layout:
              cells: |
                E . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                . . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                S . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
          - layout:
              cells: |
                . . . .
              walls:
                vertical: |
                  # # # # #
                horizontal: |
                  # # # #
                  # # # #
  connectors:
    - type: elevator
      from: {level: ground, row: 0, col: 0, arm: 0}
      to: {level: upper, row: 0, col: 0, arm: 0}
    - type: escalator
      from: {level: ground, row: 0, col: 1, arm: 2}
      to: {level: upper, row: 0, col: 0, arm: 2}
`;
