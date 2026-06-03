import random
from config import (
    GRID_WIDTH, GRID_HEIGHT, MIN_TILES_PER_LAND, MAX_TILES_PER_LAND,
    MIN_TILES_FOR_CENTER, COUNTRY_NUM, LAND_PER_COUNTRY, AVERAGE_DICE, DICE_MAX,
)
from hex_utils import get_neighbours, get_all_neighbours
from models import Land


def _generate_country_assignments(country_num, land_per_country):
    assignments = list(range(1, country_num + 1)) * land_per_country
    random.shuffle(assignments)
    return assignments


def _generate_dice_for_country(land_per_country, avg_dice, country_index):
    total = avg_dice * land_per_country + country_index * 2
    dice_list = [random.randint(1, DICE_MAX) for _ in range(land_per_country)]
    diff = sum(dice_list) - total
    while diff != 0:
        idx = random.randint(0, land_per_country - 1)
        if diff > 0 and dice_list[idx] > 1:
            dice_list[idx] -= 1
            diff -= 1
        elif diff < 0 and dice_list[idx] < DICE_MAX:
            dice_list[idx] += 1
            diff += 1
    return dice_list


def _generate_all_dice(country_num, land_per_country, avg_dice, assignments):
    dice_map = [0] * (country_num * land_per_country)
    for country_id in range(1, country_num + 1):
        dice_list = _generate_dice_for_country(land_per_country, avg_dice, country_id)
        indices = [i for i, c in enumerate(assignments) if c == country_id]
        for j, idx in enumerate(indices):
            dice_map[idx] = dice_list[j]
    return dice_map


def _grow_land(start_x, start_y, num_tiles, bg_map):
    """从起始点生长一块地"""
    land = {(start_x, start_y)}
    border = get_neighbours(start_x, start_y, bg_map)

    while len(land) < num_tiles:
        if not border:
            break
        weights = []
        for n in border:
            w = sum(1 for nb in get_neighbours(n[0], n[1], bg_map) if nb in land)
            weights.append(w)
        total = sum(weights)
        if total == 0:
            chosen = random.choice(border)
        else:
            chosen = random.choices(border, weights=weights, k=1)[0]
        land.add(chosen)
        border.remove(chosen)
        for nb in get_neighbours(chosen[0], chosen[1], bg_map):
            if nb not in land and nb not in border:
                border.append(nb)

    return land


def _find_next_center(last_land, all_lands, bg_map):
    """从上一块地的邻居中找到下一块地的起点"""
    candidates = set()
    for tile in last_land:
        for n in get_neighbours(tile[0], tile[1], bg_map):
            candidates.add(n)
    candidates = list(candidates)
    random.shuffle(candidates)

    for center in candidates:
        explored = {center}
        border = set(get_neighbours(center[0], center[1], bg_map))
        while len(explored) < MIN_TILES_FOR_CENTER and border:
            tile = border.pop()
            explored.add(tile)
            border.update(n for n in get_neighbours(tile[0], tile[1], bg_map) if n not in explored)
        if len(explored) >= MIN_TILES_FOR_CENTER:
            return center

    # 从历史地块列表中回溯
    for old_land in reversed(all_lands):
        result = _find_center_simple(old_land, bg_map)
        if result:
            return result
    return None


def _find_center_simple(land_tiles, bg_map):
    candidates = set()
    for tile in land_tiles:
        for n in get_neighbours(tile[0], tile[1], bg_map):
            candidates.add(n)
    candidates = list(candidates)
    random.shuffle(candidates)
    for center in candidates:
        explored = {center}
        border = set(get_neighbours(center[0], center[1], bg_map))
        while len(explored) < MIN_TILES_FOR_CENTER and border:
            tile = border.pop()
            explored.add(tile)
            border.update(n for n in get_neighbours(tile[0], tile[1], bg_map) if n not in explored)
        if len(explored) >= MIN_TILES_FOR_CENTER:
            return center
    return None



def _compute_adjacency(lands_dict, tile_to_land):
    """计算每块地的相邻地块"""
    for land_id, land in lands_dict.items():
        adj = set()
        for tile in land.tiles:
            for nb in get_all_neighbours(tile[0], tile[1]):
                nb_land = tile_to_land.get(nb, 0)
                if nb_land != 0 and nb_land != land_id:
                    adj.add(nb_land)
        land.set_adj_lands(adj)


def generate_map(country_num=COUNTRY_NUM, land_per_country=LAND_PER_COUNTRY, avg_dice=AVERAGE_DICE,
                  on_land_created=None):
    """生成完整地图，返回 (lands_dict, bg_map, tile_to_land)

    on_land_created: 可选回调，每生成一块地后调用 on_land_created(lands_dict, bg_map, tile_to_land)
    """
    land_num = country_num * land_per_country
    bg_map = [["EMPTY" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    tile_to_land = {}

    assignments = _generate_country_assignments(country_num, land_per_country)
    dice_map = _generate_all_dice(country_num, land_per_country, avg_dice, assignments)

    lands_dict = {}
    all_lands = []
    start_x = random.randint(0, GRID_WIDTH - 1)
    start_y = random.randint(0, GRID_HEIGHT - 1)

    for i in range(land_num):
        num_tiles = random.randint(MIN_TILES_PER_LAND, MAX_TILES_PER_LAND)
        tiles = _grow_land(start_x, start_y, num_tiles, bg_map)

        land_id = i + 1
        land = Land(land_id, tiles, assignments[i], dice_map[i])
        lands_dict[land_id] = land
        all_lands.append(tiles)

        for tx, ty in tiles:
            bg_map[ty][tx] = assignments[i]
            tile_to_land[(tx, ty)] = land_id

        if on_land_created:
            on_land_created(lands_dict, bg_map, tile_to_land)

        center = _find_next_center(tiles, all_lands, bg_map)
        if center is None:
            break
        start_x, start_y = center

    _compute_adjacency(lands_dict, tile_to_land)
    return lands_dict, bg_map, tile_to_land
