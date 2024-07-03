import os
import json
import copy
import pickle

import pygame as pg

from autoTiler import *

pg.init()

block_stats = {
    1: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32)},
}

font = pg.font.SysFont('helvetica', 30)

def create_button(buttons, pos, title, func):
    title = font.render(title, False, (255, 255, 255))
    buttons.append({"position": pos, "title": title, "function": func[0], 'args': func[1]})

class LevelEditor:
    def __init__(self):
        print("""HOW TO USE:
        use middle mouse button to navigate the world
        layer +/- switch between tilesets.
        Export: export level into JSON
        Save: Save level in bytes
        Load: Load bytes into level""")
        self.running = True
        self.fps = 60
        self.tilemap_size = (30, 20)
        self.block_size = 32
        self.resolution = (self.tilemap_size[0] * self.block_size, self.tilemap_size[1] * self.block_size)
        self.display = pg.display.set_mode(self.resolution)
        self.clock = pg.time.Clock()
        self.type = 1
        self.scroll = [0, 0]
        self.mouse_pos = (0, 0)
        self.render_list = []
        self.textures = {}
        self.tilemaps = {0: []}
        self.tilemap_id = 0
        self.buttons = []
        self.selected_objects = []
        create_button(self.buttons, pg.Rect(10, 10, 100, 50), 'Export', [self.export, self.get_objects])
        create_button(self.buttons, pg.Rect(10, 70, 100, 50), 'Save', [self.save, self.get_tilemaps])
        create_button(self.buttons, pg.Rect(10, 130, 100, 50), 'Load', [self.load, None])

        create_button(self.buttons, pg.Rect(10, 190, 100, 50), '+1 Layer', [self.change_layer, 1])
        create_button(self.buttons, pg.Rect(10, 250, 100, 50), '-1 Layer', [self.change_layer, -1])

        amount_of_textures = 24
        for x in range(amount_of_textures):
            self.textures[x] = pg.image.load(os.path.join(os.getcwd(), 'tiles', f'Albasee{x}.png')).convert_alpha()
    
    def change_layer(self, i):
        self.tilemap_id += i

        if not self.tilemap_id in self.tilemaps:
            self.tilemaps[self.tilemap_id] = []

    def get_objects(self):
        return self.tilemaps[self.tilemap_id]
    
    def get_tilemaps(self):
        return self.tilemaps

    def convert_to_tilemap(self, objects, selected = False):
        tilemap = {}
        selection = []

        for x in range(self.tilemap_size[0]*self.tilemap_size[1]):
            tilemap[f"{x%self.tilemap_size[0]};{x//self.tilemap_size[1]}"] = 0

        for object in objects:
            pos = f'{int(object[1][0]//self.block_size)};{int(object[1][1]//self.block_size)}'
            tilemap[pos] = [object[0]] + object[2:]

            if object in self.selected_objects:
                selection.append(pos)

        if selected:
            return tilemap, selection

        else:
            return tilemap

    def export(self, data):
        with open('file.json', 'w') as file:
            json.dump(self.convert_to_tilemap(data), file)

    def save(self, data):
        name = input('save name: ')
        with open(f'{name}.level', 'wb') as file:
            pickle.dump(data, file)

    def load(self):
        name = input('save name: ')
        with open(f'{name}.level', 'rb') as file:
            self.tilemaps = pickle.load(file)

        self.tilemap_id = 0

    def update_render(self, objects):
        selection = []
        tilemap, selection = self.convert_to_tilemap(objects, selected=True)
        self.render_list = []
        for tile in tilemap:
            tile_data = tilemap[tile]
            if tile_data:
                origin_tile = tile.split(';')
                x = int(origin_tile[0])
                y = int(origin_tile[1])
                surface = pg.transform.flip(pg.transform.scale(self.textures[get_neighboring_tiles(tilemap, tile)], tile_data[3]), tile_data[2][0], tile_data[2][1])

                if tile in selection:
                    surface.fill((0, 255, 0), special_flags = pg.BLEND_RGB_MULT)

                self.render_list.append([surface, (x*self.block_size, y*self.block_size)])

    def run(self):
        while self.running:
            self.clock.tick(self.fps)

            self.display.fill((0, 20, 50))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_d:
                        self.rotation -= 90

                    if event.key == pg.K_a:
                        self.rotation += 90
                
                    if event.key == pg.K_ESCAPE:
                        self.running = False

                    if event.key == pg.K_DELETE:
                        for object in self.selected_objects:
                            self.tilemaps[self.tilemap_id].remove(object)

                        self.selected_objects = []

                        self.update_render(self.tilemaps[self.tilemap_id])

                    if event.key == pg.K_t:
                        self.export(self.tilemaps[self.tilemap_id])

                if event.type == pg.MOUSEBUTTONDOWN:

                    on_mouse = False

                    if event.button == 1:
                        for button in self.buttons:
                            if button['position'].collidepoint(mouse_pos):
                                if button['args']:
                                    button['function'](button['args']() if callable(button['args']) else button['args'])
                                else:
                                    button['function']()
                                    
                                self.update_render(self.tilemaps[self.tilemap_id])

                                on_mouse = True

                    if not on_mouse:
                        if event.button == 1:
                            collide, flip, hitbox = block_stats[self.type].values()
                            self.tilemaps[self.tilemap_id].append([self.type, (mx, my), collide, flip, hitbox])

                        elif event.button == 3:
                            #selected_objects
                            if not pg.key.get_pressed()[pg.K_LSHIFT]:
                                self.selected_objects = []

                            for block in self.tilemaps[self.tilemap_id]:
                                if not block in self.selected_objects:
                                    rect = pg.Rect(block[1][0], block[1][1], block[4][0], block[4][1])
                                    if rect.collidepoint((mx, my)):
                                        self.selected_objects.append(block)
                                        break
                            '''if [self.type, (mx, my), collide, flip, hitbox] in self.tilemaps[self.tilemap_id]:
                                self.tilemaps[self.tilemap_id].remove([self.type, (mx, my), collide, flip, hitbox])'''

                        self.update_render(self.tilemaps[self.tilemap_id])

            if pg.mouse.get_pressed()[1]:
                self.scroll[0] -= mouse_pos[0] - pg.mouse.get_pos()[0]
                self.scroll[1] -= mouse_pos[1] - pg.mouse.get_pos()[1]

            mouse_pos = [pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]]

            mx, my = mouse_pos
            
            mx = (((mx-self.resolution[0]/2)) + self.resolution[0]/2 - self.scroll[0]) // self.block_size * self.block_size
            my = (((my-self.resolution[1]/2)) + self.resolution[1]/2 - self.scroll[1]) // self.block_size * self.block_size 

            pg.draw.line(self.display, (255, 255, 255), (0, self.scroll[1]), (self.resolution[0], self.scroll[1]))

            pg.draw.line(self.display, (255, 255, 255), (self.scroll[0], 0), (self.scroll[0], self.resolution[0]))

            for i, object in enumerate(self.render_list):
                #pg.draw.rect(self.display, (255, 0, 0), (object[1][0] + self.scroll[0], object[1][1] + self.scroll[1], 32, 32))
                self.display.blit(object[0], (object[1][0] + self.scroll[0], object[1][1] + self.scroll[1]))

                    #pg.draw.rect(self.display, (0, 255, 0), (tile[1][0] + self.scroll[0], tile[1][1] + self.scroll[1], tile[4][0], tile[4][1]), )
    
            pg.draw.rect(self.display, (0, 0, 255), (mx + self.scroll[0], my + self.scroll[1], 32, 32), 3)

            for button in self.buttons:
                rectangle = button['position']
                pg.draw.rect(self.display, (10, 10, 10), rectangle)

                self.display.blit(button['title'], (rectangle.center[0] - button['title'].get_width()/2, rectangle.center[1] - button['title'].get_height()/2))

            pg.display.update()


if __name__ == '__main__':
    LevelEditor().run()
