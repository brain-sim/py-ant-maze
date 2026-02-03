/**
 * Pyodide Service
 * 
 * Handles all Python/Pyodide interactions for maze parsing and manipulation.
 * Eliminates duplicate Python code by using reusable helper functions.
 */

import { loadPyodide, type PyodideInterface } from "pyodide";
import type { MazeData, MazeResult, GridType, ElementType, MazeType } from "../types/maze";
import {
    DEFAULT_OCCUPANCY_YAML,
    DEFAULT_EDGE_YAML,
    DEFAULT_RADIAL_ARM_YAML,
    DEFAULT_RADIAL_ARM_POLYGON_YAML,
    DEFAULT_OCCUPANCY_GRID_3D_YAML,
    DEFAULT_EDGE_GRID_3D_YAML,
    DEFAULT_RADIAL_ARM_3D_YAML,
} from "../constants/defaults";

// Re-export types for convenience
export type { MazeData, MazeResult };

let pyodide: PyodideInterface | null = null;

const WHEEL_URL = "/py_ant_maze-0.1.1-py3-none-any.whl";

/**
 * Initialize and return the Pyodide instance.
 * Lazy-loads Pyodide and installs required packages.
 */
export async function getPyodide(): Promise<PyodideInterface> {
    if (pyodide) return pyodide;

    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
    });

    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");

    // Install PyYAML first (required dependency)
    await micropip.install("PyYAML");

    // Install py_ant_maze from local wheel
    await micropip.install(window.location.origin + WHEEL_URL);

    // Initialize the module and define helper function
    pyodide.runPython(`
import json
import yaml
from py_ant_maze import Maze

def _extract_level_layout(level, maze_type):
    """Extract layout data from a single level based on base maze type."""
    level_data = {
        'id': level.definition.name,
        'index': level.definition.index,
    }
    
    if 'occupancy_grid' in maze_type:
        level_data['grid'] = level.layout.grid
    elif 'edge_grid' in maze_type:
        layout = level.layout
        level_data['cells'] = layout.cells
        level_data['vertical_walls'] = layout.vertical_walls
        level_data['horizontal_walls'] = layout.horizontal_walls
    elif 'radial_arm' in maze_type:
        # For radial_arm_3d, level has arms directly (no layout wrapper)
        arms_data = []
        for arm in level.arms:
            arms_data.append({
                'cells': arm.cells,
                'vertical_walls': arm.vertical_walls,
                'horizontal_walls': arm.horizontal_walls,
            })
        level_data['arms'] = arms_data
        # Hub is shared across levels in radial_arm_3d (at root level)
    
    return level_data

def _extract_connectors(connectors):
    """Extract connector data from a list of LevelConnector objects."""
    result = []
    for conn in connectors:
        result.append({
            'type': conn.kind,
            'from': {
                'level': conn.start.level.name,
                'row': conn.start.row,
                'col': conn.start.col,
                'arm': conn.start.arm,
            },
            'to': {
                'level': conn.end.level.name,
                'row': conn.end.row,
                'col': conn.end.col,
                'arm': conn.end.arm,
            },
        })
    return result

def _extract_maze_data(maze):
    """Helper to extract maze data as a dictionary - eliminates duplication."""
    data = {'maze_type': maze.maze_type}
    
    # Check if this is a 3D maze type
    is_3d = maze.maze_type.endswith('_3d')
    
    if is_3d:
        # Extract levels and connectors for 3D mazes
        levels_data = []
        for level in maze.layout.levels:
            levels_data.append(_extract_level_layout(level, maze.maze_type))
        data['levels'] = levels_data
        
        # Extract connectors
        data['connectors'] = _extract_connectors(maze.layout.connectors)
        
        # Extract elements (same for all levels)
        data['elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.cell_elements.elements()
        ]
        
        # Wall elements for edge_grid_3d and radial_arm_3d
        if hasattr(maze.config, 'wall_elements'):
            data['wall_elements'] = [
                {'name': e.name, 'token': e.token, 'value': e.value}
                for e in maze.config.wall_elements.elements()
            ]
        
        # Hub for radial_arm_3d - hub is now at root layout level
        if 'radial_arm' in maze.maze_type:
            hub = maze.layout.hub
            data['hub'] = {
                'shape': hub.shape,
                'angle_degrees': hub.angle_degrees,
            }
            if hub.shape == 'circular':
                data['hub']['radius'] = hub.radius
            else:
                data['hub']['side_length'] = hub.side_length
    
    elif maze.maze_type == 'occupancy_grid':
        data['grid'] = maze.layout.grid
        data['elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.cell_elements.elements()
        ]
    elif maze.maze_type == 'edge_grid':
        data['cells'] = maze.layout.cells
        data['vertical_walls'] = maze.layout.vertical_walls
        data['horizontal_walls'] = maze.layout.horizontal_walls
        data['elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.cell_elements.elements()
        ]
        data['wall_elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.wall_elements.elements()
        ]
    elif maze.maze_type == 'radial_arm':
        # Arms are list of EdgeGrid-like structures
        arms_data = []
        for arm in maze.layout.arms:
            arms_data.append({
                'cells': arm.cells,
                'vertical_walls': arm.vertical_walls,
                'horizontal_walls': arm.horizontal_walls,
            })
        data['arms'] = arms_data
        hub = maze.layout.hub
        data['hub'] = {
            'shape': hub.shape,
            'angle_degrees': hub.angle_degrees,
        }
        if hub.shape == 'circular':
            data['hub']['radius'] = hub.radius
        else:
            data['hub']['side_length'] = hub.side_length
            # Note: 'sides' is derived from arm count, don't include in data
        data['elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.cell_elements.elements()
        ]
        data['wall_elements'] = [
            {'name': e.name, 'token': e.token, 'value': e.value}
            for e in maze.config.wall_elements.elements()
        ]
    
    return data

def _maze_to_result(maze):
    """Convert maze to result dict with text and data."""
    return {
        'text': maze.to_text(with_grid_numbers=True),
        'data': _extract_maze_data(maze)
    }

print("py_ant_maze loaded successfully")
  `);

    return pyodide;
}


/**
 * Parse YAML text into maze data.
 */
export async function parseMaze(yamlText: string): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);

    const jsonResult = py.runPython(`
maze = Maze.from_text(yaml_text)
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Format YAML text with proper structure.
 */
export async function formatMaze(yamlText: string): Promise<string> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);

    return py.runPython(`
maze = Maze.from_text(yaml_text)
maze.to_text(with_grid_numbers=True)
  `);
}

/**
 * Update a cell or wall value in the maze.
 */
export async function updateMaze(
    yamlText: string,
    row: number,
    col: number,
    value: number,
    gridType: GridType = 'grid'
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("row", row);
    py.globals.set("col", col);
    py.globals.set("value", value);
    py.globals.set("grid_type", gridType);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access
maze = Maze.from_text(yaml_text).thaw()

if maze.maze_type == 'occupancy_grid':
    maze.layout.grid[row][col] = value
elif maze.maze_type == 'edge_grid':
    if grid_type == 'cells':
        maze.layout.cells[row][col] = value
    elif grid_type == 'vertical_walls':
        maze.layout.vertical_walls[row][col] = value
    elif grid_type == 'horizontal_walls':
        maze.layout.horizontal_walls[row][col] = value

maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Update a cell or wall value within a specific arm of a radial_arm maze.
 */
export async function updateRadialArmCell(
    yamlText: string,
    armIndex: number,
    row: number,
    col: number,
    value: number,
    gridType: 'cells' | 'vertical_walls' | 'horizontal_walls' = 'cells'
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("arm_index", armIndex);
    py.globals.set("row", row);
    py.globals.set("col", col);
    py.globals.set("value", value);
    py.globals.set("grid_type", gridType);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access
maze = Maze.from_text(yaml_text).thaw()

if maze.maze_type != 'radial_arm':
    raise ValueError('updateRadialArmCell only works with radial_arm mazes')

arm = maze.layout.arms[arm_index]
if grid_type == 'cells':
    arm.cells[row][col] = value
elif grid_type == 'vertical_walls':
    arm.vertical_walls[row][col] = value
elif grid_type == 'horizontal_walls':
    arm.horizontal_walls[row][col] = value

maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Resize the maze grid to new dimensions.
 * For 3D mazes, resizes all levels to the same dimensions.
 */
export async function resizeMaze(
    yamlText: string,
    newRows: number,
    newCols: number,
    defaultValue: number
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("new_rows", newRows);
    py.globals.set("new_cols", newCols);
    py.globals.set("default_value", defaultValue);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access
maze = Maze.from_text(yaml_text).thaw()

def resize_grid(grid, target_rows, target_cols, fill_value):
    current_rows = len(grid)
    current_cols = len(grid[0]) if grid else 0
    
    # Adjust rows
    if target_rows > current_rows:
        for _ in range(target_rows - current_rows):
            grid.append([fill_value] * current_cols)
    elif target_rows < current_rows:
        grid[:] = grid[:target_rows]
        
    # Adjust cols for each row
    for row in grid:
        current_row_len = len(row)
        if target_cols > current_row_len:
            row.extend([fill_value] * (target_cols - current_row_len))
        elif target_cols < current_row_len:
            row[:] = row[:target_cols]

if maze.maze_type == 'occupancy_grid':
    resize_grid(maze.layout.grid, new_rows, new_cols, default_value)
elif maze.maze_type == 'edge_grid':
    resize_grid(maze.layout.cells, new_rows, new_cols, default_value)
    # Walls have slightly different dimensions
    # vertical: H x (W+1)
    # horizontal: (H+1) x W
    resize_grid(maze.layout.vertical_walls, new_rows, new_cols + 1, 0)
    resize_grid(maze.layout.horizontal_walls, new_rows + 1, new_cols, 0)
elif maze.maze_type == 'occupancy_grid_3d':
    # Resize all levels for 3D occupancy grid
    for level in maze.layout.levels:
        resize_grid(level.layout.grid, new_rows, new_cols, default_value)
elif maze.maze_type == 'edge_grid_3d':
    # Resize all levels for 3D edge grid
    for level in maze.layout.levels:
        resize_grid(level.layout.cells, new_rows, new_cols, default_value)
        resize_grid(level.layout.vertical_walls, new_rows, new_cols + 1, 0)
        resize_grid(level.layout.horizontal_walls, new_rows + 1, new_cols, 0)
# radial_arm resize not supported - use resizeRadialArm instead

maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Resize a specific arm in a radial arm maze.
 * Width is the number of rows (arm width), Length is the number of columns (arm length).
 */
export async function resizeRadialArm(
    yamlText: string,
    armIndex: number,
    newWidth: number,
    newLength: number,
    defaultCellValue: number,
    defaultWallValue: number
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("arm_index", armIndex);
    py.globals.set("new_width", newWidth);
    py.globals.set("new_length", newLength);
    py.globals.set("default_cell_value", defaultCellValue);
    py.globals.set("default_wall_value", defaultWallValue);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access (Maze objects are frozen)
maze = Maze.from_text(yaml_text).thaw()

def resize_grid(grid, target_rows, target_cols, fill_value):
    current_rows = len(grid)
    current_cols = len(grid[0]) if grid else 0
    
    # Adjust rows
    if target_rows > current_rows:
        for _ in range(target_rows - current_rows):
            grid.append([fill_value] * current_cols)
    elif target_rows < current_rows:
        grid[:] = grid[:target_rows]
        
    # Adjust cols for each row
    for row in grid:
        current_row_len = len(row)
        if target_cols > current_row_len:
            row.extend([fill_value] * (target_cols - current_row_len))
        elif target_cols < current_row_len:
            row[:] = row[:target_cols]

if maze.maze_type == 'radial_arm':
    arm = maze.layout.arms[arm_index]
    # Cells: width (rows) x length (cols)
    resize_grid(arm.cells, new_width, new_length, default_cell_value)
    # Vertical walls: width x (length + 1)
    resize_grid(arm.vertical_walls, new_width, new_length + 1, default_wall_value)
    # Horizontal walls: (width + 1) x length
    resize_grid(arm.horizontal_walls, new_width + 1, new_length, default_wall_value)
    
    # Recalculate minimum hub size based on new arm widths
    import math
    hub = maze.layout.hub
    arm_widths = [len(a.cells) for a in maze.layout.arms]
    
    if hub.shape == 'circular':
        # Minimum radius based on max arm width - assume all arms have max width
        # This ensures the hub can properly connect to the widest arm
        angle_radians = math.radians(hub.angle_degrees)
        max_width = max(arm_widths)
        arm_count = len(arm_widths)
        total_width = max_width * arm_count
        min_radius = total_width / angle_radians
        if hub.radius is None or hub.radius < min_radius:
            hub.radius = min_radius
    elif hub.shape == 'polygon':
        # Minimum side_length = max arm width
        min_side = max(arm_widths)
        if hub.side_length is None or hub.side_length < min_side:
            hub.side_length = float(min_side)

# Freeze back to Maze for result
maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}


/**
 * Set the number of arms in a radial arm maze.
 * Adds new arms (copying from the last arm) or removes arms from the end.
 */
export async function setRadialArmCount(
    yamlText: string,
    newCount: number,
    defaultCellValue: number = 0,
    defaultWallValue: number = 1
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("new_count", newCount);
    py.globals.set("default_cell_value", defaultCellValue);
    py.globals.set("default_wall_value", defaultWallValue);

    const jsonResult = py.runPython(`
import json
from py_ant_maze.mazes.two_d.edge_grid import EdgeGridLayout

maze = Maze.from_text(yaml_text).thaw()

if maze.maze_type != 'radial_arm':
    raise ValueError("setRadialArmCount only works on radial_arm mazes")

current_count = len(maze.layout.arms)
target_count = new_count

if target_count < 1:
    raise ValueError("Must have at least 1 arm")

if target_count > current_count:
    # Add new arms - copy structure from the last existing arm
    template_arm = maze.layout.arms[-1]
    rows = len(template_arm.cells)
    cols = len(template_arm.cells[0]) if template_arm.cells else 4
    
    for _ in range(target_count - current_count):
        # Create new arm with same dimensions as template
        new_cells = [[default_cell_value] * cols for _ in range(rows)]
        new_v_walls = [[default_wall_value] * (cols + 1) for _ in range(rows)]
        new_h_walls = [[default_wall_value] * cols for _ in range(rows + 1)]
        
        # Create EdgeGridLayout for the new arm
        new_arm = EdgeGridLayout(
            cells=new_cells,
            vertical_walls=new_v_walls,
            horizontal_walls=new_h_walls
        )
        maze.layout.arms.append(new_arm)
        
elif target_count < current_count:
    # Remove arms from the end
    maze.layout.arms = maze.layout.arms[:target_count]

# Recalculate minimum hub size based on new arm count
import math
hub = maze.layout.hub
arm_widths = [len(a.cells) for a in maze.layout.arms]

if hub.shape == 'circular':
    # Minimum radius based on max arm width × arm count
    angle_radians = math.radians(hub.angle_degrees)
    max_width = max(arm_widths)
    arm_count = len(arm_widths)
    total_width = max_width * arm_count
    min_radius = total_width / angle_radians
    if hub.radius is None or hub.radius < min_radius:
        hub.radius = min_radius
elif hub.shape == 'polygon':
    # Minimum side_length = max arm width
    min_side = max(arm_widths)
    if hub.side_length is None or hub.side_length < min_side:
        hub.side_length = float(min_side)

# Freeze back to Maze for result
maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Set the angle degrees (angular span) of a radial arm hub.
 */
export async function setRadialArmAngle(
    yamlText: string,
    angleDegrees: number
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("angle_degrees", angleDegrees);

    const jsonResult = py.runPython(`
import json

maze = Maze.from_text(yaml_text).thaw()

if maze.maze_type != 'radial_arm':
    raise ValueError("setRadialArmAngle only works on radial_arm mazes")

if angle_degrees < 1 or angle_degrees > 360:
    raise ValueError("angle_degrees must be between 1 and 360")

maze.layout.hub.angle_degrees = float(angle_degrees)

# Freeze back to Maze for result
maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Set the hub size (radius for circular, side_length for polygon).
 */
export async function setRadialArmHubSize(
    yamlText: string,
    size: number
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("new_size", size);

    const jsonResult = py.runPython(`
import json
import math

maze = Maze.from_text(yaml_text).thaw()

if maze.maze_type != 'radial_arm':
    raise ValueError("setRadialArmHubSize only works on radial_arm mazes")

hub = maze.layout.hub
arm_widths = [len(a.cells) for a in maze.layout.arms]

if hub.shape == 'circular':
    # Calculate minimum radius
    angle_radians = math.radians(hub.angle_degrees)
    max_width = max(arm_widths)
    arm_count = len(arm_widths)
    total_width = max_width * arm_count
    min_radius = total_width / angle_radians
    
    if new_size < min_radius:
        raise ValueError(f"Hub radius must be >= {min_radius:.2f}")
    hub.radius = float(new_size)
elif hub.shape == 'polygon':
    # Minimum side_length = max arm width
    min_side = max(arm_widths)
    if new_size < min_side:
        raise ValueError(f"Side length must be >= {min_side:.2f}")
    hub.side_length = float(new_size)

# Freeze back to Maze for result
maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Add a new element to the maze configuration.
 */
export async function addElement(
    yamlText: string,
    name: string,
    token: string,
    elementType: ElementType = 'cell'
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("new_name", name);
    py.globals.set("new_token", token);
    py.globals.set("element_type", elementType);

    const jsonResult = py.runPython(`
# Convert JS strings to Python strings
yaml_text_str = str(yaml_text)
new_name_str = str(new_name)
new_token_str = str(new_token)
element_type_str = str(element_type)

data_dict = yaml.safe_load(yaml_text_str)
if 'config' not in data_dict:
    data_dict['config'] = {}

key = 'cell_elements' if element_type_str == 'cell' else 'wall_elements'
if key not in data_dict['config']:
    data_dict['config'][key] = []

elements = data_dict['config'][key]

for el in elements:
    if el.get('name') == new_name_str:
        raise ValueError(f"Element with name '{new_name_str}' already exists in {key}")
    if el.get('token') == new_token_str:
        raise ValueError(f"Element with token '{new_token_str}' already exists in {key}")

elements.append({'name': new_name_str, 'token': new_token_str})

# Convert to ensure proper Python dict with string keys
data_dict_clean = json.loads(json.dumps(data_dict))
temp_yaml = yaml.safe_dump(data_dict_clean, sort_keys=False, default_flow_style=False)

maze = Maze.from_text(temp_yaml)
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Update a cell value within a specific level of a 3D maze.
 */
export async function update3DMazeCell(
    yamlText: string,
    levelIndex: number,
    row: number,
    col: number,
    value: number,
    gridType: GridType = 'grid'
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("level_index", levelIndex);
    py.globals.set("row", row);
    py.globals.set("col", col);
    py.globals.set("value", value);
    py.globals.set("grid_type", gridType);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access
maze = Maze.from_text(yaml_text).thaw()

level = maze.layout.levels[level_index]
layout = level.layout

if 'occupancy_grid' in maze.maze_type:
    layout.grid[row][col] = value
elif 'edge_grid' in maze.maze_type:
    if grid_type == 'cells':
        layout.cells[row][col] = value
    elif grid_type == 'vertical_walls':
        layout.vertical_walls[row][col] = value
    elif grid_type == 'horizontal_walls':
        layout.horizontal_walls[row][col] = value

maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Update a cell or wall within a specific arm of a specific level in radial_arm_3d.
 */
export async function update3DRadialArmCell(
    yamlText: string,
    levelIndex: number,
    armIndex: number,
    row: number,
    col: number,
    value: number,
    gridType: 'cells' | 'vertical_walls' | 'horizontal_walls' = 'cells'
): Promise<MazeResult> {
    const py = await getPyodide();
    py.globals.set("yaml_text", yamlText);
    py.globals.set("level_index", levelIndex);
    py.globals.set("arm_index", armIndex);
    py.globals.set("row", row);
    py.globals.set("col", col);
    py.globals.set("value", value);
    py.globals.set("grid_type", gridType);

    const jsonResult = py.runPython(`
# Use MazeDraft for mutable access
maze = Maze.from_text(yaml_text).thaw()

if 'radial_arm' not in maze.maze_type:
    raise ValueError('update3DRadialArmCell only works with radial_arm mazes')

level = maze.layout.levels[level_index]
arm = level.layout.arms[arm_index]

if grid_type == 'cells':
    arm.cells[row][col] = value
elif grid_type == 'vertical_walls':
    arm.vertical_walls[row][col] = value
elif grid_type == 'horizontal_walls':
    arm.horizontal_walls[row][col] = value

maze = maze.freeze()
json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Create a new maze with default configuration.
 */
export async function createNewMaze(
    type: MazeType,
    hubType?: 'circular' | 'polygon'
): Promise<MazeResult> {
    let yamlTemplate: string;
    if (type === 'occupancy_grid') {
        yamlTemplate = DEFAULT_OCCUPANCY_YAML;
    } else if (type === 'edge_grid') {
        yamlTemplate = DEFAULT_EDGE_YAML;
    } else if (type === 'radial_arm') {
        if (hubType === 'polygon') {
            yamlTemplate = DEFAULT_RADIAL_ARM_POLYGON_YAML;
        } else {
            yamlTemplate = DEFAULT_RADIAL_ARM_YAML;
        }
    } else if (type === 'occupancy_grid_3d') {
        yamlTemplate = DEFAULT_OCCUPANCY_GRID_3D_YAML;
    } else if (type === 'edge_grid_3d') {
        yamlTemplate = DEFAULT_EDGE_GRID_3D_YAML;
    } else if (type === 'radial_arm_3d') {
        yamlTemplate = DEFAULT_RADIAL_ARM_3D_YAML;
    } else {
        yamlTemplate = DEFAULT_OCCUPANCY_YAML;
    }

    return parseMaze(yamlTemplate.trim());
}
