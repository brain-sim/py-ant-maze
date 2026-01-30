/**
 * useMaze Hook
 * 
 * Manages all maze-related state and operations.
 */

import { useState, useCallback, useEffect } from 'react';
import type { MazeData, LayerType, MazeType, ElementType } from '../types/maze';
import {
    getPyodide,
    parseMaze,
    formatMaze,
    updateMaze,
    resizeMaze,
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
    /** Selected wall element value (edge_grid only) */
    selectedWallElementValue: number;
    /** Currently selected layer (cells or walls) */
    selectedLayer: LayerType;
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
    /** Parse the current input */
    parse: () => Promise<void>;
    /** Format and parse the current input */
    format: () => Promise<void>;
    /** Update a cell value */
    updateCell: (row: number, col: number) => Promise<void>;
    /** Update a wall value */
    updateWall: (row: number, col: number, wallType: 'vertical' | 'horizontal') => Promise<void>;
    /** Resize the maze grid */
    resize: (rows: number, cols: number) => Promise<void>;
    /** Add a new element */
    addNewElement: (name: string, token: string, type: ElementType) => Promise<void>;
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
    const [selectedElementValue, setSelectedElementValue] = useState(1);
    const [selectedWallElementValue, setSelectedWallElementValue] = useState(1);
    const [selectedLayer, setSelectedLayer] = useState<LayerType>('cells');

    // Parse YAML and update maze data
    const parse = useCallback(async (yamlText?: string) => {
        try {
            const textToParse = yamlText ?? input;
            const { data } = await parseMaze(textToParse);
            setMazeData(data);
            setError(null);
        } catch (err) {
            setError(String(err));
            setMazeData(null);
        }
    }, [input]);

    // Initialize Pyodide and parse default maze
    useEffect(() => {
        getPyodide()
            .then(() => {
                setLoading(false);
                parse(DEFAULT_OCCUPANCY_YAML);
            })
            .catch((err) => {
                console.error(err);
                setError("Failed to load Pyodide: " + err.message);
                setLoading(false);
            });
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

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

    // Update a cell
    const updateCell = useCallback(async (row: number, col: number) => {
        if (!mazeData) return;

        const currentVal = mazeData.grid ? mazeData.grid[row][col] : mazeData.cells?.[row][col];
        if (currentVal === selectedElementValue) return;

        try {
            const { text, data } = await updateMaze(input, row, col, selectedElementValue, 'cells');
            setInput(text);
            setMazeData(data);
            setError(null);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue]);

    // Update a wall
    const updateWall = useCallback(async (
        row: number,
        col: number,
        wallType: 'vertical' | 'horizontal'
    ) => {
        if (!mazeData) return;

        const currentVal = wallType === 'vertical'
            ? mazeData.vertical_walls?.[row][col]
            : mazeData.horizontal_walls?.[row][col];
        if (currentVal === selectedWallElementValue) return;

        try {
            const gridType = wallType === 'vertical' ? 'vertical_walls' : 'horizontal_walls';
            const { text, data } = await updateMaze(input, row, col, selectedWallElementValue, gridType);
            setInput(text);
            setMazeData(data);
            setError(null);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedWallElementValue]);

    // Resize the maze
    const resize = useCallback(async (rows: number, cols: number) => {
        if (!mazeData) return;

        try {
            const { text, data } = await resizeMaze(input, rows, cols, selectedElementValue);
            setInput(text);
            setMazeData(data);
            setError(null);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input, selectedElementValue]);

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
            const { text, data } = await addElement(input, name, token, type);
            setInput(text);
            setMazeData(data);
            setError(null);
        } catch (err) {
            setError(String(err));
        }
    }, [mazeData, input]);

    // Create a new maze
    const create = useCallback(async (type: MazeType) => {
        try {
            const { text, data } = await createNewMaze(type);
            setInput(text);
            setMazeData(data);
            setError(null);

            // Reset selections
            setSelectedLayer('cells');
            if (data.elements?.[0]) setSelectedElementValue(data.elements[0].value);
            if (data.wall_elements?.[0]) setSelectedWallElementValue(data.wall_elements[0].value);
        } catch (err) {
            setError(String(err));
        }
    }, []);

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
        // Actions
        setInput,
        setSelectedElementValue,
        setSelectedWallElementValue,
        setSelectedLayer,
        parse: () => parse(),
        format,
        updateCell,
        updateWall,
        resize,
        addNewElement,
        create,
        clearError,
    };
}
