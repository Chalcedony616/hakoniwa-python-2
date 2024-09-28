from django.core.management.base import BaseCommand
from game.models import GlobalSettings, Island, IslandBackup, Plan, MapTile
from game.config import GIVEUP_ABSENT, FOOD_PRODUCTIVITY, MONEY_PRODUCTIVITY, FOOD_REQUIREMENT, POPULATION_SETTING, MAXTREE, MONSTER_SETTING, DISASTER_SETTING, MAX_FOOD_STRAGE, MAX_MONEY_STRAGE, FOOD_SELL_PRICE, PRIZE_SETTING, OILINCOME, PROB_OILEND
from game.command_data import COMMAND_LIST
from game.terrain_data import TERRAIN_LIST
from game.log_messages import *
from game.utils import random_chance, get_map_tile, generate_random_coordinates, count_adjacent_terrains, get_adjacent_hexes, get_two_distance_hexes, calculate_island_status
import random, time, os, shutil
from datetime import datetime

class Command(BaseCommand):
    help = 'ターン更新処理を行います'

    def handle(self, *args, **kwargs):
        update_turn()

import time

def update_turn():
    global current_turn
    # GlobalSettingsから現在のターン数を取得
    settings = GlobalSettings.objects.first()
    if settings is None:
        raise ValueError("GlobalSettings object does not exist. Please create one.")
    current_turn = settings.turn_count

    # ターン数をインクリメント
    start_time = time.time()
    increment_turn_count()
    print(f"increment_turn_count: {time.time() - start_time:.4f} seconds")

    # 所得と食料消費フェイズ
    start_time = time.time()
    income_and_food_consumption_phase()
    print(f"income_and_food_consumption_phase: {time.time() - start_time:.4f} seconds")

    # コマンドフェイズ
    start_time = time.time()
    command_phase()
    print(f"command_phase: {time.time() - start_time:.4f} seconds")

    # HEX処理フェイズ
    start_time = time.time()
    hex_processing_phase()
    print(f"hex_processing_phase: {time.time() - start_time:.4f} seconds")

    # 災害フェイズ
    start_time = time.time()
    disaster_phase()
    print(f"disaster_phase: {time.time() - start_time:.4f} seconds")

    # ターン終了フェイズ
    start_time = time.time()
    turn_end_phase()
    print(f"turn_end_phase: {time.time() - start_time:.4f} seconds")

    # ターン数が6の倍数である場合にバックアップを作成
    if current_turn % 6 == 0:
        start_time = time.time()
        backup_database()
        print(f"backup_phase: {time.time() - start_time:.4f} seconds")

def backup_database():
    # バックアップの保存先ディレクトリを設定
    backup_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # バックアップファイル名を作成 (例: backup_1368_20240901_150000.sqlite3)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{current_turn}_{timestamp}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_filename)

    # データベースファイルのパスを取得 (例: hakoniwa_backend/db.sqlite3)
    original_db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'db.sqlite3')

    # データベースファイルをバックアップ先にコピー
    shutil.copy2(os.path.abspath(original_db_path), os.path.abspath(backup_path))

    print(f"Database backup created: {backup_path}")

# ターン数を1増やす
def increment_turn_count():
    global current_turn
    global_settings = GlobalSettings.objects.first()
    
    if global_settings:
        # ターン数を1加算
        global_settings.turn_count += 1
        global_settings.save()

        current_turn = global_settings.turn_count  # 現在のターンをグローバル変数に保存
    else:
        # エラーハンドリング（レコードが存在しない場合）
        raise Exception("GlobalSettingsのレコードが存在しません。初期化が必要です。")

# 収入フェイズ
def income_and_food_consumption_phase():
    global current_turn

    # 1. 現在存在する島をランダムに並べたリストを用意する
    islands = list(Island.objects.all())
    random.shuffle(islands)  # ランダムに並べ替え
    
    # 2. 各島ごとに収入と食料消費の処理を実行する
    for island in islands:
        # (1) 食料収入
        food_income = int(min(island.population, island.farm_size) * FOOD_PRODUCTIVITY)
        island.food += food_income
        
        # (2) 資金収入
        available_workers = max(island.population - island.farm_size, 0)
        factory_and_mine_capacity = island.factory_size + island.mine_size
        money_income = int(min(available_workers, factory_and_mine_capacity) * MONEY_PRODUCTIVITY)
        island.funds += money_income
        
        # (3) ログに収入を記録する
        log_income(current_turn, island.id, island.name, money_income, food_income)
        
        # (4) 食料消費 = int(population * FOOD_REQUIREMENT)
        food_consumed = int(island.population * FOOD_REQUIREMENT)
        island.food -= food_consumed
        
        island.save()

def command_phase():
    global current_turn

    # 1. 現在存在する島をランダムに並べたリストを用意する
    islands = list(Island.objects.all())
    random.shuffle(islands)  # ランダムに並べ替え
    
    # 2. 各島ごとにコマンドを処理
    for island in islands:
        order = 0
        try:
            while order == 0:
                order = do_command(island)
        except Exception as e:
            # エラーログを出力し、次の島に進む
            print(f"Error processing commands for island {island.name}: {e}")
            continue

        island.save()

def do_command(island):
    global current_turn

    # (1) plansリストの最初のPlanオブジェクトを取得
    current_plan = island.plans.first()
    
    if not current_plan:
        return 1  # 計画が存在しない場合は終了

    # (2) Plan.commandを取得（整数値）
    command_code = current_plan.command
    
    # (3) COMMAND_LISTからコマンド情報を取得
    command_info = COMMAND_LIST.get(command_code, None)
    
    if not command_info:
        return 1  # 無効なコマンドの場合は終了
    
    # コマンドの名前とコストを取得
    name = command_info.get("name", "")
    cost = command_info.get("cost", 0)
    
    # (4) COMMAND_LIST上の「function」要素を実行
    function_to_call = command_info["function"]
    command_result = function_to_call(current_turn, island, current_plan, name, cost)  # 0=失敗, 1=成功, 2=成功＆続行 を返す
    
    # (5) plansリストを更新
    if command_result == 2:  # 「続行」が帰ってきた場合は数量を1減らすだけ
        current_plan.quantity -= 1
        current_plan.save()
    else:
        island.plans.remove(current_plan)  # 実行済みのPlanを削除
        current_plan.delete()  # Planオブジェクトを削除

        # 放置期間を確認し、規定のターン数より長ければ「島の放棄」をリストの最初に追加
        if island.absent >= GIVEUP_ABSENT:
            # 放棄コマンド (command=39) を作成
            giveup_plan = Plan.objects.create(command=39, coordinates="0,0", target_island_id=island.id, quantity=0)
            
            # 現在の plans リストを全て取得
            current_plans = list(island.plans.all())
            
            # リストの最初に giveup_plan を挿入
            current_plans.insert(0, giveup_plan)

            # 現在の plans を一度クリアしてから、新しい順序で再追加
            island.plans.clear()
            island.plans.add(*current_plans)
        else:
            # 新しいPlanオブジェクト（資金繰り）を作成し、リストの最後に追加
            if island.plans.count() < 30:
                new_plan = Plan.objects.create(command=0, coordinates="0,0", target_island_id=island.id, quantity=0)
                island.plans.add(new_plan)
    
    # (6) COMMAND_LIST上の「turn_expend」要素をチェック
    if command_result != 0 and command_info.get("turn_expend", False):
        return 1  # コマンドが成功し、ターン消費ありの場合は終了
    else:
        return 0  # コマンドが失敗したか、ターン消費なしのコマンドが実行されたので、次の計画を実行

def hex_processing_phase():
    global current_turn

    # 1. 現在存在する島をランダムに並べたリストを用意する
    islands = list(Island.objects.all())
    random.shuffle(islands)  # ランダムに並べ替え

    # 2. 各島ごとに単HEX処理を行うdo_each_hex()関数を実行する
    for island in islands:
        
        # 3. マップデータの読み込み
        temp_map = [[{'terrain': None, 'landvalue': None, 'monster_move': None} for _ in range(12)] for _ in range(12)]
        map_tiles = list(island.map_data.all())

        for map_tile in map_tiles:
            temp_map[map_tile.x][map_tile.y]['terrain'] = map_tile.terrain
            temp_map[map_tile.x][map_tile.y]['landvalue'] = map_tile.landvalue

        # 4. 人口増加のタネ値設定
        if island.food < 0:
            addpop_town = POPULATION_SETTING["ADDPOP_STARVE"]
            addpop_city = POPULATION_SETTING["ADDPOP_STARVE"]
        elif island.propaganda:
            addpop_town = POPULATION_SETTING["ADDPOP_PROPAGANDA_TOWN"]
            addpop_city = POPULATION_SETTING["ADDPOP_PROPAGANDA_CITY"]
        else:
            addpop_town = POPULATION_SETTING["ADDPOP_TOWN"]
            addpop_city = POPULATION_SETTING["ADDPOP_CITY"]

        # 5. ランダムな順番で各HEXに対して単HEX処理を実行
        random_coordinates = generate_random_coordinates()
        for hex in random_coordinates:
            x, y = hex
            temp_map = do_each_hex(island, x, y, temp_map, addpop_town, addpop_city)

        # 6. すべての処理が終わった後、temp_mapのデータで実際のマップデータを一括更新
        for map_tile in map_tiles:
            map_tile.terrain = temp_map[map_tile.x][map_tile.y]['terrain']
            map_tile.landvalue = temp_map[map_tile.x][map_tile.y]['landvalue']

        MapTile.objects.bulk_update(map_tiles, ['terrain', 'landvalue'])

        island.save()

def do_each_hex(island, x, y, temp_map, addpop_town, addpop_city):
    global current_turn

    if temp_map[x][y]['monster_move'] == 0: # monster_moveがゼロだった場合はこのHEXの処理を飛ばす
        return temp_map
    
    # 現在の地形とlandvalueを取得
    terrain = temp_map[x][y]['terrain']
    landvalue = temp_map[x][y]['landvalue']

    if terrain in [10, 11]: # 村、町
        if addpop_town < 0: # 人口減少
            landvalue -= random.randint(1, -addpop_town)
            if landvalue < 0: # 人口ゼロ
                terrain = 2 # 荒地にする（本来は平地だが、人口が500人未満だと食料を消費しない関係で平地が大量にあると死滅しにくくなる）
                landvalue = 0
            elif landvalue < POPULATION_SETTING["POP_TOWN"]: # 人口町基準未満
                terrain = 10 # 村に戻す
        else:
            landvalue += random.randint(1, addpop_town)
            if landvalue >= POPULATION_SETTING["POP_CITY"]: # 人口都市基準以上
                terrain = 12 # 都市にする
                landvalue = POPULATION_SETTING["POP_CITY"] # 都市の下限人口
            elif landvalue >= POPULATION_SETTING["POP_TOWN"]: # 人口町基準以上
                terrain = 11 # 町にする
    elif terrain == 12: # 都市
        if addpop_city < 0: # 人口減少
            landvalue -= random.randint(1, -addpop_town)
            if landvalue < 0: # 人口ゼロ
                terrain = 3 # 平地に戻す
                landvalue = 0
            elif landvalue < POPULATION_SETTING["POP_TOWN"]: # 人口町基準未満
                terrain = 10 # 村に戻す
            elif landvalue < POPULATION_SETTING["POP_CITY"]: # 人口都市基準未満
                terrain = 11 # 町に戻す
        else:
            if addpop_city > 0: # 通常時はゼロなので人口は増やさない
                landvalue += random.randint(1, addpop_city) # 
                if landvalue > POPULATION_SETTING["MAXPOP_CITY"]:
                    landvalue = POPULATION_SETTING["MAXPOP_CITY"]
    elif terrain == 3: # 平地
        if count_adjacent_terrains(island.id, x, y, [10, 11, 12, 20]) > 0: # 周辺に町系と農場が1個以上あるなら
            if random_chance(0.2):
                terrain = 10 # 確率20％で村を生やす
                landvalue = 1
    elif terrain == 4: # 森
        landvalue += 1
        if landvalue > MAXTREE:
            landvalue = MAXTREE
    elif terrain == 31 and landvalue == 489: # 自爆装置セット済みの防衛施設
        log_bomb_fire(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'])
        temp_map = wide_damage_temp(island, temp_map, tx, ty)
    elif terrain == 32 and landvalue == 489: # 自爆装置セット済みのハリボテ
        log_bomb_fire(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'])
        log_widedamage_arechi(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'])
        terrain = 2 # 荒地にする
        landvalue = 0
    elif terrain == 40: # 海底油田
        log_oil_money(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'], OILINCOME)
        island.funds += OILINCOME
        island.save()
        if random_chance(PROB_OILEND):
            log_oil_end(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'])
            terrain = 0 # 海にする
            landvalue = 0
    elif terrain in [79, 80]: # 硬化中の怪獣
        if terrain == 79 and current_turn % 2 == 1: # 硬化中のサンジラなら（今は奇数ターンのはず）
            terrain = 75 # 硬化していないサンジラにする
        elif terrain == 80 and current_turn % 2 == 0: # 硬化中のクジラなら（今は偶数ターンのはず）
            terrain = 76 # 硬化していないクジラにする
    elif terrain in [70, 71, 72, 73, 75, 76, 77, 78]:  # 硬化していない怪獣
        adjacent_hexes = get_adjacent_hexes(x, y)
        for _ in range(5):  # 最大5回移動を試みる（すべて失敗した場合この怪獣は移動しない）
            tx, ty = random.choice(adjacent_hexes)  # 移動を試みるHEX
            if tx < 0 or tx > 11 or ty < 0 or ty > 11:  # マップ外ならスキップ
                continue
            target_terrain = temp_map[tx][ty]['terrain']
            if target_terrain in [2, 3, 4, 10, 11, 12, 20, 21, 30, 31, 32]:  # 怪獣が踏み荒らせるHEX
                log_monster_move(current_turn, island.id, island.name, (tx, ty), TERRAIN_LIST[terrain]['name'], TERRAIN_LIST[target_terrain]['name'])
                if target_terrain == 31:  # 防衛施設踏んだ
                    log_monster_defence(current_turn, island.id, island.name, (tx, ty), TERRAIN_LIST[terrain]['name'], TERRAIN_LIST[target_terrain]['name'])
                    temp_map = wide_damage_temp(island, temp_map, tx, ty)
                    terrain = 1
                    landvalue = 0  # 隣で防衛施設が自爆したはずなので浅瀬にしている（少々強引な処理）
                else:
                    temp_map[tx][ty]['terrain'] = terrain  # 移動先HEXを当該怪獣にする
                    temp_map[tx][ty]['landvalue'] = landvalue  # 体力を引き継ぎ

                    if temp_map[x][y]['monster_move'] is None:  # 初めて移動する怪獣
                        if terrain in [70, 71, 73, 77]:  # 無能力怪獣
                            temp_map[tx][ty]['monster_move'] = 0  # 移動済みにする
                        elif terrain in [72]:  # 最大2HEX移動する怪獣
                            temp_map[tx][ty]['monster_move'] = 1  # あと1歩移動できる
                        elif terrain == 75 and current_turn % 2 == 0:  # 奇数ターンに硬化する怪獣（今は偶数ターンのはず）
                            temp_map[tx][ty]['terrain'] = 79
                            temp_map[tx][ty]['monster_move'] = 0 # 移動済みにする（硬化中怪獣は単HEX処理が定義されないが、処理軽減）
                        elif terrain == 76 and current_turn % 2 == 1:  # 偶数ターンに硬化する怪獣（今は奇数ターンのはず）
                            temp_map[tx][ty]['terrain'] = 80
                            temp_map[tx][ty]['monster_move'] = 0  # 移動済みにする（硬化中怪獣は単HEX処理が定義されないが、処理軽減）
                    else:  # 既に「残りの移動回数」が記録されている怪獣
                        temp_map[tx][ty]['monster_move'] = temp_map[x][y]['monster_move'] - 1  # 残りの移動回数を1つ減らす（ゼロになると処理が飛ばされる）
                    terrain = 2  # 移動元HEXを荒地にする
                    landvalue = 0
                break  # 移動に成功したのでループから抜ける
    
    temp_map[x][y]['terrain'] = terrain # terrainとlandvalueをメモリ変数として使っていたので、最後に元データを書き換える
    temp_map[x][y]['landvalue'] = landvalue

    return temp_map  # 更新されたtemp_mapを返す

# 広域被害ルーチン
def wide_damage(island, x, y):
    global current_turn

    # 被害中心点
    map_tile = get_map_tile(island, x, y)
    if map_tile.terrain != 0:
        log_widedamage_center(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
        map_tile.terrain = 0
        map_tile.landvalue = 0 # もとが何だとしても問答無用で海
        map_tile.save()
    
    # 周囲 1HEX
    adjacent_hexes = get_adjacent_hexes(x, y)
    for hex in adjacent_hexes:
        ax, ay = hex
        if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外なら
            continue # 処理を飛ばして次へ
        else:
            map_tile = get_map_tile(island, ax, ay)
            if map_tile.terrain == 33: # 海底基地
                log_widedamage_seabase(current_turn, island.id, island.name, (ax, ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 0
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 怪獣
                log_widedamage_monster_sea(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 1 # 浅瀬にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain == 2: # 浅瀬
                map_tile.terrain = 0 # 海にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain != 0: # 海以外すべて
                log_widedamage_sea(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                if map_tile.terrain == 40: # 海底油田
                    map_tile.terrain = 0 # 海にする
                    map_tile.landvalue = 0
                    map_tile.save()
                else:
                    map_tile.terrain = 1 # 浅瀬にする
                    map_tile.landvalue = 0
                    map_tile.save()
    
    # 周囲 2HEX
    two_distance_hexes = get_two_distance_hexes(x, y)
    for hex in two_distance_hexes:
        ax, ay = hex
        if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外なら
            continue # 処理を飛ばして次へ
        else:
            map_tile = get_map_tile(island, ax, ay)
            if map_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 怪獣
                log_widedamage_monster_arechi(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 2 # 荒地にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain not in [0, 1, 2, 5, 22, 33, 40]: # 海、浅瀬、荒地、山、採掘場、海底基地、海底油田には無効
                log_widedamage_arechi(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 2 # 荒地にする
                map_tile.landvalue = 0
                map_tile.save()

# 広域被害ルーチン（単HEX処理用）
def wide_damage_temp(island, temp_map, x, y):
    global current_turn

    # 被害中心点
    terrain = temp_map[x][y]['terrain']
    if terrain != 0:
        log_widedamage_center(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[terrain]['name'])
        temp_map[x][y]['terrain'] = 0
        temp_map[x][y]['landvalue'] = 0 # もとが何だとしても問答無用で海
    
    # 周囲 1HEX
    adjacent_hexes = get_adjacent_hexes(x, y)
    for hex in adjacent_hexes:
        ax, ay = hex
        if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外なら
            continue # 処理を飛ばして次へ
        else:
            terrain = temp_map[ax][ay]['terrain']
            if terrain == 33: # 海底基地
                log_widedamage_seabase(current_turn, island.id, island.name, (ax, ay), TERRAIN_LIST[terrain]['name'])
                temp_map[ax][ay]['terrain'] = 0
                temp_map[ax][ay]['landvalue'] = 0
            elif terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 怪獣
                log_widedamage_monster_sea(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[terrain]['name'])
                temp_map[ax][ay]['terrain'] = 1 # 浅瀬にする
                temp_map[ax][ay]['landvalue'] = 0
            elif terrain == 2: # 浅瀬
                temp_map[ax][ay]['terrain'] = 0 # 海にする
                temp_map[ax][ay]['landvalue'] = 0
            elif terrain != 0: # 海以外すべて
                log_widedamage_sea(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[terrain]['name'])
                if terrain == 40: # 海底油田
                    temp_map[ax][ay]['terrain'] = 0 # 海にする
                    temp_map[ax][ay]['landvalue'] = 0
                else:
                    temp_map[ax][ay]['terrain'] = 1 # 浅瀬にする
                    temp_map[ax][ay]['landvalue'] = 0
    
    # 周囲 2HEX
    two_distance_hexes = get_two_distance_hexes(x, y)
    for hex in two_distance_hexes:
        ax, ay = hex
        if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外なら
            continue # 処理を飛ばして次へ
        else:
            terrain = temp_map[ax][ay]['terrain']
            if terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 怪獣
                log_widedamage_monster_arechi(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[terrain]['name'])
                temp_map[ax][ay]['terrain'] = 2 # 荒地にする
                temp_map[ax][ay]['landvalue'] = 0
            elif terrain not in [0, 1, 2, 5, 33, 40]: # 海、浅瀬、荒地、山、海底基地、海底油田には無効
                log_widedamage_arechi(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[terrain]['name'])
                temp_map[ax][ay]['terrain'] = 2 # 荒地にする
                temp_map[ax][ay]['landvalue'] = 0
    
    return temp_map

def disaster_phase():
    global current_turn

    # 1. 現在存在する島をランダムに並べたリストを用意する
    islands = list(Island.objects.all())
    random.shuffle(islands)  # ランダムに並べ替え

    # 2. 各島ごとに災害処理を行うdo_disaster()関数を実行する
    for island in islands:
        do_disaster(island)
        island.save()

def do_disaster(island):
    global current_turn

    random_coordinates = generate_random_coordinates() # 処理順は最初に固定してしまう
    
    # 地震
    if random_chance(DISASTER_SETTING["PROB_EARTHQUAKE"] * (1 + island.preparing)): # 地ならしの回数だけ発生確率増加
        log_earth_quake(current_turn, island.id, island.name)
        for hex in random_coordinates:
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain in [12, 32, 21]:
                if random_chance(0.25):
                    log_eq_damage(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = 2 # 荒地にする
                    map_tile.landvalue = 0
                    map_tile.save()
    
    # 食料不足
    if island.food < 0:
        log_starve(current_turn, island.id, island.name)
        island.food = 0

        for hex in random_coordinates:
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain in [21, 30, 31]: # 農場は食料不足の破壊対象から除外する。これは仕様。
                if random_chance(0.10): # 誘致活動で人口を伸ばした都市が大量に破壊されるとキツ過ぎるので25％→10％へ削減
                    log_starve_damage(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = 2 # 荒地にする
                    map_tile.landvalue = 0
                    map_tile.save()

    # 津波
    if random_chance(DISASTER_SETTING["PROB_TSUNAMI"]):
        log_tsunami(current_turn, island.id, island.name)
        for hex in random_coordinates:
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain in [10, 11, 12, 20, 21, 30, 31, 32]: 
                # 周りにある陸上地形の数を数える
                land_count = count_adjacent_terrains(island.id, x, y, [key for key, value in TERRAIN_LIST.items() if value.get('is_land', True)])
                if random_chance((5 - land_count) / 24): # 本来の仕様から確率を半減
                    log_tsunami_damage(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = 2 # 荒地にする
                    map_tile.landvalue = 0
                    map_tile.save()
    
    # 怪獣出現
    if random_chance(island.area * MONSTER_SETTING["PROB_MONSTER"]) and island.population >= MONSTER_SETTING["MONSTER_BORDER"][0]:
        # 出現できる怪獣の範囲を決定
        if island.population >= MONSTER_SETTING["MONSTER_BORDER"][2]:
            possible_monster = MONSTER_SETTING["MONSTER_LEVEL"][2]
        elif island.population >= MONSTER_SETTING["MONSTER_BORDER"][1]:
            possible_monster = MONSTER_SETTING["MONSTER_LEVEL"][1]
        else:
            possible_monster = MONSTER_SETTING["MONSTER_LEVEL"][0]
    
        # 実際に出現する怪獣を決定
        # 1から「出現する可能性がある怪獣の重みの総和」までの乱数を生成
        rnd = random.randint(0, sum(MONSTER_SETTING["MONSTER_WEIGHT"][:possible_monster+1]) - 1)  
        kind = None  # 初期化

        for i in range(possible_monster + 1):
            if rnd < MONSTER_SETTING["MONSTER_WEIGHT"][i]:
                kind = MONSTER_SETTING["MONSTER_LIST"][i]  # 乱数がMONSTER_WEIGHTの中より小さいときにその怪獣を返す
                hp = MONSTER_SETTING["MONSTER_BHP"][i] + random.randint(0, MONSTER_SETTING["MONSTER_DHP"][i])
                break
            else:
                rnd -= MONSTER_SETTING["MONSTER_WEIGHT"][i]
        
        # 怪獣の出現 HEXを決定して怪獣を出現
        for i in range(144):
            x, y = random_coordinates[i-1]
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain in [10, 11, 12]: # 村か町か都市に出現
                log_monster_come(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[kind]['name'], TERRAIN_LIST[map_tile.terrain]['name'])
                # 硬化中の怪獣の種類変更処理はログを出した後に行う
                if kind == 75 and current_turn % 2 == 0: # サンジラが偶数ターンに出現するなら
                    kind = 79 # 硬化中のサンジラにする
                elif kind == 76 and current_turn % 2 == 1: # クジラが奇数ターンに出現するなら
                    kind = 80 # 硬化中のクジラにする
                map_tile.terrain = kind
                map_tile.landvalue = hp
                map_tile.save()
                break

    # 人造怪獣出現
    if island.monstersend > 0:
        for _ in island.monstersend:
            kind = 77 # メカいのら
            hp = MONSTER_SETTING["ARTIFICIAL_MONSTER_HP"]
            # 怪獣の出現 HEXを決定して怪獣を出現
            for i in range(144):
                x, y = random_coordinates[i-1]
                map_tile = get_map_tile(island, x, y)
                if map_tile.terrain in [10, 11, 12]: # 村か町か都市に出現
                    log_monster_come(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[kind]['name'], TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = kind
                    map_tile.landvalue = hp
                    map_tile.save()
                    break

    # 地盤沈下
    if island.area > DISASTER_SETTING["FALLDOWN_BORDER"] and random_chance(DISASTER_SETTING["PROB_FALLDOWN"]): # 面積が地盤沈下限界を超えている場合に確率 PROB_FALLDOWNで沈下
        log_falldown(current_turn, island.id, island.name)
        falldown_list = [] # 沈下するHEXのリスト
        shallow_list = [] # 浅瀬のリスト
        for hex in random_coordinates: # random_coordinatesを使いまわしているので、怪獣が出現したHEXは早く沈む
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            land_count = count_adjacent_terrains(island.id, x, y, [key for key, value in TERRAIN_LIST.items() if value.get('is_land', True)]) # 周辺の陸地の数を数える
            if land_count < 6 and map_tile.terrain not in [0, 1, 33]: # 周囲すべてが陸地でない海、浅瀬、海底基地以外の地形
                falldown_list.append(hex)
            elif map_tile.terrain == 1: # 浅瀬
                shallow_list.append(hex)
        
        for hex in falldown_list: # 沈下するHEXのリスト上にあるHEXを全て沈める
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            log_falldown_land(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
            map_tile.terrain = 1 # 浅瀬にする
            map_tile.landvalue = 0
            map_tile.save()
        
        for hex in shallow_list: # 浅瀬をすべて海にする
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            map_tile.terrain = 0 # 海にする
            map_tile.landvalue = 0
            map_tile.save()
    
    # 台風
    if random_chance(DISASTER_SETTING["PROB_TYHOON"]):
        log_typhoon(current_turn, island.id, island.name)
        for hex in random_coordinates:
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain == 20: # 農場なら
                forest_count = count_adjacent_terrains(island.id, x, y, [4]) # 周辺の森の数を数える
                if random_chance((6 - forest_count)/12): # 本来の仕様から確率を半減
                    log_typhoon_damage(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = 3 # 平地にする
                    map_tile.landvalue = 0
                    map_tile.save()

    # 巨大隕石
    if random_chance(DISASTER_SETTING["PROB_HUGEMETRO"]):
        x, y = random.choice(random_coordinates) # HEXを1つランダムに選ぶ
        map_tile = get_map_tile(island, x, y)
        log_huge_meteo(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
        wide_damage(island, x, y)

    # 隕石
    if random_chance(DISASTER_SETTING["PROB_METEO"]):
        while True: # breakするまで無限ループ
            x, y = random.choice(random_coordinates) # HEXを1つランダムに選ぶ
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain == 0: # 海
                log_meteo_sea(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
            elif map_tile.terrain == 1: # 浅瀬
                log_meteo_shallow(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 0 # 海にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain == 33: # 海底基地
                log_meteo_seabase(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 0 # 海にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain in [70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 怪獣
                log_meteo_monster(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 0 # 海にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain in [5, 22]: # 山、採掘場
                log_meteo_mountain(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 2 # 荒地にする
                map_tile.landvalue = 0
                map_tile.save()
            else:
                log_meteo_damage(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 0 # 海にする
                map_tile.landvalue = 0
                map_tile.save()
            
            if random_chance(1 - DISASTER_SETTING["PROB_NEXT_METEO"]):
                break # 「次が落ちる」以外で break

    # 噴火
    if random_chance(DISASTER_SETTING["PROB_ERUPTION"]):
        x, y = random.choice(random_coordinates) # HEXを1つランダムに選ぶ
        map_tile = get_map_tile(island, x, y)

        # 噴火地点
        log_eruption(current_turn, island.id, island.name, (x,y))
        map_tile.terrain = 5 # 山にする
        map_tile.landvalue = 0
        map_tile.save()
        
        # 隣接地点
        adjacent_hexes = get_adjacent_hexes(x, y)
        for hex in adjacent_hexes:
            ax, ay = hex
            map_tile = get_map_tile(island, ax, ay)
            if ax < 0 or ax > 11 or ay < 0 or ay > 11: # 域外なら
                continue # 処理を飛ばして次へ
            if map_tile.terrain in [0, 33, 40]: # 海、海底基地、油田なら
                log_eruption_shallow(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 1 # 浅瀬にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain == 1: # 浅瀬なら
                log_eruption_uplift(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 2 # 荒地にする
                map_tile.landvalue = 0
                map_tile.save()
            elif map_tile.terrain in [2, 5, 70, 71, 72, 73, 75, 76, 77, 78, 79, 80]: # 荒地、山、怪獣には無効
                continue
            else:
                log_eruption_damage(current_turn, island.id, island.name, (ax,ay), TERRAIN_LIST[map_tile.terrain]['name'])
                map_tile.terrain = 2 # 荒地にする
                map_tile.landvalue = 0
                map_tile.save()

    # 火災（オリジナル箱庭諸島２は火災判定を単HEX処理中に行っているようだが、一応災害なのでここで実施する）
    for hex in random_coordinates:
        x, y = hex
        map_tile = get_map_tile(island, x, y)
        if map_tile.terrain in [11, 12, 21, 32]: # 町、都市、工場、ハリボテに判定あり
            if random_chance(DISASTER_SETTING["PROB_FIRE"]): # 火災の確率判定を先に行う（count_adjacent_terrainsの実行回数を減らして処理軽減）
                forest_count = count_adjacent_terrains(island.id, x, y, [4, 50]) # 周辺の森と記念碑の数を数える
                if forest_count == 0: # 森が無い
                    log_fire(current_turn, island.id, island.name, (x,y), TERRAIN_LIST[map_tile.terrain]['name'])
                    map_tile.terrain = 2 # 荒地にする
                    map_tile.landvalue = 0
                    map_tile.save()

    # 記念碑落下
    if island.monumentfly > 0:
        for _ in island.monumentfly:
            x, y = random.choice(random_coordinates) # HEXを1つランダムに選ぶ
            log_mon_fall(current_turn, island.id, island.name, (x,y))
            wide_damage(island, x, y)

    # 難民の漂着
    if island.boatpeople > 0:
        boatpeople = island.boatpeople
        log_boat_people(current_turn, island.id, island.name, boatpeople)
        for hex in random_coordinates:
            x, y = hex
            map_tile = get_map_tile(island, x, y)
            if map_tile.terrain in [3, 10, 11, 12]: # 平地、村、町、都市に対して判定
                # 難民の数だけその地形の人口を増やすが、たかだか都市の最大人口まで
                addpop = min(POPULATION_SETTING["MAXPOP_CITY"] - map_tile.landvalue, boatpeople)
                map_tile.landvalue += addpop
                if map_tile.landvalue >= POPULATION_SETTING["POP_CITY"]: # 人口都市基準以上
                    map_tile.terrain = 12 # 都市にする
                elif map_tile.landvalue >= POPULATION_SETTING["POP_TOWN"]: # 人口町基準以上
                    map_tile.terrain = 11 # 町にする
                else:
                    map_tile.terrain = 10 # 村にする
                map_tile.save()
                boatpeople -= addpop # 待機中の難民を削減
            if boatpeople <= 0: # もう待機中の難民が残ってないなら処理終了
                break
        
        # 都市がパンパンで難民に入る場所がない場合、すべてのHEXを巡回し終えた後でその難民は消滅する
        # かわいそう

    # 埋蔵金は整地コマンドに結び付けて判定済み

def turn_end_phase():
    global current_turn

    # 1. 現在存在する島をランダムに並べたリストを用意する
    islands = list(Island.objects.all())
    random.shuffle(islands)  # ランダムに並べ替え

    # 2. 各島ごとにターン終了処理を行う
    for island in islands:
        do_endphase(island)

    # 3. 島を人口順に並び替える（人口が同じ場合は前のランキングを使用）
    islands_sorted = sorted(islands, key=lambda island: (-island.population, island.ranking))

    # 4. 順位を更新
    for idx, island in enumerate(islands_sorted):
        island.ranking = idx + 1  # `ranking` を更新
        island.save()

    # 5. ターン杯の処理
    if current_turn % 100 == 0:
        islands_sorted[0].turnprize = True
        log_prize(current_turn, islands_sorted[0].id, islands_sorted[0].name, f'{current_turn}{PRIZE_SETTING["TURNPRIZE_NAME"]}')
        islands_sorted[0].save()

def do_endphase(island):
    global current_turn

    # 最大食料を超えていたら自動換金
    if island.food > MAX_FOOD_STRAGE:
        # 輸出しようとする数量
        quantity = island.food - MAX_FOOD_STRAGE

        island.funds += int(quantity * FOOD_SELL_PRICE)
        island.food = MAX_FOOD_STRAGE
        log_food_sell(current_turn, island.id, island.name, "食料自動換金", quantity, int(quantity * FOOD_SELL_PRICE))
    
    # 最大資金を超えていたら切り捨て
    if island.funds > MAX_MONEY_STRAGE:
        island.funds = MAX_MONEY_STRAGE

    # 前のターン時点での人口の記録（災難賞の判定に使用）
    oldpop = island.population # このタイミングまでに island.populationを書き換える処理はなかったはずではあるが、ここまで待つのは危険か？

    # 島の面積や人口、産業規模の計算
    calculated_status = calculate_island_status(island.id)
    island.area = calculated_status["area"]
    island.population = calculated_status["population"]
    island.farm_size = calculated_status["farm_size"]
    island.factory_size = calculated_status["factory_size"]
    island.mine_size = calculated_status["mine_size"]
    island.missile_capacity = calculated_status["missile_capacity"]

    # 繁栄賞の判定
    if island.population > PRIZE_SETTING["PROSPERITY_BORDER"][0] and not island.prosperity:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PROSPERITY_NAME"][0])
        island.prosperity = True
    elif island.population > PRIZE_SETTING["PROSPERITY_BORDER"][1] and not island.superprosperity:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PROSPERITY_NAME"][1])
        island.superprosperity = True
    elif island.population > PRIZE_SETTING["PROSPERITY_BORDER"][2] and not island.ultraprosperity:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PROSPERITY_NAME"][2])
        island.ultraprosperity = True

    # 平和賞の判定
    if island.boatpeople > PRIZE_SETTING["PEACE_BORDER"][0] and not island.peace:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PEACE_NAME"][0])
        island.peace = True
    elif island.boatpeople > PRIZE_SETTING["PEACE_BORDER"][1] and not island.superpeace:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PEACE_NAME"][1])
        island.superpeace = True
    elif island.boatpeople > PRIZE_SETTING["PEACE_BORDER"][2] and not island.ultrapeace:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["PEACE_NAME"][2])
        island.ultrapeace = True

    # 災難賞の判定
    if oldpop - island.population > PRIZE_SETTING["TRAGEDY_BORDER"][0] and not island.tragedy:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["TRAGEDY_NAME"][0])
        island.tragedy = True
    elif oldpop - island.population > PRIZE_SETTING["TRAGEDY_BORDER"][1] and not island.supertragedy:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["TRAGEDY_NAME"][1])
        island.supertragedy = True
    elif oldpop - island.population > PRIZE_SETTING["TRAGEDY_BORDER"][2] and not island.ultratragedy:
        log_prize(current_turn, island.id, island.name, PRIZE_SETTING["TRAGEDY_NAME"][2])
        island.ultratragedy = True

    # ターンごとに定義される変数のリセット
    island.propaganda = False
    island.preparing = 0
    island.monstersend = 0
    island.monumentfly = 0
    island.boatpeople = 0
    
    island.save()

    if island.population == 0: # 人口がゼロの場合の死滅処理
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
            map_data=[tile.to_dict() for tile in island.map_data.all()], # MapTile情報をJSONに変換
            backup_date=current_turn
        )
        
        # 無人化のログを出力
        log_dead(current_turn, island.id, island.name)

        # まず、関連するPlanオブジェクトを削除
        Plan.objects.filter(island__id=island.id).delete()
        
        # 島のデータを削除
        island.delete()