import random
import time
import traceback
import copy
from threading import Thread
import TestSnakes.battleJake2019.main

'''

TODO:
Fix head-on-head detection

'''

COLORS = {  "black": "\033[1;37;40m",
            "red": "\033[1;37;41m",
            "green": "\033[1;37;42m",
            "yellow": "\033[1;37;43m",
            "blue": "\033[1;37;44m",
            "purple": "\033[1;37;45m",
            "cyan": "\033[1;37;46m",
            "grey": "\033[1;37;47m"}

FOOD_COLOR = COLORS["green"]
BORDER_COLOR = COLORS["grey"]
DEFAULT_COLOR = "\033[0m"

class BattleSnake():

    def __init__(self, dims=[20,20], food=5):
        self.dims = {"width": dims[0], "height": dims[1]}
        self.snakes = []
        self.turn = 0
        self.food = []
        self.food = self.init_food(food)


    # Initialize the positions of food
    def init_food(self, food):
        places = []
        for i in range(food):
            places.append(self.empty_spot())
        return places


    # Add a food
    def add_food(self):
        self.food.append(self.empty_spot())


    # Find a random empty spot
    def empty_spot(self):
        taken = list(self.food)
        for s in self.snakes:
            taken.extend(s.body)

        spot = (random.choice(range(self.dims["width"])),
                random.choice(range(self.dims["height"])))
        while spot in taken:
            spot = (random.choice(range(self.dims["width"])),
                    random.choice(range(self.dims["height"])))
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
            self.move_snakes(debug=debug)

            if outputBoard:
                s.print_board()
                print("\n" + BORDER_COLOR + " " * 2 * self.dims["width"] + "    " + DEFAULT_COLOR + "\n", end="")
                print(DEFAULT_COLOR) # Restore default coloring to terminal

            if self.check_winner(solo):
                break

            while(time.time()-t1 <= float(100-speed)/float(100)):
                pass

        if not len(self.snakes) == 0:
            return(self.snakes[0].id)


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
                head[0] >= self.dims["width"] or
                head[1] >= self.dims["height"]):
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
                        self.add_food()


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
        jsonobj["board"]["height"] = self.dims["height"]
        jsonobj["board"]["width"] = self.dims["width"]
        jsonobj["board"]["snakes"] = [s.jsonize() for s in self.snakes]
        jsonobj["board"]["food"] = self.jsonize_food()
        return jsonobj


    # Print the board
    def print_board(self):
        snakes = []
        for s in self.snakes:
            snakes.append(s.body)

        food = self.food

        print(BORDER_COLOR + " " * 2 * self.dims["width"] + "    " + DEFAULT_COLOR, end="")
        for j in range(self.dims["height"]):
	        print("\n" + BORDER_COLOR + "  " + DEFAULT_COLOR, end="")
	        for i in range(self.dims["width"]):

	            if ((i, j)) in food:
	                print(FOOD_COLOR + "  " + DEFAULT_COLOR, end="")
	            else:
	                done = False
	                for ind, s in enumerate(snakes):
	                    if ((i, j)) in s:
	                        if s[0] == ((i, j)):
	                            print(self.snakes[ind].color + "OO" + DEFAULT_COLOR, end="")
	                        else:
	                            print(self.snakes[ind].color + "  " + DEFAULT_COLOR, end="")
	                        done = True

	                if not done:
	                    print(DEFAULT_COLOR + "  " + DEFAULT_COLOR, end="")

	        print(BORDER_COLOR + "  " + DEFAULT_COLOR, end="")



class Snake():

    def __init__(self, moveFunction, id, color):
        self.body = []
        self.health = 100
        self.ateFood = False
        self.color = color
        self.id = id
        self.getMove = moveFunction


    # Puts the snakes information into the required json format
    def jsonize(self):
        jsonobj = {}
        jsonobj["health"] = self.health
        jsonobj["body"] = [{"x": b[0], "y": b[1]} for b in self.body]
        jsonobj["id"] = self.id
        jsonobj["name"] = self.id
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

"""
if __name__ == "__main__":
    gameWinners = []
    for i in range(1000):
        print("*"+ str(i) + "*")
        s = BattleSnake(food=10)
        s.add_snake(Snake(TestSnakes.BattleJake2018.Jake2018.move, "Jake2018", color=COLORS["cyan"]))
        s.add_snake(Snake(TestSnakes.MitchellNursey.MitchellNursey.move, "MitchellNursey", color=COLORS["yellow"]))
        s.add_snake(Snake(TestSnakes.MitchellNursey.MitchellNursey.move, "CornbreadMan", color=COLORS["yellow"]))
        s.add_snake(Snake(TestSnakes.SimpleJake.SimpleJake.move, "SimpleJake", color=COLORS["blue"]))
        homies = []
        for h in s.snakes:
            homies.append(h.id)
        try:
            winner = s.start_game(speed=100, outputBoard=False, debug=False)
            print(s.turn)
            gameWinners.append(winner)
            for h in homies:
                print(h, sum([1 for s in gameWinners if s == h]))
        except Exception as e:
            print("FAILURE: ", e)


"""

if __name__ == "__main__":
    s = BattleSnake(food=1)
    s.add_snake(Snake(TestSnakes.battleJake2019.main.move, "Jake2019", color=COLORS["blue"]))
    s.add_snake(Snake(TestSnakes.battleJake2019.main.move, "Jake2019-2", color=COLORS["blue"]))
    winner = s.start_game(speed=95, outputBoard=True, debug=True)
    print("Winner: ", winner)
