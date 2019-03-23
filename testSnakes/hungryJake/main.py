"""
hungryJake

hungryJake is simpleJake but always looking for food.
"""
import os
import random
import time
import bottle
import traceback
import json

DEBUG = False

FOOD_THRESHOLD = 99999
FOOD_SEARCH_DIST = 99999

@bottle.route('/')
def index():
	return "<h1>HungryJake</h1>"

@bottle.route('/static/<path:path>')
def static(path):
	return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    return {}

@bottle.post('/end')
def end():
    return {}

@bottle.post('/start')
def start():
    headUrl = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    print("\n\n\n\n\n\n")

    return {
        'color': '#00AA00',
        'taunt': 'Wake up Jaque, you\'re a snaque',
        'head_url': headUrl
    }

@bottle.post('/move')
def move(data=None):
    global ate_food_last_turn
    if not data:
        data = bottle.request.json
    # Get all the data
    you = data['you']
    you['body'] = [ (b['x'], b['y']) for b in you['body'] ]
    you['head'] = you['body'][0]
    you['size'] = len(you['body'])
    health = you["health"]
    walls = (data['board']['width'], data['board']['height'])
    snakesTogether = []
    [ [ snakesTogether.append(( b['x'], b['y'] )) for b in s["body"] ] for s in data['board']['snakes'] ]

    snakes = data["board"]['snakes']
    for s in snakes:
        s['size'] = len(s['body'])
        s['body'] = [ (b['x'], b['y']) for b in s['body'] ]
        s['head'] = s['body'][0]
        s['tail'] = s['body'][-1]

    food = [(f['x'], f['y']) for f in data['board']['food']]
    numFood = len(food)

    try:
        moves = ['left', 'right', 'up', 'down']

        # Don't hit the walls
        movesTmp = dont_hit_wall(moves, you['head'], walls)
        if movesTmp != []:
            moves = movesTmp

        # Don't hit other snakes
        movesTmp = dont_hit_snakes(moves, you['head'], snakesTogether, [])
        if movesTmp != []:
            moves = movesTmp

        # Don't get eaten
        movesTmp = dont_get_eaten(moves, you, snakes)
        if movesTmp != []:
            moves = movesTmp

        # Search for food if your health is low
        if you['size'] < FOOD_THRESHOLD:
            for i in range(1, min([FOOD_SEARCH_DIST, max(walls)])):
                movesTmp = get_food(moves, you['head'], food, i)
                if movesTmp != []:
                    moves = movesTmp
                    break

        # Choose the previous move or a random one
        if you['size'] != 1:
            previous_move = get_previous_move(you['head'], you['body'][1])
        else:
            previous_move = 'noMoveYall'
        if previous_move in moves:
            move = previous_move
        elif moves != []:
            move = random.choice(moves)
        else:
            move = 'up'

    except Exception as e:
        traceback.print_tb(e.__traceback__)
        if moves == []:
            move = "up"
        else:
            move = random.choice(moves)

    return {
        'move': move,
        'taunt': 'Battle Jake!'
    }


def get_space(space, move):

    if move == 'left':
        return (space[0] - 1, space[1])

    elif move == 'right':
        return (space[0] + 1, space[1])

    elif move == 'up':
        return (space[0], space[1] - 1)

    else:
        return (space[0], space[1] + 1)


def get_previous_move(head, second):

    if head[0] == second[0]:
        if head[1] > second[1]:
            return 'down'

        else:
            return 'up'
    else:
        if head[0] > second[0]:
            return 'right'

        else:
            return 'left'


def get_food(moves, head, food, dist):
    validMoves = []
    for f in food:
        xdist = f[0]-head[0]
        ydist = f[1]-head[1]

        if (abs(xdist) + abs(ydist)) <= dist:

            if xdist > 0 and 'right' in moves:
                validMoves.append('right')

            elif xdist < 0 and 'left' in moves:
                validMoves.append('left')

            elif ydist > 0 and 'down' in moves:
                validMoves.append('down')

            elif ydist < 0 and 'up' in moves:
                validMoves.append('up')

    return list(set(validMoves))


def dont_hit_wall(moves, head, walls):
    if head[0] == walls[0]-1 and 'right' in moves:
        moves.remove('right')

    elif head[0] == 0 and 'left' in moves:
        moves.remove('left')

    if head[1] == 0 and 'up' in moves:
        moves.remove('up')

    elif head[1] == walls[1]-1 and 'down' in moves:
        moves.remove('down')

    return moves


def dont_hit_snakes(moves, head, snakesTogether, ignore):
    if get_space(head, 'left') in snakesTogether and 'left' in moves:
        moves.remove('left')

    if get_space(head, 'right') in snakesTogether and 'right' in moves:
        moves.remove('right')

    if get_space(head, 'up') in snakesTogether and 'up' in moves:
        moves.remove('up')

    if get_space(head, 'down') in snakesTogether and 'down' in moves:
        moves.remove('down')

    return moves


def dont_get_eaten(moves, you, snakes, sameSize=True):

    prevMoves = list(moves)

    for s in snakes:
        if (s['size'] >= you['size']) and sameSize or \
           (s['size'] > you['size']) and not sameSize:
            xdist = s['head'][0]-you['head'][0]
            ydist = s['head'][1]-you['head'][1]

            if abs(xdist) == 1 and abs(ydist) == 1:
                if xdist > 0 and 'right' in moves:
                    moves.remove('right')

                elif xdist < 0 and 'left' in moves:
                    moves.remove('left')

                if ydist > 0 and 'down' in moves:
                    moves.remove('down')

                elif ydist < 0 and 'up' in moves:
                    moves.remove('up')

            elif (abs(xdist) == 2 and ydist == 0) or (abs(ydist) == 2 and xdist == 0):
                if xdist == 2 and 'right' in moves:
                    moves.remove('right')

                elif xdist == -2 and 'left' in moves:
                    moves.remove('left')

                elif ydist == 2 and 'down' in moves:
                    moves.remove('down')

                elif ydist == -2 and 'up' in moves:
                    moves.remove('up')

    return moves


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug = True)
