import tcod
import opensimplex
import pickle
import os
import math
import threading
from numpy import sign, polynomial
from objects import Tile
from structures import Vector2

WIDTH, HEIGHT = 63, 63  # Console width and height in tiles.

CHUNK_SIZE = 64
RENDER_DISTANCE = 2
WORLD_NAME = "world1"
SEED = 123

walls = {} # TEMPORARYGARBAGESHUTUP

# the world currently being processed

tiles = {} # the world's tiles
chunks = [] # store what chunks are currently in play
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
        render_radius = RENDER_DISTANCE * CHUNK_SIZE
        # go through surrounding things to see if there are any needed to be generated
        flag = False
        for i in range(-1,2):
            for j in range(-1,2):
                if Vector2(current_chunk.x+i,current_chunk.y+j) not in chunks:
                    load_chunk(current_chunk.x+i,current_chunk.y+j)
            
# circle get all tiles whatever
def circle_tiles(centre: Vector2, view_radius:int):
    tiles_in_circle = []
    for i in range(centre.y-view_radius,centre.y+view_radius + 1):
        # i will be the y value
        x_values = [
            math.ceil(-math.sqrt( (view_radius**2) - (i-centre.y)**2 ) + centre.x),
            math.floor(math.sqrt( (view_radius**2) - (i-centre.y)**2 ) + centre.x)
            ]
        # get all tiles inbetween
        for j in range(x_values[0],x_values[1]+1):
            tiles_in_circle.append(Vector2(j,i))
    return tiles_in_circle

## CHUNK STUFF!!!!!!!!!!!!!!!!!!!!!!!!!!1

# generate a chunk of the world and store it in file

def generate_chunk(x: int, y: int):
    print(f"Generating chunk {x},{y}...")
    chunk_tiles = {}
    chunk_noise_map = {}
    #print(x*CHUNK_SIZE,y*CHUNK_SIZE)
    # go through each tile in the chunk noise
    for xx in range(CHUNK_SIZE):
        for yy in range(CHUNK_SIZE):
            pos = Vector2(xx+x*CHUNK_SIZE,yy+y*CHUNK_SIZE)
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
            if altitude >= 0.25:
                chunk_tiles[pos] = Tile(pos.x,pos.y,"grass")
            elif altitude<0.25 and altitude >= 0.2:
                chunk_tiles[pos] = Tile(pos.x,pos.y,"grass")
            elif altitude < 0.2:
                chunk_tiles[pos] = Tile(pos.x,pos.y,"water")
    with open(f"saves/{WORLD_NAME}/{x},{y}.gchunk","wb+") as f:
        pickle.dump(chunk_tiles,f, pickle.HIGHEST_PROTOCOL)
        print("saved")
        f.close()
    load_chunk(x,y)



def load_chunk(x,y):
    try:
        chunk_tiles = {}
        chunks.append(Vector2(x,y))
        with open(f"saves/{WORLD_NAME}/{x},{y}.gchunk","rb") as f:
            chunk_tiles = pickle.load(f)
            for tile in chunk_tiles.keys():
                tiles[tile] = chunk_tiles[tile]
            f.close()
    except:
        
        generation_thread = threading.Thread(target=generate_chunk,args=(x,y,),daemon=True)
        generation_thread.start()
        #generation_thread.join()
        

def unload_chunk(x,y):
    with open(f"/saves/{WORLD_NAME}/{x},{y}.gchunk","+b") as f:

        f.close()
    chunks.pop(chunks.index(Vector2(x,y)))
    pass

       
def main():
    """Script entry point. Start the gaming."""

    player = Player() # create the player instance
    tileset = tcod.tileset.load_tilesheet(
        "data/tiles2.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )

    # Create a window based on this console and tileset.
    with tcod.context.new(
        width=768, height=768, tileset=tileset, title="Galos",
    ) as context:
        # create the goddamn console already!!
        console = context.new_console(WIDTH,HEIGHT,4,"F")
        while True:  # main loop, where cool stuff happens!!!!!!
            console.clear(bg=(45, 50, 70))
            try:
                for tilepos in circle_tiles(player.position, 16): # go through the positions
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
            context.present(console)
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