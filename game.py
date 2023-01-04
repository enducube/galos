import tcod
import opensimplex
import pickle

WIDTH, HEIGHT = 64, 64  # Console width and height in tiles.

WORLD_WIDTH, WORLD_HEIGHT = 128, 128

SEED = 1234

walls = {} # TEMPORARYGARBAGESHUTUP

# the world currently being processed

tiles = {} # the world's tiles
entities = {}

KEY_COMMANDS = {
    tcod.event.KeySym.UP: "move N",
    tcod.event.KeySym.DOWN: "move S",
    tcod.event.KeySym.LEFT: "move W",
    tcod.event.KeySym.RIGHT: "move E",
}

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


class Player:
    def __init__(self):
        self.position = Vector2(5,5)
        self.velocity = Vector2(0,0)
    def update(self):
        # check for x movement to see if there is wall
        
        if Vector2(self.position.x+self.velocity.x, self.position.y) not in walls:
            self.position.x += self.velocity.x
        # check for y movement to see if there is wall
        if Vector2(self.position.x, self.position.y+self.velocity.y) not in walls:
            self.position.y += self.velocity.y
        self.velocity = Vector2(0,0)


def main():
    """Script entry point."""

    player = Player() # create the player instance

    # GENERATE A NEW WORLD (wip)

    tileset = tcod.tileset.load_tilesheet(
        "data/tiles.png", 16, 16, tcod.tileset.CHARMAP_CP437,
    )
 


    # Create a window based on this console and tileset.
    with tcod.context.new(
        width=512, height=512, tileset=tileset, title="Galos",
    ) as context:
        # create the goddamn console already!!
        console = context.new_console(WIDTH,HEIGHT,4,"F")
        while True:  # main loop, where cool stuff happens!!!!!!
            console.clear() 

            for tilepos in tiles.keys(): # go through the positions
                tile = tiles[tilepos]
                console.print(x=tilepos.x, y=tilepos.y, string="█", fg=(128,128,0))
            
            # draw the player!!!!!! (awesome)
            console.print(x=player.position.x, y=player.position.y, string="@")
            context.present(console)
            flag = False # checking if a move has been made by the player
            # event checking
            for event in tcod.event.wait():
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
                            walls[Vector2(event.tile.x,event.tile.y)] = True
                if isinstance(event, tcod.event.Quit): # quitting like loser!!!
                    raise SystemExit()
            if flag:
                player.update() # update the player
                for entity in entities: # update all the current entities
                    entity.update()


if __name__ == "__main__":
    main()