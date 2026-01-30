/**
 * Header Component
 * 
 * App header with logo, title, and status indicator.
 */

import { Grid3X3 } from 'lucide-react';

export function Header() {
    return (
        <header className="shrink-0 bg-black/30 backdrop-blur-sm border-b border-white/10 px-6 py-4">
            <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                        <Grid3X3 size={20} />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-tight">Maze Editor</h1>
                        <p className="text-xs text-slate-400">Visual maze configuration tool</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                        <span className="text-xs font-medium text-emerald-300">Pyodide Ready</span>
                    </div>
                </div>
            </div>
        </header>
    );
}
