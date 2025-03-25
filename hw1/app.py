from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

grid_state = {
    'size': 5,
    'grid': None,
    'start': None,
    'end': None,
    'obstacles': [],
    'policy': None,
    'values': None
}

def initialize_grid(size):
    grid_state['size'] = size
    grid_state['grid'] = np.zeros((size, size), dtype=int).tolist()
    grid_state['start'] = None
    grid_state['end'] = None
    grid_state['obstacles'] = []
    grid_state['policy'] = None
    grid_state['values'] = None

def manhattan_distance(pos1, pos2):
    """計算曼哈頓距離"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_grid', methods=['POST'])
def init_grid():
    size = int(request.form['size'])
    if 5 <= size <= 9:
        initialize_grid(size)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Size must be between 5 and 9'})

@app.route('/reset', methods=['POST'])
def reset():
    size = grid_state['size']
    initialize_grid(size)
    return jsonify({'success': True})

@app.route('/update_cell', methods=['POST'])
def update_cell():
    x = int(request.form['x'])
    y = int(request.form['y'])
    cell_type = request.form['type']
    
    if (x, y) == grid_state['start'] or (x, y) == grid_state['end'] or \
       (x, y) in grid_state['obstacles']:
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
    if not grid_state['start'] or not grid_state['end']:
        return jsonify({'success': False, 'message': 'Start and End must be set'})
    
    size = grid_state['size']
    policy = np.full((size, size), '', dtype=object)
    for i in range(size):
        for j in range(size):
            if (i, j) != grid_state['end'] and (i, j) not in grid_state['obstacles']:
                policy[i, j] = np.random.choice(['↑', '↓', '←', '→'])
    
    grid_state['policy'] = [[str(cell) for cell in row] for row in policy.tolist()]
    
    # 初始化價值表
    values = np.full((size, size), 0.0, dtype=float)
    for i in range(size):
        for j in range(size):
            if (i, j) == grid_state['end']:
                values[i, j] = 100.0  # 終點固定為 100
            elif (i, j) == grid_state['start']:
                values[i, j] = -100.0  # 起點固定為 -100
            elif (i, j) in grid_state['obstacles']:
                values[i, j] = None
    
    gamma = 0.9  # 折扣因子
    for _ in range(100):  # 價值迭代
        new_values = np.full((size, size), 0.0, dtype=float)
        for i in range(size):
            for j in range(size):
                if (i, j) == grid_state['end']:
                    new_values[i, j] = 100.0  # 終點固定為 100
                elif (i, j) == grid_state['start']:
                    new_values[i, j] = -100.0  # 起點固定為 -100
                elif (i, j) in grid_state['obstacles']:
                    new_values[i, j] = None  # 障礙保持 None
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
                    
                    # 計算即時獎勵
                    reward = 0.0
                    if is_out_of_bounds or is_obstacle:
                        reward = -10.0  # 撞到障礙或邊界
                    else:
                        current_dist = manhattan_distance((i, j), grid_state['end'])
                        next_dist = manhattan_distance((next_i, next_j), grid_state['end'])
                        if next_dist < current_dist:
                            reward = 1.0  # 更接近終點
                        elif next_dist > current_dist:
                            reward = -1.0  # 遠離終點
                        # 如果距離不變，reward 保持 0
                    
                    next_value = values[next_i, next_j] if values[next_i, next_j] is not None else 0.0
                    new_values[i, j] = reward + gamma * next_value
        
        values = new_values
    
    grid_state['values'] = [[cell if not np.isnan(cell) else None for cell in row] for row in values.tolist()]
    
    print("Calculate completed:", grid_state)
    return jsonify({
        'success': True,
        'policy': grid_state['policy'],
        'values': grid_state['values']
    })

@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify(grid_state)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)