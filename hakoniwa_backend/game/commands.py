from django.core.exceptions import ObjectDoesNotExist
from game.models import Island, Plan, IslandBackup
from game.log_messages import *
from game.terrain_data import TERRAIN_LIST
from game.utils import random_chance, get_map_tile, generate_random_coordinates, get_adjacent_hexes, get_two_distance_hexes, count_adjacent_terrains, count_two_distance_terrains, get_missile_base_level, get_sea_base_level
from game.config import UNIT_MONEY, UNIT_FOOD, TREE_VALUE, FOOD_SELL_PRICE, INDUSTRY_SETTING, PROB_MAIZO
import random

# 注意：このファイルはcommand_data.pyで読み込まれているので、循環参照を回避するためにcommand_data.pyを読み込むことは禁止

def com_donothing(turn, island, plan, name, cost):
    """
    資金繰り
    """
    island.funds += 10
    island.absent += 1
    island.save()

    return 1

def com_prepare(turn, island, plan, name, cost):
    """
    整地
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain
    
    # preparableである地形だけが整地可能
    if terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['preparable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    island.funds -= cost
    map_tile.terrain = 3  # 平地にする
    map_tile.landvalue = 0
    map_tile.save()
    log_command_success(turn, island.id, island.name, (x,y), name) 

    # 埋蔵金チェック
    if random_chance(PROB_MAIZO):
        value = random.randint(100,900) # 100億円から1000億円まで
        island.funds += value
        log_maizo(turn, island.id, island.name, name, value)
    
    island.save()
    return 1
    
def com_fastprepare(turn, island, plan, name, cost):
    """
    地ならし
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain
    
    # preparableである地形だけが地ならし可能
    if terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['preparable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    island.funds -= cost
    island.preparing += 1 # 地ならし回数（地震の判定に使用）
    map_tile.terrain = 3  # 平地にする
    map_tile.landvalue = 0
    map_tile.save()

    # ログには「整地が行われました」を出力する（STミサイル擬装用）
    log_command_success(turn, island.id, island.name, (x,y), '整地') 

    island.save()
    return 1

def com_reclaim(turn, island, plan, name, cost):
    """
    埋め立て
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain
    
    # 海、浅瀬、海底基地が埋め立て可能
    reclaimable = [0, 1, 33]
    if terrain_id not in reclaimable:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    # 周りにある陸上地形の数を数える
    land_count = count_adjacent_terrains(island.id, x, y, [key for key, value in TERRAIN_LIST.items() if value.get('is_land', True)])
    
    # 周りに陸地が無いなら埋め立て失敗
    if land_count == 0:
        log_no_land_around(turn, island.id, island.name, (x,y), name)
        island.save()
        return 0
    
    island.funds -= cost
    if terrain_id in [0, 33]: # 海と海底基地
        map_tile.terrain = 1  # 浅瀬にする
        map_tile.landvalue = 0
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    elif terrain_id == 1: # 浅瀬
        map_tile.terrain = 2  # 荒地にする
        map_tile.save()
        if land_count >= 3: # 周りに陸地が3HEX以上あるなら
            adjacent_hexes = get_adjacent_hexes(x, y)
            for hex in adjacent_hexes:
                ax, ay = hex
                if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外の場合はスキップ
                    continue
                else:
                    target_tile = get_map_tile(island, ax, ay)
                    if target_tile.terrain == 0:
                        target_tile.terrain = 1 # 海なら浅瀬にする（注：海底基地は浅瀬にならないのでバレる）
                        target_tile.landvalue = 0
                        target_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    
    if plan.quantity >= 2: # 数量が2以上の場合はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1
    
def com_dig(turn, island, plan, name, cost):
    """
    掘削
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain
    
    # 怪獣以外のすべてのHEXが掘削可能
    diggable = list(range(70))
    if terrain_id not in diggable:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    if terrain_id == 0: #海を掘削して油田探査
        quantity = 1 if plan.quantity == 0 else plan.quantity
        if island.funds < quantity * cost: #油田探査の場合は費用が異なるのでもう一度チェック
            log_no_money(turn, island.id, island.name, name)
            return 0
        else:
            island.funds -= quantity * cost
            if random_chance(quantity / 100):
                map_tile.terrain = 40  # 海底油田にする
                map_tile.landvalue = 0
                map_tile.save()
                log_oil_found(turn, island.id, island.name, (x,y), name, quantity * cost)
                return 1 #油田探査の場合は数量や成否に関わらず完了するので返り値 1
            else:
                log_oil_fail(turn, island.id, island.name, (x,y), name, quantity * cost)
                return 1
    elif terrain_id in [1, 33, 40]: #浅瀬か海底基地か海底油田
        island.funds -= cost
        map_tile.terrain = 0 # 海にする
        map_tile.landvalue = 0
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    elif terrain_id in [5, 22]: # 山か採掘場
        island.funds -= cost
        map_tile.terrain = 2 #荒地にする
        map_tile.landvalue = 0
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    else: #それ以外
        island.funds -= cost
        island.area -= 1 # 面積を1減らす（最終的にはターン処理の最後に再計算することになるが、地盤沈下を回避するための緊急掘削を有効にする）
        map_tile.terrain = 1 #浅瀬にする
        map_tile.landvalue = 0
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    
    if plan.quantity >= 2: # 数量が2以上の場合（かつ、油田探査でない場合）はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1

def com_selltree(turn, island, plan, name, cost):
    """
    伐採
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    bassayable = [4, 30] # 森とミサイル基地が伐採可能
    if terrain_id not in bassayable:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    # 資金不足チェック （ただし、現在の設定では伐採はタダ）
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    if terrain_id == 4: #森
        island.funds += map_tile.landvalue * TREE_VALUE
        map_tile.terrain = 3 # 平地にする
        map_tile.landvalue = 0
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    else: # ミサイル基地に伐採コマンドを入力した場合、伐採ログだけは出る（適切に使えばミサイル基地を森に偽装することができる）
        log_command_success(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_plant(turn, island, plan, name, cost):
    """
    植林
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 地形がミサイル基地の場合はログだけ出力して終了
    if terrain_id == 30:
        log_forest_increase(turn, island.id, island.name)
        log_plant_pretend(turn, island.id, island.name, (x,y), name)
        island.save()
        return 1 # ターン消費させる（消費が無いとたぶん意味ない）

    # buildableである地形だけが建設コマンドを受け付ける
    if terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    
    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    island.funds -= cost
    map_tile.terrain = 4 # 森にする
    map_tile.landvalue = 1 # 100本
    map_tile.save()
    log_forest_increase(turn, island.id, island.name)
    log_plant_success(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_farm(turn, island, plan, name, cost):
    """
    農場整備
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が既に農場の場合は規模を拡大、農場でもbuildableでもない場合はエラー、buildableなら初期規模の農場を設置
    if terrain_id == 20:
        island.funds -= cost
        map_tile.landvalue += INDUSTRY_SETTING["FARM_EXPANSION"]
        if map_tile.landvalue > INDUSTRY_SETTING["FARM_MAXIMUM"]:
            map_tile.landvalue = INDUSTRY_SETTING["FARM_MAXIMUM"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    elif terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 20 # 農場にする
        map_tile.landvalue = INDUSTRY_SETTING["FARM_INITIAL"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)

    if plan.quantity >= 2: # 数量が2以上の場合はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1
    
def com_factory(turn, island, plan, name, cost):
    """
    工場建設
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が既に工場の場合は規模を拡大、工場でもbuildableでもない場合はエラー、buildableなら初期規模の工場を設置
    if terrain_id == 21:
        island.funds -= cost
        map_tile.landvalue += INDUSTRY_SETTING["FACTORY_EXPANSION"]
        if map_tile.landvalue > INDUSTRY_SETTING["FACTORY_MAXIMUM"]:
            map_tile.landvalue = INDUSTRY_SETTING["FACTORY_MAXIMUM"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    elif terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 21 # 工場にする
        map_tile.landvalue = INDUSTRY_SETTING["FACTORY_INITIAL"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)

    if plan.quantity >= 2: # 数量が2以上の場合はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1

def com_mine(turn, island, plan, name, cost):
    """
    採掘場整備
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が既に採掘場の場合は規模を拡大、採掘場でも山でもない場合はエラー、山なら初期規模の工場を設置
    if terrain_id == 22:
        island.funds -= cost
        map_tile.landvalue += INDUSTRY_SETTING["MINE_EXPANSION"]
        if map_tile.landvalue > INDUSTRY_SETTING["MINE_MAXIMUM"]:
            map_tile.landvalue = INDUSTRY_SETTING["MINE_MAXIMUM"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)
    elif terrain_id != 5:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 22 # 採掘場にする
        map_tile.landvalue = INDUSTRY_SETTING["MINE_INITIAL"]
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)

    if plan.quantity >= 2: # 数量が2以上の場合はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1
    
def com_mbase(turn, island, plan, name, cost):
    """
    ミサイル基地建設
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形がbuildableならミサイル基地を設置、それ以外はすべてエラー
    if terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 30 # ミサイル基地にする
        map_tile.landvalue = 0 # 経験値ゼロ
        map_tile.save()
        log_forest_increase(turn, island.id, island.name)
        log_plant_success(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_defence(turn, island, plan, name, cost):
    """
    防衛施設建設
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が防衛施設なら自爆装置作動、地形がbuildableなら防衛施設を設置、それ以外はすべてエラー
    if terrain_id == 31:
        island.funds -= cost # 防衛施設って自爆する場合にも建設コストかかるんだっけ？
        map_tile.landvalue = 489 # landvalue = 489の防衛施設は単HEX処理で自爆する
        log_bomb_set(turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain_id]['name'])
    elif terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 31 # 防衛施設にする
        map_tile.landvalue = 0
        map_tile.save()
        log_defence(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_seabase(turn, island, plan, name, cost):
    """
    海底基地建設
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が海なら海底基地を設置、それ以外はすべてエラー
    if terrain_id != 0:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 33 # 海底基地にする
        map_tile.landvalue = 0 # 経験値ゼロ
        map_tile.save()
        log_plant_success(turn, island.id, island.name, (x,y), name)
        # 森が増えたようです系の代替ログが出ないので客観的に見ても海底基地建設を実行したことが分かるのでは？

    island.save()
    return 1

def com_haribote(turn, island, plan, name, cost):
    """
    ハリボテ設置
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形がハリボテなら自爆装置作動（！？）、地形がbuildableならハリボテを設置、それ以外はすべてエラー
    if terrain_id == 32:
        island.funds -= cost
        map_tile.landvalue = 489 # landvalue = 489のハリボテは単HEX処理で自爆する（！？）
        map_tile.save()
        log_bomb_set(turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain_id]['name'])
    elif terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 32 # ハリボテにする
        map_tile.landvalue = 0
        map_tile.save()
        log_defence(turn, island.id, island.name, (x,y), name)
        log_plant_success(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_monument(turn, island, plan, name, cost):
    """
    記念碑建設
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック 
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形がbuildableなら記念碑を設置、それ以外はすべてエラー
    if terrain_id not in TERRAIN_LIST or not TERRAIN_LIST[terrain_id]['buildable']:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        map_tile.terrain = 50 # 記念碑にする
        if plan.quantity in [0, 1, 2]: # 名称などの割当がある記念碑
            map_tile.landvalue = plan.quantity
        else:
            map_tile.landvalue = 0 # 割当がない数量で建設を実行した場合、基本的な記念碑（モノリス）にする
        map_tile.save()
        log_command_success(turn, island.id, island.name, (x,y), name)

    island.save()
    return 1

def com_sellfood(turn, island, plan, name, cost):
    """
    食料輸出
    """
    island.absent = 0

    # 輸出しようとする数量
    quantity = 100 if plan.quantity == 0 else plan.quantity

    # 食料不足チェック
    if island.food < cost * quantity:
        log_no_food(turn, island.id, island.name, name)
        island.save()
        return 0
    else:
        island.funds += int(cost * quantity * FOOD_SELL_PRICE)
        island.food -= cost * quantity
        log_food_sell(turn, island.id, island.name, name, cost * quantity, int(cost * quantity * FOOD_SELL_PRICE))
        island.save()
        return 1

def com_buyfood(turn, island, plan, name, cost):
    """
    食料輸入
    """
    island.absent = 0

    # 輸入しようとする数量
    quantity = 100 if plan.quantity == 0 else plan.quantity

    # 資金不足チェック
    if island.funds < cost * quantity:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    else:
        island.funds -= cost * quantity
        island.food += quantity * 100
        log_food_buy(turn, island.id, island.name, name, quantity * 100, cost * quantity)
        island.save()
        return 1

def com_moneyaid(turn, island, plan, name, cost):
    """
    資金援助
    """
    island.absent = 0

    # 援助しようとする数量
    quantity = 100 if plan.quantity == 0 else plan.quantity

    # 資金不足チェック
    if island.funds < cost * quantity:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    island.funds -= cost * quantity
    target_island.funds += cost * quantity
    log_aid(turn, island.id, island.name, target_island.id, target_island.name, name, cost * quantity, UNIT_MONEY)

    island.save()
    target_island.save()
    return 1

def com_foodaid(turn, island, plan, name, cost):
    """
    食料援助
    """
    island.absent = 0

    # 援助しようとする数量
    quantity = 100 if plan.quantity == 0 else plan.quantity

    # 食料不足チェック
    if island.funds < cost * quantity:
        log_no_food(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    island.food -= cost * quantity
    target_island.food += cost * quantity
    log_aid(turn, island.id, island.name, target_island.id, target_island.name, name, cost * quantity, UNIT_FOOD)

    island.save()
    target_island.save()
    return 1

def com_propaganda(turn, island, plan, name, cost):
    """
    誘致活動
    """
    island.absent = 0

    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    island.funds -= cost
    island.propaganda = True # 誘致活動実行中フラグを立てる
    log_propaganda(turn, island.id, island.name, name)

    if plan.quantity >= 2: # 数量が2以上の場合はコマンドを削除せずに次のターンも実施
        island.save()
        return 2
    else:
        island.save()
        return 1

def com_giveup(turn, island, plan, name, cost):
    """
    島の放棄
    """
    # まず、島データを保存してから関連フィールドを処理
    island.save()
    
    # 島データのバックアップ
    IslandBackup.objects.create(
        original_island_id=island.id,
        user=island.user,
        name=island.name,
        owner=island.owner,
        discovery_turn=island.discovery_turn,
        population=island.population,
        area=island.area,
        funds=island.funds,
        food=island.food,
        farm_size=island.farm_size,
        factory_size=island.factory_size,
        mine_size=island.mine_size,
        missile_capacity=island.missile_capacity,
        turnprize = island.turnprize,
        prosperity = island.prosperity,
        superprosperity = island.superprosperity,
        ultraprosperity = island.ultraprosperity,
        peace = island.peace,
        superpeace = island.superpeace,
        ultrapeace = island.ultrapeace,
        tragedy = island.tragedy,
        supertragedy = island.supertragedy,
        ultratragedy = island.ultratragedy,
        map_data=[tile.to_dict() for tile in island.map_data.all()],  # MapTile情報をJSONに変換
        backup_date=turn
    )
    
    # 放棄のログを出力
    log_giveup(turn, island.id, island.name)

    # まず、関連するPlanオブジェクトを削除
    Plan.objects.filter(island__id=island.id).delete()
    
    # 島のデータを削除
    island.delete()
    
    return 1  # 正常終了

def com_sendmonster(turn, island, plan, name, cost):
    """
    怪獣派遣
    """
    island.absent = 0

    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0
    
    island.funds -= cost
    target_island.monstersend += 1 # 対象の島の「派遣された怪獣の数」を1つ増やす（全体災害フェイズで出現）
    log_monster_send(turn, island.id, island.name, target_island.id, target_island.name)

    island.save()
    target_island.save()
    return 1

def com_launchmonument(turn, island, plan, name, cost):
    """
    記念碑発射
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))
    map_tile = get_map_tile(island, x, y)
    
    # 現在の地形IDを取得
    terrain_id = map_tile.terrain

    # 資金不足チェック
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0
    
    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    # 地形が記念碑なら発射成功、それ以外ならすべてエラー
    if terrain_id != 50:
        log_land_fail(turn, island.id, island.name, (x, y), name, TERRAIN_LIST[terrain_id]['name'])
        island.save()
        return 0
    else:
        island.funds -= cost
        target_island.monumentfly += 1 # 対象の島の「発射された記念碑の数」を1つ増やす（全体災害フェイズで落下）
        map_tile.terrain = 3 # 発射元HEXは平地にする
        map_tile.landvalue = 0
        map_tile.save()
        log_mon_fly(turn, island.id, island.name, target_island.id, target_island.name, (x,y))

    island.save()
    target_island.save()
    return 1

def com_missile(turn, island, plan, name, cost):
    """
    ミサイル発射
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))

    # 資金不足チェック
    # 1発も撃てない場合だけキャンセル
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    # 1. ランダムな順番に並んだ座標のリストを作成
    random_coordinates = generate_random_coordinates()

    # 2. ミサイル基地(30)または海底基地(33)が存在する座標をフィルタリング
    missile_bases = [(bx, by) for (bx, by) in random_coordinates if (map_tile := get_map_tile(island, bx, by)) and map_tile.terrain in [30, 33]]
    
    # ターゲットから半径2HEX範囲を全て取得
    ZOD = [(x, y)] + get_adjacent_hexes(x, y) + get_two_distance_hexes(x, y)

    nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect = (0,) * 7
    for base_hex in missile_bases:
        bx, by = base_hex
        base_tile = get_map_tile(island, bx, by)
        if base_tile.terrain == 30:
            lv = get_missile_base_level(base_tile.landvalue)
        elif base_tile.terrain == 33:
            lv = get_sea_base_level(base_tile.landvalue)
        for _ in range(lv):
            # 資金不足または指定された発射数撃ち尽くした場合は break（ループ全体から抜ける）
            if island.funds < cost:
                break
            if nMissiles >= plan.quantity and plan.quantity != 0:
                break
            island.funds -= cost
            nMissiles += 1
            tx, ty = random.choice(ZOD) # 着弾点を特定
            if tx < 0 or tx > 11 or ty < 0 or ty > 11:
                outOfArea += 1 # 域外落下
            else:
                # 域内に落下する場合のみターゲットを取得して処理を続行
                target_tile = get_map_tile(target_island, tx, ty)
                if count_two_distance_terrains(target_island.id, tx, ty, [31]) >= 1 and target_tile.terrain != 31:
                    # 着弾点周辺の防衛施設の数を数えて1以上かつ、着弾点が防衛施設でないなら
                    defence += 1 # 防衛された
                elif target_tile.terrain in [0, 1, 5, 22, 33]: # 海、浅瀬、山、採掘場、海底基地には無効
                    noEffect += 1 
                elif target_tile.terrain == 2: # 荒地にも無効
                    noEffect += 1 
                    target_tile.landvalue = 1 # 着弾跡にする
                elif target_tile.terrain in [79, 80]:
                    failMonster += 1 # 硬化中の怪獣に命中
                    log_missile_monster_fail(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78]: # 怪獣に命中
                    sucMonster += 1
                    target_tile.landvalue -= 1 # １ダメージ
                    target_tile.save()
                    if target_tile.landvalue == 0:
                        base_tile.landvalue += TERRAIN_LIST[target_tile.terrain]['exp'] # 倒した怪獣の経験値をミサイル基地に加算
                        island.funds += TERRAIN_LIST[target_tile.terrain]['value'] # 倒した怪獣の残骸資金を倒した島に加算
                        base_tile.save()
                        log_missile_monster_success(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name']) # 怪獣HEXを荒地に変える前にログを出しておく
                        log_monster_money(turn, island.id, island.name, TERRAIN_LIST[target_tile.terrain]['name'], TERRAIN_LIST[target_tile.terrain]['value'])
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                    else:
                        log_missile_monster_damage(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [10, 11, 12]: # 町系に命中
                    success += 1
                    pop = target_tile.landvalue # 破壊した町の人口
                    base_tile.landvalue += int(pop/20) # 2000人につき経験値+1
                    base_tile.save()
                    if island.id != target_island.id: # 他人の島を撃った場合しか難民は得られない
                        island.boatpeople += int(pop/2) # 200人につき難民100人
                    log_missile_success(turn, island.id, target_island.id, (tx, ty),  TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 2 # 荒地にする
                    target_tile.landvalue = 1 # 着弾跡にする
                    target_tile.save()
                elif target_tile.terrain in [3, 4, 20, 21, 30, 31, 32, 40, 50]:
                    # 平地、森、農場、工場、ミサイル基地、防衛施設、ハリボテ、海底油田、記念碑に命中
                    success += 1
                    log_missile_success(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                    if target_tile.terrain == 40: # 油田に当たった場合
                        target_tile.terrain = 0 # 海にする
                        target_tile.landvalue = 0
                        target_tile.save()
                    else: 
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                else: # ここまでですべての地形を網羅できているはずだが、これら以外に命中した場合は失敗扱い
                    noEffect += 1 
        else:
            continue
        break

    log_missile_launch(turn, island.id, island.name, target_island.id, target_island.name, (x,y), name, nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect)

    island.save()
    target_island.save()
    return 1  # 正常終了

def com_ppmissile(turn, island, plan, name, cost):
    """
    PPミサイル発射
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))

    # 資金不足チェック
    # 1発も撃てない場合だけキャンセル
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    # 1. ランダムな順番に並んだ座標のリストを作成
    random_coordinates = generate_random_coordinates()

    # 2. ミサイル基地(30)または海底基地(33)が存在する座標をフィルタリング
    missile_bases = [(bx, by) for (bx, by) in random_coordinates if (map_tile := get_map_tile(island, bx, by)) and map_tile.terrain in [30, 33]]

    if not missile_bases:
        log_no_base(turn, island.id, island.name, name)
        island.save()
        return 0
    
    # ターゲットから半径1HEX範囲を全て取得
    # ここ以外の処理はミサイル発射と一緒
    ZOD = [(x, y)] + get_adjacent_hexes(x, y)

    nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect = (0,) * 7
    for base_hex in missile_bases:
        bx, by = base_hex
        base_tile = get_map_tile(island, bx, by)
        if base_tile.terrain == 30:
            lv = get_missile_base_level(base_tile.landvalue)
        elif base_tile.terrain == 33:
            lv = get_sea_base_level(base_tile.landvalue)
        for _ in range(lv):
            # 資金不足または指定された発射数撃ち尽くした場合は break（ループ全体から抜ける）
            if island.funds < cost:
                break
            if nMissiles >= plan.quantity and plan.quantity != 0:
                break
            island.funds -= cost
            nMissiles += 1
            tx, ty = random.choice(ZOD) # 着弾点を特定
            if tx < 0 or tx > 11 or ty < 0 or ty > 11:
                outOfArea += 1 # 域外落下
            else:
                # 域内に落下する場合のみターゲットを取得して処理を続行
                target_tile = get_map_tile(target_island, tx, ty)
                if count_two_distance_terrains(target_island.id, tx, ty, [31]) >= 1 and target_tile.terrain != 31:
                    # 着弾点周辺の防衛施設の数を数えて1以上かつ、着弾点が防衛施設でないなら
                    defence += 1 # 防衛された
                elif target_tile.terrain in [0, 1, 5, 22, 33]: # 海、浅瀬、山、採掘場、海底基地には無効
                    noEffect += 1 
                elif target_tile.terrain == 2: # 荒地にも無効
                    noEffect += 1 
                    target_tile.landvalue = 1 # 着弾跡にする
                elif target_tile.terrain in [79, 80]:
                    failMonster += 1 # 硬化中の怪獣に命中
                    log_missile_monster_fail(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78]: # 怪獣に命中
                    sucMonster += 1
                    target_tile.landvalue -= 1 # １ダメージ
                    target_tile.save()
                    if target_tile.landvalue == 0:
                        base_tile.landvalue += TERRAIN_LIST[target_tile.terrain]['exp'] # 倒した怪獣の経験値をミサイル基地に加算
                        island.funds += TERRAIN_LIST[target_tile.terrain]['value'] # 倒した怪獣の残骸資金を倒した島に加算
                        base_tile.save()
                        log_missile_monster_success(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name']) # 怪獣HEXを荒地に変える前にログを出しておく
                        log_monster_money(turn, island.id, island.name, TERRAIN_LIST[target_tile.terrain]['name'], TERRAIN_LIST[target_tile.terrain]['value'])
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                    else:
                        log_missile_monster_damage(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [10, 11, 12]: # 町系に命中
                    success += 1
                    pop = target_tile.landvalue # 破壊した町の人口
                    base_tile.landvalue += int(pop/20) # 2000人につき経験値+1
                    base_tile.save()
                    if island.id != target_island.id: # 他人の島を撃った場合しか難民は得られない
                        island.boatpeople += int(pop/2) # 200人につき難民100人
                    log_missile_success(turn, island.id, target_island.id, (tx, ty),  TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 2 # 荒地にする
                    target_tile.landvalue = 1 # 着弾跡にする
                    target_tile.save()
                elif target_tile.terrain in [3, 4, 20, 21, 30, 31, 32, 40, 50]:
                    # 平地、森、農場、工場、ミサイル基地、防衛施設、ハリボテ、海底油田、記念碑に命中
                    success += 1
                    log_missile_success(turn, island.id, target_island.id, (tx, ty),  TERRAIN_LIST[target_tile.terrain]['name'])
                    if target_tile.terrain == 40: # 油田に当たった場合
                        target_tile.terrain = 0 # 海にする
                        target_tile.landvalue = 0
                        target_tile.save()
                    else: 
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                else: # ここまでですべての地形を網羅できているはずだが、これら以外に命中した場合は失敗扱い
                    noEffect += 1 
        else:
            continue
        break

    log_missile_launch(turn, island.id, island.name, target_island.id, target_island.name, (x,y), name, nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect)

    island.save()
    target_island.save()
    
    return 1  # 正常終了

def com_stmissile(turn, island, plan, name, cost):
    """
    STミサイル発射
    """
    island.absent = 0
    #FIXME: 今の時点ではログをSTログにしているだけだが、これだと全体ログの順番で誰が撃ったか分かってしまう気がする
    x, y = map(int, plan.coordinates.split(','))

    # 資金不足チェック
    # 1発も撃てない場合だけキャンセル
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name) # 失敗ログでST撃とうとしたことバレる
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name) # 失敗ログでST撃とうとしたことバレる
        island.save()
        return 0

    # 1. ランダムな順番に並んだ座標のリストを作成
    random_coordinates = generate_random_coordinates()

    # 2. ミサイル基地(30)または海底基地(33)が存在する座標をフィルタリング
    missile_bases = [(bx, by) for (bx, by) in random_coordinates if (map_tile := get_map_tile(island, bx, by)) and map_tile.terrain in [30, 33]]

    if not missile_bases:
        log_no_base(turn, island.id, island.name, name)
        island.save()
        return 0
    
    # ターゲットから半径2HEX範囲を全て取得
    ZOD = [(x, y)] + get_adjacent_hexes(x, y) + get_two_distance_hexes(x, y)

    nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect = (0,) * 7
    for base_hex in missile_bases:
        bx, by = base_hex
        base_tile = get_map_tile(island, bx, by)
        if base_tile.terrain == 30:
            lv = get_missile_base_level(base_tile.landvalue)
        elif base_tile.terrain == 33:
            lv = get_sea_base_level(base_tile.landvalue)
        for i in range(lv):
            # 資金不足または指定された発射数撃ち尽くした場合は break（ループ全体から抜ける）
            if island.funds < cost:
                break
            if nMissiles >= plan.quantity and plan.quantity != 0:
                break
            island.funds -= cost
            nMissiles += 1
            tx, ty = random.choice(ZOD) # 着弾点を特定
            if tx < 0 or tx > 11 or ty < 0 or ty > 11:
                outOfArea += 1 # 域外落下
            else:
                # 域内に落下する場合のみターゲットを取得して処理を続行
                target_tile = get_map_tile(target_island, tx, ty)
                if count_two_distance_terrains(target_island.id, tx, ty, [31]) >= 1 and target_tile.terrain != 31:
                    # 着弾点周辺の防衛施設の数を数えて1以上かつ、着弾点が防衛施設でないなら
                    defence += 1 # 防衛された
                elif target_tile.terrain in [0, 1, 5, 22, 33]: # 海、浅瀬、山、採掘場、海底基地には無効
                    noEffect += 1 
                elif target_tile.terrain == 2: # 荒地にも無効
                    noEffect += 1 
                    target_tile.landvalue = 1 # 着弾跡にする
                elif target_tile.terrain in [79, 80]:
                    failMonster += 1 # 硬化中の怪獣に命中
                    log_stmissile_monster_fail(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78]: # 怪獣に命中
                    sucMonster += 1
                    target_tile.landvalue -= 1 # １ダメージ
                    target_tile.save()
                    if target_tile.landvalue == 0:
                        base_tile.landvalue += TERRAIN_LIST[target_tile.terrain]['exp'] # 倒した怪獣の経験値をミサイル基地に加算
                        base_tile.save()
                        log_stmissile_monster_success(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name']) # 怪獣HEXを荒地に変える前にログを出しておく
                        # STミサイルで怪獣を倒しても残骸資金は得られない
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                    else:
                        log_stmissile_monster_damage(turn, island.id, target_island.id, (tx, ty), TERRAIN_LIST[target_tile.terrain]['name'])
                elif target_tile.terrain in [10, 11, 12]: # 町系に命中
                    success += 1
                    pop = target_tile.landvalue # 破壊した町の人口
                    base_tile.landvalue += int(pop/20) # 2000人につき経験値+1
                    base_tile.save()
                    # STミサイルは難民なし
                    log_stmissile_success(turn, island.id, target_island.id, (tx, ty),  TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 2 # 荒地にする
                    target_tile.landvalue = 1 # 着弾跡にする
                    target_tile.save()
                elif target_tile.terrain in [3, 4, 20, 21, 30, 31, 32, 40, 50]:
                    # 平地、森、農場、工場、ミサイル基地、防衛施設、ハリボテ、海底油田、記念碑に命中
                    success += 1
                    log_stmissile_success(turn, island.id, target_island.id, (tx, ty),  TERRAIN_LIST[target_tile.terrain]['name'])
                    if target_tile.terrain == 40: # 油田に当たった場合
                        target_tile.terrain = 0 # 海にする
                        target_tile.landvalue = 0
                        target_tile.save()
                    else: 
                        target_tile.terrain = 2 # 荒地にする
                        target_tile.landvalue = 1 # 着弾跡にする
                        target_tile.save()
                else: # ここまでですべての地形を網羅できているはずだが、これら以外に命中した場合は失敗扱い
                    noEffect += 1 
        else:
            continue
        break

    log_stmissile_launch(turn, island.id, island.name, target_island.id, target_island.name, (x,y), name, nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect)

    island.save()
    target_island.save()
    return 1  # 正常終了

def com_ldmissile(turn, island, plan, name, cost):
    """
    陸地破壊弾発射
    """
    island.absent = 0
    x, y = map(int, plan.coordinates.split(','))

    # 資金不足チェック
    # 1発も撃てない場合だけキャンセル
    if island.funds < cost:
        log_no_money(turn, island.id, island.name, name)
        island.save()
        return 0

    # 対象の島が存在するかどうかチェック
    try:
        target_island = Island.objects.get(id=plan.target_island_id)
    except ObjectDoesNotExist:
        log_no_target(turn, island.id, island.name, name)
        island.save()
        return 0

    # 1. ランダムな順番に並んだ座標のリストを作成
    random_coordinates = generate_random_coordinates()

    # 2. ミサイル基地(30)または海底基地(33)が存在する座標をフィルタリング
    missile_bases = [(bx, by) for (bx, by) in random_coordinates if (map_tile := get_map_tile(island, bx, by)) and map_tile.terrain in [30, 33]]

    if not missile_bases:
        log_no_base(turn, island.id, island.name, name)
        island.save()
        return 0
    
    # ターゲットから半径2HEX範囲を全て取得
    ZOD = [(x, y)] + get_adjacent_hexes(x, y) + get_two_distance_hexes(x, y)

    nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect = (0,) * 7
    for base_hex in missile_bases:
        bx, by = base_hex
        base_tile = get_map_tile(island, bx, by)
        if base_tile.terrain == 30:
            lv = get_missile_base_level(base_tile.landvalue)
        elif base_tile.terrain == 33:
            lv = get_sea_base_level(base_tile.landvalue)
        for i in range(lv):
            # 資金不足または指定された発射数撃ち尽くした場合は break（ループ全体から抜ける）
            if island.funds < cost:
                break
            if nMissiles >= plan.quantity and plan.quantity != 0:
                break
            island.funds -= cost
            nMissiles += 1
            tx, ty = random.choice(ZOD) # 着弾点を特定
            if tx < 0 or tx > 11 or ty < 0 or ty > 11:
                outOfArea += 1 # 域外落下
            else:
                # 域内に落下する場合のみターゲットを取得して処理を続行
                target_tile = get_map_tile(target_island, tx, ty)
                if count_two_distance_terrains(target_island.id, tx, ty, [31]) >= 1 and target_tile.terrain != 31:
                    # 着弾点周辺の防衛施設の数を数えて1以上かつ、着弾点が防衛施設でないなら
                    defence += 1 # 防衛された
                elif target_tile.terrain == 0: # 海には無効
                    noEffect += 1 
                elif target_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]:
                    sucMonster += 1 # 硬化中を含めた怪獣に命中
                    log_ldmissile_monster(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 1 # 浅瀬にする
                    target_tile.landvalue = 0
                    target_tile.save()
                elif target_tile.terrain in [5, 22]: # 山あるいは採掘場に命中
                    success += 1
                    log_ldmissile_mountain(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 2 # 荒地にする
                    target_tile.landvalue = 0 # 山を陸破で削った場合は着弾跡にしない
                    target_tile.save()
                elif target_tile.terrain == 33: # 海底基地に命中
                    success += 1
                    log_ldmissile_sbase(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name'])
                    target_tile.terrain = 0 # 海にする
                    target_tile.landvalue = 0
                    target_tile.save()
                elif target_tile.terrain == 1: # 浅瀬に命中
                    success += 1
                    log_ldmissile_shallow(turn, island.id, target_island.id, (tx,ty))
                    target_tile.terrain = 0 # 海にする
                    target_tile.landvalue = 0
                    target_tile.save()
                else: # 他すべて
                    success += 1
                    log_ldmissile_success(turn, island.id, target_island.id, (tx,ty), TERRAIN_LIST[target_tile.terrain]['name'])
                    if target_tile.terrain == 40: # 油田に当たった場合
                        target_tile.terrain = 0 # 海にする
                        target_tile.landvalue = 0
                        target_tile.save()
                    else: 
                        target_tile.terrain = 1 # 浅瀬にする
                        target_tile.landvalue = 0
                        target_tile.save()
        else:
            continue
        break

    island.save()
    target_island.save()
    return 1  # 正常終了