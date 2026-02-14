/**
 * useMaze Hook
 * 
 * Manages all maze-related state and operations.
 */

import { useState, useCallback, useEffect } from 'react';
import type { MazeData, LayerType, MazeType, ElementType, WallType } from '../types/maze';
import { is3DMazeType } from '../types/maze';
import {
    getPyodide,
    parseMaze,
    formatMaze,
    updateMaze,
    updateRadialArmCell,
    update3DMazeCell,
    resizeMaze,
    resizeRadialArm,
    setRadialArmCount,
    setRadialArmAngle,
    setRadialArmHubSize,
    setLevelCount,
    addElement,
    createNewMaze,
} from '../services/pyodide';
import { DEFAULT_OCCUPANCY_YAML } from '../constants/defaults';

export interface UseMazeState {
    /** Whether Pyodide is loading */
    loading: boolean;
    /** Current error message, if any */
    error: string | null;
    /** Raw YAML input text */
    input: string;
    /** Parsed maze data */
    mazeData: MazeData | null;
    /** Selected cell element value */
    selectedElementValue: number;
    /** Selected wall element value */
    selectedWallElementValue: number;
    /** Currently selected layer (cells or walls) */
    selectedLayer: LayerType;
    /** Currently selected level index (for 3D mazes) */
    selectedLevelIndex: number;
}

export interface UseMazeActions {
    /** Set the YAML input text */
    setInput: (text: string) => void;
    /** Set the selected cell element */
    setSelectedElementValue: (value: number) => void;
    /** Set the selected wall element */
    setSelectedWallElementValue: (value: number) => void;
    /** Set the selected layer */
    setSelectedLayer: (layer: LayerType) => void;
    /** Set the selected level index (for 3D mazes) */
    setSelectedLevelIndex: (index: number) => void;
    /** Parse the current input (or provided YAML text) */
    parse: (yamlText?: string) => Promise<void>;
    /** Format and parse the current input */
    format: () => Promise<void>;
    /** Update a cell value (for occupancy_grid and edge_grid) */
    updateCell: (row: number, col: number) => Promise<void>;
    /** Update a wall value (for edge_grid) */
    updateWall: (row: number, col: number, wallType: WallType) => Promise<void>;
    /** Update a radial_arm cell (arm index + row/col within arm) */
    updateRadialCell: (armIndex: number, row: number, col: number) => Promise<void>;
    /** Update a radial_arm wall (arm index + row/col within arm) */
    updateRadialWall: (armIndex: number, row: number, col: number, wallType: WallType) => Promise<void>;
    /** Resize the maze grid */
    resize: (rows: number, cols: number) => Promise<void>;
    /** Resize a specific arm in radial_arm maze */
    resizeArm: (armIndex: number, width: number, length: number) => Promise<void>;
    /** Set the number of arms in radial_arm maze */
    setArmCount: (count: number) => Promise<void>;
    /** Set the hub angle degrees in radial_arm maze */
    setAngle: (degrees: number) => Promise<void>;
    /** Set the hub size (radius or side_length) in radial_arm maze */
    setHubSize: (size: number) => Promise<void>;
    /** Add a new element */
    addNewElement: (name: string, token: string, type: ElementType) => Promise<void>;
    /** Set the number of levels in 3D maze */
    setLevelCountAction: (count: number) => Promise<void>;
    /** Create a new maze of the specified type */
    create: (type: MazeType) => Promise<void>;
    /** Clear the current error */
    clearError: () => void;
}

export type UseMazeResult = UseMazeState & UseMazeActions;

/**
 * Hook for managing maze state and operations.
 */
export function useMaze(): UseMazeResult {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [input, setInput] = useState(DEFAULT_OCCUPANCY_YAML);
    const [mazeData, setMazeData] = useState<MazeData | null>(null);
    const [selectedElementValue, setSelectedElementValue] = useState(0);
    const [selectedWallElementValue, setSelectedWallElementValue] = useState(1);
    const [selectedLayer, setSelectedLayer] = useState<LayerType>('cells');
    const [selectedLevelIndex, setSelectedLevelIndex] = useState(0);

    const syncSelectionState = useCallback((data: MazeData) => {
        const cellElements = data.elements ?? [];
        const wallElements = data.wall_elements ?? [];

        if (cellElements.length > 0) {
            const validCellValues = new Set(cellElements.map((el) => el.value));
            setSelectedElementValue((prev) => (
                validCellValues.has(prev) ? prev : cellElements[0].value
            ));
        }

        if (wallElements.length > 0) {
            const validWallValues = new Set(wallElements.map((el) => el.value));
            setSelectedWallElementValue((prev) => (
                validWallValues.has(prev) ? prev : wallElements[0].value
            ));
        }

        setSelectedLayer((prev) => (
            prev === 'walls' && wallElements.length === 0 ? 'cells' : prev
        ));

        if (is3DMazeType(data.maze_type)) {
            const levelCount = data.levels?.length ?? 0;
            const maxIndex = Math.max(0, levelCount - 1);
            setSelectedLevelIndex((prev) => Math.min(prev, maxIndex));
        } else {
            setSelectedLevelIndex(0);
        }
    }, []);

    const applyMazeResult = useCallback((result: { text: string; data: MazeData }) => {
        setInput(result.text);
        setMazeData(result.data);
        syncSelectionState(result.data);
        setError(null);
    }, [syncSelectionState]);

    // Parse YAML and update maze data
    const parse = useCallback(async (yamlText?: string) => {
        try {
            const textToParse = typeof yamlText === 'string' ? yamlText : input;
            const { data } = await parseMaze(textToParse);
            setMazeData(data);
            syncSelectionState(data);
            setError(null);
        } catch (err) {
            setError(String(err));
            setMazeData(null);
        }
    }, [input, syncSelectionState]);

    // Initialize Pyodide and parse default maze
    useEffect(() => {
        getPyodide()
            .then(async () => {
                setLoading(false);
                const result = await parseMaze(DEFAULT_OCCUPANCY_YAML);
                applyMazeResult(result);
            })
            .catch((err) => {
                console.error(err);
                setError("Failed to load Pyodide: " + err.message);
                setLoading(false);
            });
    }, [applyMazeResult]);

    // Format and parse
    const format = useCallback(async () => {
        try {
            const result = await formatMaze(input);
            setInput(result);
            await parse(result);
            setError(null);
        } catch (err) {
            setError(String(err));
        }
    }, [input, parse]);

    // Update a cell (works for both 2D and 3D mazes)
    const updateCell = useCallback(async (row: number, col: number) => {
        if (!mazeData) return;
        if (mazeData.maze_type === 'radial_arm' || mazeData.maze_type === 'radial_arm_3d') return; // Use updateRadialCell instead

        const is3D = is3DMazeType(mazeData.maze_type);
        const isOccupancyGrid = mazeData.maze_type === 'occupancy_grid' || mazeData.maze_type === 'occupancy_grid_3d';

        // For occupancy_grid, cells and walls share the same grid.
        // Use the wall element value when the walls layer is selected.
        const paintValue = (isOccupancyGrid && selectedLayer === 'walls')
            ? selectedWallElementValue
            : selectedElementValue;

        // Get current value based on maze type
        let currentVal: number | undefined;
        if (is3D) {
            const level = mazeData.levels?.[selectedLevelIndex];
            if (mazeData.maze_type === 'occupancy_grid_3d') {
                currentVal = level?.grid?.[row]?.[col];
            } else if (mazeData.maze_type === 'edge_grid_3d') {
                currentVal = level?.cells?.[row]?.[col];
            }
        } else {
            if (mazeData.maze_type === 'occupancy_grid') {
                currentVal = mazeData.grid?.[row][col];
            } else if (mazeData.maze_type === 'edge_grid') {
                currentVal = mazeData.cells?.[row][col];
            }
        }
        if (currentVal === paintValue) return;

        try {
            let result;
            if (is3D) {
                result = await update3DMazeCell(input, selectedLevelIndex, row, col, paintValue, isOccupancyGrid ? 'grid' : 'cells');
            } else {
                result = await updateMaze(input, row, col, paintValue, isOccupancyGrid ? 'grid' : 'cells');
            }
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, selectedWallElementValue, selectedLayer, selectedLevelIndex, applyMazeResult]);

    // Update a wall (edge_grid and edge_grid_3d)
    const updateWall = useCallback(async (
        row: number,
        col: number,
        wallType: WallType
    ) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'edge_grid' && mazeData.maze_type !== 'edge_grid_3d') return;

        const is3D = is3DMazeType(mazeData.maze_type);

        // Get current value based on wall type
        let currentVal: number | undefined;
        if (is3D) {
            const level = mazeData.levels?.[selectedLevelIndex];
            if (wallType === 'vertical') {
                currentVal = level?.vertical_walls?.[row]?.[col];
            } else if (wallType === 'horizontal') {
                currentVal = level?.horizontal_walls?.[row]?.[col];
            }
        } else {
            if (wallType === 'vertical') {
                currentVal = mazeData.vertical_walls?.[row][col];
            } else if (wallType === 'horizontal') {
                currentVal = mazeData.horizontal_walls?.[row][col];
            }
        }
        if (currentVal === selectedWallElementValue) return;

        const gridType = wallType === 'vertical' ? 'vertical_walls' : 'horizontal_walls';

        try {
            let result;
            if (is3D) {
                result = await update3DMazeCell(input, selectedLevelIndex, row, col, selectedWallElementValue, gridType);
            } else {
                result = await updateMaze(input, row, col, selectedWallElementValue, gridType);
            }
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedWallElementValue, selectedLevelIndex, applyMazeResult]);

    // Update a radial_arm cell
    const updateRadialCell = useCallback(async (
        armIndex: number,
        row: number,
        col: number
    ) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;

        // Get current value based on 2D or 3D
        let currentVal: number | undefined;
        if (mazeData.maze_type === 'radial_arm_3d') {
            const level = mazeData.levels?.[selectedLevelIndex];
            currentVal = level?.arms?.[armIndex]?.cells?.[row]?.[col];
        } else {
            const arm = mazeData.arms?.[armIndex];
            currentVal = arm?.cells?.[row]?.[col];
        }
        if (currentVal === selectedElementValue) return;

        try {
            const levelIndex = mazeData.maze_type === 'radial_arm_3d' ? selectedLevelIndex : undefined;
            const result = await updateRadialArmCell(input, armIndex, row, col, selectedElementValue, 'cells', levelIndex);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, selectedLevelIndex, applyMazeResult]);

    // Update a radial_arm wall
    const updateRadialWall = useCallback(async (
        armIndex: number,
        row: number,
        col: number,
        wallType: WallType
    ) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;

        // Get current value based on 2D or 3D
        let currentVal: number | undefined;
        if (mazeData.maze_type === 'radial_arm_3d') {
            const level = mazeData.levels?.[selectedLevelIndex];
            const arm = level?.arms?.[armIndex];
            if (wallType === 'vertical') {
                currentVal = arm?.vertical_walls?.[row]?.[col];
            } else if (wallType === 'horizontal') {
                currentVal = arm?.horizontal_walls?.[row]?.[col];
            }
        } else {
            const arm = mazeData.arms?.[armIndex];
            if (wallType === 'vertical') {
                currentVal = arm?.vertical_walls?.[row]?.[col];
            } else if (wallType === 'horizontal') {
                currentVal = arm?.horizontal_walls?.[row]?.[col];
            }
        }
        if (currentVal === selectedWallElementValue) return;

        const gridType = wallType === 'vertical' ? 'vertical_walls' : 'horizontal_walls';

        try {
            const levelIndex = mazeData.maze_type === 'radial_arm_3d' ? selectedLevelIndex : undefined;
            const result = await updateRadialArmCell(input, armIndex, row, col, selectedWallElementValue, gridType, levelIndex);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedWallElementValue, selectedLevelIndex, applyMazeResult]);

    // Resize the maze
    const resize = useCallback(async (rows: number, cols: number) => {
        if (!mazeData) return;

        try {
            const result = await resizeMaze(input, rows, cols, selectedElementValue);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, applyMazeResult]);

    // Resize a specific arm in radial_arm maze
    const resizeArm = useCallback(async (armIndex: number, width: number, length: number) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;

        try {
            const result = await resizeRadialArm(
                input, armIndex, width, length,
                selectedElementValue,
                selectedWallElementValue
            );
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, selectedWallElementValue, applyMazeResult]);

    // Set the number of arms in radial_arm maze
    const setArmCount = useCallback(async (count: number) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;
        if (count < 1) return;

        try {
            const result = await setRadialArmCount(
                input, count,
                selectedElementValue,
                selectedWallElementValue
            );
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, selectedWallElementValue, applyMazeResult]);

    // Set the hub angle degrees in radial_arm maze
    const setAngle = useCallback(async (degrees: number) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;
        if (degrees < 1 || degrees > 360) return;

        try {
            const result = await setRadialArmAngle(input, degrees);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, applyMazeResult]);

    // Set the hub size (radius or side_length) in radial_arm maze
    const setHubSize = useCallback(async (size: number) => {
        if (!mazeData) return;
        if (mazeData.maze_type !== 'radial_arm' && mazeData.maze_type !== 'radial_arm_3d') return;
        if (size <= 0) return;

        try {
            const result = await setRadialArmHubSize(input, size);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, applyMazeResult]);

    // Add a new element
    const addNewElement = useCallback(async (
        name: string,
        token: string,
        type: ElementType
    ) => {
        if (!mazeData || !name || !token) return;

        if (token.length !== 1) {
            setError("Token must be a single character");
            return;
        }

        try {
            const result = await addElement(input, name, token, type);
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, applyMazeResult]);

    // Set the number of levels in 3D maze
    const setLevelCountAction = useCallback(async (count: number) => {
        if (!mazeData) return;
        if (!is3DMazeType(mazeData.maze_type)) return;
        if (count < 1) return;

        try {
            const result = await setLevelCount(
                input, count,
                selectedElementValue,
                selectedWallElementValue
            );
            applyMazeResult(result);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue, selectedWallElementValue, applyMazeResult]);

    // Create a new maze
    const create = useCallback(async (type: MazeType, hubType?: 'circular' | 'polygon') => {
        try {
            const result = await createNewMaze(type, hubType);
            applyMazeResult(result);
            setSelectedLayer('cells');
        } catch (err) {
            setError(String(err));
        }
    }, [applyMazeResult]);

    const clearError = useCallback(() => setError(null), []);

    return {
        // State
        loading,
        error,
        input,
        mazeData,
        selectedElementValue,
        selectedWallElementValue,
        selectedLayer,
        selectedLevelIndex,
        // Actions
        setInput,
        setSelectedElementValue,
        setSelectedWallElementValue,
        setSelectedLayer,
        setSelectedLevelIndex,
        parse,
        format,
        updateCell,
        updateWall,
        updateRadialCell,
        updateRadialWall,
        resize,
        resizeArm,
        setArmCount,
        setAngle,
        setHubSize,
        addNewElement,
        setLevelCountAction,
        create,
        clearError,
    };
}
