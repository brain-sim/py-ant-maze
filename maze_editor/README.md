# Maze Editor

Web-based visual editor for creating and editing mazes. Built with React, Vite, and Pyodide to run `py_ant_maze` directly in the browser.

## Features

### Maze Types
- **Occupancy Grid**: Classic blocked/open cell representation
- **Edge Grid**: Thin walls between cells
- **Radial Arm**: Center hub with multiple configurable arms

### 2D and 3D Support
- Toggle between 2D (single layer) and 3D (multi-level) modes
- **Level Controls**: Add/remove levels dynamically for 3D mazes
- **Level Tabs**: Switch between levels with visual indicators
- **Connectors**: Elevators and escalators between floors

### Visual Editing
- Click and drag to paint maze elements
- Click walls directly in edge grid mode
- Real-time synchronization between grid and YAML

### Radial Arm Controls
- Adjustable hub shape (circular or polygon)
- Configurable hub angle (0-360°) and size
- Per-arm width, length and layout (same as EdgeGrid type) controls
- Add or remove arms dynamically

### Import/Export
- Upload existing YAML maze files
- Download edited mazes as YAML
- Export grids as PNG images (all levels exported separately for 3D)

### Keyboard Shortcuts
- Press element tokens (e.g., `#`, `.`) for quick selection

## Getting Started

### Prerequisites

- Node.js v18+
- Python 3.10+ (for building the wheel)

### Installation

1. Build the Python wheel:
   ```bash
   cd ../py_ant_maze
   pip install build
   python -m build
   ```

2. Install and run:
   ```bash
   npm install
   npm run dev
   ```

The dev server automatically copies the wheel from `../py_ant_maze/dist/` to `public/`.

## Project Structure

```
src/
├── components/
│   ├── layout/         # Header, LoadingScreen
│   ├── editor/         # CodePanel, VisualEditor
│   ├── controls/       # MazeTypeSelector, GridSizeControl, RadialArmSizeControl,
│   │                   # LevelCountControl, LevelSelector, AddElementForm
│   └── MazeGrid.tsx    # Grid renderer (supports all maze types)
├── hooks/
│   ├── useMaze.ts          # Maze state and actions
│   └── useFileOperations.ts # Import/export functionality
├── services/
│   └── pyodide.ts      # Pyodide integration with py_ant_maze
├── types/
│   └── maze.ts         # TypeScript type definitions
├── constants/          # Default YAML templates
└── App.tsx             # Main application
```

## Building

```bash
npm run build
```

Output is in the `dist/` directory.
