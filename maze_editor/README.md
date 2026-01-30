# Maze Editor

Web-based visual editor for creating and editing mazes. Built with React, Vite, and Pyodide to run `py_ant_maze` directly in the browser.

## Features

- **Visual Grid Editor**: Click and drag to paint maze elements
- **Dual Maze Types**: Support for occupancy grids and edge grids
- **Custom Elements**: Add new elements with custom names and tokens
- **Real-time Sync**: Bidirectional synchronization between grid and YAML
- **Keyboard Shortcuts**: Press element tokens for quick selection
- **Export**: Download as YAML file or PNG image

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
├── components/     # React components
│   ├── layout/     # Header, LoadingScreen
│   ├── editor/     # CodePanel, VisualEditor
│   ├── controls/   # Element palette, controls
│   └── MazeGrid.tsx
├── hooks/          # Custom React hooks
├── services/       # Pyodide integration
├── types/          # TypeScript types
├── constants/      # Default values
└── App.tsx         # Main application
```

## Building

```bash
npm run build
```

Output is in the `dist/` directory.
