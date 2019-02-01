from TestSnakes.MitchellNursey.graph_algorithms import find_path, generate_waypoints, link_waypoints, enough_space, flood_fill
import random
import os
import time

EMPTY = 0
WALL = 1
SNAKE = 2
FOOD = 3
DANGER = 4
SNAKE_HEAD = 5
SNAKE_TAIL = 6
DEAD_END = 7
DIRECTIONS = ['up', 'down', 'left', 'right']
BAD_POSITIONS = [WALL, SNAKE, DANGER, SNAKE_HEAD, SNAKE_TAIL, DEAD_END]
PATH_FINDING_OBSTACLES = [WALL, SNAKE, DANGER, SNAKE_HEAD, SNAKE_TAIL]
GOOD_POSITIONS = [EMPTY, FOOD]
DEATH_POSITIONS = [WALL, SNAKE, SNAKE_HEAD]
GOAL_POSITIONS = [FOOD]
taunt = 'Make money sell money'

def point_to_list(json_object):
    return (json_object['x'], json_object['y'])


def objectives(data):
    results = []
    food = data['food']['data']
    for f in food:
        results.append(point_to_list(f))
    return results


def generate_grid(snake_id, my_snake_length, data):
    grid = [[0 for col in range(data['height'])] for row in range(data['width'])]

    for food in data['food']['data']:
        food = point_to_list(food)
        grid[food[0]][food[1]] = FOOD

    for snake in data['snakes']['data']:
        for coord in snake['body']['data']:
            coord = point_to_list(coord)
            # Add in once accounting for eating an apple
            # if coord != snake['coords'][-1]:
            grid[coord[0]][coord[1]] = SNAKE

        if snake_id != snake['id']:
            if my_snake_length <= snake['length']:
                danger_spots = neighbours(point_to_list(snake['body']['data'][0]), grid, PATH_FINDING_OBSTACLES)
                for n in danger_spots:
                    grid[n[0]][n[1]] = DANGER
        snake_head = point_to_list(snake['body']['data'][-1])
        grid[snake_head[0]][snake_head[1]] = SNAKE_TAIL
        snake_head = point_to_list(snake['body']['data'][0])
        grid[snake_head[0]][snake_head[1]] = SNAKE_HEAD

    # start = time.time()
    possible_dead_end = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            pos = (x, y)
            if grid[x][y] in GOOD_POSITIONS:
                neigh = neighbours(pos, grid, BAD_POSITIONS)
                if(len(neigh) <= 1):
                    grid[x][y] = DEAD_END
                    for n in neigh:
                        possible_dead_end.append(n)
                    # print('Found dead end')
    while len(possible_dead_end) > 0:
        for pos in possible_dead_end:
            possible_dead_end.remove(pos)
            if grid[pos[0]][pos[1]] in GOOD_POSITIONS:
                neigh = neighbours(pos, grid, BAD_POSITIONS)
                if(len(neigh) <= 1):
                    grid[pos[0]][pos[1]] = DEAD_END
                    for n in neigh:
                        possible_dead_end.append(n)
                    # print('Found dead end')
    # end = time.time()
    # print('Time to tag DEAD_ENDs: ' + str((end - start) * 1000) + 'ms')
    # display_grid(grid)
    return grid


def direction(a, b):
    if(a[0] > b[0]):
        return 'left'
    if(a[0] < b[0]):
        return 'right'
    if(a[1] > b[1]):
        return 'up'
    if(a[1] < b[1]):
        return 'down'


def get_forward_node(head, neck, grid):
    width = len(grid)
    height = len(grid[0])
    if(direction(neck, head) is 'left' and head[0] - 2 > 0):
        return (head[0] - 2, head[1])
    if(direction(neck, head) is 'right' and head[0] + 2 < width):
        return (head[0] + 2, head[1])
    if(direction(neck, head) is 'top' and head[1] - 2 > 0):
        return (head[0], head[1] - 2)
    if(direction(neck, head) is 'down' and head[1] + 2 < height):
        return (head[0], head[1] + 2)
    return None


def smart_attack_move(my_head, b, enemy_head, grid, obstacles, overlapping):
    raw_move = direction(my_head, b)

    if(move_to_position(my_head, raw_move)[0] == b[0] and move_to_position(my_head, raw_move)[1] == b[1] and not overlapping):
        return raw_move

    possible_moves = []
    if(my_head[0] > b[0] and grid[my_head[0] - 1][my_head[1]] not in obstacles):
        possible_moves.append('left')
    if(my_head[0] < b[0] and grid[my_head[0] + 1][my_head[1]] not in obstacles):
        possible_moves.append('right')
    if(my_head[1] > b[1] and grid[my_head[0]][my_head[1] - 1] not in obstacles):
        possible_moves.append('up')
    if(my_head[1] < b[1] and grid[my_head[0]][my_head[1] + 1] not in obstacles):
        possible_moves.append('down')

    if len(possible_moves) == 1:
        return possible_moves[0]

    if 'left' in possible_moves:
        if distance(my_head, b) < distance(enemy_head, b) and my_head[0] > enemy_head[0]:
            return 'left'
    if 'right' in possible_moves:
        if distance(my_head, b) < distance(enemy_head, b) and my_head[0] < enemy_head[0]:
            return 'right'
    if 'up' in possible_moves:
        if distance(my_head, b) < distance(enemy_head, b) and my_head[1] > enemy_head[1]:
            return 'up'
    if 'down' in possible_moves:
        if distance(my_head, b) < distance(enemy_head, b) and my_head[1] < enemy_head[1]:
            return 'down'

    return smart_direction(my_head, b, grid, obstacles, overlapping)


def smart_direction(a, b, grid, obstacles, overlapping):
    raw_move = direction(a, b)
    if(move_to_position(a, raw_move)[0] == b[0] and move_to_position(a, raw_move)[1] == b[1] and not overlapping):
        return raw_move
    if(a[0] > b[0] and grid[a[0] - 1][a[1]] not in obstacles):
        return 'left'
    if(a[0] < b[0] and grid[a[0] + 1][a[1]] not in obstacles):
        return 'right'
    if(a[1] > b[1] and grid[a[0]][a[1] - 1] not in obstacles):
        return 'up'
    if(a[1] < b[1] and grid[a[0]][a[1] + 1] not in obstacles):
        return 'down'


def move_to_position(origin, direction):
    if direction is 'up':
        return (origin[0], origin[1] - 1)
    if direction is 'down':
        return (origin[0], origin[1] + 1)
    if direction is 'right':
        return (origin[0] + 1, origin[1])
    if direction is 'left':
        return (origin[0] - 1, origin[1])


def path_distance(path):
    dis = 0
    path = tuple(path)
    index = 0
    while index < len(path) - 1:
        dis = dis + distance(path[index], path[index + 1])
        index = index + 1
    return dis


def distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx+dy


def neighbours(node, grid, ignore_list):
    width = len(grid)
    height = len(grid[0])
    result = []
    if(node[0] > 0):
        result.append((node[0]-1, node[1]))
    if(node[0] < width - 1):
        result.append((node[0]+1, node[1]))
    if(node[1] > 0):
        result.append((node[0], node[1]-1))
    if(node[1] < height-1):
        result.append((node[0], node[1]+1))
    result = filter(lambda n: (grid[n[0]][n[1]] not in ignore_list), result)
    open_set = []
    for r in result:
        open_set.append(r)
    return open_set


def is_body_overlapping(body):
    for b in body:
        counter = 0
        for d in body:
            if b == d:
                counter = counter + 1
        if counter > 1:
            return True
    return False


def enemy_near_tail(my_head, tail, grid):
    for n in neighbours(tail, grid, []):
        if n[0] == my_head[0] and n[1] == my_head[1]:
            continue
        if grid[n[0]][n[1]] == SNAKE_HEAD:
            return True
            #print('Enemy near tail')
    return False


def get_snake_tails(data):
    tails = []
    for snake in data['snakes']['data']:
        snake_tail = point_to_list(snake['body']['data'][-1])
        tails.append(snake_tail)
    return tails


def add_bad_moves_to_grid(my_snake_head, my_snake_id, snakes, grid):
    #print('my head is at ' + str(my_snake_head))
    my_head_neighbours = neighbours(my_snake_head, grid, PATH_FINDING_OBSTACLES)
    enemy_moves = []

    for enemy in snakes:
        if enemy['id'] == my_snake_id:
            continue
        neigh = neighbours(point_to_list(enemy['body']['data'][0]), grid, DEATH_POSITIONS)
        for n in neigh:
            if n not in enemy_moves:
                enemy_moves.append(n)

    bad_moves = []

    enemy_future_moves = []
    for enemy_move in enemy_moves:
        future_moves = neighbours(enemy_move, grid, DEATH_POSITIONS)
        for future_move in future_moves:
            if future_move not in enemy_future_moves:
                enemy_future_moves.append(future_move)

    # Check if move would put me in a position of chance
    for my_head_neighbour in my_head_neighbours:
        counter = 0
        skip = 0
        future_neighbours = neighbours(my_head_neighbour, grid, DEATH_POSITIONS)
        for future_neigh in future_neighbours:
            if any(future_neigh) in my_head_neighbour:
                skip += 1
                #print('SKIPPED!!!!')
                continue
            for enemy_future_move in enemy_future_moves:
                if future_neigh[0] == enemy_future_move[0] and future_neigh[1] == enemy_future_move[1]:
                    counter += 1

        if counter >= len(future_neighbours) - skip:
            if my_head_neighbour not in bad_moves:
                bad_moves.append(my_head_neighbour)
                #print('Removed Chance move')
    # Check if move would put me in a position to be attacked
    for h in my_head_neighbours:
        f = get_forward_node(h, my_snake_head, grid)
        if f in enemy_moves:
            if h not in bad_moves:
                bad_moves.append(h)
                #print('Removed Vulnerable move')

    if len(bad_moves) != len(my_head_neighbours):
        for b in bad_moves:
            if grid[b[0]][b[1]] not in PATH_FINDING_OBSTACLES:
                grid[b[0]][b[1]] = DANGER


def run_ai(data):
    # Important Info:
    global taunt
    move = None
    current_path = None

    snake_id = data['you']['id']
    goals = objectives(data)
    my_snake_length = data['you']['length']
    my_snake_health = data['you']['health']
    my_snake_overlapping = is_body_overlapping(data['you']['body']['data'])

    grid = generate_grid(snake_id, my_snake_length, data)
    my_snake_head = point_to_list(data['you']['body']['data'][0])
    my_snake_tail = point_to_list(data['you']['body']['data'][-1])
    snakes = data['snakes']['data']

    add_bad_moves_to_grid(my_snake_head, snake_id, snakes, grid)

    # start = time.time()
    interest_points = []
    interest_points.append(my_snake_head)
    for tail in get_snake_tails(data):
        interest_points.append(tail)
    waypoints = generate_waypoints(grid, PATH_FINDING_OBSTACLES, interest_points)
    # end = time.time()
    # print('Time to waypoints: ' + str((end - start) * 1000) + 'ms')
    # start = time.time()
    links = link_waypoints(waypoints, grid, PATH_FINDING_OBSTACLES)
    # end = time.time()
    # print('Time to link waypoints: ' + str((end - start) * 1000) + 'ms')

    # Do I want or need food?
    # Can I bully?
    # Should I find free space?
    # Is food near me?
    # Safe Roam or chase tail?
    if move is None:
        if my_snake_health < 20:
            current_path = path_to_desperation_food(my_snake_head, my_snake_length, my_snake_health, snake_id, goals, waypoints, links, grid, my_snake_overlapping)
            if current_path is not None:
                move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                #print('Desperate to get food at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        if my_snake_health < 50:
            current_path = path_to_safe_food(my_snake_head, my_snake_length, snake_id, goals, snakes, waypoints, links, grid, my_snake_overlapping)
            if current_path is not None:
                move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                #print('Going to food at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        corner_info = corner_enemy(my_snake_head, my_snake_length, snake_id, snakes, waypoints, links, grid)
        if corner_info is not None:
            current_path = corner_info[0]
        if current_path is not None:
            if len(current_path) > 1:
                possible_move = smart_attack_move(my_snake_head, current_path[1], corner_info[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                if possible_move is not None:
                    move = possible_move
                    #print('Going to corner enemy at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        bully_info = path_to_bully_enemy(my_snake_head, my_snake_length, snake_id, goals, snakes, waypoints, links, grid, my_snake_overlapping)
        if bully_info is not None:
            current_path = bully_info[0]
        if current_path is not None:
            if len(current_path) > 1:
                possible_move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                if possible_move is not None:
                    move = possible_move
                    #print('Going to bully enemy at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        if not (enemy_near_tail(my_snake_head, my_snake_tail, grid) and distance(my_snake_head, my_snake_tail) <= 3):
            current_path = path_to_tail(my_snake_head, my_snake_tail, waypoints, links, grid)
        else:
            current_path = None
        if current_path is not None:
            if len(current_path) > 1:
                possible_move = smart_direction(my_snake_head, current_path[1], grid, BAD_POSITIONS + GOAL_POSITIONS, my_snake_overlapping)
                if possible_move is None:
                    possible_move = smart_direction(my_snake_head, current_path[1], grid, BAD_POSITIONS, my_snake_overlapping)
                if possible_move is None:
                    possible_move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                if possible_move is not None:
                    move = possible_move
                    #print('Going to tail at' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        current_path = path_to_enemy_tail(my_snake_head, snake_id, snakes, waypoints, links, grid)
        if current_path is not None:
            if len(current_path) > 1:
                possible_move = smart_direction(my_snake_head, current_path[1], grid, BAD_POSITIONS, my_snake_overlapping)
                if possible_move is None:
                    possible_move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                if possible_move is not None:
                    move = possible_move
                    #print('Going to enemy tail at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        current_path = path_to_snake_body(my_snake_head, snake_id, snakes, waypoints, links, grid)
        if current_path is not None:
            if len(current_path) > 1:
                possible_move = smart_direction(my_snake_head, current_path[1], grid, BAD_POSITIONS + GOAL_POSITIONS, my_snake_overlapping)
                if possible_move is None:
                    possible_move = smart_direction(my_snake_head, current_path[1], grid, BAD_POSITIONS, my_snake_overlapping)
                if possible_move is None:
                    possible_move = smart_direction(my_snake_head, current_path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
                if possible_move is not None:
                    move = possible_move
                    #print('Going to Snake body at ' + str(current_path[-1]) + ' by going ' + str(move))

    if move is None:
        #print('Desperation Move time...')
        move = find_best_move(my_snake_head, my_snake_tail, snake_id, snakes, grid, waypoints, links, my_snake_overlapping)

    return move


def path_to_safe_food(my_snake_head, my_snake_length, snake_id, goals, snakes, waypoints, links, grid, my_snake_overlapping):
    global taunt
    current_path = None
    for goal in goals:
        if current_path is not None:
            if distance(my_snake_head, goal) > path_distance(current_path):
                continue
        easy = True
        for n in neighbours(goal, grid, PATH_FINDING_OBSTACLES):
            if n is DEAD_END:
                easy = False
        for snake in snakes:
            if(snake['id'] != snake_id):
                enemy_dist = distance(point_to_list(snake['body']['data'][0]), goal)
                if enemy_dist <= distance(my_snake_head, goal):
                    easy = False
                    break
        if not easy:
            continue
        # start = time.time()
        path = find_path(my_snake_head, goal, waypoints, links, grid, PATH_FINDING_OBSTACLES)
        # end = time.time()
        # print('Time to get path from o_path: ' + str((end - start) * 1000) + 'ms')
        if path is not None:
            possible_move = smart_direction(my_snake_head, path[1], grid, [], my_snake_overlapping)
            # print('possible_move:' + str(possible_move))
            # print(path)
            block_pos = move_to_position(my_snake_head, possible_move)
            # display_grid(grid)
            # print('block pos:' + str(block_pos))
            temp_hold = grid[block_pos[0]][block_pos[1]]
            grid[block_pos[0]][block_pos[1]] = SNAKE_HEAD
            if my_snake_length <= enough_space(path[-1], my_snake_length, grid, BAD_POSITIONS):
                if current_path is not None:
                    if(path_distance(path) < path_distance(current_path)):
                        current_path = path
                else:
                    current_path = path
            grid[block_pos[0]][block_pos[1]] = temp_hold
            # display_grid(grid)
            # end = time.time()
            # print('Time to fill: ' + str((end - start) * 1000) + 'ms')
    if current_path is not None:
        taunt = 'Safe food'
    return current_path


def path_to_desperation_food(my_snake_head, my_snake_length, my_snake_health, snake_id, goals, waypoints, links, grid, my_snake_overlapping):
    # display_grid(grid)
    global taunt
    current_path = None
    possible_paths = []
    for goal in goals:
        if current_path is not None:
            if distance(my_snake_head, goal) > path_distance(current_path):
                continue
        # start = time.time()
        path = find_path(my_snake_head, goal, waypoints, links, grid, PATH_FINDING_OBSTACLES)
        # end = time.time()
        # print('Time to get path from o_path: ' + str((end - start) * 1000) + 'ms')
        if path is not None:
            # print(str(my_snake_health) + ' ' + str(path_distance(path)) + ' ' + str(goal) + ' ' + str(path))
            # if goal[0] == 19 and goal[1] == 0:
            #    display_grid(grid)
            if my_snake_health < path_distance(path):
                # print('would be dead')
                continue
            possible_paths.append(path)
            possible_move = smart_direction(my_snake_head, path[1], grid, PATH_FINDING_OBSTACLES, my_snake_overlapping)
            block_pos = move_to_position(my_snake_head, possible_move)
            temp_hold = grid[block_pos[0]][block_pos[1]]
            grid[block_pos[0]][block_pos[1]] = SNAKE_HEAD
            if my_snake_length <= enough_space(goal, my_snake_length, grid, BAD_POSITIONS):
                if current_path is not None:
                    if(path_distance(path) < path_distance(current_path)):
                        current_path = path
                else:
                    current_path = path
            else:
                possible_paths.append(path)
            grid[block_pos[0]][block_pos[1]] = temp_hold
        # end = time.time()
        # print('Time to fill: ' + str((end - start) * 1000) + 'ms')
    # print('possible path: ' + str(len(possible_paths)) + ' ' + str(my_snake_health))
    if current_path is None:
        if len(possible_paths) > 0:
            current_path = possible_paths[0]
    taunt = 'Desperation food'
    return current_path


def path_to_tail(my_snake_head, my_snake_tail, waypoints, links, grid):
    global taunt
    current_path = None
    tail_neighbours = neighbours(my_snake_tail, grid, [])
    for n in tail_neighbours:
        path = None
        # print('Looking for tail at ' + str(n) + ' my head at ' + str(my_snake_head))
        if n[0] == my_snake_head[0] and n[1] == my_snake_head[1]:
            r = []
            r.append(my_snake_tail)
            r.append(my_snake_tail)
            current_path = r
            taunt = 'Just going to eat my tail...'
            break
        if n in PATH_FINDING_OBSTACLES:
            continue
        path = find_path(my_snake_head, n, waypoints, links, grid, PATH_FINDING_OBSTACLES)
        if path is not None:
            # print(str(path))
            if current_path is not None:
                if path_distance(current_path) > path_distance(path):
                    current_path = path
            else:
                current_path = path
    if current_path is not None:
        taunt = 'Following my tail'

    return current_path


def path_to_enemy_tail(my_snake_head, snake_id, snakes, waypoints, links, grid):
    global taunt
    current_path = None
    for snake in snakes:
        if snake_id == snake['id']:
            continue
        enemy_tail = point_to_list(snake['body']['data'][-1])
        tail_neighbours = neighbours(enemy_tail, grid, [])
        for n in tail_neighbours:
            path = None
            # print('Looking for tail at ' + str(n) + ' my head at ' + str(my_snake_head))
            if n in PATH_FINDING_OBSTACLES:
                continue
            path = find_path(my_snake_head, n, waypoints, links, grid, PATH_FINDING_OBSTACLES)
            if path is not None:
                # print(str(path))
                if current_path is not None:
                    if path_distance(current_path) > path_distance(path):
                        current_path = path
                else:
                    current_path = path
    if current_path is not None:
        taunt = 'Following Enemy Tail'
        '''print('Found path to enemy tail')'''
    return current_path


def path_to_snake_body(my_snake_head, my_snake_id, snakes, waypoints, links, grid):
    global taunt
    current_path = None
    could_go_to = flood_fill(my_snake_head, grid, DEATH_POSITIONS)
    for snake in snakes:
        body_pos_counter = 0
        snake['body']['data'].reverse()
        for body in snake['body']['data']:
            body_pos_counter = body_pos_counter + 1
            '''if body_pos_counter % 2:
                continue'''
            # TODO go for body only if it's index in body is greater then the distance to it.
            if current_path is not None:
                continue
                '''if path_distance(current_path) < distance(my_snake_head, point_to_list(body)):
                    continue'''
            body_neighbours = neighbours(point_to_list(body), grid, [])
            for n in body_neighbours:
                if n not in could_go_to:
                    continue
                path = None
                if n in PATH_FINDING_OBSTACLES:
                    continue
                path = find_path(my_snake_head, n, waypoints, links, grid, PATH_FINDING_OBSTACLES)
                if path is None:
                    continue
                if(path_distance(path) < body_pos_counter):
                    continue
                if path is not None:
                    # print(str(path))
                    if current_path is not None:
                        if path_distance(current_path) > path_distance(path):
                            current_path = path
                    else:
                        current_path = path

    for snake in snakes:
        snake['body']['data'].reverse()

    if current_path is not None:
        taunt = 'Following Anybody'
        '''print('Found path to snake body:' + str(current_path[-1]) + ' ' + str(path_distance(current_path)))
    else:
        print('Could not find path to any body of any snake')'''
    return current_path


def corner_enemy(my_snake_head, my_snake_length, my_snake_id, snakes, waypoints, links, grid):
    global taunt
    current_path = None
    target_snake_head = None
    for snake in snakes:
        if my_snake_id == snake['id']:
            continue

        enemy_head = point_to_list(snake['body']['data'][0])

        enemy_head_neighbours = neighbours(enemy_head, grid, DEATH_POSITIONS)
        if len(enemy_head_neighbours) != 1:
            continue

        search_node = enemy_head_neighbours[0]
        search_node_neighbours = neighbours(enemy_head, grid, DEATH_POSITIONS)
        visted = []
        while len(search_node_neighbours) == 1:
            visted.append(search_node)
            search_node = search_node_neighbours[0]
            new_neigh = neighbours(search_node, grid, DEATH_POSITIONS)

            for v in visted:
                if v in new_neigh:
                    new_neigh.remove(v)
            search_node_neighbours = new_neigh

        exit_point = search_node
        if len(search_node_neighbours) == 0:
            continue
        # print('Exit point: ' + str(exit_point))
        my_path = find_path(my_snake_head, exit_point, waypoints, links, grid, DEATH_POSITIONS)
        enemy_path = find_path(enemy_head, exit_point, waypoints, links, grid, DEATH_POSITIONS)

        if my_path is None:
            continue

        if enemy_path is None:
            enemy_dist = distance(enemy_head, exit_point)
        else:
            enemy_dist = path_distance(enemy_path)

        larger_and_close = False
        if(path_distance(my_path) <= enemy_dist and my_snake_length > snake['length']):
            larger_and_close = True

        if(path_distance(my_path) < enemy_dist or larger_and_close):
            if current_path is not None:
                if(path_distance(my_path) < path_distance(current_path)):
                    current_path = my_path
                    target_snake_head = enemy_head
            else:
                current_path = my_path
                target_snake_head = enemy_head

    if current_path is not None:
        taunt = 'Cornering'
    else:
        return None
    return (current_path, target_snake_head)


def path_to_bully_enemy(my_snake_head, my_snake_length, snake_id, goals, snakes, waypoints, links, grid, my_snake_overlapping):
    global taunt
    current_path = None
    target_snake_head = None
    for snake in snakes:
        if snake_id == snake['id']:
            continue

        enemy_head = point_to_list(snake['body']['data'][0])
        if my_snake_length > snake['length']:
            head_neighbours = neighbours(enemy_head, grid, [])
        else:
            head_neighbours = []
        forward = get_forward_node(enemy_head, point_to_list(snake['body']['data'][1]), grid)
        if forward is not None:
            move_dir = direction(enemy_head, forward)
            pos = move_to_position(enemy_head, move_dir)
            if grid[pos[0]][pos[1]] not in DEATH_POSITIONS:
                head_neighbours.append(forward)

        for n in head_neighbours:
            path = None
            # print('Looking for tail at ' + str(n) + ' my head at ' + str(my_snake_head))
            if n in DEATH_POSITIONS:
                continue
            # Check if another enemy is closer
            '''easy = True
            for s in snakes:
                if(not s['id'] == snake_id and not s['id'] == snake['id']):
                    enemy_dist = distance(enemy_head, n)
                    if enemy_dist <= distance(my_snake_head, n):
                        easy = False
                        break
            if not easy:
                # print('another enemy closer')
                continue'''
            path = find_path(my_snake_head, n, waypoints, links, grid, DEATH_POSITIONS)

            if path is not None:
                if len(path) < 2:
                    continue
                    '''result = []
                    result.append((n[0], n[1]))
                    result.append((n[0], n[1]))
                    print('Moving in to the kill enemy, path is short')
                    if current_path is not None:
                        if(path_distance(result) < path_distance(current_path)):
                            current_path = result
                            continue
                    else:
                        current_path = result
                        continue'''

                # Check if move would lead to snake getting trapped
                possible_move = smart_direction(my_snake_head, path[1], grid, DEATH_POSITIONS, my_snake_overlapping)
                blocked_positions = []
                block_pos = move_to_position(my_snake_head, possible_move)
                blocked_positions.append((block_pos, grid[block_pos[0]][block_pos[1]]))
                grid[block_pos[0]][block_pos[1]] = SNAKE_HEAD
                # print('possible moves after attack: ' + str(neighbours(block_pos, grid, PATH_FINDING_OBSTACLES)))
                # Code to reset grid:
                '''for pos in blocked_positions:
                    grid[pos[0][0]][pos[0][1]] = pos[1]'''

                # Check if the enemy is in a position to block me off
                for n in neighbours(enemy_head, grid, DEATH_POSITIONS):
                    blocked_positions.append((n, grid[n[0]][n[1]]))
                    grid[n[0]][n[1]] = SNAKE_HEAD

                if len(neighbours(block_pos, grid, PATH_FINDING_OBSTACLES)) < 2:
                    for pos in blocked_positions:
                        grid[pos[0][0]][pos[0][1]] = pos[1]
                    continue

                target_surrounding_node = neighbours(block_pos, grid, PATH_FINDING_OBSTACLES)[0]
                if my_snake_length <= enough_space(target_surrounding_node, my_snake_length, grid, BAD_POSITIONS):

                    if current_path is not None:
                        if(path_distance(path) < path_distance(current_path)):
                            current_path = path
                            target_snake_head = enemy_head
                    else:
                        current_path = path
                        target_snake_head = enemy_head
                for pos in blocked_positions:
                    grid[pos[0][0]][pos[0][1]] = pos[1]
    if current_path is not None:
        taunt = 'Attacking'
    else:
        return None
    return (current_path, target_snake_head)


def find_best_move(my_snake_head, my_snake_tail, snake_id, snakes, grid, waypoints, links, my_snake_overlapping):
    global taunt
    possible_positions = neighbours(my_snake_head, grid, BAD_POSITIONS)
    if len(possible_positions) > 0:
        taunt = 'I love the smell of battle snake in the...'
        size = None
        for n in possible_positions:
            s = enough_space(n, 100, grid, BAD_POSITIONS)
            if size is None:
                size = s
            if size <= s:
                #print('Moving to position with space')
                move = move = direction(my_snake_head, n)
                size = s
    else:
        possible_positions = neighbours(my_snake_head, grid, PATH_FINDING_OBSTACLES)
        if len(possible_positions) > 0:
            taunt = 'I taste bad! Don\'t eat me!'
            size = None
            for n in possible_positions:
                s = enough_space(n, 100, grid, DEATH_POSITIONS)
                if size is None:
                    size = s
                if size <= s:
                    move = move = direction(my_snake_head, n)
                    size = s
            #print('Desperation move:' + str(move))
        else:
            obstacles = PATH_FINDING_OBSTACLES[:]
            obstacles.remove(DANGER)
            possible_positions = neighbours(my_snake_head, grid, obstacles)
            if len(possible_positions) > 0:
                taunt = 'Is this the end?'
                size = None
                for n in possible_positions:
                    s = enough_space(n, 100, grid, DEATH_POSITIONS)
                    if size is None:
                        size = s
                    if size <= s:
                        move = move = direction(my_snake_head, n)
                        size = s
                #print('Desperation move:' + str(move))
            else:
                possible_positions = neighbours(my_snake_head, grid, DEATH_POSITIONS)
                if len(possible_positions) > 0:
                    taunt = 'I\'m too young to die!'
                    size = None
                    for n in possible_positions:
                        s = enough_space(n, 100, grid, DEATH_POSITIONS)
                        if size is None:
                            size = s
                        if size <= s:
                            move = move = direction(my_snake_head, n)
                            size = s
                    #print('Desperation move:' + str(move))
                else:
                    move = 'down'
                    taunt = 'That was irrational of you. Not to mention unsportsmanlike.'
                    #print('No where to go!!!')
    return move



def get_restrictions(head, mySize, walls, snakes, heads, size, op=True):

    directions = {'up':1, 'down':1, 'left':1, 'right':1}

    # Don't hit a wall
    if(head[0] == walls[0]-1):
        directions['right'] = 0

    elif(head[0] == 0):
        directions['left'] = 0

    if(head[1] == 0):
        directions['up'] = 0

    elif(head[1] == walls[1]-1):
        directions['down'] = 0

    # Don't hit other snakes
    for s in snakes:
        xdist = abs(s[0]-head[0])
        ydist = abs(s[1]-head[1])

        if(xdist + ydist == 1):

            if(xdist == 1):

                if(s[0] > head[0]):
                    directions['right'] = 0

                else:
                    directions['left'] = 0

            else:

                if(s[1] > head[1]):
                    directions['down'] = 0

                else:
                    directions['up'] = 0

    directions2 = {key: value for key, value in directions.items()}

    # Be scared of the heads of others if they're scary
    for i, h in enumerate(heads):

        if(not (size[i] < mySize)):
            xdist = h[0]-head[0]
            ydist = h[1]-head[1]

            if(abs(xdist) == 1 and abs(ydist) == 1):

                if(xdist > 0):
                    directions['right'] = 0

                elif(xdist < 0):
                    directions['left'] = 0

                if(ydist > 0):
                    directions['down'] = 0

                elif(ydist < 0):
                    directions['up'] = 0

            elif((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):

                if(xdist == 2):
                    directions['right'] = 0

                elif(xdist == -2):
                    directions['left'] = 0

                elif(ydist == 2):
                    directions['down'] = 0

                else:
                    directions['up'] = 0

    # If there's no other choice but to possibly collide with a head
    if(1 not in directions.values() and op):
        directions = directions2

    if not op:
        directions = directions2

    moves = [k for k in directions.keys() if directions[k] is 1]

    return moves



def move(data2):
    global taunt
    # print(str(data))
    data = dict(data2)
    try:
        taunt = 'Make money sell money'
        start = time.time()
        output = run_ai(data)
        end = time.time()
    except:
        data = dict(data2)
        you = data['you']
        health = you['health']
        mySize = you['length']
        body = you['body']['data']
        head = (body[0]['x'], body[0]['y'])
        snakes = data['snakes']['data']
        size = []
        walls = (data['width'], data['height'])
        for s in snakes:
            size.append(s['length'])
        snakes = [s['body']['data'] for s in snakes]
        snakes2 = []
        heads = []
        for s1 in snakes:
            heads.append((s1[0]['x'], s1[0]['y']))
            for s2 in s1:
                snakes2.append((s2['x'], s2['y']))
        snakes = snakes2
        moves = get_restrictions(head, mySize, walls, snakes, heads, size)
        if moves == []:
            return {"move": "up"}
        else:
            output = random.choice(moves)

    #print('Time to get AI move: ' + str((end - start) * 1000) + 'ms')
    return {
        'move': output,
        'taunt': taunt
    }
