/**
 * Pyodide Service
 * 
 * Handles all Python/Pyodide interactions for maze parsing and manipulation.
 * Eliminates duplicate Python code by using reusable helper functions.
 */

import { loadPyodide, type PyodideInterface } from "pyodide";
import type { MazeData, MazeResult, GridType, ElementType, MazeType } from "../types/maze";
import { DEFAULT_OCCUPANCY_YAML, DEFAULT_EDGE_YAML } from "../constants/defaults";

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

def _extract_maze_data(maze):
    """Helper to extract maze data as a dictionary - eliminates duplication."""
    data = {'maze_type': maze.maze_type}
    
    if maze.maze_type == 'occupancy_grid':
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
    
    data['config'] = maze.config.to_mapping()
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
maze = Maze.from_text(yaml_text)

if maze.maze_type == 'occupancy_grid':
    maze.layout.grid[row][col] = value
elif maze.maze_type == 'edge_grid':
    if grid_type == 'cells':
        maze.layout.cells[row][col] = value
    elif grid_type == 'vertical_walls':
        maze.layout.vertical_walls[row][col] = value
    elif grid_type == 'horizontal_walls':
        maze.layout.horizontal_walls[row][col] = value

json.dumps(_maze_to_result(maze))
  `);

    return JSON.parse(jsonResult);
}

/**
 * Resize the maze grid to new dimensions.
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
maze = Maze.from_text(yaml_text)

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
 * Create a new maze with default configuration.
 */
export async function createNewMaze(type: MazeType): Promise<MazeResult> {
    const yamlTemplate = type === 'occupancy_grid'
        ? DEFAULT_OCCUPANCY_YAML
        : DEFAULT_EDGE_YAML;

    return parseMaze(yamlTemplate.trim());
}
