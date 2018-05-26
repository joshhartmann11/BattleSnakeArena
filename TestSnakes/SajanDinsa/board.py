from collections import namedtuple


Point = namedtuple('Point', ['x', 'y'])


class Food(Point):
    pass


class Snake(object):
    def __init__(self, body, length, health, snake_id):
        self.body = body
        self.length = length
        self.health = health
        self.id = snake_id

    @property
    def head(self):
        return self.body[0]

    @property
    def tip(self):
        return self.body[-1]

    @property
    def tail(self):
        return self.body[1:]

    def tip_stack(self):
        return sum([1 if i == self.body[-1] else 0 for i in self.body])


class Board(list):
    def __init__(self, agent_id, width, height, snakes, food):
        self.agent_id = agent_id
        self.width = width
        self.height = height
        self.snakes = snakes
        self.food = food
        self._grid = [[None for _ in range(height)] for _ in range(width)]

        self._populate_grid()

    @property
    def agent_snake(self):
        for snake in self.snakes.values():
            if snake.id == self.agent_id:
                return snake

    def prune_agent_tail(self, num_points):
        if num_points == 0:
            return None
        snake = self.snakes[self.agent_id]
        for tip in snake.tail:
            self._grid[tip.y][tip.x] = None
        for tip in snake.tail[:-num_points]:
            self._grid[tip.y][tip.x] = snake
        return snake.body[-num_points]

    def pt_distance(self, a, b):
        return  abs(b.y - a.y) + abs(b.x - a.x)

    def _populate_grid(self):
        for snake in self.snakes.values():
            # Excluding tip of snake since we can tail-chase
            for point in snake.body:
                self._grid[point.y][point.x] = snake

        # TK: disabled for now while experimenting with pathfinding library
        #for point in self.food:
        #    self._grid[point.x][point.y] = point

    def __getitem__(self, arg):
        if isinstance(arg, Point):
            return self._grid[arg.y][arg.x]
        return self._grid[arg]

    def __len__(self):
        return len(self._grid)

    def __str__(self):
        return '\n'.join([str([1 if i else 0 for i in row]) for row in self._grid])


def _parse_food(data):
    return [Food(point['x'], point['y']) for point in data['food']['data']]


def _parse_snakes(data):
    snakes = {}
    for snake in data['snakes']['data']:
        body = [Point(point['x'], point['y']) for point in snake['body']['data']]
        snakes[snake['id']] = Snake(body, snake['length'], snake['health'], snake['id'])
    return snakes


def get_board(data):
    snakes = _parse_snakes(data)
    food = _parse_food(data)
    return Board(data['you']['id'], data['width'], data['height'], snakes, food)
