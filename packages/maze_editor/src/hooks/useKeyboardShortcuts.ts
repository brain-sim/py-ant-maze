/**
 * useKeyboardShortcuts Hook
 * 
 * Handles keyboard shortcuts for element selection.
 * Supports both cell and wall elements for EdgeGrid type.
 */

import { useEffect, useCallback } from 'react';
import type { MazeElement, LayerType } from '../types/maze';

export interface UseKeyboardShortcutsOptions {
    /** Cell elements */
    cellElements: MazeElement[];
    /** Wall elements (for edge_grid only) */
    wallElements: MazeElement[];
    /** Currently selected layer */
    selectedLayer: LayerType;
    /** Callback when a cell element is selected via keyboard */
    onCellElementSelect: (value: number) => void;
    /** Callback when a wall element is selected via keyboard */
    onWallElementSelect: (value: number) => void;
    /** Whether shortcuts are enabled */
    enabled?: boolean;
}

/**
 * Hook for handling keyboard shortcuts.
 * Allows selecting elements by pressing their token key.
 * For EdgeGrid, prioritizes elements from the currently selected layer.
 */
export function useKeyboardShortcuts({
    cellElements,
    wallElements,
    selectedLayer,
    onCellElementSelect,
    onWallElementSelect,
    enabled = true,
}: UseKeyboardShortcutsOptions): void {
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        // Ignore typing in input fields
        const target = e.target as HTMLElement;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            return;
        }

        const key = e.key;

        // First, check if the key matches an element in the currently selected layer
        if (selectedLayer === 'walls') {
            const wallElement = wallElements.find(el => el.token === key);
            if (wallElement) {
                onWallElementSelect(wallElement.value);
                return;
            }
            // If not found in walls, check cells as fallback
            const cellElement = cellElements.find(el => el.token === key);
            if (cellElement) {
                onCellElementSelect(cellElement.value);
                return;
            }
        } else {
            // cells layer selected - check cells first
            const cellElement = cellElements.find(el => el.token === key);
            if (cellElement) {
                onCellElementSelect(cellElement.value);
                return;
            }
            // If not found in cells, check walls as fallback
            const wallElement = wallElements.find(el => el.token === key);
            if (wallElement) {
                onWallElementSelect(wallElement.value);
                return;
            }
        }
    }, [cellElements, wallElements, selectedLayer, onCellElementSelect, onWallElementSelect]);

    useEffect(() => {
        if (!enabled) return;

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [enabled, handleKeyDown]);
}
