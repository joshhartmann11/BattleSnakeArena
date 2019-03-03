import os
import random
import time
import bottle
import traceback
import json

DEBUG = False

# The higher the quicker we start searching for food
HUNGRY = 60
# Starting search radius
FOOD_MIN = 1
# When we start searching our max radius
STARVING = 40
# Max searching radius
FOOD_MAX = 40

SIZE_THRESHOLD = 0

ate_food_last_turn = False;

@bottle.route('/')
def index():
	return "<h1>BattleJake</h1>"

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
        'color': '#EADA50',
        'taunt': 'Wake up Blake, you\'re a snake',
        'head_url': headUrl
    }

@bottle.post('/move')
def move(data=None):
    global ate_food_last_turn
    if not data:
        data = bottle.request.json
    debug_print('-'*50)
    debug_print('-'*50)
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

    debug_print("Move Number: ", data['turn'])
    debug_print("My Size:    ", you['size'])
    debug_print("My Health:  ", you['health'])

    try:
        move = None
        moves = ['left', 'right', 'up', 'down']


        # Moving restrictions
        if ate_food_last_turn:
            moves = dont_hit_wall(moves, you['head'], walls)
            debug_print("Don't hit wall:", moves)
            moves = dont_hit_snakes(moves, you['head'], snakesTogether, [])
            debug_print("Don't hit snak:", moves)
            moves = dont_get_eaten(moves, you, snakes)
            debug_print("Don't get eat :", moves)
        else:
            moves = dont_hit_wall(moves, you['head'], walls)
            debug_print("Don't hit wall:", moves)
            moves = dont_hit_snakes(moves, you['head'], snakesTogether, [you['body'][-1]])
            debug_print("Don't hit snak:", moves)
            moves = dont_get_eaten(moves, you, snakes)
            debug_print("Don't get eat :", moves)


        # Don't choose nothing that'll kill you next time
        if len(moves) > 1:
            tmpMoves = list(moves)
            for m in moves:
                nextHead = get_space(you['head'], m)
                nextMoves = ['left', 'right', 'up', 'down']
                nextMoves = dont_hit_wall(nextMoves, nextHead, walls)
                nextMoves = dont_hit_snakes(nextMoves, nextHead, snakesTogether + [you['head']], [])
                if nextMoves == []:
                    tmpMoves.remove(m)
            if tmpMoves != []:
                moves = tmpMoves
        debug_print("Restrictions2: ", moves)

        # Take food as first preference is I'm smol
        if you['size'] < 6:
            you["health"] = you["health"]/2

        # Take food as preference as I get more hungry
        if have_choice(move, moves) and (you["health"] < HUNGRY):
            maxFood = round( (1 - ((you["health"]-STARVING) / (HUNGRY-STARVING))) * (FOOD_MAX-FOOD_MIN) )

            for i in reversed(range(1, maxFood)):
                if have_choice(move, moves):
                    moves = get_food(moves, you['head'], food, i)
                    debug_print("Gimme Brunch {}:".format(i), moves)

        if have_choice(moves, moves):
            move = strangle_others(moves, you['head'], you['size'], you['body'], snakes, walls)
            debug_print("Stangle Others:", move)

        # Flee from a wall as preference
        if have_choice(move, moves):
            moves = flee_wall(moves, walls, you['head'])
            debug_print("Flee Wall:     ", moves)

        # Flee others (including yourself) as preference
        if have_choice(move, moves):
            moves = flee_others(moves, [you['body'][0], you['body'][-1]], snakesTogether,you['head'], 1)
            debug_print("Flee Others:   ", moves)

        # Take killing others as preference
        if have_choice(move, moves):
            moves = eat_others(moves, you['head'], you['size'], snakes)
            debug_print("Kill Others:   ", moves)

        # Move away from the heads of others
        if have_choice(move, moves):
            moves = flee_heads(moves, snakes, you['head'], dist=3)
            debug_print("Flee Heads:    ", move)

        # Go straight as preference
        if have_choice(move, moves):
            move = go_straight(moves, you['head'], you['body'])
            debug_print("Go Straight:   ", move)

        # Flee heads
        if have_choice(move, moves):
            moves = flee_heads(moves, snakes, you['head'])
            debug_print("Flee Choice:  ", moves)

        if have_choice(move, moves):
            move = random.choice(moves)
            debug_print("Random Choice:", move)

        # No suggested moves
        if move == None:

            # There is only one choice
            if len(moves) == 1:
                move = moves[0]
                debug_print("Only Choice:   ", move)

            # There is no choice
            else:
                moves = eat_tail(you['head'], snakes)
                debug_print("Eat Tail:      ", moves)
                moves = dont_get_eaten(moves, you, snakes, sameSize=False)
                if moves != []:
                    move = move[0]

                if move == None:
                    moves = ['left', 'right', 'up', 'down']
                    moves = dont_hit_wall(moves, you['head'], walls)
                    debug_print("Don't hit wall:", moves)
                    moves = dont_hit_snakes(moves, you['head'], snakesTogether, [])
                    moves = dont_get_eaten(moves, you, snakes, sameSize=False)
                    debug_print("Don't hit snac:", moves)
                    if moves == []:
                        move = 'up'
                        debug_print("Death:        ", move)
                    else:
                        move = random.choice(moves)


    except Exception as e:
        debug_print("ERROR: ", str(e))
        traceback.print_tb(e.__traceback__)
        if moves == []:
            move = "up"
            debug_print("ERROR: Going up")
        else:
            move = random.choice(moves)
            debug_print("ERROR: Random choice")

    debug_print("MOVE: ", move)

    if ate_food(you['head'], food, move):
        ate_food_last_turn = True
    else:
        ate_food_last_turn = False

    return {
        'move': move,
        'taunt': 'Battle Jake!'
    }


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def have_choice(move, moves):
    if move != None:
        return False
    if len(moves) <= 1:
        return False
    return True


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


def eat_tail(head, snakes):
    moves = []
    for s in snakes:
        xdist = head[0] - s['tail'][0]
        ydist = head[1] - s['tail'][1]
        if abs(xdist) == 1 and ydist == 0:
            if xdist > 0:
                moves.append('left')
            else:
                moves.append('right')

        if abs(ydist) == 1 and xdist == 0:
            if ydist > 0:
                moves.append('up')
            else:
                moves.append('down')
    return moves


def go_straight(moves, head, body):
    if len(body) > 1:
        pm = get_previous_move(head, body[1])
        if pm in moves:
            return pm


def flee_heads(moves, snakes, head, dist=999):
    headManhattan = [ abs(s['head'][0]-head[0]) + abs(s['head'][1]-head[1]) for s in snakes]
    closestSnakes = sorted( [(x,i) for (i,x) in enumerate(headManhattan)] )

    tmpMoves = list(moves)

    for s in closestSnakes:
        snake = snakes[s[1]]
        xdist = head[0] - snake['body'][0][0]
        ydist = head[1] - snake['body'][0][1]

        if len(moves) == 1:
            return moves

        if abs(xdist) < abs(ydist) and xdist < dist:
            if ('left' in moves) and (xdist > 0):
                moves.remove('left')

            if ('right' in moves) and (xdist < 0):
                moves.remove('right')
        elif ydist < dist:
            if ('down' in moves) and (ydist < 0):
                moves.remove('down')

            if ('up' in moves) and (ydist > 0):
                moves.remove('up')
        else:
            return moves

    if moves == []:
        moves = tmpMoves
    return moves


def flee_others(moves, delMoves, snakesTogether, head, dist):

    prevMoves = list(moves)
    validMoves = list(moves)
    for s in snakesTogether:
        if s not in delMoves:
            for m in moves:
                fh = get_space(head, m)
                xdist = s[0]-fh[0]
                ydist = s[1]-fh[1]

                # If the future head is beside a snake
                if (abs(xdist) == dist and ydist == 0) or (abs(ydist) == dist and xdist == 0):
                    validMoves.remove(m)
            moves = validMoves

    if moves == []:
        return prevMoves
    return moves


def ate_food(head, food, move):
    if get_space(head, move) in food:
        return True
    else:
        return False


def flee_wall(moves, walls, head):

    # Flee the wall if I'm against it
    if head[0] >= walls[0]-1:
        if 'left' in moves:
            return ['left']

    elif head[0] <= 0:
        if 'right' in moves:
            return ['right']

    if head[1] <= 0:
        if 'down' in moves:
            return ['down']

    elif head[1] >= walls[1]-1:
        if 'up' in moves:
            return ['up']

    validMoves = list(moves)

    # Keep 1 space buffer between you and the wall
    if head[0] >= walls[0]-2:
        if 'right' in moves:
            validMoves.remove('right')

    elif head[0] <= 1:
        if 'left' in moves:
            validMoves.remove('left')

    if len(moves) > 1:

        if head[1] <= 1:
            if 'up' in moves:
                validMoves.remove('up')

        elif head[1] >= walls[1]-2:
            if 'down' in moves:
                validMoves.remove('down')


    if validMoves == []:
        return moves
    return validMoves

def strangle_others(moves, head, mySize, body, snakes, walls):

    if head[0] == 0 or head[0] == walls[0]-2 or \
       head[1] == 0 or head[1] == walls[1]-2:

        mydir = (head[0] - body[1][0], head[1] - body[1][1])
        for s in snakes:
            snakedir = (s['head'][0] - s['body'][1][0], s['head'][1] - s['body'][1][1])
            # snake heading in same direction
            if snakedir == mydir:
                # snake on the wall
                if s['head'][0] == 0 or \
                   s['head'][0] == walls[0]-1 or \
                   s['head'][1] == 0 or \
                   s['head'][1] == walls[0]-1:
                    if mydir[0] > 0 and 'right' in moves and \
                       head[0] - s['head'][0] < mySize and head[0] - s['head'][0] > 0:
                        return 'right'
                    elif mydir[0] < 0 and 'left' in moves and \
                         head[0] - s['head'][0] > -mySize and head[0] - s['head'][0] < 0:
                        return 'left'
                    elif mydir[1] > 1 and 'down' in moves and \
                         head[1] - s['head'][1] > mySize and head[1] - s['head'][1] > 0:
                        return 'down'
                    elif mydir[1] < 1 and 'up' in moves and \
                         head[1] - s['head'][1] > -mySize and head[1] - s['head'][1] < 0:
                        return 'up'



# If you're bigger than other snake, kill them
def eat_others(moves, head, mySize, snakes):
    validMoves = []
    for s in snakes:

        if s['size'] < mySize-1:
            xdist = s['head'][0]-head[0]
            ydist = s['head'][1]-head[1]

            if (abs(xdist) == 1) and (abs(ydist) == 1):
                if xdist > 0 and 'right' in moves:
                    validMoves.append('right')

                elif xdist < 0 and 'left' in moves:
                    validMoves.append('left')

                if ydist > 0 and 'down' in moves:
                    validMoves.append('down')

                elif ydist < 0 and 'up' in moves:
                    validMoves.append('up')

            elif (abs(xdist) == 2 and ydist == 0) or (abs(ydist) == 2 and xdist == 0):
                if xdist == 2 and 'right' in moves:
                    validMoves.append('right')

                elif xdist == -2 and 'left' in moves:
                    validMoves.append('left')

                elif ydist == 2 and 'down' in moves:
                    validMoves.append('down')

                elif 'up' in moves:
                    validMoves.append('up')

    if validMoves == []:
        return moves
    return list(set(validMoves))


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

    if validMoves == []:
        return moves
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
