import testSnakes.battleJake2019.main
import testSnakes.battleJake2018.main
import testSnakes.simpleJake.main
import testSnakes.hungryJake.main

COLORS = {
    "black": "\033[1;37;40m",
    "red": "\033[1;37;41m",
    "green": "\033[1;37;42m",
    "yellow": "\033[1;37;43m",
    "blue": "\033[1;37;44m",
    "purple": "\033[1;37;45m",
    "cyan": "\033[1;37;46m",
    "grey": "\033[1;37;47m",
    "default": "\033[0m"
    }

"""
{
 "move": {The function that responds to the /move request},
 "name": {The snakes name, must be unique},
 "color": {A color from the list of colors}
 }
"""

MAIN_SNAKES = [
    {
        "move": testSnakes.battleJake2019.main.move,
        "name": "battleJake2019",
        "color": COLORS["purple"]
    },
    {
        "move": testSnakes.battleJake2018.main.move,
        "name": "battleJake2018",
        "color": COLORS["cyan"]
    },
    {
        "move": testSnakes.simpleJake.main.move,
        "name": "simpleJake",
        "color": COLORS["black"]
    },
    {
        "move": testSnakes.hungryJake.main.move,
        "name": "hungryJake",
        "color": COLORS["yellow"]
    }
]
