/**
 * useFileOperations Hook
 * 
 * Handles file import/export operations for the maze editor.
 */

import { useRef, useCallback } from 'react';
import { toPng } from 'html-to-image';
import { IMAGE_EXPORT_CONFIG } from '../constants/defaults';

export interface UseFileOperationsOptions {
    /** Current YAML input text */
    input: string;
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
    /** Export grid as PNG image */
    exportImage: () => Promise<void>;
    /** Trigger file upload dialog */
    triggerUpload: () => void;
    /** Handle file input change event */
    handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * Hook for file import/export operations.
 */
export function useFileOperations({
    input,
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

    const exportImage = useCallback(async () => {
        if (!gridRef.current) return;

        try {
            const dataUrl = await toPng(gridRef.current, {
                cacheBust: true,
                backgroundColor: IMAGE_EXPORT_CONFIG.backgroundColor,
            });
            const link = document.createElement('a');
            link.download = 'maze-layout.png';
            link.href = dataUrl;
            link.click();
        } catch (err) {
            console.error('Failed to export image:', err);
            onError("Failed to export image");
        }
    }, [onError]);

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
