from .config import TAG_COMNAME_START, TAG_COMNAME_END, TAG_QUANTITY_START, TAG_QUANTITY_END, TAG_CONFIDENTIAL_START, TAG_CONFIDENTIAL_END, TAG_DISASTER_START, TAG_DISASTER_END, TAG_NUMBER_START, TAG_NUMBER_END, SERVER_ADDRESS, UNIT_POPULATION, UNIT_MONEY, UNIT_FOOD
from django.shortcuts import get_object_or_404
from .models import Island, Log, History

#==================================================
# コマンド実行系ログ
#==================================================
# コマンド成功
# 整地、地ならし、埋め立て、掘削、伐採、農場整備、工場建設、採掘場整備、記念碑建造に使用
def log_command_success(turn, island_id, island_name, coordinates, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}で{formatted_comName}が行われました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# コマンド成功（極秘）
# 植林、ミサイル基地建設、防衛施設建設、ハリボテ設置、海底基地建設に使用
# 関数名が"plant"なのは植林用を想定していたから（修正するのめんどくさい……）
def log_plant_success(turn, island_id, island_name, coordinates, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_CONFIDENTIAL_START}（極秘）{TAG_CONFIDENTIAL_END}{link}{coordinates}で{formatted_comName}が行われました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message,
        is_confidential=True,
        is_allLog=False
    )

# 植林偽装
def log_plant_pretend(turn, island_id, island_name, coordinates, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_CONFIDENTIAL_START}（極秘）{TAG_CONFIDENTIAL_END}{link}{coordinates}で{formatted_comName}が偽装されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message,
        is_confidential=True,
        is_allLog=False
    )

# 森が増えたようです
def log_forest_increase(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：こころなしか、{link}の{TAG_QUANTITY_START}森{TAG_QUANTITY_END}が増えたようです。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 防衛施設建設
def log_defence(turn, island_id, island_name, coordinates, comName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}で{formatted_comName}が行われました。"
    confidential = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_CONFIDENTIAL_START}（極秘）{TAG_CONFIDENTIAL_END}{link}{coordinates}で{formatted_comName}が行われました。"

    # Log オブジェクトを作成し保存（公開ログ）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（機密ログ）
    Log.objects.create(
        island=island,
        turn=turn,
        message=confidential,
        is_confidential=True,
        is_allLog=False
    )

# ハリボテ設置
def log_haribote(turn, island_id, island_name, coordinates, comName, comName2):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    formatted_comName2 = f"{TAG_COMNAME_START}{comName2}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}で{formatted_comName}が行われました。"
    confidential = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_CONFIDENTIAL_START}（極秘）{TAG_CONFIDENTIAL_END}{link}{coordinates}で{formatted_comName2}が行われました。"

    # Log オブジェクトを作成し保存（公開ログ）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（機密ログ）
    Log.objects.create(
        island=island,
        turn=turn,
        message=confidential,
        is_confidential=True,
        is_allLog=False
    )

# コマンド失敗（資金不足）
def log_no_money(turn, island_id, island_name, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、資金不足のため中止されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# コマンド失敗（食料不足）
def log_no_food(turn, island_id, island_name, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、備蓄食料不足のため中止されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# コマンド失敗（実効座標が不適切地形）
def log_land_fail(turn, island_id, island_name, coordinates, comName, kind):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、予定地の{coordinates}が{TAG_QUANTITY_START}{kind}{TAG_QUANTITY_END}だったため中止されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 周りに陸がなくて埋め立て失敗
def log_no_land_around(turn, island_id, island_name, coordinates, comName):
    island = get_object_or_404(Island, id=island_id)
    
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、予定地の{coordinates}の周辺に陸地がなかったため中止されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# 油田関係ログ
#==================================================
# 油田発見
def log_oil_found(turn, island_id, island_name, coordinates, comName, budget):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}で{TAG_QUANTITY_START}{budget}{UNIT_MONEY}{TAG_QUANTITY_END}の予算を注ぎ込んだ{formatted_comName}が行われ、{TAG_QUANTITY_START}油田{TAG_QUANTITY_END}が掘り当てられました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 油田発見ならず
def log_oil_fail(turn, island_id, island_name, coordinates, comName, budget):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}で{TAG_QUANTITY_START}{budget}{UNIT_MONEY}{TAG_QUANTITY_END}の予算を注ぎ込んだ{formatted_comName}が行われましたが、油田は見つかりませんでした。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 油田からの収入
def log_oil_money(turn, island_id, island_name, coordinates, lName, income):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}から、{TAG_QUANTITY_START}{income}{UNIT_MONEY}{TAG_QUANTITY_END}の収益が上がりました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 油田枯渇
def log_oil_end(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は枯渇したようです。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# 攻撃系コマンド（ミサイル以外）のログ
#==================================================
# 怪獣派遣
def log_monster_send(turn, island_id, island_name, target_id, target_name):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{target_id}">{target_name}</a>'

    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link1}が{TAG_COMNAME_START}人造怪獣{TAG_COMNAME_END}を建造。{link2}へ送り込みました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（送られた島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }

# 記念碑、発射
def log_mon_fly(turn, island_id, island_name, target_id, target_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを作成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{target_id}">{target_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link1}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}が{link2}へ向かって飛び立ちました。"

    # Log オブジェクトを作成し保存（発射島のログ）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（飛来島のログ）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message,
        is_allLog = False
    )

# 記念碑が飛来
def log_mon_fall(turn, island_id, island_name, coordinates):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを作成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}何かとてつもないもの{TAG_QUANTITY_END}が{link}{coordinates}地点に飛来しました！！"

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 攻撃・援助系コマンド失敗（相手の島が存在しない）
def log_no_target(turn, island_id, island_name, comName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、{TAG_QUANTITY_START}目標の島が存在しない{TAG_QUANTITY_END}ため中止されました。"

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# ミサイル発射コマンドのログ
#==================================================
# 通常/PPミサイル、陸地破壊弾の発射
def log_missile_launch(turn, island_id, island_name, target_id, target_name, coordinates, comName,
                       nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{target_id}">{target_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link1}が{link2}の{coordinates}地点に向けて{TAG_QUANTITY_START}{nMissiles}発{TAG_QUANTITY_END}の{formatted_comName}を行いました。（有効：{success}発、怪獣有効：{sucMonster}発、怪獣硬化：{failMonster}発、防衛：{defence}発、域外落下：{outOfArea}発、無効：{noEffect}発）'

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }

# STミサイルの発射
# STミサイルを自島に撃った場合、この「発射」ログは極秘ログ（○○島が○○島の(x,y)地点に向けて……）と通常ログ（何者かが○○島の(x,y)地点に向けて……）の両方を出力するが、着弾ログは片方だけを出力する。
def log_stmissile_launch(turn, island_id, island_name, target_id, target_name, coordinates, comName,
                         nMissiles, success, sucMonster, failMonster, defence, outOfArea, noEffect):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{target_id}">{target_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}何者か{TAG_QUANTITY_END}が{link2}の{coordinates}地点に向けて{TAG_QUANTITY_START}{nMissiles}発{TAG_QUANTITY_END}の{formatted_comName}を行いました。（有効：{success}発、怪獣有効：{sucMonster}発、怪獣硬化：{failMonster}発、防衛：{defence}発、域外落下：{outOfArea}発、無効：{noEffect}発）'
    confidential = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_CONFIDENTIAL_START}（極秘）{TAG_CONFIDENTIAL_END}{link1}が{link2}の{coordinates}地点に向けて{TAG_QUANTITY_START}{nMissiles}発{TAG_QUANTITY_END}の{formatted_comName}を行いました。（有効：{success}発、怪獣有効：{sucMonster}発、怪獣硬化：{failMonster}発、防衛：{defence}発、域外落下：{outOfArea}発、無効：{noEffect}発）'

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=confidential,
        is_confidential=True,
        is_allLog=False
    )

    # Log オブジェクトを作成し保存（被弾島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message
    )

# ミサイル発射失敗（基地がない）
def log_no_base(turn, island_id, island_name, comName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で予定されていた{formatted_comName}は、{TAG_QUANTITY_START}ミサイル基地を保有していない{TAG_QUANTITY_END}ため中止されました。"

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# ミサイル命中時のサブログ
#==================================================
# 通常/PPミサイル、有効弾
def log_missile_success(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。一帯は壊滅しました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 通常/PPミサイル、怪獣有効弾
def log_missile_monster_damage(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は苦しそうに咆哮しました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 通常/PPミサイル、怪獣退治
def log_missile_monster_success(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は力尽き、倒れました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 通常/PPミサイル、怪獣無効弾
def log_missile_monster_fail(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中、しかし硬化状態だったため効果がありませんでした。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# STミサイル、有効弾
def log_stmissile_success(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。一帯は壊滅しました。"

    # Log オブジェクトを作成し保存（攻撃島のログは自分の島に撃った場合は通常ログと被るので出力不要）
    if (island != target):{
        Log.objects.create(
            island=island,
            turn=turn,
            message=message,
            is_confidential=True,
            is_allLog=False
        )
    }

    # Log オブジェクトを作成し保存（被弾島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message
    )

# STミサイル、怪獣有効弾
def log_stmissile_monster_damage(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は苦しそうに咆哮しました。"

    # Log オブジェクトを作成し保存（攻撃島のログは自分の島に撃った場合は通常ログと被るので出力不要）
    if (island != target):{
        Log.objects.create(
            island=island,
            turn=turn,
            message=message,
            is_confidential=True,
            is_allLog=False
        )
    }

    # Log オブジェクトを作成し保存（被弾島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message
    )

# STミサイル、怪獣退治
def log_stmissile_monster_success(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は力尽き、倒れました。"

    # Log オブジェクトを作成し保存（攻撃島のログは自分の島に撃った場合は通常ログと被るので出力不要）
    if (island != target):{
        Log.objects.create(
            island=island,
            turn=turn,
            message=message,
            is_confidential=True,
            is_allLog=False
        )
    }

    # Log オブジェクトを作成し保存（被弾島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message
    )

# STミサイル、怪獣無効弾
def log_stmissile_monster_fail(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中、しかし硬化状態だったため効果がありませんでした。"

    # Log オブジェクトを作成し保存（攻撃島のログは自分の島に撃った場合は通常ログと被るので出力不要）
    if (island != target):{
        Log.objects.create(
            island=island,
            turn=turn,
            message=message,
            is_confidential=True,
            is_allLog=False
        )
    }

    # Log オブジェクトを作成し保存（被弾島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message
    )

# 陸地破壊弾、山（あるいは採掘場）に命中
def log_ldmissile_mountain(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に命中。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は消し飛び、荒地と化しました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }

# 陸地破壊弾、海底基地に命中
def log_ldmissile_sbase(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}に着水後爆発、同地点にあった{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は跡形もなく吹き飛びました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }

# 陸地破壊弾、怪獣に命中
def log_ldmissile_monster(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}に着弾し爆発。陸地は{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}ごと水没しました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 陸地破壊弾、浅瀬に命中
def log_ldmissile_shallow(turn, island_id, target_id, coordinates):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}に着弾。海底がえぐられました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 陸地破壊弾、その他の地形に命中
def log_ldmissile_success(turn, island_id, target_id, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    message = f"ー{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に着弾。陸地は水没しました。"

    # Log オブジェクトを作成し保存（攻撃島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被弾島）
    if (island != target):{
        Log.objects.create(
            island=target,
            turn=turn,
            message=message,
            is_allLog = False
        )
    }
        
# 怪獣の死体
def log_monster_money(turn, island_id, island_name, lName, value):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"ー{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}の残骸には{TAG_QUANTITY_START}{value}{UNIT_MONEY}{TAG_QUANTITY_END}の値が付きました。"

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# その他のコマンドログ
#==================================================
# 防衛施設、自爆セット
def log_bomb_set(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}の{TAG_QUANTITY_START}自爆装置がセット{TAG_QUANTITY_END}されました。"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 防衛施設、自爆作動
def log_bomb_fire(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}、{TAG_QUANTITY_START}自爆装置作動！！{TAG_QUANTITY_END}"
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )
     
# 食料輸出
def log_food_sell(turn, island_id, island_name, comName, quantity, value):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}が{TAG_QUANTITY_START}{quantity}{UNIT_FOOD}{TAG_QUANTITY_END}の{comName}を行い、{TAG_QUANTITY_START}{value}{UNIT_MONEY}{TAG_QUANTITY_END}を得ました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 食料輸入
def log_food_buy(turn, island_id, island_name, comName, quantity, value):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}が{TAG_QUANTITY_START}{value}{UNIT_MONEY}{TAG_QUANTITY_END}を投入して{TAG_QUANTITY_START}{quantity}{UNIT_FOOD}{TAG_QUANTITY_END}の{comName}を行いました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 資金援助/食料援助
def log_aid(turn, island_id, island_name, target_id, target_name, comName, quantity, unit):
    island = get_object_or_404(Island, id=island_id)
    target = get_object_or_404(Island, id=target_id)

    # メッセージを生成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{target_id}">{target_name}</a>'
    
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link1}が{link2}へ{TAG_QUANTITY_START}{quantity}{unit}{TAG_QUANTITY_END}の{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}を行いました。'

    # Log オブジェクトを作成し保存（援助島）
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Log オブジェクトを作成し保存（被援助島）
    Log.objects.create(
        island=target,
        turn=turn,
        message=message,
        is_allLog=False
    )

# 誘致活動
def log_propaganda(turn, island_id, island_name, comName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}が行われました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# 災害系ログ
#==================================================
# 食料不足
def log_starve(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}の{TAG_DISASTER_START}食料が不足{TAG_DISASTER_END}しています！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 怪獣出現
def log_monster_come(turn, island_id, island_name, coordinates, mName, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}に{TAG_DISASTER_START}{mName}{TAG_DISASTER_END}出現！！{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}が踏み荒らされました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 怪獣動く
def log_monster_move(turn, island_id, island_name, coordinates, mName, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}が{TAG_DISASTER_START}{mName}{TAG_DISASTER_END}に踏み荒らされました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 怪獣、防衛施設を踏む
def log_monster_defence(turn, island_id, island_name, coordinates, mName, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_DISASTER_START}{mName}{TAG_DISASTER_END}が{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}へ到達、{TAG_QUANTITY_START}{lName}の自爆装置が作動！！{TAG_QUANTITY_END}'
    
    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 火災
def log_fire(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}が{TAG_DISASTER_START}火災{TAG_DISASTER_END}により壊滅しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 埋蔵金
def log_maizo(turn, island_id, island_name, comName, value):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    formatted_comName = f"{TAG_COMNAME_START}{comName}{TAG_COMNAME_END}"

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}での{formatted_comName}中に、{TAG_QUANTITY_START}{value}{UNIT_MONEY}もの埋蔵金{TAG_QUANTITY_END}が発見されました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 地震発生
def log_earth_quake(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で大規模な{TAG_DISASTER_START}地震{TAG_DISASTER_END}が発生！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 地震被害
def log_eq_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は{TAG_DISASTER_START}地震{TAG_DISASTER_END}によって壊滅しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 食料不足
def log_starve_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に{TAG_QUANTITY_START}食料を求めて住民が殺到{TAG_QUANTITY_END}。{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は壊滅しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 津波発生
def log_tsunami(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}付近で{TAG_DISASTER_START}津波{TAG_DISASTER_END}発生！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 津波被害
def log_tsunami_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は{TAG_DISASTER_START}津波{TAG_DISASTER_END}により崩壊しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 台風発生
def log_typhoon(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'

    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}に{TAG_DISASTER_START}台風{TAG_DISASTER_END}上陸！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 台風被害
def log_typhoon_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は{TAG_DISASTER_START}台風{TAG_DISASTER_END}で飛ばされました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、海
def log_meteo_sea(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、山ないし採掘場
def log_meteo_mountain(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下、{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は消し飛びました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、海底基地
def log_meteo_seabase(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下、{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は崩壊しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、怪獣
def log_meteo_monster(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}がいた{link}の{coordinates}地点に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下、陸地は{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}もろとも水没しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、浅瀬
def log_meteo_shallow(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}の{coordinates}地点に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下、海底がえぐられました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 隕石、その他
def log_meteo_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}の{coordinates}地点の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}に{TAG_DISASTER_START}隕石{TAG_DISASTER_END}が落下、{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は水没しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 巨大隕石が落下
def log_huge_meteo(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}地点に{TAG_DISASTER_START}巨大隕石{TAG_DISASTER_END}が落下！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 噴火発生
def log_eruption(turn, island_id, island_name, coordinates):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}地点で{TAG_DISASTER_START}火山{TAG_DISASTER_END}{TAG_QUANTITY_START}が噴火、山{TAG_QUANTITY_END}が出来ました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 噴火、海・海底基地が浅瀬に
def log_eruption_shallow(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}地点の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は、{TAG_DISASTER_START}噴火{TAG_DISASTER_END}の影響で海底が隆起、浅瀬になりました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 噴火、浅瀬が荒地に
def log_eruption_uplift(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}地点の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は、{TAG_DISASTER_START}噴火{TAG_DISASTER_END}の影響で陸地になりました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 噴火、その他の地形
def log_eruption_damage(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}地点の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は、{TAG_DISASTER_START}噴火{TAG_DISASTER_END}の影響で壊滅しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 地盤沈下発生
def log_falldown(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}で{TAG_DISASTER_START}地盤沈下{TAG_DISASTER_END}が発生しました！！'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 地盤沈下被害
def log_falldown_land(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は海の中へ沈みました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、被害中心点
def log_widedamage_center(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は跡形もなくなりました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、水没
def log_widedamage_sea(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は{TAG_QUANTITY_START}水没{TAG_QUANTITY_END}しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、海底基地壊滅
def log_widedamage_seabase(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は跡形もなくなりました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、荒地
def log_widedamage_arechi(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は一瞬にして{TAG_QUANTITY_START}荒地{TAG_QUANTITY_END}と化しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、怪獣水没
def log_widedamage_monster_sea(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の陸地は{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}もろとも{TAG_QUANTITY_START}水没{TAG_QUANTITY_END}しました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 広域被害ルーチン（巨大隕石・記念碑の落下、防衛施設自爆）、怪獣が荒地
def log_widedamage_monster_arechi(turn, island_id, island_name, coordinates, lName):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}{coordinates}の{TAG_QUANTITY_START}{lName}{TAG_QUANTITY_END}は消し飛びました。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

#==================================================
# その他ログ
#==================================================
# 難民流入
def log_boat_people(turn, island_id, island_name, nPeople):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f"{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}にどこからともなく{TAG_QUANTITY_START}{nPeople}{UNIT_POPULATION}{TAG_QUANTITY_END}の難民が漂着しました。{link}は快く受け入れたようです。"

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 島の放棄
def log_giveup(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    # 放棄されているはずなのでリンクは張らない
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}{island_name}{TAG_QUANTITY_END}は{TAG_COMNAME_START}放棄{TAG_COMNAME_END}され、{TAG_QUANTITY_START}無人{TAG_QUANTITY_END}になりました。'
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}{island_name}{TAG_QUANTITY_END}、放棄され{TAG_QUANTITY_START}無人{TAG_QUANTITY_END}となる。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # History オブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )

# 無人化
def log_dead(turn, island_id, island_name):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    # 放棄されているはずなのでリンクは張らない
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}{island_name}{TAG_QUANTITY_END}から人がいなくなり、{TAG_QUANTITY_START}無人{TAG_QUANTITY_END}になりました。'
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{TAG_QUANTITY_START}{island_name}{TAG_QUANTITY_END}、人がいなくなり{TAG_QUANTITY_START}無人{TAG_QUANTITY_END}となる。'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # History オブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )

# 島の発見
def log_discover(turn, island_id, island_name):
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}が{TAG_QUANTITY_START}発見{TAG_QUANTITY_END}される。'

    # History オブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )

# 名前の変更
def log_change_name(turn, island_id, island_old_name, island_new_name):
    # メッセージを生成
    link1 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_old_name}</a>'
    link2 = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_new_name}</a>'
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link1}、名称を{link2}に変更する。'

    # History オブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )

# オーナー名の変更
def log_change_owner(turn, island_id, island_name, island_new_owner):
    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}、所有者を{TAG_QUANTITY_START}{island_new_owner}{TAG_QUANTITY_END}に変更する。'

    # History オブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )

# 収入フェイズ
def log_income(turn, island_id, island_name, money_income, food_income):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}　今期の食料生産：{TAG_QUANTITY_START}{food_income}{UNIT_FOOD}{TAG_QUANTITY_END}、今期の資金収入：{TAG_QUANTITY_START}{money_income}{UNIT_MONEY}{TAG_QUANTITY_END}'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

# 受賞
def log_prize(turn, island_id, island_name, prize):
    island = get_object_or_404(Island, id=island_id)

    # メッセージを生成
    link = f'<a href="{SERVER_ADDRESS}/island/{island_id}">{island_name}</a>'
    message = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}が{TAG_QUANTITY_START}{prize}{TAG_QUANTITY_END}を受賞しました。'

    # 発見の記録を生成
    history = f'{TAG_NUMBER_START}ターン{turn}{TAG_NUMBER_END}：{link}、{TAG_QUANTITY_START}{prize}{TAG_QUANTITY_END}を受賞'

    # Log オブジェクトを作成し保存
    Log.objects.create(
        island=island,
        turn=turn,
        message=message
    )

    # Historyオブジェクトを作成し保存
    History.objects.create(
        turn=turn,
        message=history
    )