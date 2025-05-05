"""
Example of a random agent navigating the AntMaze environment.

This example demonstrates how to implement a simple random agent
that navigates through the maze environment.
"""
import numpy as np
import time
from py_ant_maze import bsAntMaze, bsAntMazeConfig


class RandomAgent:
    """A simple random agent for maze navigation."""
    
    def __init__(self, maze):
        """
        Initialize the random agent.
        
        Args:
            maze (bsAntMaze): The maze environment
        """
        self.maze = maze
        self.position = maze.get_start_position()
        self.goal = maze.get_goal_position()
        self.maze_array = maze.get_maze()
        
        # Possible actions: up, right, down, left
        self.actions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Track visited positions
        self.visited = set()
        self.visited.add(self.position)
        
        # Track number of steps
        self.steps = 0
        
        # Maximum number of steps
        self.max_steps = maze.get_config().max_episode_steps
    
    def get_valid_actions(self):
        """
        Get list of valid actions from current position.
        
        Returns:
            list: List of valid action indices
        """
        valid = []
        
        for i, (dr, dc) in enumerate(self.actions):
            new_r = self.position[0] + dr
            new_c = self.position[1] + dc
            
            # Check if new position is valid (within bounds and not a wall)
            if (0 <= new_r < self.maze_array.shape[0] and
                0 <= new_c < self.maze_array.shape[1] and
                self.maze_array[new_r, new_c] == 0):
                valid.append(i)
        
        return valid
    
    def step(self):
        """
        Take a single step in the environment.
        
        Returns:
            bool: True if goal reached, False otherwise
            bool: True if episode terminated, False otherwise
        """
        self.steps += 1
        
        # Get valid actions
        valid_actions = self.get_valid_actions()
        
        if not valid_actions:
            # No valid actions, episode terminated
            return False, True
        
        # Choose a random valid action
        action_idx = np.random.choice(valid_actions)
        dr, dc = self.actions[action_idx]
        
        # Update position
        new_r = self.position[0] + dr
        new_c = self.position[1] + dc
        self.position = (new_r, new_c)
        
        # Add to visited positions
        self.visited.add(self.position)
        
        # Check if goal reached
        if self.position == self.goal:
            return True, True
        
        # Check if max steps reached
        if self.steps >= self.max_steps:
            return False, True
        
        return False, False
    
    def visualize_step(self):
        """
        Visualize the current state of the environment.
        
        Returns:
            str: ASCII representation of the maze with agent position
        """
        rows = []
        
        for i in range(self.maze_array.shape[0]):
            row = []
            for j in range(self.maze_array.shape[1]):
                if (i, j) == self.position:
                    row.append('A')  # Agent
                elif (i, j) == self.goal:
                    row.append('G')  # Goal
                elif (i, j) == self.maze.get_start_position():
                    row.append('S')  # Start
                elif self.maze_array[i, j] == 1:
                    row.append('#')  # Wall
                elif (i, j) in self.visited:
                    row.append('.')  # Visited
                else:
                    row.append(' ')  # Empty
            
            rows.append(''.join(row))
        
        return '\n'.join(rows)
    
    def run_episode(self, visualize=False, delay=0.1):
        """
        Run a complete episode.
        
        Args:
            visualize (bool): Whether to visualize each step
            delay (float): Delay between steps for visualization
            
        Returns:
            bool: True if goal reached, False otherwise
            int: Number of steps taken
        """
        if visualize:
            print("\033c", end="")  # Clear console
            print(self.visualize_step())
            time.sleep(delay)
        
        while True:
            goal_reached, terminated = self.step()
            
            if visualize:
                print("\033c", end="")  # Clear console
                print(self.visualize_step())
                print(f"Steps: {self.steps}/{self.max_steps}")
                time.sleep(delay)
            
            if terminated:
                return goal_reached, self.steps


def main():
    """
    Main function to demonstrate the random agent.
    """
    # Create a custom maze
    custom_maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    # Create maze object and set the maze
    config = bsAntMazeConfig(max_episode_steps=100)
    maze = bsAntMaze(config)
    maze.create_maze(custom_maze)
    
    # Set start and goal positions
    maze.set_start_position((1, 1))
    maze.set_goal_position((5, 7))
    
    # Create and run agent
    agent = RandomAgent(maze)
    goal_reached, steps = agent.run_episode(visualize=True, delay=0.2)
    
    # Print results
    if goal_reached:
        print(f"Goal reached in {steps} steps!")
    else:
        print(f"Failed to reach goal. Took {steps} steps.")
    
    # Run multiple episodes to get statistics
    num_episodes = 100
    successes = 0
    total_steps = 0
    
    print(f"\nRunning {num_episodes} episodes...")
    
    for i in range(num_episodes):
        agent = RandomAgent(maze)
        goal_reached, steps = agent.run_episode(visualize=False)
        
        if goal_reached:
            successes += 1
            total_steps += steps
    
    success_rate = successes / num_episodes * 100
    avg_steps = total_steps / successes if successes > 0 else 0
    
    print(f"Success rate: {success_rate:.2f}%")
    if successes > 0:
        print(f"Average steps to reach goal: {avg_steps:.2f}")


if __name__ == "__main__":
    main()
