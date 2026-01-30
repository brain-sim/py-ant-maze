/**
 * LoadingScreen Component
 * 
 * Full-screen loading indicator shown during Pyodide initialization.
 */

export function LoadingScreen() {
    return (
        <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            <div className="flex flex-col items-center gap-6 text-white">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-purple-500/30 rounded-full"></div>
                    <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-purple-400 rounded-full animate-spin"></div>
                </div>
                <div className="text-lg font-medium">Loading Maze Editor...</div>
                <div className="text-sm text-purple-300/70">Initializing Python runtime</div>
            </div>
        </div>
    );
}
