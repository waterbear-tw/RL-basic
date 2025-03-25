from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

grid_state = {
    'size': 5,
    'grid': None,
    'start': None,
    'end': None,
    'obstacles': [],
    'policy_eval_values': None,
    'value_iter_values': None,
    'value_iter_policy': None,
    'optimal_path': None  # 新增最佳路徑
}

def initialize_grid(size):
    grid_state['size'] = size
    grid_state['grid'] = np.zeros((size, size), dtype=int).tolist()
    grid_state['start'] = None
    grid_state['end'] = None
    grid_state['obstacles'] = []
    grid_state['policy_eval_values'] = None
    grid_state['value_iter_values'] = None
    grid_state['value_iter_policy'] = None
    grid_state['optimal_path'] = None

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

@app.route('/')
def index():
    print("Rendering index.html")
    return render_template('index.html')

@app.route('/init_grid', methods=['POST'])
def init_grid():
    print("Received POST to /init_grid:", request.form)
    size = int(request.form['size'])
    if 5 <= size <= 9:
        initialize_grid(size)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Size must be between 5 and 9'})

@app.route('/reset', methods=['POST'])
def reset():
    print("Received POST to /reset")
    size = grid_state['size']
    initialize_grid(size)
    return jsonify({'success': True})

@app.route('/update_cell', methods=['POST'])
def update_cell():
    print("Received POST to /update_cell:", request.form)
    x = int(request.form['x'])
    y = int(request.form['y'])
    cell_type = request.form['type']
    if (x, y) == grid_state['start'] or (x, y) == grid_state['end'] or (x, y) in grid_state['obstacles']:
        return jsonify({'success': False, 'message': 'Cell already occupied'})
    if cell_type == 'start':
        grid_state['start'] = (x, y)
    elif cell_type == 'end':
        grid_state['end'] = (x, y)
    elif cell_type == 'obstacle' and len(grid_state['obstacles']) < grid_state['size'] - 2:
        grid_state['obstacles'].append((x, y))
    return jsonify({'success': True})

@app.route('/calculate', methods=['POST'])
def calculate():
    print("Received POST to /calculate")
    if not grid_state['start'] or not grid_state['end']:
        return jsonify({'success': False, 'message': 'Start and End must be set'})
    
    size = grid_state['size']
    actions = ['↑', '↓', '←', '→']

    # Policy Evaluation (隨機策略)
    policy = np.full((size, size), '', dtype=object)
    for i in range(size):
        for j in range(size):
            if (i, j) != grid_state['end'] and (i, j) not in grid_state['obstacles']:
                policy[i, j] = np.random.choice(actions)
    
    values = np.full((size, size), 0.0, dtype=float)
    for i in range(size):
        for j in range(size):
            if (i, j) == grid_state['end']:
                values[i, j] = 100.0
            elif (i, j) in grid_state['obstacles']:
                values[i, j] = float('nan')
    
    gamma = 0.9
    theta = 0.001
    while True:
        delta = 0.0
        new_values = np.full((size, size), 0.0, dtype=float)
        for i in range(size):
            for j in range(size):
                if (i, j) == grid_state['end']:
                    new_values[i, j] = 100.0
                elif (i, j) in grid_state['obstacles']:
                    new_values[i, j] = float('nan')
                else:
                    action = policy[i, j]
                    next_i, next_j = i, j
                    if action == '↑' and i > 0: next_i -= 1
                    elif action == '↓' and i < size-1: next_i += 1
                    elif action == '←' and j > 0: next_j -= 1
                    elif action == '→' and j < size-1: next_j += 1
                    
                    is_out_of_bounds = (action == '↑' and i == 0) or \
                                      (action == '↓' and i == size-1) or \
                                      (action == '←' and j == 0) or \
                                      (action == '→' and j == size-1)
                    is_obstacle = (next_i, next_j) in grid_state['obstacles']
                    
                    reward = 0.0
                    if is_out_of_bounds or is_obstacle:
                        reward = -10.0
                    else:
                        current_dist = manhattan_distance((i, j), grid_state['end'])
                        next_dist = manhattan_distance((next_i, next_j), grid_state['end'])
                        if next_dist < current_dist:
                            reward = 1.0
                        elif next_dist > current_dist:
                            reward = -1.0
                    
                    next_value = values[next_i, next_j] if not np.isnan(values[next_i, next_j]) else 0.0
                    new_v = reward + gamma * next_value
                    new_values[i, j] = new_v
                    delta = max(delta, abs(new_v - values[i, j]))
        values = new_values
        if delta < theta:
            break
    
    grid_state['policy_eval_values'] = [[cell if not np.isnan(cell) else None for cell in row] for row in values.tolist()]

    # Value Iteration
    value_iter_values = np.full((size, size), 0.0, dtype=float)
    value_iter_policy = np.full((size, size), '', dtype=object)
    for i in range(size):
        for j in range(size):
            if (i, j) == grid_state['end']:
                value_iter_values[i, j] = 100.0
            elif (i, j) in grid_state['obstacles']:
                value_iter_values[i, j] = float('nan')
    
    while True:
        delta = 0.0
        new_values = np.full((size, size), 0.0, dtype=float)
        for i in range(size):
            for j in range(size):
                if (i, j) == grid_state['end']:
                    new_values[i, j] = 100.0
                elif (i, j) in grid_state['obstacles']:
                    new_values[i, j] = float('nan')
                else:
                    best_value = float('-inf')
                    best_action = ''
                    for action in actions:
                        next_i, next_j = i, j
                        if action == '↑' and i > 0: next_i -= 1
                        elif action == '↓' and i < size-1: next_i += 1
                        elif action == '←' and j > 0: next_j -= 1
                        elif action == '→' and j < size-1: next_j += 1
                        
                        is_out_of_bounds = (action == '↑' and i == 0) or \
                                          (action == '↓' and i == size-1) or \
                                          (action == '←' and j == 0) or \
                                          (action == '→' and j == size-1)
                        is_obstacle = (next_i, next_j) in grid_state['obstacles']
                        
                        reward = 0.0
                        if is_out_of_bounds or is_obstacle:
                            reward = -10.0
                        else:
                            current_dist = manhattan_distance((i, j), grid_state['end'])
                            next_dist = manhattan_distance((next_i, next_j), grid_state['end'])
                            if next_dist < current_dist:
                                reward = 1.0
                            elif next_dist > current_dist:
                                reward = -1.0
                        
                        next_value = value_iter_values[next_i, next_j] if not np.isnan(value_iter_values[next_i, next_j]) else 0.0
                        action_value = reward + gamma * next_value
                        if action_value > best_value:
                            best_value = action_value
                            best_action = action
                    new_values[i, j] = best_value
                    value_iter_policy[i, j] = best_action
                    delta = max(delta, abs(best_value - value_iter_values[i, j]))
        value_iter_values = new_values
        if delta < theta:
            break
    
    grid_state['value_iter_values'] = [[cell if not np.isnan(cell) else None for cell in row] for row in value_iter_values.tolist()]
    grid_state['value_iter_policy'] = [[str(cell) for cell in row] for row in value_iter_policy.tolist()]

    # 計算最佳路徑
    optimal_path = []
    current_pos = grid_state['start']
    while current_pos != grid_state['end']:
        optimal_path.append(current_pos)
        i, j = current_pos
        action = grid_state['value_iter_policy'][i][j]
        next_i, next_j = i, j
        if action == '↑' and i > 0: next_i -= 1
        elif action == '↓' and i < size-1: next_i += 1
        elif action == '←' and j > 0: next_j -= 1
        elif action == '→' and j < size-1: next_j += 1
        current_pos = (next_i, next_j)
        # 避免無限迴圈（若策略有問題）
        if current_pos in optimal_path or current_pos in grid_state['obstacles']:
            break
    optimal_path.append(grid_state['end'])  # 加入終點
    grid_state['optimal_path'] = optimal_path
    
    print("Calculate completed:", grid_state)
    return jsonify({
        'success': True,
        'policy_eval_values': grid_state['policy_eval_values'],
        'value_iter_values': grid_state['value_iter_values'],
        'value_iter_policy': grid_state['value_iter_policy'],
        'optimal_path': grid_state['optimal_path']
    })

@app.route('/get_state', methods=['GET'])
def get_state():
    print("Received GET to /get_state")
    return jsonify(grid_state)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)