from config import HEX_X_SIZE, HEX_Y_SIZE, GRID_WIDTH, GRID_HEIGHT


def hex_pos(x, y):
    """将网格坐标转换为像素坐标（六边形左上角）"""
    x_len = HEX_X_SIZE // 2
    y_len = HEX_Y_SIZE // 2
    if y % 2 == 0:
        base_x = x_len * 2 * x
        base_y = y_len * 3 * (y // 2)
    else:
        base_x = x_len * 2 * x + x_len
        base_y = y_len * 3 * (y // 2) + y_len // 2 + y_len
    return (base_x, base_y)


def _cross(ax, ay, bx, by):
    return ax * by - ay * bx


def _in_triangle(x1, y1, x2, y2, x3, y3, px, py):
    pa_x, pa_y = x1 - px, y1 - py
    pb_x, pb_y = x2 - px, y2 - py
    pc_x, pc_y = x3 - px, y3 - py
    t1 = _cross(pa_x, pa_y, pb_x, pb_y)
    t2 = _cross(pb_x, pb_y, pc_x, pc_y)
    t3 = _cross(pc_x, pc_y, pa_x, pa_y)
    return (t1 * t2 >= 0) and (t1 * t3 >= 0)


def hex_index(x, y):
    """将像素坐标转换为网格坐标"""
    x_len = HEX_X_SIZE // 2
    y_len = HEX_Y_SIZE // 2
    tmp_x, offset_x = divmod(x, HEX_X_SIZE)
    tmp_y, offset_y = divmod(y, y_len * 3)
    map_x, map_y = 0, 0

    if offset_y <= (y_len + y_len // 2):
        if offset_y >= y_len // 2:
            map_x, map_y = tmp_x, tmp_y * 2
        else:
            triangles = [
                (0, 0, 0, y_len // 2, x_len, 0),
                (0, y_len // 2, x_len, 0, HEX_X_SIZE, y_len // 2),
                (x_len, 0, HEX_X_SIZE, 0, HEX_X_SIZE, y_len // 2),
            ]
            targets = [
                (tmp_x - 1, tmp_y * 2 - 1),
                (tmp_x, tmp_y * 2),
                (tmp_x, tmp_y * 2 - 1),
            ]
            for i, tri in enumerate(triangles):
                if _in_triangle(*tri, offset_x, offset_y):
                    map_x, map_y = targets[i]
                    break
    elif offset_y >= HEX_Y_SIZE:
        if offset_x <= x_len:
            map_x, map_y = tmp_x - 1, tmp_y * 2 + 1
        else:
            map_x, map_y = tmp_x, tmp_y * 2 + 1
    else:
        triangles = [
            (0, y_len + y_len // 2, 0, HEX_Y_SIZE, x_len, HEX_Y_SIZE),
            (0, y_len + y_len // 2, x_len, HEX_Y_SIZE, HEX_X_SIZE, y_len + y_len // 2),
            (x_len, HEX_Y_SIZE, HEX_X_SIZE, y_len + y_len // 2, HEX_X_SIZE, HEX_Y_SIZE),
        ]
        targets = [
            (tmp_x - 1, tmp_y * 2 + 1),
            (tmp_x, tmp_y * 2),
            (tmp_x, tmp_y * 2 + 1),
        ]
        for i, tri in enumerate(triangles):
            if _in_triangle(*tri, offset_x, offset_y):
                map_x, map_y = targets[i]
                break

    return (map_x, map_y)


def get_neighbours(x, y, bg_map):
    """获取空地邻居（用于地图生成）"""
    if y % 2 == 0:
        steps = [(-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (0, 1)]
    else:
        steps = [(0, 1), (-1, 0), (0, -1), (1, -1), (1, 0), (1, 1)]
    result = []
    for dx, dy in steps:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and bg_map[ny][nx] == "EMPTY":
            result.append((nx, ny))
    return result


def get_all_neighbours(x, y):
    """获取所有邻居（不限空地）"""
    if y % 2 == 0:
        steps = [(-1, 0), (-1, -1), (0, -1), (-1, 1), (1, 0), (0, 1)]
    else:
        steps = [(-1, 0), (1, 1), (0, -1), (1, -1), (1, 0), (0, 1)]
    result = []
    for dx, dy in steps:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            result.append((nx, ny))
    return result


def hex_vertices(x, y):
    """返回六边形的 6 个顶点坐标"""
    x_len = HEX_X_SIZE // 2
    y_len = HEX_Y_SIZE // 2
    bx, by = hex_pos(x, y)
    return [
        (bx, by + y_len // 2 + y_len),
        (bx, by + y_len // 2),
        (bx + x_len, by),
        (bx + x_len * 2, by + y_len // 2),
        (bx + x_len * 2, by + y_len // 2 + y_len),
        (bx + x_len, by + y_len * 2),
    ]
