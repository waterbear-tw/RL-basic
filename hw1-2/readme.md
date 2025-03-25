# GridWorld Visualization Project

This project is a web-based visualization tool for GridWorld, built using Flask and JavaScript, to demonstrate reinforcement learning concepts such as Policy Evaluation and Value Iteration.
**It combines assignments HW1 and HW2 into a single interactive application.**

## Demo

![](static/demo.gif)

## Work Description

### HW1-1: Perform GridWorld Website with Flask

- **Objective**: Create a web application using Flask to visualize a GridWorld environment.
- **Implementation**: A dynamic grid is displayed where users can set a start point, end point, and obstacles. The grid supports sizes from 5x5 to 9x9, with a futuristic UI featuring a starry background and neon controls.

### HW1-2: Show the Value of Policy Evaluation

- **Objective**: Display the values computed by Policy Evaluation on the grid.
- **Note**: Since HW1 and HW2 are combined, instead of showing Policy Evaluation's policy, this project displays the **Policy of Value Iteration** alongside its values. Policy Evaluation values are still computed and visualized with a heatmap.

### HW2: Perform Value of Value Iteration and the Path of GridWorld Question

- **Objective**: Compute and display the values of Value Iteration, along with the optimal path from start to end.
- **Implementation**: The application calculates Value Iteration values and policies, visualizes them with a heatmap, and animates the optimal path using a Rocket (🛸) icon that moves along the grid, leaving a trail and stopping at the endpoint.

---

## How to Run Code

1. **Prerequisites**:

   - Python 3.x installed.
   - Flask library installed (`pip install flask`).

2. **Project Structure**:
   GridWorld/
   ├── app.py # Flask backend
   ├── templates/
   │ └── index.html # Frontend HTML with JavaScript and CSS
   └── README.md # This file

3. **Steps to Run**:

- Clone or download the project repository.
- Open a terminal and navigate to the project directory:

  ```bash
   cd GridWorld
   #Run the Flask application:
   python app.py
  ```

- Open a web browser and visit:

  ```bash
  http://127.0.0.1:5000
  ```

- Interact with the interface:
  - Set grid size (5-9).
  - Click to set start (green), end (red), and obstacles (gray).
  - Click "Calculate" to compute values and policies.
  - Click "Play Path" to animate the optimal path with the Rocket.

---

## Policy Evaluation and Value Iteration in the Code

### Policy Evaluation

**Location**: Handled in app.py under the /calculate endpoint.

**Description**:

1. Computes the value function for a random policy across the grid.
2. Values are stored in state["policy_eval_values"] as a 2D array, where each cell represents the expected cumulative reward starting from that position under the random policy.

**Visualization**:

1. In index.html, the updateGrids function fetches policy_eval_values and displays them in the "Policy Evaluation Values" grid.
2. A heatmap is applied using getHeatmapColor, where colors transition from blue (low values) to red (high values) based on the raw (non-integer) values.
3. Displayed values are rounded to integers, with full precision shown on hover via a custom tooltip.

---

### Value Iteration

**Location**: Also in app.py under the /calculate endpoint.

**Description**:

1. Implements the Value Iteration algorithm to find the optimal value function and policy.
2. Values are stored in state["value_iter_values"], and the optimal policy (actions: ↑↓←→) is stored in state["value_iter_policy"].
3. The optimal path from start to end is computed and stored in state["optimal_path"].

**Visualization**:

1. In index.html, updateGrids displays value_iter_values in the "Value Iteration Values" grid and value_iter_policy in the "Value Iteration Policy" grid.
2. Heatmap colors are based on raw values, with integer display and hover tooltips similar to Policy Evaluation.
3. The playPath function animates the optimal path:
4. A Rocket (🚀) moves along optimal_path, rotating based on value_iter_policy directions (↑: 0°, ↓: 180°, ←: 270°, →: 90°).
5. Path cells are highlighted Gold (.path), forming a trail, and the Rocket stops at the endpoint.

---

## Prompts to Reconstruct This Project

If you want to recreate this project from scratch using a conversational AI (e.g., Grok), here are suggested prompts for each major component:

1. Setting Up Flask Backend

   ```test
   I want to create a Flask web application for a GridWorld visualization. It should:
   - Initialize a grid (size 5-9) with endpoints and obstacles.
   - Handle POST requests to set grid size, update cells (start, end, obstacles), and calculate Policy Evaluation and Value Iteration.
   - Store state in a global dictionary with keys: size, start, end, obstacles, policy_eval_values, value_iter_values, value_iter_policy, optimal_path.
   - Return JSON responses.
   Please provide the complete app.py code.
   ```

2. Building the Frontend

   ```text

    Create an HTML file with JavaScript and CSS for a GridWorld visualization:

    - Use Flask's templates folder (index.html).
    - Display a starry background with neon-styled controls (input for grid size, buttons: Initialize, Reset, Calculate, Play Path).
    - Show four grids: Main Grid, Policy Evaluation Values, Value Iteration Values, Value Iteration Policy.
    - Main Grid supports clicking to set start (green), end (red), obstacles (gray).
    - Fetch state from Flask via /get_state and update grids dynamically.
    - Include a heatmap (blue to red) for value grids based on raw values, displaying integers with hover tooltips for full precision

   ```

3. Adding Path Animation with Rocket

   ```text
    Modify my GridWorld HTML file to animate the optimal path:

    - Use a Rocket emoji (🚀) that moves along the path from start to end.
    - Rotate the Rocket based on policy directions (↑: 0°, ↓: 180°, ←: 270°, →: 90°) with smooth transitions.
    - Leave a Gold trail (.path class) on the grid as the Rocket moves.
    - Ensure the Rocket stops at the endpoint and remains visible.
    - Update the playPath function to handle this animation with a 500ms delay between steps.
   ```

4. Combining Features

   ```text
       I have a Flask GridWorld project with separate Policy Evaluation and Value Iteration grids. Combine them into one interface:

       - Show Policy Evaluation values with a heatmap (blue to red) based on raw values, rounded to integers, with hover tooltips for full precision.
       - Show Value Iteration values and policy similarly, with an animated Rocket path that leaves a trail and stops at the end.
       - Ensure the UI is futuristic with a starry background and neon buttons, supporting grid sizes 5-9.
       Provide the updated index.html and explain changes.
   ```

- These prompts should guide an AI to rebuild the project step-by-step, matching the current functionality.
