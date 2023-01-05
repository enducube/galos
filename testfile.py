import os
import pickle
import opensimplex
from game import Vector2
import math
# circle view radius
centre = Vector2(5,5)
view_radius = 3 # number in tiles
tiles = [] # will be a list of Vector2 when I'm done
for i in range(centre.y-view_radius,centre.y+view_radius + 1):
    # i will be the y value
    x_values = [
        round(-math.sqrt( (view_radius**2) - (i-centre.y)**2 ) + centre.x),
        round(math.sqrt( (view_radius**2) - (i-centre.y)**2 ) + centre.x)
        ]
    # get all tiles inbetween
    for j in range(x_values[0],x_values[1]+1):
        tiles.append(Vector2(j,i))
print(tiles)