def distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx+dy


def direction(a, b):
    if(a[0] > b[0]):
        return 'left'
    if(a[0] < b[0]):
        return 'right'
    if(a[1] > b[1]):
        return 'up'
    if(a[1] < b[1]):
        return 'down'


def flood_fill(target, grid, obstacles):
    visited = []
    frontier = []
    # print(str('Target is ' + str(grid[target[0]][target[1]])))
    frontier.append(target)
    '''if grid[target[0]][target[1]] not in obstacles:
        frontier.append(target)
    else:
        print('early fail ' + str(target))
        return 0'''
    # even earlier exist
    while len(frontier) > 0:
        for f in frontier:
            frontier.remove(f)
            if f not in visited:
                visited.append(f)
            neigh = neighbours(f, grid, obstacles)
            for n in neigh:
                if n not in visited and n not in frontier:
                    frontier.append(n)
            break
    # print(str(target) + ' room for ' + str(len(visited)))
    return visited


def enough_space(target, target_size, grid, obstacles):
    visited = []
    frontier = []
    # print(str('Target is ' + str(grid[target[0]][target[1]])))
    frontier.append(target)
    '''if grid[target[0]][target[1]] not in obstacles:
        frontier.append(target)
    else:
        print('early fail ' + str(target))
        return 0'''
    # even earlier exist
    while len(frontier) > 0 and len(visited) < target_size:
        for f in frontier:
            frontier.remove(f)
            if f not in visited:
                visited.append(f)
            neigh = neighbours(f, grid, obstacles)
            for n in neigh:
                if n not in visited and n not in frontier:
                        frontier.append(n)
            break
    # print(str(target) + ' room for ' + str(len(visited)))
    return len(visited)


def get_diagonals(node, grid, ignore_list):
    width = len(grid)
    height = len(grid[0])
    result = []
    if(node[0] > 0 and node[1] > 0):
        result.append((node[0]-1, node[1]-1))
    if(node[0] < width - 1 and node[1] < height - 1):
        result.append((node[0]+1, node[1]+1))
    if(node[0] < width - 1 and node[1] > 0):
        result.append((node[0]+1, node[1]-1))
    if(node[0] > 0 and node[1] < height - 1):
        result.append((node[0]-1, node[1]+1))
    result = filter(lambda n: (grid[n[0]][n[1]] not in ignore_list), result)
    open_set = []
    for r in result:
        open_set.append(r)
    return open_set


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


def on_edge_of_grid(node, grid):
    width = len(grid)
    height = len(grid[0])
    if(node[0] == 0):
        return True
    if(node[0] == width - 1):
        return True
    if(node[1] == 0):
        return True
    if(node[1] == height-1):
        return True

    return False


def trace_path(came_from, current):
    result = [current]

    while current in came_from.keys():
        current = came_from[current]
        result.append(current)

    result.reverse()
    return result


def find_path(start, goal, waypoints, links, grid, obstacles):
    if type(start) is not tuple:
        start = tuple(start)
    if type(goal) is not tuple:
        goal = tuple(goal)
    temp = grid[start[0]][start[1]]
    grid[start[0]][start[1]] = 0
    links[start] = connecting_points(start, waypoints, grid, obstacles)
    connect_points_to(goal, waypoints, links, grid, obstacles)
    connect_point_to(start, goal, links, grid, obstacles)
    ''' Make Waypoints point to the goal!'''
    open_set = [start]
    closed_set = []
    came_from = {}

    g_score = {}
    for w in waypoints:
        g_score[w] = 10000
    g_score[start] = 0

    f_score = {}
    for w in waypoints:
        f_score[w] = 10000
    f_score[start] = distance(start, goal)

    while len(open_set) > 0:
        # print(open_set)
        # print(len(open_set))
        # fix... adapt for waypoints
        current = None
        for w in open_set:
            # print(w)
            if current is None:
                current = w
            if(f_score[w] < f_score[current]):
                current = w

        if(current == goal):
            path = trace_path(came_from, current)
            grid[start[0]][start[1]] = temp
            for w in waypoints:
                if goal in links[w]:
                    links[w].remove(goal)
            '''for x in path:
                print(str(x))'''
            return path

        open_set.remove(current)
        closed_set.append(current)

        for n in links[current]:
            if n in closed_set:
                continue

            tentative_g_score = g_score[current] + distance(current, n)

            if n not in open_set:
                open_set.append(n)
            elif tentative_g_score >= g_score[n]:
                continue

            came_from[n] = current
            g_score[n] = tentative_g_score
            f_score[n] = tentative_g_score + distance(n, goal)
    grid[start[0]][start[1]] = temp
    for w in waypoints:
        if goal in links[w]:
            links[w].remove(goal)
    return None


def generate_waypoints(grid, obstacles, interest_points):
    '''Fix waypoint placement, also include waypoints around the head.
    A few more waypoints would be better than a broken path'''
    waypoints = []
    generated_points = []
    # width = len(grid)
    # height = len(grid[0])
    for interest_point in interest_points:
        neigh = neighbours(interest_point, grid, obstacles)
        for n in neigh:
            if n not in generated_points:
                generated_points.append(n)
                waypoints.append(n)
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] in obstacles:
                pos = (x, y)
                dia = get_diagonals(pos, grid, obstacles)
                for d in dia:
                    neigh = neighbours(d, grid, [])
                    add = True
                    for n in neigh:
                        if grid[n[0]][n[1]] in obstacles:
                            add = False
                            break
                    if d not in generated_points and add:
                        generated_points.append(d)
                        waypoints.append(d)
                neigh = neighbours(pos, grid, obstacles)
                if len(neigh) == 2:
                    if neigh[0][0] != neigh[1][0] and neigh[0][1] != neigh[1][1]:
                        for n in neigh:
                            if n not in generated_points:
                                generated_points.append(n)
                                waypoints.append(n)
                        dia = get_diagonals(pos, grid, obstacles)
                        for d in dia:
                            if d not in generated_points:
                                generated_points.append(d)
                                waypoints.append(d)
                if len(neigh) == 3:
                    for n in neigh:
                        if n not in generated_points:
                            generated_points.append(n)
                            waypoints.append(n)
                if on_edge_of_grid(pos, grid):
                    for n in neigh:
                        if n not in generated_points:
                            generated_points.append(n)
                            waypoints.append(n)
    '''for w in waypoints:
        grid[w[0]][w[1]] = 'W'
        # print(w)
    display_grid(grid)'''
    return waypoints


def link_waypoints(waypoints, grid, obstacles):
    links = {}
    for a in waypoints:
        results = []
        for b in waypoints:
            if a is b:
                continue
            x = min([a[0], b[0]])
            y = min([a[1], b[1]])
            x_max = max([a[0], b[0]])
            y_max = max([a[1], b[1]])
            # print(str(x) + '->' + str(x_max) + ' ' + str(y) + '->' + str(y_max))
            add = True
            while x <= x_max:
                y = min([a[1], b[1]])
                while y <= y_max:
                    # print(str(x) + ':' + str(y) + ' value:' + str(grid[x][y]))
                    if grid[x][y] in obstacles:
                        # print('Something in the way from linking' + str(a) + ' ' + str(b))
                        add = False
                        break
                    y = y + 1
                x = x + 1
                if not add:
                    break
            if add:
                # print(a)
                # print(b)
                # print('Connected two waypoints: ' + str(a) + '->' + str(b))
                results.append(b)
        links[a] = results

    return links


def connecting_points(target, waypoints, grid, obstacles):
    results = []
    a = target
    for b in waypoints:
        if a is b:
            continue
        x = min([a[0], b[0]])
        y = min([a[1], b[1]])
        x_max = max([a[0], b[0]])
        y_max = max([a[1], b[1]])
        # print(str(x) + '->' + str(x_max) + ' ' + str(y) + '->' + str(y_max))
        add = True
        while x <= x_max:
            y = min([a[1], b[1]])
            while y <= y_max:
                # print(str(x) + ':' + str(y) + ' value:' + str(grid[x][y]))
                if grid[x][y] in obstacles:
                    # print('Something in the way from linking' + str(a) + ' ' + str(b))
                    add = False
                    break
                y = y + 1
            x = x + 1
            if not add:
                break
        if add:
            # print(a)
            # print(b)
            # print('Connected two waypoints: ' + str(a) + '->' + str(b))
            results.append(b)

    return results


def connect_points_to(target, waypoints, links, grid, obstacles):
    a = target
    for b in waypoints:
        if a is b:
            continue
        x = min([a[0], b[0]])
        y = min([a[1], b[1]])
        x_max = max([a[0], b[0]])
        y_max = max([a[1], b[1]])
        # print(str(x) + '->' + str(x_max) + ' ' + str(y) + '->' + str(y_max))
        add = True
        while x <= x_max:
            y = min([a[1], b[1]])
            while y <= y_max:
                # print(str(x) + ':' + str(y) + ' value:' + str(grid[x][y]))
                if grid[x][y] in obstacles:
                    # print('Something in the way from linking' + str(a) + ' ' + str(b))
                    add = False
                    break
                y = y + 1
            x = x + 1
            if not add:
                break
        if add:
            links[b].append(target)
            # print(a)
            # print(b)
            # print('Connected two waypoints')


def connect_point_to(start, target, links, grid, obstacles):
    b = start
    a = target
    if a is b:
        return
    x = min([a[0], b[0]])
    y = min([a[1], b[1]])
    x_max = max([a[0], b[0]])
    y_max = max([a[1], b[1]])
    # print(str(x) + '->' + str(x_max) + ' ' + str(y) + '->' + str(y_max))
    add = True
    while x <= x_max:
        y = min([a[1], b[1]])
        while y <= y_max:
            # print(str(x) + ':' + str(y) + ' value:' + str(grid[x][y]))
            if grid[x][y] in obstacles:
                # print('Something in the way from linking' + str(a) + ' ' + str(b))
                add = False
                break
            y = y + 1
        x = x + 1
        if not add:
            break
    if add:
        links[b].append(target)


def display_grid(grid):
    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[y])):
            row = row + str(grid[x][y]) + " "
        print(row)
