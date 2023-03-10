"""
Data structure classes, containing methods of storing data
"""
import math
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __hash__(self):
        return hash((self.x,self.y))
    def __eq__(self, __o: object):
        return (self.x,self.y) == (__o.x,__o.y)
    def __repr__(self):
        return f"Vector2({self.x},{self.y})"
    def distance_to(self,point):
        return math.sqrt((self.x-point.x)**2 + (self.y-point.y)**2)