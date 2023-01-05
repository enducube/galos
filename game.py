import tcod
import opensimplex
import pickle
import os
import math
import threading
from numpy import sign, polynomial
from objects import Tile, Chunk
from structures import Vector2
import configparser
config = configparser.ConfigParser()
config.read("config.ini")

WIDTH, HEIGHT = 63, 63  # Console width and height in tiles.

CHUNK_SIZE = int(config["WORLD_SETTINGS"]["chunk_size"])
print(type(CHUNK_SIZE))
print(int(CHUNK_SIZE))
WORLD_NAME = config["WORLD_SETTINGS"]["world_name"]
SEED = int(config["WORLD_SETTINGS"]["seed"])

walls = {} # TEMPORARYGARBAGESHUTUP

# the world currently being processed

tiles = {} # the world's tiles
chunks = {} # store what chunks are currently in play
entities = {}

generation_thread = None # will be set later, just here to be referenced by load_chunk

# Key commands for possible actions
KEY_COMMANDS = {
    tcod.event.KeySym.UP: "move N",
    tcod.event.KeySym.DOWN: "move S",
    tcod.event.KeySym.LEFT: "move W",
    tcod.event.KeySym.RIGHT: "move E",
}


# they got shoes for hands bruhhh

class Player:
    def __init__(self):
        self.position = Vector2(5,5)
        self.velocity = Vector2(0,0)
        self.health = 10
        self.inventory = []
    def update(self):
        # check for x movement to see if there is wall
        if Vector2(self.position.x+self.velocity.x, self.position.y) not in walls:
            self.position.x += self.velocity.x
        # check for y movement to see if there is wall
        if Vector2(self.position.x, self.position.y+self.velocity.y) not in walls:
            self.position.y += self.velocity.y
        self.velocity = Vector2(0,0)

        current_chunk = Vector2(math.floor(self.position.x/CHUNK_SIZE), 
                        math.floor(self.position.y/CHUNK_SIZE)) # check the current chunk player is in
        # go through surrounding things to see if there are any that need to load
        for i in range(-1,2):
            for j in range(-1,2):
                if Vector2(current_chunk.x+i,current_chunk.y+j) not in chunks:
                    load_chunk(current_chunk.x+i,current_chunk.y+j)
        # unload any chunks that aren't needed anymore
            
# circle get all tiles whatever
def circle_tiles(centre: Vector2, view_radius:int):
    tiles_in_circle = []
    for i in range(0,360,1):
        # i will be the angle
        for j in range(0, view_radius):
            new_tile = Vector2(round(centre.x + math.cos(i)*j),round(centre.y + math.sin(i)*j))
            if new_tile not in tiles_in_circle:
                tiles_in_circle.append(new_tile)
    return tiles_in_circle

## Generation of the world

def generate_world(world_size):
    try:
        world_size = int(world_size)
    except:
        print("World size should be an integer.")
        return None
    # make world folder
    if os.path.exists(f"saves/{WORLD_NAME}"):
        print(f"A folder already exists with the name {WORLD_NAME}!")
        print(f"Attempting to load the world instead...")
        return None
    else:
        print(f"Generating {WORLD_NAME}...")
        os.mkdir(f"saves/{WORLD_NAME}")
        # make chunks folder
        if not os.path.exists(f"saves/{WORLD_NAME}/chunks"):
            os.mkdir(f"saves/{WORLD_NAME}/chunks")
        
        for i in range(-round(world_size/2),round(world_size/2)):
            for j in range(-round(world_size/2),round(world_size/2)):
                c = Chunk(i,j)
                c.generate_chunk(SEED)
                c.save_chunk()
        print(f"Generation finished. Have fun!")



def load_chunk(x,y):
    try:
        with open(f"saves/{WORLD_NAME}/chunks/{x},{y}.gchunk","rb") as f:
            chunk = pickle.load(f)
            for tile in chunk.data["tiles"]:
                tiles[tile] = chunk.data["tiles"][tile]
            f.close()
    except:
        if config["WORLD_SETTINGS"]["infinite_generation"] == "True":
            c = Chunk(x,y)
            # fix this later
            #generation_thread = threading.Thread(target=generate_chunk,args=(x,y,),daemon=True)
            #generation_thread.start()
        else:
            pass 

def unload_chunk(x,y):
    with open(f"/saves/{WORLD_NAME}/{x},{y}.gchunk","+b") as f:

        f.close()
    chunks.pop(Vector2(x,y)) # remove the chunk from 
    pass

       
def main():
    """Script entry point. Start the gaming."""

    player = Player() # create the player instance
    tileset = tcod.tileset.load_tilesheet(
        "data/tiles2.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )
    print("ham")
    generate_world(int(config["WORLD_SETTINGS"]["world_size"]))

    # Create a window based on this console and tileset.
    with tcod.context.new(
        width=768, height=768, tileset=tileset, title="Galos"
    ) as context:
        # create the goddamn console already!!
        console = context.new_console(WIDTH,HEIGHT,2,"F")
        while True:  # main loop, where cool stuff happens!!!!!!
            console.clear(bg=(45, 50, 70))
            try:
                for tilepos in circle_tiles(player.position, 10): # go through the positions
                    #print(tilepos in tiles.keys())
                    tile = tiles[tilepos]
                    console.print(x=tilepos.x-player.position.x + 32, 
                                  y=tilepos.y-player.position.y + 32,
                                  string=tile.char,
                                  bg=tile.tile_bg, fg=tile.tile_colour)
            except:
                pass
            # draw the player!!!!!! (awesome)
            console.print(x=32, y=32, string="@",fg=(255,255,255))
            #console.draw_rect(0,48,63,15,ord("█"),(255,255,255))
            context.present(console, integer_scaling=True,keep_aspect=True)
            flag = False # checking if a move has been made by the player
            # event checking
            for event in tcod.event.get():
                context.convert_event(event)
                #print(event)  # Print event names and attributes.
                match event:
                    case tcod.event.KeyDown(sym=sym) if sym in KEY_COMMANDS:
                        match KEY_COMMANDS[sym]:
                            # movement
                            case "move S":
                                player.velocity.y +=1
                            case "move N":
                                player.velocity.y -=1
                            case "move E":
                                player.velocity.x +=1
                            case "move W":
                                player.velocity.x -=1
                        
                        if player.velocity != Vector2(0,0): # check if player has moved
                            flag = True 
                    case tcod.event.MouseButtonDown(tile=tile):
                        if event.button == tcod.event.BUTTON_LEFT:
                            print(event.tile)
                            tiles[Vector2(event.tile.x,event.tile.y)] = "land"
                if isinstance(event, tcod.event.Quit): # quitting like loser!!!
                    raise SystemExit()
            if flag:
                player.update() # update the player
                for entity in entities: # update all the current entities
                    entity.update()


if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    main_thread.start()