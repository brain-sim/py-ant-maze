import clsx from 'clsx';
import { type MazeData } from '../lib/pyodide';

interface ToolbarProps {
    elements: MazeData['elements'];
    selectedElementValue: number;
    onSelectElement: (value: number) => void;
}

export function Toolbar({ elements, selectedElementValue, onSelectElement }: ToolbarProps) {
    return (
        <div className="flex gap-2 p-2 bg-white border-b border-gray-200">
            {elements.map((el) => (
                <button
                    key={el.value}
                    onClick={() => onSelectElement(el.value)}
                    className={clsx(
                        "px-3 py-1 rounded border text-sm font-medium transition-colors flex items-center gap-2",
                        selectedElementValue === el.value
                            ? "bg-blue-100 border-blue-500 text-blue-700"
                            : "bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100"
                    )}
                >
                    <span className="font-mono bg-gray-200 px-1 rounded w-5 text-center">{el.token}</span>
                    {el.name}
                </button>
            ))}
        </div>
    );
}
