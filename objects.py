"""
This is where the classes of different objects will be defined
"""
import random
import json
from structures import Vector2
import opensimplex
import pickle
import configparser
import os
import codecs # used to open unicode stuff
config = configparser.ConfigParser()
config.read("config.ini")

CHUNK_SIZE = int(config["WORLD_SETTINGS"]["chunk_size"])
tile_types = json.load(codecs.open("data/tile_types.json",encoding="utf-8"))


class Tile: # A tile in the world
    def __init__(self,x,y,type):
        self.position = Vector2(x,y)
        self.tile_type = type
        self.char = tile_types[type]["char"]
        try:
            self.char = list(self.char)
            self.char = random.choice(self.char)
        except:
            pass
        self.tile_colour = tile_types[type]["fg"]
        self.tile_bg = tile_types[type]["bg"]
class Chunk:
    def __init__(self,chunk_x,chunk_y):
        self.data = {
            "tiles": {},
            "entities": {},
            "objects": {},
            "walls": {}
            }
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
    def generate_chunk(self,SEED):
        chunk_noise_map = {}
        # go through each tile in the chunk noise
        for xx in range(CHUNK_SIZE):
            for yy in range(CHUNK_SIZE):
                pos = Vector2(xx+self.chunk_x*CHUNK_SIZE,yy+self.chunk_y*CHUNK_SIZE)
                chunk_noise_map[pos] = {}
                opensimplex.seed(SEED) # set seed to the normal seed
                scale = 40 # enlarge the scale of the "blobs"
                chunk_noise_map[pos]["altitude"] = opensimplex.noise2(pos.x/scale,pos.y/scale) 
                opensimplex.seed(SEED + 4) # set seed to a slightly different one
                scale=10
                chunk_noise_map[pos]["flora"] = opensimplex.noise2(pos.x/scale,pos.y/scale)
                altitude = chunk_noise_map[pos]["altitude"]
                flora = chunk_noise_map[pos]["flora"]
                # decide on what tiles should be what depending on variables given
                if altitude >= 0.32:
                    self.data["tiles"][pos] = Tile(pos.x,pos.y,"grass")
                elif altitude<0.32 and altitude >= 0.2:
                    self.data["tiles"][pos] = Tile(pos.x,pos.y,"sand")
                elif altitude < 0.2:
                    self.data["tiles"][pos] = Tile(pos.x,pos.y,"water")
    def save_chunk(self):
        if not os.path.exists(f"saves/{config['WORLD_SETTINGS']['world_name']}"):
            os.mkdir(f"saves/{config['WORLD_SETTINGS']['world_name']}")
        if not os.path.exists(f"saves/{config['WORLD_SETTINGS']['world_name']}/chunks"):
            os.mkdir(f"saves/{config['WORLD_SETTINGS']['world_name']}/chunks")
        with open(f"saves/{config['WORLD_SETTINGS']['world_name']}/chunks/{self.chunk_x},{self.chunk_y}.gchunk","wb+") as f:
            pickle.dump(self,f, pickle.HIGHEST_PROTOCOL)
            f.close()
        


class Entity:
    def __init__(self,x,y,type):
        self.position = Vector2(x,y)
        self.entity_type = type
        self.health = 5
        self.damage = 1
        self.inventory = []
