import os
import json
import copy
import pickle

import pygame as pg

from autoTiler import *

pg.init()

block_stats = {
    1: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
    2: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
    3: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
    4: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
    5: {'collide': False, 'flip': [False, False], 'hitbox': (32, 64), 'tileset': False},
    6: {'collide': False, 'flip': [False, False], 'hitbox': (48*2,48*2), 'tileset': False},
    7: {'collide': False, 'flip': [False, False], 'hitbox': (48*2,48*2), 'tileset': False},
    8: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    9: {'collide': False, 'flip': [False, False], 'hitbox': (32, 64), 'tileset': False},
    10: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
    11: {'collide': False, 'flip': [False, False], 'hitbox': (48*2, 48*2), 'tileset': False},
    12: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    13: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    14: {'collide': False, 'flip': [False, False], 'hitbox': (32, 64), 'tileset': False},
    15: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    16: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    17: {'collide': False, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': False},
    18: {'collide': True, 'flip': [False, False], 'hitbox': (32, 32), 'tileset': True},
}

name_id = {
    1: 'Albasee',
    2: 'AlbaseeBG',
    3: 'Vulakit',
    4: 'VulakitBasalt',
    5: 'Vulakitplantsmall1',
    6: 'Vulakitplant1',
    7: 'Vulakitplant2',
    8: 'Vulakitplantsmallhanging',
    9: 'Vulakitcacti',
    10: 'AlbaseeHedrol',
    11: 'Albaseeplant1',
    12: 'Albaseeplantsmall1',
    13: 'Albaseeprop1',
    14: 'Albaseeprop2',
    15: 'Albaseeprop3',
    16: 'Albaseeprop4',
    17: 'Albaseeprop5',
    18: 'VulakitAuramite',
}

font = pg.font.SysFont('helvetica', 30)

def create_button(buttons, pos, title, func, img = None):
    title = font.render(title, False, (255, 255, 255))
    buttons.append({"position": pos, "title": title, "function": func[0], 'args': func[1], 'image': img})

order_ = ['Albasee', 'Vulakit', 'AlbaseeBG', 'VulakitBasalt']

str_to_int = {
}

for x in range(16*len(order_)):
    id_ = x%16
    type_ = order_[x//16]

    str_to_int[f'{type_}{id_}'] = x
#print(str_to_int)
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
        self.display = pg.display.set_mode(self.resolution, vsync=1)
        self.clock = pg.time.Clock()
        self.type = 1
        self.scroll = [0, 0]
        self.mouse_pos = (0, 0)
        self.render_list = []
        self.textures = {}
        self.tilemaps = {0: []}
        self.tilemap_id = 0
        self.buttons = []
        self.flipx = False
        self.flipy = False

        self.textures['Albasee'] = []
        self.textures['AlbaseeBG'] = []
        self.textures['Vulakit'] = []
        self.textures['VulakitBasalt'] = []
        self.textures['AlbaseeHedrol'] = []
        self.textures['VulakitAuramite'] = []

        self.props_textures = {}

        for name in sorted(os.listdir(os.path.join(os.getcwd(), 'tiles', 'props')), key=len):
            self.props_textures[name[:-4]] = pg.image.load(os.path.join(os.getcwd(), 'tiles', 'props', name)).convert_alpha()

        for name in sorted(os.listdir(os.path.join(os.getcwd(), 'tiles')), key=len):
            if 'AlbaseeBG' in name:
                self.textures['AlbaseeBG'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())

            elif 'AlbaseeHedrol' in name:
                self.textures['AlbaseeHedrol'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())

            elif 'Albasee' in name:
                self.textures['Albasee'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())
    
            elif 'VulakitBasalt' in name:
                self.textures['VulakitBasalt'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())

            elif 'VulakitAuramite' in name:
                self.textures['VulakitAuramite'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())

            elif 'Vulakit' in name:
                self.textures['Vulakit'].append(pg.image.load(os.path.join(os.getcwd(), 'tiles', name)).convert_alpha())

        create_button(self.buttons, pg.Rect(10, 10, 100, 50), 'Export', [self.export, self.get_tilemaps])
        create_button(self.buttons, pg.Rect(10, 70, 100, 50), 'Save', [self.save, self.get_tilemaps])
        create_button(self.buttons, pg.Rect(10, 130, 100, 50), 'Load', [self.load, None])

        create_button(self.buttons, pg.Rect(10, 190, 100, 50), '+1 Layer', [self.change_layer, 1])
        create_button(self.buttons, pg.Rect(10, 250, 100, 50), '-1 Layer', [self.change_layer, -1])

        create_button(self.buttons, pg.Rect(150, 10, 100, 50), '', [self.select_block, 1], self.textures['Albasee'][15])
        create_button(self.buttons, pg.Rect(250, 10, 100, 50), '', [self.select_block, 2], self.textures['AlbaseeBG'][15])
        create_button(self.buttons, pg.Rect(350, 10, 100, 50), '', [self.select_block, 3], self.textures['Vulakit'][15])
        create_button(self.buttons, pg.Rect(450, 10, 100, 50), '', [self.select_block, 4], self.textures['VulakitBasalt'][15])
        create_button(self.buttons, pg.Rect(550, 10, 100, 50), '', [self.select_block, 5], self.props_textures['Vulakitplantsmall1'])
        create_button(self.buttons, pg.Rect(650, 10, 100, 50), '', [self.select_block, 6], self.props_textures['Vulakitplant1'])
        create_button(self.buttons, pg.Rect(750, 10, 100, 50), '', [self.select_block, 7], self.props_textures['Vulakitplant2'])
        create_button(self.buttons, pg.Rect(850, 10, 100, 50), '', [self.select_block, 8], self.props_textures['Vulakitplantsmallhanging'])
        create_button(self.buttons, pg.Rect(150, 60, 100, 50), '', [self.select_block, 9], self.props_textures['Vulakitcacti'])
        create_button(self.buttons, pg.Rect(250, 60, 100, 50), '', [self.select_block, 10], self.textures['AlbaseeHedrol'][15])
        create_button(self.buttons, pg.Rect(350, 60, 100, 50), '', [self.select_block, 11], self.props_textures['Albaseeplant1'])
        create_button(self.buttons, pg.Rect(450, 60, 100, 50), '', [self.select_block, 12], self.props_textures['Albaseeplantsmall1'])
        create_button(self.buttons, pg.Rect(550, 60, 100, 50), '', [self.select_block, 13], self.props_textures['Albaseeprop1'])
        create_button(self.buttons, pg.Rect(650, 60, 100, 50), '', [self.select_block, 14], self.props_textures['Albaseeprop2'])
        create_button(self.buttons, pg.Rect(750, 60, 100, 50), '', [self.select_block, 15], self.props_textures['Albaseeprop3'])
        create_button(self.buttons, pg.Rect(850, 60, 100, 50), '', [self.select_block, 16], self.props_textures['Albaseeprop4'])
        create_button(self.buttons, pg.Rect(150, 110, 100, 50), '', [self.select_block, 17], self.props_textures['Albaseeprop5'])
        create_button(self.buttons, pg.Rect(250, 110, 100, 50), '', [self.select_block, 18], self.textures['VulakitAuramite'][15])

    def select_block(self, type):
        self.type = type

    def change_layer(self, i):
        self.tilemap_id += i

        if not self.tilemap_id in self.tilemaps:
            self.tilemaps[self.tilemap_id] = []

    def get_tilemaps(self):
        return self.tilemaps

    def convert_to_tilemap(self, objects):
        tilemap = {}

        for object in objects:
            pos = f'{int(object[1][0]//self.block_size)};{int(object[1][1]//self.block_size)}'
            tilemap[pos] = [object[0]] + object[2:]

        return tilemap

    def export(self, data):

        ids, tilemap = self.update_render(data)

        for id in ids:
            tex_id, tilemap_id = ids[id]

            tilemap[tilemap_id][id][4] = tex_id

        with open('file.json', 'w') as file:
            json.dump(tilemap, file)

    def save(self, data):
        name = input('save the name of the level: ')
        with open(f'{name}.level', 'wb') as file:
            pickle.dump(data, file)

    def load(self):
        try:
            name = input('load the name of the level: ')
            with open(f'{name}.level', 'rb') as file:
                self.tilemaps = pickle.load(file)

            self.tilemap_id = 0
        except FileNotFoundError:
            print('world doesnt exist')
            
    def update_render(self, objects):
        self.render_list = []
        block_ids = {}
        tilemaps = {}
        for tilemap in sorted(objects):
            tilemap_ = self.convert_to_tilemap(objects[tilemap])
            tilemaps[tilemap] = tilemap_
            for tile in tilemap_:
                tile_data = tilemap_[tile]
                #print(tile_data)
                if tile_data:

                    origin_tile = tile.split(';')
                    x = int(origin_tile[0])
                    y = int(origin_tile[1])   

                    name = name_id[tile_data[0]]

                    texture_id = 0

                    if block_stats[tile_data[0]]['tileset']:
                        texture_id = get_neighboring_tiles(tilemap_, tile, tile_data[0])
                        texture = self.textures[name][texture_id]
                    else:
                        texture = self.props_textures[name]

                    surface = pg.transform.flip(pg.transform.scale(texture, tile_data[3]), tile_data[2][0], tile_data[2][1])
                    self.render_list.append([surface, (x*32, y*32), tilemap])
                    block_ids[tile] = name+(str(texture_id) if block_stats[tile_data[0]]['tileset'] else ''), tilemap

        return block_ids, tilemaps

    def block_texture_id_block_ids(tilemap, block_ids):
        for id in block_ids:
            tilemap_id, value = block_ids[id]
            tilemap[tilemap_id][id][4] = value

    def run(self):
        while self.running:
            self.clock.tick(self.fps)

            self.display.fill((15, 20, 31))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                    
                    if event.key == pg.K_d and self.type + 1 in block_stats:
                        self.type += 1

                    if event.key == pg.K_a and self.type - 1 in block_stats:
                        self.type -= 1

                    if event.key == pg.K_t:
                        self.export(self.tilemaps[self.tilemap_id])

                    if event.key == pg.K_p:
                        self.flipx = not self.flipx

                    if event.key == pg.K_o:
                        self.flipy = not self.flipy

                if event.type == pg.MOUSEBUTTONDOWN:

                    on_mouse = False

                    if event.button == 1:
                        for button in self.buttons:
                            if button['position'].collidepoint(mouse_pos):
                                if button['args']:
                                    button['function'](button['args']() if callable(button['args']) else button['args'])
                                else:
                                    button['function']()
                                    
                                self.update_render(self.tilemaps)

                                on_mouse = True

            if pg.mouse.get_pressed()[1] or (pg.key.get_pressed()[pg.K_LCTRL] and pg.mouse.get_pressed()[0]):
                self.scroll[0] -= mouse_pos[0] - pg.mouse.get_pos()[0]
                self.scroll[1] -= mouse_pos[1] - pg.mouse.get_pos()[1]

            mouse_pos = [pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]]

            mx, my = mouse_pos
            
            mx = (((mx-self.resolution[0]/2)) + self.resolution[0]/2 - self.scroll[0]) // self.block_size * self.block_size
            my = (((my-self.resolution[1]/2)) + self.resolution[1]/2 - self.scroll[1]) // self.block_size * self.block_size 

            pg.draw.line(self.display, (255, 255, 255), (0, self.scroll[1]), (self.resolution[0], self.scroll[1]))

            pg.draw.line(self.display, (255, 255, 255), (self.scroll[0], 0), (self.scroll[0], self.resolution[0]))

            for i, object in enumerate(self.render_list):
                self.display.blit(object[0], (object[1][0] + self.scroll[0], object[1][1] + self.scroll[1]))
    
            pg.draw.rect(self.display, (0, 0, 255), (mx + self.scroll[0], my + self.scroll[1], self.block_size, self.block_size), 3)

            on_mouse = False

            for button in self.buttons:
                rectangle = button['position']

                pg.draw.rect(self.display, (255, 255, 255), rectangle, 1)

                if button['position'].collidepoint(mouse_pos):
                    on_mouse = True

                self.display.blit(button['title'], (rectangle.center[0] - button['title'].get_width()/2, rectangle.center[1] - button['title'].get_height()/2))

                if button['image']:
                    width = button['image'].get_width()
                    height = button['image'].get_height()
                    self.display.blit(button['image'], (rectangle.center[0] - width/2, rectangle.center[1] - height/2))

            if not on_mouse:
                collide, flip, hitbox, x = block_stats[self.type].values()

                flip = (self.flipx, self.flipy)

                if pg.mouse.get_pressed()[0] and not [self.type, (mx, my), collide, flip, hitbox, 0] in self.tilemaps[self.tilemap_id] and not (pg.key.get_pressed()[pg.K_LSHIFT] or pg.key.get_pressed()[pg.K_LCTRL]):
                    self.tilemaps[self.tilemap_id].append([self.type, (mx, my), collide, flip, hitbox, 0])
                    self.update_render(self.tilemaps)

                elif pg.mouse.get_pressed()[2] or (pg.key.get_pressed()[pg.K_LSHIFT] and pg.mouse.get_pressed()[0]):
                    for block in self.tilemaps[self.tilemap_id][:]:
                        rect = pg.Rect(block[1][0], block[1][1], block[4][0], block[4][1])
                        if rect.collidepoint((mx, my)):
                            self.tilemaps[self.tilemap_id].remove(block)
                    
                    self.update_render(self.tilemaps)

            pg.display.update()

if __name__ == '__main__':
    LevelEditor().run()
