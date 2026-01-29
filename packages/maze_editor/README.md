# Maze Editor

A modern, web-based visual editor for configuring mazes for `py_ant_maze`. Built with React, Vite, and Pyodide, it runs the Python maze logic directly in the browser.

## Features

-   **Visual Grid Editor**: Interactive grid for painting maze elements.
-   **Full-Width Layout**: Responsive design that utilizes the full browser window.
-   **Dynamic Resizing**: Adjust maze rows and columns on the fly.
-   **Custom Elements**: Create new maze elements (e.g., "Fire", "Water") with custom tokens and dynamic colors.
-   **Drag & Paint**: Click and drag to quickly paint multiple cells.
-   **Image Export**: Download high-quality PNG images of your maze layout.
-   **Configuration Sync**:
    -   Import/Export YAML configuration files.
    -   Real-time bidirectional sync between Visual Editor and YAML Code.
-   **Keyboard Shortcuts**: Use element tokens (e.g., `#`, `.`) as hotkeys for quick selection.

## Getting Started

### Prerequisites

-   Node.js (v18+)
-   Python 3.10+ (for building the backend wheel)

### Installation

1.  **Build the Python Backend**: The editor requires a compiled wheel of `py_ant_maze`.
    ```bash
    cd ../py_ant_maze
    # Ensure you have the 'build' package
    pip install build
    python -m build
    ```

2.  **Setup Editor**:
    ```bash
    cd ../maze_editor
    npm install
    ```

### Development

To start the development server:

```bash
npm run dev
```

**Note**: The `npm run dev` and `npm run build` commands automatically run a `pre` script that copies the built `.whl` from `../py_ant_maze/dist/` into the `public/` folder for Pyodide to load. Ensure you have built the wheel (Step 1 above) before starting.

### Building

To build for production:

```bash
npm run build
```

The output will be in the `dist` directory.

## project Structure

-   `src/components`: React components (MazeGrid, etc.)
-   `src/lib`: Pyodide integration and helper functions.
-   `src/App.tsx`: Main application logic and state management.
