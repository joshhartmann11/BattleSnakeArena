import os
import random
import time

class SimpleJake():

    def __init__(self):
        pass


    def move(self, data):
        # Get all the data
        you = data['you']
        health = you["health"]
        mySize = you['length']
        body = you['body']['data']
        head = (body[0]['x'], body[0]['y'])
        walls = (data['width'], data['height'])
        snakes = data['snakes']['data']
        size = []
        for s in snakes:
            size.append(s['length'])
        snakes = [s['body']['data'] for s in snakes]
        snakes2 = []
        heads = []
        for s1 in snakes:
            heads.append((s1[0]['x'], s1[0]['y']))
            for s2 in s1:
                snakes2.append((s2['x'], s2['y']))
        snakes = snakes2
        food = data['food']['data']
        food = [(f['x'], f['y']) for f in food]
        numFood = len(food)
    
        # Moving restrictions
        try:
            moves = self.get_restrictions(head, mySize, walls, snakes, heads, size)
            move = random.choice(moves)
        except:
            return {'move': 'up'}
    
        return {
            'move': move,
            'taunt': 'Battle Jake!'
        }
                
                

    def get_restrictions(self, head, mySize, walls, snakes, heads, size, op=True):

        directions = {'up':1, 'down':1, 'left':1, 'right':1}
    
        # Don't hit a wall
        if(head[0] == walls[0]-1):
            directions['right'] = 0
        
        elif(head[0] == 0):
            directions['left'] = 0
        
        if(head[1] == 0):
            directions['up'] = 0
        
        elif(head[1] == walls[1]-1):
            directions['down'] = 0
    
        # Don't hit other snakes
        for s in snakes:
            xdist = abs(s[0]-head[0])
            ydist = abs(s[1]-head[1])
        
            if(xdist + ydist == 1):
        
                if(xdist == 1):
            
                    if(s[0] > head[0]):
                        directions['right'] = 0
                    
                    else:
                        directions['left'] = 0
                    
                else:
        
                    if(s[1] > head[1]):
                        directions['down'] = 0
                    
                    else:
                        directions['up'] = 0
    
        directions2 = {key: value for key, value in directions.items()}
    
        # Be scared of the heads of others if they're scary
        for i, h in enumerate(heads):
    
            if(not (size[i] < mySize)):
                xdist = h[0]-head[0]
                ydist = h[1]-head[1]
            
                if(abs(xdist) == 1 and abs(ydist) == 1):

                    if(xdist > 0):
                        directions['right'] = 0

                    elif(xdist < 0):
                        directions['left'] = 0

                    if(ydist > 0):
                        directions['down'] = 0

                    elif(ydist < 0):
                        directions['up'] = 0

                elif((abs(xdist) == 2 and ydist == 0) ^ (abs(ydist) == 2 and xdist == 0)):

                    if(xdist == 2):
                        directions['right'] = 0

                    elif(xdist == -2):
                        directions['left'] = 0

                    elif(ydist == 2):
                        directions['down'] = 0

                    else:
                        directions['up'] = 0

        # If there's no other choice but to possibly collide with a head
        if(1 not in directions.values() and op):
            directions = directions2
        
        if not op:
            directions = directions2
    
        moves = [k for k in directions.keys() if directions[k] is 1]
    
        return moves
