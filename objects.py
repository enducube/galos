"""
This is where the classes of different objects will be defined
"""
import random
from structures import Vector2

class Tile: # A tile in the world
    def __init__(self,x,y,type):
        self.position = Vector2(x,y)
        self.tile_type = type
        self.char = ""
        self.tile_colour = (255,255,255)
        self.tile_bg = (0,0,0)
        match self.tile_type:
            case "grass":
                self.char = random.choice([",","'",'"'])
                self.tile_bg = (34, 100, 34)
                self.tile_colour = (0, 200, 124)
            case "water":
                self.char = "≈"
                self.tile_bg = (0, 0, 64)
                self.tile_colour = (65,65,185)
            case "sand":
                self.char = "▒"
                self.tile_bg = (245, 222, 179)
                self.tile_colour = (222,184,135)
