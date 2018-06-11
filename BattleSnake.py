import random
import time
from TestSnakes.BattleJake2018.Jake2018 import Jake2018
from TestSnakes.SimpleJake.SimpleJake import SimpleJake
from TestSnakes.MitchellNursey.MitchellNursey import MitchellNursey
from TestSnakes.SajanDinsa.SajanDinsa import SajanDinsa

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
DEFAULT_COLOR = "\033[0;30;48m"

class BattleSnake():

    def __init__(self, dims=[20,20], food=15):
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
            taken.extend(s["snake"].body)
            
        spot = (random.choice(range(self.dims["width"])), 
                random.choice(range(self.dims["height"])))
        while spot in taken:
            spot = (random.choice(range(self.dims["width"])), 
                    random.choice(range(self.dims["height"])))
        return spot
    
    
    # Add the snakes
    def add_snake(self, snake, ai):
        snake.body.append(self.empty_spot())
        self.snakes.append({"snake": snake, "ai": ai})
        
    
    # Move snakes
    def move_snakes(self, debug=False):
        json = self.generic_board_json()
        for s in self.snakes:
            input = self.specific_board_json(s["snake"], json)
            if(not debug):
                try:
                    output = s["ai"].move(input)
                except Exception as e:
                    print("Exception in ", s["snake"].id, ":", e)
                    output = {"move": "up"}
                s["snake"].move(output["move"])
            else:
                output = s["ai"].move(input)
                s["snake"].move(output["move"])
        
        self.check_food()
        self.detect_death()
        
        self.turn += 1
        
    
    # Delete snakes
    def delete_snakes(self, snakes, reason=None):
        
        if not snakes == []:
            if not reason == None:
                print(reason)
            for s in snakes:
                self.snakes.remove(s)
    
    
    # Checks to see if there's a winner
    def check_winner(self, solo):
        if(len(self.snakes) == 1 and not solo):
            print("Game Over\nWinner: " + self.snakes[0]["snake"].id)
            return True
        if(len(self.snakes) == 0):
            if solo:
                print("Game Over")
            else:
                print("Game Over\nTie")
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
                
            if self.check_winner(solo):
                break
                
            while(time.time()-t1 <= (100-speed)/800):
                pass
        
        print(DEFAULT_COLOR) # Restore default coloring to terminal
        if not len(self.snakes) == 0:
            return(self.snakes[0]["snake"].id)
        
    
    # Resolve Head-on-head Collisions
    def resolve_head_collisions(self):
        allHeads = []
        for s in self.snakes:
            allHeads.append(s["snake"].body[0])
        
        delSnakes = []
        for s1 in self.snakes:
            s1head = s1["snake"].body[0]
            heads = list(allHeads)
            heads.remove(s1head)
            if s1head in heads:
                s1len = len(s1["snake"].body)
                
                s2 = self.snakes[heads.index(s1head)]
                ind = heads.index(s1head)
                s2len = len(self.snakes[ind]["snake"].body)
                
                if s1len >= s2len and s1 not in delSnakes:
                    delSnakes.append(s1)

                if s2len >= s1len and s2 not in delSnakes:
                    delSnakes.append(s2)
        
        self.delete_snakes(delSnakes, reason="HEAD-ON-HEAD")
        
    
    # Detect Snake Collision
    def detect_snake_collision(self):
        allSnakes = []
        for s in self.snakes:
            allSnakes.extend(s["snake"].body[1:])
        
        delSnakes = []
        for s in self.snakes:
            head = s["snake"].body[0]
            if head in allSnakes:
                delSnakes.append(s)
                
        self.delete_snakes(delSnakes, reason="SNAKE COLLISION")

    
    # Detect Wall Collision
    def detect_wall_collision(self):
        delSnakes = []
        for s in self.snakes:
            head = s["snake"].body[0]
            if( head[0] < 0 or head[1] < 0 or
                head[0] >= self.dims["width"] or
                head[1] >= self.dims["height"]):
                delSnakes.append(s)
                
        self.delete_snakes(delSnakes, reason="WALL COLLISION")
    
    
    # Detect Starvation
    def detect_starvation(self):
        delSnakes = []
        for s in self.snakes:
            if(s["snake"].health <= 0):
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
                if f in s["snake"].body:
                    s["snake"].ateFood = True
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
        jsonobj["width"] = self.dims["width"]
        jsonobj["height"] = self.dims["height"]
        jsonobj["turn"] = self.turn
        jsonobj["snakes"] = {"data": [s["snake"].jsonize() for s in self.snakes]}
        jsonobj["food"] = {"data": self.jsonize_food()}
        return jsonobj
    
    
    # Print the board
    def print_board(self):
        snakes = []
        for s in self.snakes:
            snakes.append(s["snake"].body)

        food = self.food
    
        print(BORDER_COLOR + " " * 2 * self.dims["width"] + "    " + DEFAULT_COLOR, end="")
        for i in range(self.dims["width"]):
	        print("\n" + BORDER_COLOR + "  " + DEFAULT_COLOR, end="")
	        for j in range(self.dims["height"]):
	            
	            if ((i, j)) in food:
	                print(FOOD_COLOR + "  " + DEFAULT_COLOR, end="")
	            else:
	                done = False
	                for ind, s in enumerate(snakes):
	                    if ((i, j)) in s:
	                        if s[0] == ((i, j)):
	                            print(self.snakes[ind]["snake"].color + "OO" + DEFAULT_COLOR, end="")
	                        else:
	                            print(self.snakes[ind]["snake"].color + "  " + DEFAULT_COLOR, end="")
	                        done = True
	                        
	                if not done:
	                    print(DEFAULT_COLOR + "  " + DEFAULT_COLOR, end="")
	        
	        print(BORDER_COLOR + "  " + DEFAULT_COLOR, end="")


	    
class Snake():

    def __init__(self, id, color):
        self.body = []
        self.health = 100
        self.ateFood = False
        self.color = color
        self.id = id
        
    
    # Puts the snakes information into the required json format
    def jsonize(self):
        jsonobj = {}
        jsonobj["health"] = self.health
        jsonobj["body"] = {"data": [{"x": b[0], "y": b[1]} for b in self.body]}
        jsonobj["length"] = len(self.body)
        jsonobj["id"] = self.id
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
        s = BattleSnake()
        s.add_snake(Snake("Jake2018", color=COLORS["blue"]), Jake2018())
        s.add_snake(Snake("SimpleJake", color=COLORS["cyan"]), SimpleJake())
        s.add_snake(Snake("MitchellNursey", color=COLORS["yellow"]), MitchellNursey(i))
        s.add_snake(Snake("SajanDinsa", color=COLORS["red"]), SajanDinsa())
        try:
            gameWinners.append(s.start_game(speed=100, outputBoard=False, debug=False))
        except Exception as e:
            print("FAILURE: ", e)
 
    homies = ["Jake2018", "SimpleJake", "MitchellNursey", "SajanDinsa"]
    for h in homies:
        print(h, sum([1 for s in gameWinners if s == h]))
"""

if __name__ == "__main__":
    s = BattleSnake(food=20)
    s.add_snake(Snake("SimpleJake", color=COLORS["cyan"]), SimpleJake())
    s.add_snake(Snake("MitchellNursey", color=COLORS["yellow"]), MitchellNursey())
    s.add_snake(Snake("SajanDinsa", color=COLORS["red"]), SajanDinsa())
    s.add_snake(Snake("Jake2018", color=COLORS["blue"]), Jake2018())
    s.start_game(speed=25, outputBoard=True, debug=False)

	    
