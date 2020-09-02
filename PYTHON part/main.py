# PLEASE SEE README.txt FIRST
# Author: Abdulmajeed alahmadi



import pygame as pg
import sys
import pytmx
import time
from os import path
import firebase as firebase
from firebase.firebase import FirebaseApplication

#Some settigns
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH = 768
HEIGHT = 768
TILESIZE = 32
PLAYER_SPEED = 900


# a class to create the map from  a tmx formatted file (XML) and parse it as a map using the pytmx library
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


# this class is responsible for creating the view (camera) of the player
class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(WIDTH / 2)
        y = -target.rect.y + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)


# a player class, it will be saved as a sprite
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #self.image = pg.Surface((TILESIZE, TILESIZE))
        #self.image.fill(BLACK)
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    # this method will be calleed before each movment and it will check if the new x or y is a wall it will not allow that movment
    def collide_with_walls(self, dir):
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if dir == 'x':
                    if self.vx > 0:
                        self.x = hits[0].rect.left - self.rect.width
                    if self.vx < 0:
                        self.x = hits[0].rect.right
                    self.vx = 0
                    self.rect.x = self.x
                if dir == 'y':
                    if self.vy > 0:
                        self.y = hits[0].rect.top - self.rect.height
                    if self.vy < 0:
                        self.y = hits[0].rect.bottom
                    self.vy = 0
                    self.rect.y = self.y

    # same concept as colliding with walls but here it's to check if player has enter either the winning or lossing predefined zones
    def collide_with_zones(self):
        hits = pg.sprite.spritecollide(self, self.game.passedZone, False)
        if hits:
            self.game.finish(1)
        hits = pg.sprite.spritecollide(self, self.game.deadZones, False)
        if hits:
            self.game.finish(2)
        hits = pg.sprite.spritecollide(self, self.game.passedZonesGPA, False)
        if hits:
            self.game.finish(3)

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')
        self.collide_with_zones()


# a wall class, to save it as a sprite in the games walls collection
class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


# a class for defining the dead zones wich the player will loose if he goes to
class deadZone(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.deadZones
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class deadZoneGPA(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.passedZonesGPA
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


# a class for defining the pass zones wich the player will win if he goes to
class passZone(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.passedZone
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


# a class to render the text and save it as sprite
class DrawText(pg.sprite.Sprite):
    def __init__(self, game, text, size, x, y):
        #print('here')
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        font = pg.font.Font(pg.font.match_font('arial'), size)
        self.image = font.render(text, True, WHITE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


# the game class
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('FCIT TRANFER GAME')
        self.clock = pg.time.Clock()
        self.load_data()
        self.running = True

    def load_data(self):
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'assits')
        self.map = TiledMap(path.join(map_folder, 'level1.tmx'))
        self.player_img = pg.image.load(path.join(map_folder, 'person.png')).convert_alpha()
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.deadZones = pg.sprite.Group()
        self.passedZonesGPA = pg.sprite.Group()
        self.passedZone = pg.sprite.Group()

        # in this loop it will read all the objects from the tmx file to load it here based on the object type (wall,txt,pass or fail zone)
        for obj in self.map.tmxdata.objects:
            if obj.name == 'wall':
                Wall(self, obj.x, obj.y, obj.width, obj.height)
            if obj.name == 'txt':
                DrawText(self, obj.text, 40, obj.x, obj.y)
            if obj.name == 'deadZone':
                deadZone(self, obj.x, obj.y, obj.width, obj.height)
            if obj.name == 'deadZone_gpa':
                deadZoneGPA(self, obj.x, obj.y, obj.width, obj.height)
            if obj.name == 'passed':
                passZone(self, obj.x, obj.y, obj.width, obj.height)

        self.player = Player(self,5,122)
        self.camera = Camera(self.map.width, self.map.height)

    # when user finish the game he either pass or fail
    def finish(self, status):
        self.running = False
        pg.display.quit()
        # check the status (true = he passed the game, false= he didn't so he can't transfer)
        # i will only asks the grades from the students who passed the game and CAN transfer
        if status == 1:
            app = FirebaseApplication('https://fcit-524fc.firebaseio.com/', authentication=None)
            # is transfer is open for this semester or not (you can close the transfer from the webpage)
            isOpen = app.get('/isOpen/', '')
            if isOpen == 'true':
                cpcs202=-1
                cpcs203=-1
                cpit201=-1
                cpit221=-1
                gpa = 0
                gpaCredit=0
                print('Congrats, you may transfer to FCIT, incase there where more than 15 students wanting to transfer there will be sorting in the end')
                print(' please enter the following information: ')
                id = input('ID: ')
                # it's better to take grades from Odus but since i don't have access to it, i'll just ask the user to put it
                math110 = int(input('MATH110 Grade: '))
                cpit110 = int(input('CPIT110 Grade: '))
                if math110<85 or cpit110<80:
                    cpcs202 = int(input('CPCS202 Grade: '))
                    if cpcs202<75:
                        cpcs203 = int(input('CPCS203 Grade: '))
                        if cpcs203<75:
                            print('Sorry your grade doesnt qualify you')
                            time.sleep(5)
                            self.running = False
                            exit()
                        else:
                            gpa += (cpcs203 * 3)
                            gpaCredit+=3
                    else:
                        gpa += (cpcs202*3)
                        gpaCredit += 3
                else:
                    gpa += (math110*3)+(cpit110*3)
                    gpaCredit += 6

                eli4 = int(input('ELI4 Grade: '))
                if eli4<85:
                    cpit201 = int(input('CPIT201 Grade: '))
                    if cpit201 >= 80:
                        gpa += (cpit201*3)
                        gpaCredit += 3
                    else:
                        cpit221 = int(input('CPIT221 Grade: '))
                        if cpit221<80:
                            print('Sorry your grade doesnt qualify you')
                            time.sleep(5)
                            self.running = False
                            exit()
                        gpa += (cpit221 * 3)
                        gpaCredit += 3
                else:
                    gpa += (eli4 * 2)
                    gpaCredit += 2
                gpa = gpa/gpaCredit
                print('Your gpa is : ')
                print(gpa)
                data = {
                            "cpcs202" : cpcs202,
                            "cpcs203" : cpcs203,
                            "cpit110" : cpit110,
                            "cpit201" : cpit201,
                            "cpit221" : cpit221,
                            "eli104" : eli4,
                            "gpa" : gpa,
                            "math110" : math110
                            }
                # submit the data to the database
                url = '/students/202101/'
                app.put(url, id, data)
                #print('شكراً لك سوف يتم إشعارك في حال قبولك أو لا بعد إنتهاء فترة التسجيل')
                print('Thanks, you will be contacted in the of the transferring time')
            else:
                #print('بإمكانك التحويل ولاكن الترم القادم بإذن الله، التحويل مغلق هذا الترم')
                print('Congrats, you may transfer, but not this semester it\'s closed')
        elif status == 2:
            #print('نعتذر منك ليس بإمكانك التحويل للكلية')
            print('Sorry you cannot transfer :(')
        elif status == 3:
            print('Sorry you cannot transfer because of your GPA :(')
            print('But there might be a chance for an exception, please contact FCIT administrators')

        # stop running
        time.sleep(5)
        self.running = False

    def update(self):
        # update portion of the game loop
        if self.running:
            self.all_sprites.update()
            self.camera.update(self.player)

    def draw(self):
        if self.running:
            self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

    def quit(self):
        self.running = False
        pg.quit()
        sys.exit()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            self.events()
            self.update()
            self.draw()


def main():
    print('\nYour goal is to finish the map and reach FCIT building and the top')
    print('you can move with WASD or the Arrows')
    print('\nPlease finish the game and come back')
    time.sleep(3)
    g = Game()
    g.new()
    g.run()


if __name__ == '__main__':
    main()
