from py_ant_maze import Maze


def main() -> None:
    maze = Maze.from_file("configs/with_grid_numbers.yaml")
    print(maze.to_text(with_grid_numbers=True))

    maze.to_file("example_maze.yaml", with_grid_numbers=True)
    loaded = Maze.from_file("example_maze.yaml")
    print(loaded.to_text(with_grid_numbers=True))


if __name__ == "__main__":
    main()
