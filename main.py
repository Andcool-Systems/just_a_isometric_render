import texture_render
import pygame
import sys
import time

pygame.init()

screen = pygame.display.set_mode((1920, 1080))
tw = 32
top_pp_collide = texture_render.Texture(["res/empty.png", "res/empty.png", "res/sand.png"], tw)
left_pp_collide = texture_render.Texture(["res/sand.png", "res/empty.png", "res/empty.png"], tw)
right_pp_collide = texture_render.Texture(["res/empty.png", "res/sand.png", "res/empty.png"], tw)

top_mask = pygame.mask.from_surface(top_pp_collide.texture)
left_mask = pygame.mask.from_surface(left_pp_collide.texture)
right_mask = pygame.mask.from_surface(right_pp_collide.texture)

selector = texture_render.Texture(["res/selector.png"] * 3, tw)
base_plate = texture_render.Texture(["res/empty.png", "res/empty.png", "res/base.png"], tw)
f2 = pygame.font.SysFont('manrope', 24)
textures = {-1: base_plate,
            1: texture_render.Texture(["res/grass_block_side.png", "res/grass_block_side.png", "res/grass_block_top.png"], tw),
            2: texture_render.Texture(["res/sand.png"] * 3, tw),
            3: texture_render.Texture(["res/dirt.png"] * 3, tw),
            4: texture_render.Texture(["res/cherry_log.png"] * 3, tw),
            5: texture_render.Texture(["res/cherry_log.png", "res/cherry_log_top.png", "res/cherry_log.png"], tw),
            6: texture_render.Texture(["res/cherry_leaves.png"] * 3, tw, 0.7)}

test_map = {1: {1: {1: 2}, 2: {1: 2}}}
last_time_fps = time.time()
fps = 0
collided = None
place_state = False
pixelize = False
selected_block = 1
max_id = list(textures.keys())[-1]
position_x = 0
position_y = 0

position_x_2d = 0
position_y_2d = 0
last_mouse_pos = pygame.mouse.get_pos()
layer_surf = pygame.Surface((screen.get_width() // 3, screen.get_height())).convert_alpha()
before_layer_surf = pygame.Surface((screen.get_width() // 3, screen.get_height())).convert_alpha()
d3_surf = pygame.Surface(((screen.get_width() // 3) * 2, screen.get_height()))
render_layer = 1


def sort_nested_dicts(d):
    if isinstance(d, dict):
        return {k: sort_nested_dicts(v) for k, v in sorted(d.items())}
    else:
        return d


def place_block(z, xy, map: dict, selected_block):
    x, y = xy
    if z in map:
        if y in map[z]:
            map[z][y].update({x: selected_block})
        else:
            map[z].update({y: {x: selected_block}})
    else:
        map.update({z: {y: {x: selected_block}}})
    return sort_nested_dicts(map)


def remove_block(z, xy, map: dict):
    x, y = xy
    if z in map:
        if y in map[z]:
            map[z][y].pop(x, 0)
            if map[z][y] == {}:
                map[z].pop(y, 0)
            if map[z] == {}:
                map.pop(z, 0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEWHEEL:
            selected_block += event.y
            if selected_block < 1: selected_block = max_id
            if selected_block > max_id: selected_block = 1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: pixelize = not pixelize

            if event.key == pygame.K_w: render_layer += 1
            if event.key == pygame.K_s: render_layer -= 1
            if event.key == pygame.K_c: test_map = {}

    for z in test_map:
        for y in test_map[z]:
            for x in test_map[z][y]:
                try:
                    if test_map[z + 1][y][x] != 0 and \
                        test_map[z][y + 1][x] != 0 and \
                        test_map[z][y][x + 1] != 0:
                        continue
                except: pass
                        
                cart_x = x * textures[1].texture.get_width() // 2
                cart_y = y * textures[1].texture.get_height() // 2  
                iso_x = (cart_x - cart_y) 
                iso_y = (cart_x + cart_y) / 2
                centered_x = int((textures[1].texture.get_width() // 2) + iso_x)
                centered_y = int((textures[1].texture.get_height() // 2) / 2 + iso_y)

                if test_map[z][y][x] != 0:
                    texture = textures[test_map[z][y][x]].texture.copy()
                    if z == render_layer:
                        texture.fill((191, 110, 150), special_flags= pygame.BLEND_RGBA_MULT)
                    d3_surf.blit(texture, (centered_x + position_x, centered_y - (z * textures[1].texture.get_height() // 2) + position_y))
    
    if render_layer in test_map:
        map_2d = test_map[render_layer]
        for y in map_2d:
            for x in map_2d[y]:
                layer_surf.blit(textures[map_2d[y][x]].top, ((x * tw) + position_x_2d, (y * tw) + position_y_2d))

    if render_layer - 1 in test_map:
        map_2d = test_map[render_layer - 1]
        for y in map_2d:
            for x in map_2d[y]:
                before_layer_surf.blit(textures[map_2d[y][x]].top, ((x * tw) + position_x_2d, (y * tw) + position_y_2d))
        before_layer_surf.set_alpha(140)

    layer_rect = layer_surf.get_rect()
    layer_rect.x = screen.get_width() - layer_surf.get_width()
    mx, my = pygame.mouse.get_pos()
    if layer_rect.collidepoint(mx, my):
        mx_layer = mx - (screen.get_width() - layer_surf.get_width()) - position_x_2d
        my -= position_y_2d
        layer_surf.blit(selector.top, ((int(mx_layer // tw) * tw) + position_x_2d, (int(my // tw) * tw) + position_y_2d))
        collided = (int(mx_layer // tw), int(my // tw))

    d3_surf.blit(textures[selected_block].texture, (0, 0))
    
    screen.blit(before_layer_surf, (screen.get_width() - layer_surf.get_width(), 0))
    screen.blit(layer_surf, (screen.get_width() - layer_surf.get_width(), 0))
    screen.blit(d3_surf, (0, 0))
    pygame.draw.line(screen, (0, 0, 0), (screen.get_width() - layer_surf.get_width(), 0), 
                     (screen.get_width() - layer_surf.get_width(), screen.get_height()), width=3)

    if pygame.mouse.get_pressed()[1]:
        mx, my = pygame.mouse.get_pos()
        if d3_surf.get_rect().collidepoint(mx, my):
            lmx, lmy = last_mouse_pos
            position_x += mx - lmx
            position_y += my - lmy
        layer_rect = layer_surf.get_rect()
        layer_rect.x = screen.get_width() - layer_surf.get_width()
        if layer_rect.collidepoint(mx, my):
            lmx, lmy = last_mouse_pos
            position_x_2d += mx - lmx
            position_y_2d += my - lmy

    if pygame.mouse.get_pressed()[0]:
        if collided:
            remove_block(render_layer, collided, test_map)
    if pygame.mouse.get_pressed()[2]:
        if collided:
            layer_rect = layer_surf.get_rect()
            layer_rect.x = screen.get_width() - layer_surf.get_width()
            mx, my = pygame.mouse.get_pos()
            if layer_rect.collidepoint(mx, my):
                test_map = place_block(render_layer, collided, test_map, selected_block)

    last_mouse_pos = pygame.mouse.get_pos()

    fps = round(1 / (time.time() - last_time_fps), 2)
    last_time_fps = time.time()

    text2 = f2.render(f"FPS: {fps} Place_state: {'place' if not place_state else 'break'}", False, (255, 255, 255))
    screen.blit(text2, (150, 10))

    pygame.display.flip()
    d3_surf.fill((148, 59, 185))
    screen.fill((100, 59, 185))
    layer_surf.fill((0, 0, 0, 0))
    before_layer_surf.fill((0, 0, 0, 0))
