/**
 * ElementPalette Component
 * 
 * Toolbar for selecting the active element for painting.
 */

import clsx from 'clsx';
import type { MazeElement, LayerType } from '../../types/maze';
import { generateColorStyle } from '../MazeGrid';

export interface ElementPaletteProps {
    /** Available elements for the current layer */
    elements: MazeElement[];
    /** Currently selected element value */
    selectedValue: number;
    /** Callback when element is selected */
    onSelect: (value: number) => void;
    /** Current layer type */
    layer: LayerType;
}

export function ElementPalette({
    elements,
    selectedValue,
    onSelect,
    layer,
}: ElementPaletteProps) {
    const layerType = layer === 'cells' ? 'cell' : 'wall';

    return (
        <div className="flex items-center gap-2 flex-nowrap min-w-max">
            <span className="text-xs text-slate-400 mr-2">Elements:</span>
            {elements.map((el) => {
                const { className: colorClass, style: colorStyle } = generateColorStyle(el.name, layerType);
                const isSelected = selectedValue === el.value;
                const textColor = colorStyle?.color || '#ffffff';

                return (
                    <button
                        key={`${layer}-${el.value}`}
                        onClick={() => onSelect(el.value)}
                        className={clsx(
                            'px-3 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 shrink-0 border',
                            isSelected
                                ? "ring-2 ring-white ring-offset-2 ring-offset-slate-900 border-transparent"
                                : "border-slate-600/50 hover:border-slate-500 opacity-80 hover:opacity-100",
                            colorClass || ''
                        )}
                        style={{
                            ...(!colorClass ? colorStyle : undefined),
                            color: textColor
                        }}
                    >
                        <span
                            className="w-5 h-5 rounded flex items-center justify-center font-mono text-xs shadow-inner"
                            style={{ backgroundColor: 'rgba(0,0,0,0.2)', color: textColor }}
                        >
                            {el.token}
                        </span>
                        <span className="font-bold" style={{ color: textColor }}>{el.name}</span>
                    </button>
                );
            })}
        </div>
    );
}
