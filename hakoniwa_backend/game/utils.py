from django.core.exceptions import ObjectDoesNotExist
from .models import Island, MapTile
import random

def random_chance(probability):
    """
    指定した確率で True を返す関数
    :param probability: 0から1の範囲の浮動小数点数 (例: 0.3 は 30% の確率)
    :return: True または False
    """
    return random.random() < probability

def get_map_tile(island, x, y):
    try:
        # x, y 座標に基づいて MapTile を取得
        return island.map_data.filter(x=x, y=y).first()
    except ObjectDoesNotExist:
        return None  # 該当するタイルが見つからない場合は None を返す

def generate_random_coordinates():
    # (0,0)から(11,11)までの144個のタプルを生成
    coordinates = [(x, y) for x in range(12) for y in range(12)]
    
    # ランダムに並び替え
    random.shuffle(coordinates)
    
    return coordinates

# 指定したHEXに対して隣接したHEXを全て出力する関数
def get_adjacent_hexes(x, y):
    directions = [(1, 0), (-1, 0)]  # 左右の隣接HEX

    if y % 2 == 0:
        # y座標が偶数の場合の隣接HEX
        directions += [(0, 1), (1, 1), (0, -1), (1, -1)]
    else:
        # y座標が奇数の場合の隣接HEX
        directions += [(-1, 1), (0, 1), (-1, -1), (0, -1)]

    # 基準座標に対して全ての方向を適用した隣接HEXリストを返す
    return [(x + dx, y + dy) for dx, dy in directions]

# 指定したHEXに対してちょうど2HEX離れたHEXを全て出力する関数
def get_two_distance_hexes(x, y):
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)] # 9時、3時、12時、6時
    directions += [(-1, -2), (1, -2), (-1, 2), (1, 2)] # 11時、1時、7時、5時

    if y % 2 == 0:
        # y座標が偶数の場合の 10時、2時、8時、4時
        directions += [(-1, -1), (2, -1), (-1, 1), (2, 1)]
    else:
        # y座標が奇数の場合の 10時、2時、8時、4時
        directions += [(-2, -1), (1, -1), (-2, 1), (1, 1)]

    # 基準座標に対して全ての方向を適用した隣接HEXリストを返す
    return [(x + dx, y + dy) for dx, dy in directions]

# 指定した島の指定した座標の周囲に、terrain_listに含まれる地形がいくつあるかを数えるための関数
def count_adjacent_terrains(island_id, x, y, terrain_list):
    try:
        island = Island.objects.get(id=island_id)
    except Island.DoesNotExist:
        raise ValueError(f"Island with id {island_id} does not exist")

    # マップデータを取得
    map_data = island.map_data.all()

    # 隣接HEXを取得
    adjacent_hexes = get_adjacent_hexes(x, y)

    count = 0
    for adj_x, adj_y in adjacent_hexes:
        # マップの範囲外の座標を無視
        if 0 <= adj_x < 12 and 0 <= adj_y < 12:
            # 隣接HEXのterrainを取得
            map_tile = map_data.get(x=adj_x, y=adj_y)
            if map_tile.terrain in terrain_list:
                count += 1

    return count

# 指定した島の指定した座標から半径2HEX以内に、terrain_listに含まれる地形がいくつあるかを数えるための関数
def count_two_distance_terrains(island_id, x, y, terrain_list):
    try:
        island = Island.objects.get(id=island_id)
    except Island.DoesNotExist:
        raise ValueError(f"Island with id {island_id} does not exist")

    # マップデータを取得
    map_data = island.map_data.all()  # map_dataはManyToManyFieldで定義されていると仮定

    # 2HEX以内のHEXを取得
    near_hexes = [(x, y)] + get_adjacent_hexes(x, y) + get_two_distance_hexes(x, y)

    count = 0
    for adj_x, adj_y in near_hexes:
        # マップの範囲外の座標を無視
        if 0 <= adj_x < 12 and 0 <= adj_y < 12:
            # 当該HEXのterrainを取得
            map_tile = map_data.get(x=adj_x, y=adj_y)
            if map_tile.terrain in terrain_list:
                count += 1

    return count

def get_missile_base_level(exp):
    """
    ミサイル基地の経験値からレベルを判定する関数。

    Parameters:
    exp (int): ミサイル基地の経験値 (0から255までの整数値)

    Returns:
    int: ミサイル基地のレベル (1から5)
    """
    if exp < 20:
        return 1
    elif exp < 60:
        return 2
    elif exp < 120:
        return 3
    elif exp < 200:
        return 4
    else:
        return 5

def get_sea_base_level(exp):
    """
    海底基地の経験値からレベルを判定する関数。

    Parameters:
    exp (int): 海底基地の経験値 (0から255までの整数値)

    Returns:
    int: 海底基地のレベル (1から3)
    """
    if exp < 50:
        return 1
    elif exp < 200:
        return 2
    else:
        return 3

def calculate_island_status(island_id):
    """
    指定された島のマップ情報を解析し、ステータス情報を計算する関数。

    Parameters:
    island_id (int): 島のID

    Returns:
    dict: 島のステータス情報 (area, population, farm_size, factory_size, mine_size, missile_capacity)
    """
    island = Island.objects.get(id=island_id)
    map_tiles = island.map_data.all()  # 島のマップデータを取得

    # ステータスの初期化
    area = 0
    population = 0
    farm_size = 0
    factory_size = 0
    mine_size = 0
    missile_capacity = 0

    for tile in map_tiles:
        terrain = tile.terrain
        landvalue = tile.landvalue

        if terrain not in [0, 1, 33]:  # 海、浅瀬、海底基地以外の場合
            area += 1

        if terrain in [10, 11, 12]:  # 村、町、都市の場合
            population += landvalue

        elif terrain == 20:  # 農場の場合
            farm_size += landvalue

        elif terrain == 21:  # 工場の場合
            factory_size += landvalue

        elif terrain == 22:  # 採掘場の場合
            mine_size += landvalue

        elif terrain == 30:  # ミサイル基地の場合
            missile_capacity += get_missile_base_level(landvalue)

        elif terrain == 33:  # 海底基地の場合
            missile_capacity += get_sea_base_level(landvalue)

    return {
        'area': area,
        'population': population,
        'farm_size': farm_size,
        'factory_size': factory_size,
        'mine_size': mine_size,
        'missile_capacity': missile_capacity,
    }
