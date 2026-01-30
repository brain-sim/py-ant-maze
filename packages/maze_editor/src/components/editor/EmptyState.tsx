/**
 * EmptyState Component
 * 
 * Displayed when no valid maze data is available.
 */

import { AlertCircle } from 'lucide-react';

export function EmptyState() {
    return (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500 gap-4 p-4 text-center">
            <AlertCircle size={48} className="opacity-30" />
            <p>Parse a valid YAML configuration to enable the visual editor</p>
        </div>
    );
}
