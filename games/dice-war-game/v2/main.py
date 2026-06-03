import pygame as pg
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, MAP_HEIGHT, COUNTRY_NUM,
)
from hex_utils import hex_index
from map_gen import generate_map
from models import Country, GameState
from renderer import draw_map, draw_status_bar


def handle_click(click_x, click_y, game_state, lands_dict, tile_to_land,
                 country_dict, bg_map, on_dice_added=None):
    """处理鼠标点击逻辑"""
    current = game_state.current_country

    if click_y > MAP_HEIGHT:
        # 点击底部状态栏 → 结束回合
        for land in lands_dict.values():
            land.apply_color(bg_map)
        country_dict[current].add_dice(lands_dict, bg_map, on_dice_added=on_dice_added)
        game_state.next_turn()
        return

    grid_x, grid_y = hex_index(click_x, click_y)
    land_id = tile_to_land.get((grid_x, grid_y), 0)
    if land_id == 0:
        return

    land = lands_dict[land_id]

    if not game_state.awaiting_target:
        # 选择进攻方
        if land.country != current:
            return
        game_state.selected_land = land_id
        game_state.awaiting_target = True
        land.apply_color(bg_map, "SELECT")
    else:
        attacker = lands_dict[game_state.selected_land]
        if land.country == current:
            # 切换选中
            attacker.apply_color(bg_map)
            game_state.selected_land = land_id
            land.apply_color(bg_map, "SELECT")
        elif land_id not in attacker.adj_lands:
            # 不接壤，取消选择
            attacker.apply_color(bg_map)
            game_state.selected_land = None
            game_state.awaiting_target = False
        else:
            # 攻击
            atk_roll = attacker.throw_dice()
            def_roll = land.throw_dice()
            if atk_roll > def_roll:
                land.defend_lose(attacker, bg_map, country_dict)
                attacker.attack_win(bg_map)
            else:
                attacker.attack_lose(bg_map)
                land.defend_win(bg_map)
            game_state.selected_land = None
            game_state.awaiting_target = False


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Dice Wars")
    font = pg.font.SysFont("Arial", 16)

    # 地图生成动画回调：每生成一块地就渲染一帧
    def on_land_created(ld, bm, ttl):
        draw_map(screen, bm, ld, ttl, font)
        pg.display.flip()
        pg.time.delay(10)

    lands_dict, bg_map, tile_to_land = generate_map(on_land_created=on_land_created)

    # 加骰子闪烁回调：黑色闪一下再恢复
    def on_dice_added(land, bm):
        land.apply_color(bm, "ADD_DICE")
        draw_map(screen, bm, lands_dict, tile_to_land, font)
        pg.display.flip()
        pg.time.delay(100)
        land.apply_color(bm)
        draw_map(screen, bm, lands_dict, tile_to_land, font)
        pg.display.flip()

    country_dict = {
        cid: Country(cid, lands_dict) for cid in range(1, COUNTRY_NUM + 1)
    }
    game_state = GameState(COUNTRY_NUM)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(
                    event.pos[0], event.pos[1],
                    game_state, lands_dict, tile_to_land,
                    country_dict, bg_map, on_dice_added,
                )

        draw_map(screen, bg_map, lands_dict, tile_to_land, font)
        draw_status_bar(screen, font, country_dict, lands_dict, game_state, COUNTRY_NUM)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
