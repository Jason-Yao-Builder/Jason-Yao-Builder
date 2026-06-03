import random
from config import DICE_MAX, COUNTRY_COLORS, GREEN, BLACK


class Land:
    def __init__(self, land_id, tiles, country, dice_num):
        self.id = land_id
        self.tiles = list(tiles)
        self.country = country
        self.dice_num = dice_num
        self.dice_pos = random.choice(self.tiles)
        self.adj_lands = set()

    def set_adj_lands(self, adj_set):
        self.adj_lands = adj_set

    def apply_color(self, bg_map, color_type=None):
        if color_type is None:
            color_type = self.country
        for x, y in self.tiles:
            bg_map[y][x] = color_type

    def throw_dice(self):
        if self.dice_num <= 1:
            return 0
        return sum(random.randint(1, 6) for _ in range(self.dice_num))

    def attack_win(self, bg_map):
        self.dice_num = 1
        self.apply_color(bg_map)

    def attack_lose(self, bg_map):
        self.dice_num = 1
        self.apply_color(bg_map)

    def defend_win(self, bg_map):
        self.apply_color(bg_map)

    def defend_lose(self, attacker, bg_map, country_dict):
        country_dict[self.country].lose_land(self)
        self.country = attacker.country
        country_dict[self.country].gain_land(self)
        self.dice_num = attacker.dice_num - 1
        self.apply_color(bg_map)


class Country:
    def __init__(self, country_id, lands_dict):
        self.id = country_id
        self.land_ids = set()
        for land in lands_dict.values():
            if land.country == self.id:
                self.land_ids.add(land.id)

    def gain_land(self, land):
        self.land_ids.add(land.id)

    def lose_land(self, land):
        self.land_ids.discard(land.id)

    def land_count(self):
        return len(self.land_ids)

    def largest_connected(self, lands_dict):
        """计算最大连通域的大小"""
        remaining = list(self.land_ids)
        max_size = 0
        while remaining:
            start = remaining[0]
            visited = set()
            queue = [start]
            while queue:
                current = queue.pop()
                if current in visited:
                    continue
                visited.add(current)
                for neighbor_id in lands_dict[current].adj_lands:
                    if lands_dict[neighbor_id].country == self.id and neighbor_id not in visited:
                        queue.append(neighbor_id)
            max_size = max(max_size, len(visited))
            remaining = [lid for lid in remaining if lid not in visited]
        return max_size

    def add_dice(self, lands_dict, bg_map, on_dice_added=None):
        """回合结束时给连通域大小数量的骰子随机分配到己方土地

        on_dice_added: 可选回调，每加一个骰子后调用 on_dice_added(land, bg_map)
        """
        add_num = self.largest_connected(lands_dict)
        available = [lid for lid in self.land_ids if lands_dict[lid].dice_num < DICE_MAX]
        while add_num > 0 and available:
            lid = random.choice(available)
            land = lands_dict[lid]
            land.dice_num += 1
            if on_dice_added:
                on_dice_added(land, bg_map)
            if land.dice_num >= DICE_MAX:
                available.remove(lid)
            add_num -= 1

    def is_eliminated(self):
        return len(self.land_ids) == 0


class GameState:
    def __init__(self, country_num):
        self.turn = 1
        self.country_num = country_num
        self.selected_land = None
        self.awaiting_target = False

    @property
    def current_country(self):
        t = self.turn % self.country_num
        return self.country_num if t == 0 else t

    def next_turn(self):
        self.turn += 1
        self.selected_land = None
        self.awaiting_target = False
