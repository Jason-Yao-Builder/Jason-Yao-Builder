import pygame as pg
from config import (
    GRID_WIDTH, GRID_HEIGHT, HEX_X_SIZE, HEX_Y_SIZE,
    MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    LIGHTYELLOW, BLACK, COUNTRY_COLORS, STATE_COLORS, DEEPSKYBLUE,
)
from hex_utils import hex_pos, hex_vertices


def draw_map(surface, bg_map, lands_dict, tile_to_land, font):
    x_len = HEX_X_SIZE // 2
    y_len = HEX_Y_SIZE // 2
    surface.fill(LIGHTYELLOW)

    # 填充六边形颜色
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = bg_map[y][x]
            if isinstance(cell, int) and cell in COUNTRY_COLORS:
                color = COUNTRY_COLORS[cell]
            elif isinstance(cell, str) and cell in STATE_COLORS:
                color = STATE_COLORS[cell]
            else:
                color = LIGHTYELLOW
            verts = hex_vertices(x, y)
            pg.draw.polygon(surface, color, verts)

    # 绘制边框（只在不同地块交界处画线）
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if y % 2 == 1 and x == GRID_WIDTH - 1:
                continue
            tile_id = tile_to_land.get((x, y), 0)
            if tile_id == 0:
                continue
            verts = hex_vertices(x, y)
            verts_closed = verts + [verts[0]]

            if y % 2 == 0:
                neighbors = [
                    (x - 1, y), (x - 1, y - 1), (x, y - 1),
                    (x + 1, y), (x, y + 1), (x - 1, y + 1),
                ]
            else:
                neighbors = [
                    (x - 1, y), (x, y - 1), (x + 1, y - 1),
                    (x + 1, y), (x + 1, y + 1), (x, y + 1),
                ]

            for i, nb in enumerate(neighbors):
                nb_id = tile_to_land.get(nb, 0)
                if nb_id != tile_id:
                    pg.draw.line(surface, BLACK, verts_closed[i], verts_closed[i + 1])

    # 绘制骰子数字
    for land in lands_dict.values():
        tx, ty = land.dice_pos
        bx, by = hex_pos(tx, ty)
        cx = bx + x_len
        cy = by + y_len
        text_surf = font.render(str(land.dice_num), True, BLACK)
        rect = text_surf.get_rect(center=(cx, cy))
        surface.blit(text_surf, rect)


def draw_status_bar(surface, font, country_dict, lands_dict, game_state, country_num):
    """绘制底部状态栏：各国连通域/总地块 + 当前行动国标记"""
    bar_y = MAP_HEIGHT + (SCREEN_HEIGHT - MAP_HEIGHT) // 2 - 10
    rect_width = 80
    color_size = 20
    start_x = (MAP_WIDTH - country_num * rect_width) // 2

    for cid in range(1, country_num + 1):
        country = country_dict[cid]
        color = COUNTRY_COLORS.get(cid, LIGHTYELLOW)
        x = start_x + (cid - 1) * rect_width
        pg.draw.rect(surface, color, (x, bar_y, color_size, color_size))
        adj = country.largest_connected(lands_dict)
        text = f"{adj} / {country.land_count()}"
        text_surf = font.render(text, True, BLACK)
        surface.blit(text_surf, (x + color_size + 4, bar_y))

    # 当前行动国标记
    current = game_state.current_country
    cx = start_x + (current - 1) * rect_width + color_size // 2
    cy = bar_y + color_size + 8
    pg.draw.circle(surface, DEEPSKYBLUE, (cx, cy), 5)
