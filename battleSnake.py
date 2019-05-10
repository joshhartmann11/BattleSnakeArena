import random
import time
import traceback
import copy
import uuid
import argparse
import snakes
from threading import Thread

FOOD_COLOR = snakes.COLORS["green"]
BORDER_COLOR = snakes.COLORS["grey"]
DEFAULT_COLOR = snakes.COLORS["default"]

VERBOSE = False

class BattleSnake():

    def __init__(self, dims=(11,11), foodStart=5, foodRate=0.008):
        self.width = dims[0]
        self.height = dims[1]
        self.snakes = []
        self.turn = 0
        self.food = []
        self.food = self.init_food(foodStart)
        self.foodProb = 0
        self.foodRate = foodRate


    # Initialize the positions of food
    def init_food(self, food):
        places = []
        for i in range(food):
            places.append(self.empty_spot())
        return places


    # Add a food
    def add_food(self):
        if random.random() < self.foodProb:
            self.food.append(self.empty_spot())
            self.foodProb = self.foodRate
        else:
            self.foodProb += self.foodRate


    # Find a random empty spot
    def empty_spot(self):
        taken = list(self.food)
        for s in self.snakes:
            taken.extend(s.body)

        spot = (random.choice(range(self.width)),
                random.choice(range(self.height)))
        while spot in taken:
            spot = (random.choice(range(self.width)),
                    random.choice(range(self.height)))
        return spot


    # Add the snakes
    def add_snake(self, snake):
        snake.body.append(self.empty_spot())
        self.snakes.append(snake)


    # Move a single snake
    def move_snake(self, snake, json):
        input = self.specific_board_json(snake, json)
        try:
            cpy = copy.deepcopy(input)
            output = snake.getMove(cpy)
        except AssertionError as e:
            traceback.print_tb(e.__traceback__)
            output = {"move": "up"}
        snake.move(output["move"])


    # Move snakes
    def move_snakes(self, debug=False):
        json = self.generic_board_json()
        threads = []
        for i, snake in enumerate(self.snakes):
            process = Thread(target=self.move_snake, args=(snake, json))
            process.start()
            threads.append(process)

        for process in threads:
            process.join()

        self.check_food()
        self.detect_death()

        self.turn += 1


    # Delete snakes
    def delete_snakes(self, snakes, reason=None):

        if not snakes == []:
            for s in snakes:
                if s in self.snakes:
                    self.snakes.remove(s)


    # Checks to see if there's a winner
    def check_winner(self, solo):
        if(len(self.snakes) == 1 and not solo):
            return True
        if(len(self.snakes) == 0):
            return True
        return False


    # Start the game
    def start_game(self, speed=50, outputBoard=True, debug=False):
        if(len(self.snakes) == 1):
            solo = True
        else:
            solo = False

        while(True):
            t1 = time.time()
            self.add_food()
            self.move_snakes(debug=debug)

            if outputBoard:
                self.print_board()
                # Restore default coloring to terminal

            if self.check_winner(solo):
                break

            while(time.time()-t1 <= float(100-speed)/float(100)):
                pass

        if not len(self.snakes) == 0:
            return(self.snakes[0].name)


    # Resolve Head-on-head Collisions
    def resolve_head_collisions(self):

        delSnakes = []
        for s1 in self.snakes:
            for s2 in self.snakes:
                if s1 != s2:
                    if s2.body[0] == s1.body[0]:
                        if len(s1.body) > len(s2.body):
                            delSnakes.append(s2)

                        elif len(s1.body) < len(s2.body):
                            delSnakes.append(s1)
                        else:
                            delSnakes.append(s1)
                            delSnakes.append(s2)

        self.delete_snakes(delSnakes, reason="HEAD-ON-HEAD")


    # Detect Snake Collision
    def detect_snake_collision(self):
        allSnakes = []
        for s in self.snakes:
            allSnakes.extend(s.body[1:])

        delSnakes = []
        for s in self.snakes:
            head = s.body[0]
            if head in allSnakes:
                delSnakes.append(s)

        self.delete_snakes(delSnakes, reason="SNAKE COLLISION")


    # Detect Wall Collision
    def detect_wall_collision(self):
        delSnakes = []
        for s in self.snakes:
            head = s.body[0]
            if( head[0] < 0 or head[1] < 0 or
                head[0] >= self.width or
                head[1] >= self.height):
                delSnakes.append(s)

        self.delete_snakes(delSnakes, reason="WALL COLLISION")


    # Detect Starvation
    def detect_starvation(self):
        delSnakes = []
        for s in self.snakes:
            if(s.health <= 0):
                delSnakes.append(s)

        self.delete_snakes(delSnakes, reason="STARVATION")


    # Death detection
    def detect_death(self):
        self.detect_starvation()
        self.detect_wall_collision()
        self.detect_snake_collision()
        self.resolve_head_collisions()


    # Detect Eaten Food
    def check_food(self):
        for f in self.food:
            for s in self.snakes:
                if f in s.body:
                    s.ateFood = True
                    if f in self.food:
                        self.food.remove(f)


    # Jsonize food
    def jsonize_food(self):
        food = []
        for f in self.food:
            food.append({"x":f[0], "y":f[1]})
        return food


    # Jsonize the board specific to the given snake
    def specific_board_json(self, snake, jsonobj):
        jsonobj["you"] = snake.jsonize()
        return jsonobj


    # Jsonize the parts of the board that are not specific to the snake
    def generic_board_json(self):
        jsonobj = {}
        jsonobj["turn"] = self.turn
        jsonobj["board"] = {}
        jsonobj["board"]["height"] = self.height
        jsonobj["board"]["width"] = self.width
        jsonobj["board"]["snakes"] = [s.jsonize() for s in self.snakes]
        jsonobj["board"]["food"] = self.jsonize_food()
        return jsonobj


    # Print the board
    def print_board(self):
        snakes = []
        for s in self.snakes:
            snakes.append(s.body)

        ywall = " " * 2 * self.width + "  "
        print(f"{BORDER_COLOR}{ywall}{DEFAULT_COLOR}") # Y Border
        for j in range(self.height):
            print(f"{BORDER_COLOR} {DEFAULT_COLOR}", end="") # X Border
            for i in range(self.width):
                if (i, j) in self.food:
                    print(f"{FOOD_COLOR}  {DEFAULT_COLOR}", end="") # Food
                else:
                    no_snake = True
                    for ind, s in enumerate(snakes):
                        if (i, j) in s:
                            if s[0] == (i, j):
                                print(f"{self.snakes[ind].color}OO{DEFAULT_COLOR}", end="") # Head
                            else:
                                print(f"{self.snakes[ind].color}  {DEFAULT_COLOR}", end="") # Body
                            no_snake = False
                    if no_snake:
                        print(f"{DEFAULT_COLOR}  {DEFAULT_COLOR}", end="") # Empty
            print(f"{BORDER_COLOR} {DEFAULT_COLOR}") # X Border
        print(f"{BORDER_COLOR}{ywall}{DEFAULT_COLOR}") # Y Border


class Snake():

    def __init__(self, moveFunction, name=None, id=None, color=None):
        self.body = []
        self.health = 100
        self.ateFood = False
        self.color = color if color else COLORS["red"]
        self.id = id if id else uuid.uuid4()
        self.name = name if name else self.id
        self.getMove = moveFunction


    # Puts the snakes information into the required json format
    def jsonize(self):
        jsonobj = {}
        jsonobj["health"] = self.health
        jsonobj["body"] = [{"x": b[0], "y": b[1]} for b in self.body]
        jsonobj["id"] = self.id
        jsonobj["name"] = self.name
        return jsonobj


    # Moves the snake
    def move(self, move):

        head = self.body[0]

        if(move == "left"):
            self.body = [(head[0]-1, head[1])] + self.body
        elif(move == "right"):
            self.body = [(head[0]+1, head[1])] + self.body
        elif(move == "down"):
            self.body =[(head[0], head[1]+1)] + self.body
        else:
            self.body = [(head[0], head[1]-1)] + self.body

        if self.ateFood:
            self.health = 100
        else:
            if len(self.body) > 3:
                self.body = self.body[:-1]
            self.health = self.health -1
        self.ateFood = False

    def reset(self):
        self.body = []
        self.health = 100
        self.ateFood = False

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--food", help="Rate of food spawning", type=float, default=0.005)
    parser.add_argument("-s", "--snakes", nargs='+', help="Snakes to battle", type=str, default=["simpleJake2019", "battleJake2019"])
    parser.add_argument("-d", "--dims", nargs='+', help="Dimensions of the board in x,y", type=int, default=[11,11])
    parser.add_argument("-p", "--silent", help="Print information about the game", action="store_true", default=False)
    parser.add_argument("-g", "--games", help="Number of games to play", type=int, default=1)
    parser.add_argument("-b", "--suppress-board", help="Don't print the board", action="store_false", default=True)
    parser.add_argument("-sp", "--speed", help="Speed of the game", type=int, default=95)
    args = parser.parse_args()
    return args


def verbose_print(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


if __name__ == "__main__":
    args = parse_args()
    VERBOSE = not args.silent
    if len(args.dims) == 1:
        dims = (args.dims[0], args.dims[0])
    elif len(args.dims) == 2:
        dims = tuple(args.dims)

    battleSnakes = []
    for input_snake in args.snakes:
        snek = [k for k in snakes.SNAKES if input_snake == k['name']]
        if len(snek) == 1:
            s = snek[0]
            battleSnakes.append(Snake(s["move"], name=s["name"], id=str(uuid.uuid4()), color=s["color"]))
        else:
            verbose_print("Malformed snakes.py file or snakes input argument.")

    gameWinners = []
    for i in range(args.games):
        game = BattleSnake(foodStart=len(args.snakes), foodRate=args.food, dims=dims)
        [game.add_snake(s) for s in battleSnakes]
        winner = game.start_game(speed=args.speed, outputBoard=args.suppress_board, debug=True)
        gameWinners.append(winner)
        if args.games > 1:
            verbose_print("Game {}: ".format(i), winner)
            [s.reset() for s in battleSnakes]
        else:
            verbose_print("Winner: ", winner)

    if args.games > 1:
        print("-"*20)
        print("Game Winners")
        print("-"*20)
        for winner in set(gameWinners):
            print(winner, sum([1 for s in gameWinners if s == winner]))
        print("-"*20)
