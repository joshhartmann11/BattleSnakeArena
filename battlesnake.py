import random
import time
import traceback
import copy
import uuid
import argparse
import tqdm
import requests
import traceback
from threading import Thread
from multiprocessing import Pool

import snakes

FOOD_COLOR = snakes.COLORS["green"]
BORDER_COLOR = snakes.COLORS["grey"]
DEFAULT_COLOR = snakes.COLORS["default"]

VERBOSE = False

class BattleSnake():

    def __init__(self, dims=(11,11), food_start=5, food_rate=0.02, seed=None):
        self.seed = seed if seed else int(time.time()*10000)
        random.seed(self.seed)
        self.width = dims[0]
        self.height = dims[1]
        self.snakes = []
        self.turn = 0
        self.food = []
        self.food = self._init_food(food_start)
        self.food_prob = 0
        self.food_rate = food_rate


    def add_snake(self, snake):
        snake.body.append(self._empty_spot())
        self.snakes.append(snake)


    def start_game(self, speed=50, output_board=True, debug=False):
        solo = (len(self.snakes) == 1)

        json = self._get_board_json()
        for s in self.snakes: s.start(json)

        while(True):
            t1 = time.time()
            self._move_snakes(debug=debug)
            self._detect_death()
            self._check_food()
            self._add_food()

            self.turn += 1

            if output_board: self.print_board()

            if self._check_winner(solo):
                break

            while(time.time()-t1 <= float(100-speed)/float(100)): pass


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


    def _init_food(self, food):
        places = []
        for i in range(food):
            places.append(self._empty_spot())
        return places


    def _add_food(self):
        if random.random() < self.food_prob:
            self.food.append(self._empty_spot())
            self.food_prob = self.food_rate
        else:
            self.food_prob += self.food_rate


    def _empty_spot(self):
        taken = list(self.food)
        for s in self.snakes:
            taken.extend(s.body)

        spot = (random.choice(range(self.width)),
                random.choice(range(self.height)))
        while spot in taken:
            spot = (random.choice(range(self.width)),
                    random.choice(range(self.height)))
        return spot


    def _move_snakes(self, debug=False):
        json = self._get_board_json()
        threads = []
        for snake in self.snakes:
            process = Thread(target=snake.move, args=(json,))
            process.start()
            threads.append(process)

        for process in threads:
            process.join()


    def _delete_snakes(self, snakes, reason=None):
        if not snakes == []:
            for s in snakes:
                if s in self.snakes:
                    s.end(self._get_board_json())
                    self.snakes.remove(s)


    def _resolve_head_collisions(self):
        del_snakes = []
        for s1 in self.snakes:
            for s2 in self.snakes:
                if s1 != s2:
                    if s2.body[0] == s1.body[0]:
                        if len(s1.body) > len(s2.body):
                            del_snakes.append(s2)

                        elif len(s1.body) < len(s2.body):
                            del_snakes.append(s1)
                        else:
                            del_snakes.append(s1)
                            del_snakes.append(s2)

        self._delete_snakes(del_snakes, reason="HEAD-ON-HEAD")


    def _detect_snake_collision(self):
        all_snakes = []
        for s in self.snakes:
            all_snakes.extend(s.body[1:])

        del_snakes = []
        for s in self.snakes:
            head = s.body[0]
            if head in all_snakes:
                del_snakes.append(s)

        self._delete_snakes(del_snakes, reason="SNAKE COLLISION")


    def _detect_wall_collision(self):
        del_snakes = []
        for s in self.snakes:
            head = s.body[0]
            if( head[0] < 0 or head[1] < 0 or
                head[0] >= self.width or
                head[1] >= self.height):
                del_snakes.append(s)

        self._delete_snakes(del_snakes, reason="WALL COLLISION")


    def _detect_starvation(self):
        del_snakes = []
        for s in self.snakes:
            if(s.health <= 0):
                del_snakes.append(s)

        self._delete_snakes(del_snakes, reason="STARVATION")


    def _check_food(self):
        for f in self.food:
            for s in self.snakes:
                if f in s.body:
                    s.health = 100
                    s.ate_food = True
                    if f in self.food:
                        self.food.remove(f)


    def _get_board_json(self):
        jsonobj = {}
        jsonobj["turn"] = self.turn
        jsonobj["board"] = {}
        jsonobj["board"]["height"] = self.height
        jsonobj["board"]["width"] = self.width
        jsonobj["board"]["snakes"] = [s.jsonize() for s in self.snakes]
        jsonobj["board"]["food"] = [{"x":f[0], "y":f[1]} for f in self.food]
        return jsonobj


    def _detect_death(self):
        self._detect_starvation()
        self._detect_wall_collision()
        self._detect_snake_collision()
        self._resolve_head_collisions()


    def _check_winner(self, solo):
        return (len(self.snakes) == 1 and not solo) or (len(self.snakes) == 0)







class Snake():

    def __init__(self, name=None, id=None, color=None, move=None, end=None, start=None, server=None, **kwargs):
        self.body = []
        self.health = 100
        self.ate_food = False
        self.color = color if color else COLORS["red"]
        self.id = id if id else str(uuid.uuid4())
        self.name = name if name else self.id
        self._move = move
        self._start = start
        self._end = end
        self.server = server
        self.kwargs = kwargs


    def jsonize(self):
        jsonobj = {}
        jsonobj["health"] = self.health
        jsonobj["body"] = [{"x": b[0], "y": b[1]} for b in self.body]
        jsonobj["id"] = self.id
        jsonobj["name"] = self.name
        return jsonobj


    def move(self, data):
        data["you"] = self.jsonize()
        try:
            if self._move:
                r = self._move(data)
            elif self.server:
                url = self.server + "/move"
                r = requests.post(url, json=data).json()
        except Exception as e:
            traceback.print_exc()
            r = {"move": "up"}
        self._move_snake(r["move"])


    def start(self, data):
        data["you"] = self.jsonize()
        try:
            if self._start:
                self._start(data)
            elif self.server:
                url = self.server + "/start"
                requests.post(url, json=data)
        except Exception as e:
            traceback.print_exc()


    def end(self, data):
        data["you"] = self.jsonize()
        try:
            if self._end:
                self._end(data)
            elif self.server:
                url = self.server + "/end"
                requests.post(url, json=data)
        except Exception as e:
            traceback.print_exc()


    def _move_snake(self, mv):
        head = self.body[0]

        if(mv == "left"):
            self.body = [(head[0]-1, head[1])] + self.body
        elif(mv == "right"):
            self.body = [(head[0]+1, head[1])] + self.body
        elif(mv == "down"):
            self.body =[(head[0], head[1]+1)] + self.body
        else:
            self.body = [(head[0], head[1]-1)] + self.body


        if len(self.body) > 3 and not self.ate_food:
            self.body = self.body[:-1]
        self.ate_food = False
        self.health = self.health -1


    def reset(self):
        self.body = []
        self.health = 100
        self.ate_food = False








def verbose_print(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


def run_game(snakes, food=0.005, dims=(11,11), suppress_board=False, speed=80, quiet=False, seed=None):
    game = BattleSnake(food_start=len(snakes), food_rate=food, dims=dims, seed=seed)
    for s in snakes: game.add_snake(s)

    game_results = {}
    game_results["winner"] = game.start_game(speed=speed, output_board=suppress_board, debug=True)
    game_results["turns"] = game.turn
    game_results["seed"] = game.seed

    if not quiet:
        print("Winner: {}, Turns: {}, Seed: {}".format(game_results["winner"], game_results["turns"], game_results["seed"] ))

    return game_results


def _run_game_from_args(args):
    return run_game(
        snakes=args.snakes,
        food=args.food,
        dims=args.dims,
        suppress_board=args.suppress_board,
        speed=args.speed,
        quiet=args.silent,
        seed=args.seed)


def parse_args(sysargs=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--food", help="Rate of food spawning", type=float, default=0.02)
    parser.add_argument("-s", "--snakes", nargs='+', help="Snakes to battle", type=str, default=["simpleJake2019", "battleJake2019"])
    parser.add_argument("-d", "--dims", nargs='+', help="Dimensions of the board in x,y", type=int, default=[11,11])
    parser.add_argument("-p", "--silent", help="Print information about the game", action="store_true", default=False)
    parser.add_argument("-g", "--games", help="Number of games to play", type=int, default=1)
    parser.add_argument("-b", "--suppress-board", help="Don't print the board", action="store_false", default=True)
    parser.add_argument("-t", "--threads", help="Number of threads to run multiple games on", type=int, default=4)
    parser.add_argument("-i", "--seed", help="Game seed", type=int, default=None)
    parser.add_argument("-sp", "--speed", help="Speed of the game", type=int, default=90)
    if sysargs:
        args = parser.parse_args(sysargs)
    else:
        args = parser.parse_args()

    if len(args.dims) == 1:
        dims = (args.dims[0], args.dims[0])
    elif len(args.dims) == 2:
        dims = tuple(args.dims)

    battle_snakes = []
    for input_snake in args.snakes:
        snek = [k for k in snakes.SNAKES if input_snake == k['name']]
        if len(snek) == 1:
            s = snek[0]
            battle_snakes.append(Snake(**s))
        else:
            verbose_print("Malformed snakes.py file or snakes input argument.")
    args.snakes = battle_snakes

    return args


def main():
    args = parse_args()

    if args.games == 1 or args.suppress_board:
        for i in range(args.games):
            _run_game_from_args(args)
    else:
        args.silent = True
        with Pool(args.threads) as p:
            outputs = list(tqdm.tqdm(p.imap_unordered(_run_game_from_args, [args for i in range(args.games)]), total=args.games))

        winners = [d["winner"] for d in outputs]

        for winner in set(winners):
            print("{}, Games Won: {}".format(winner, sum([1 for s in winners if s == winner])))


if __name__ == "__main__":
    main()
