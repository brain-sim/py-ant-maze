/**
 * useFileOperations Hook
 * 
 * Handles file import/export operations for the maze editor.
 */

import { useRef, useCallback } from 'react';
import { toPng } from 'html-to-image';
import { IMAGE_EXPORT_CONFIG } from '../constants/defaults';
import type { MazeData } from '../types/maze';
import { is3DMazeType } from '../types/maze';

export interface UseFileOperationsOptions {
    /** Current YAML input text */
    input: string;
    /** Current maze data (for 3D level iteration) */
    mazeData: MazeData | null;
    /** Current selected level index */
    selectedLevelIndex: number;
    /** Callback to set the selected level */
    setSelectedLevelIndex: (index: number) => void;
    /** Callback when a file is uploaded */
    onFileLoaded: (content: string) => void;
    /** Callback when an error occurs */
    onError: (error: string) => void;
}

export interface UseFileOperationsResult {
    /** Ref to attach to grid element for image export */
    gridRef: React.RefObject<HTMLDivElement>;
    /** Ref to attach to hidden file input */
    fileInputRef: React.RefObject<HTMLInputElement>;
    /** Download current YAML as file */
    downloadYaml: () => void;
    /** Export grid as PNG image (all levels for 3D mazes) */
    exportImage: () => Promise<void>;
    /** Trigger file upload dialog */
    triggerUpload: () => void;
    /** Handle file input change event */
    handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Wait for a specified time.
 */
function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Hook for file import/export operations.
 */
export function useFileOperations({
    input,
    mazeData,
    selectedLevelIndex,
    setSelectedLevelIndex,
    onFileLoaded,
    onError,
}: UseFileOperationsOptions): UseFileOperationsResult {
    const gridRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const downloadYaml = useCallback(() => {
        const blob = new Blob([input], { type: "text/yaml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "maze.yaml";
        a.click();
        URL.revokeObjectURL(url);
    }, [input]);

    /**
     * Capture the current grid as PNG and download it.
     */
    const captureAndDownload = useCallback(async (filename: string): Promise<void> => {
        if (!gridRef.current) return;

        const dataUrl = await toPng(gridRef.current, {
            cacheBust: true,
            backgroundColor: IMAGE_EXPORT_CONFIG.backgroundColor,
        });
        const link = document.createElement('a');
        link.download = filename;
        link.href = dataUrl;
        link.click();
    }, []);

    const exportImage = useCallback(async () => {
        if (!gridRef.current) return;

        try {
            // Check if this is a 3D maze with multiple levels
            const is3D = mazeData && is3DMazeType(mazeData.maze_type);
            const levels = mazeData?.levels || [];

            if (is3D && levels.length > 1) {
                // Export all levels for 3D mazes
                const originalLevel = selectedLevelIndex;

                for (let i = 0; i < levels.length; i++) {
                    // Switch to this level
                    setSelectedLevelIndex(i);

                    // Wait for React to re-render the grid
                    await delay(200);

                    // Capture this level
                    const levelId = levels[i].id || `level-${i}`;
                    await captureAndDownload(`maze-${levelId}.png`);
                }

                // Restore original level
                setSelectedLevelIndex(originalLevel);
            } else {
                // 2D maze or single level - just export once
                await captureAndDownload('maze-layout.png');
            }
        } catch (err) {
            console.error('Failed to export image:', err);
            onError("Failed to export image");
        }
    }, [mazeData, selectedLevelIndex, setSelectedLevelIndex, captureAndDownload, onError]);

    const triggerUpload = useCallback(() => {
        fileInputRef.current?.click();
    }, []);

    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            const content = ev.target?.result as string;
            onFileLoaded(content);
        };
        reader.readAsText(file);
        e.target.value = ""; // Reset for re-upload of same file
    }, [onFileLoaded]);

    return {
        gridRef,
        fileInputRef,
        downloadYaml,
        exportImage,
        triggerUpload,
        handleFileChange,
    };
}
