# BattleSnakeArena
A modified, terminal based, [Battle Snake](https://play.battlesnake.io/) arena to bypass servers and have complete control.

## Requirements
- Python3
- A few packages for Python3 that you probably already have

## Test Snakes
This repository comes with a few snakes for testing.

### battleJake2019
This was my snake entered into Battle Snake 2019.

### battleJake2018
This was my snake entered into Battle Snake 2018.

### simpleJake
A snake that only knows how to not hit walls and other snakes but has a good smell for food.

### hungryJake
A snake whos top priority is to "get that brunch".

## Adding Your Own Snake
Adding your own snake is simple! Your snake just needs to be written in python3.

1. Make a quick modification to your snake in the "move" function. (Don't worry, it can still function as a server)
```python3
def move(data=None):
    if not data:
        data = bottle.request.json
```

2. Add your snake to the snakes file (snakes.py)

Import your file and make a dictionary in the SNAKES list to tell the arena about your snake.

## Running A Game
There is a command line interface for running games through battleSnake.py. For help run:
```
python3 battlesnake.py -h
```

### Running A Single Game
"Run a game with the snakes battleJake2018 and battleJake2019"
```
python3 battlesnake.py -s battleJake2018 battleJake2019
```

### Running Many Games Without Board Output
"Run 10 games without board output at 100% speed with battleJake2018, battleJake2019, simpleJake, and hungryJake"
```
python3 battlesnake.py -g 10 -b -sp 100 -s battleJake2018 battleJake2019 simpleJake hungryJake
```

## Why?
- Speed: Run 100s or 1000s of games, in parallel, to gather training data, assess your changes and test your snake
- No Server: Take as long as you want to respond, save that $$$ on server costs
- Debugging: See your console debugging realtime printed between game states
