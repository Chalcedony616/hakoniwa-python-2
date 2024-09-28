from game.commands import *

# コマンドの情報に関する辞書
COMMAND_LIST = {
    0: {
        'name' : '資金繰り',
        'turn_expend' : True,
        'function' : com_donothing,
        'cost' : 0
    },
    1: {
        'name' : '整地',
        'turn_expend' : True,
        'function' : com_prepare,
        'cost' : 5
    },
    2: {
        'name' : '地ならし',
        'turn_expend' : False,
        'function' : com_fastprepare,
        'cost' : 100
    },
    3: {
        'name' : '埋め立て',
        'turn_expend' : True,
        'function' : com_reclaim,
        'cost' : 150
    },
    4: {
        'name' : '掘削',
        'turn_expend' : True,
        'function' : com_dig,
        'cost' : 200
    },
    5: {
        'name' : '伐採',
        'turn_expend' : False,
        'function' : com_selltree,
        'cost' : 0
    },
    6: {
        'name' : '植林',
        'turn_expend' : True,
        'function' : com_plant,
        'cost' : 50
    },
    10: {
        'name' : '農場整備',
        'turn_expend' : True,
        'function' : com_farm,
        'cost' : 20
    },
    11: {
        'name' : '工場建設',
        'turn_expend' : True,
        'function' : com_factory,
        'cost' : 100
    },
    12: {
        'name' : '採掘場整備',
        'turn_expend' : True,
        'function' : com_mine,
        'cost' : 300
    },
    20: {
        'name' : 'ミサイル基地建設',
        'turn_expend' : True,
        'function' : com_mbase,
        'cost' : 300
    },
    21: {
        'name' : '防衛施設建設',
        'turn_expend' : True,
        'function' : com_defence,
        'cost' : 1000
    },
    22: {
        'name' : '海底基地建設',
        'turn_expend' : True,
        'function' : com_seabase,
        'cost' : 8000
    },
    23: {
        'name' : 'ハリボテ設置',
        'turn_expend' : True,
        'function' : com_haribote,
        'cost' : 1
    },
    24: {
        'name' : '記念碑建設',
        'turn_expend' : True,
        'function' : com_monument,
        'cost' : 9999
    },
    30: {
        'name' : '食料輸出',
        'turn_expend' : False,
        'function' : com_sellfood,
        'cost' : 100
    },
    31: {
        'name' : '食料輸入',
        'turn_expend' : False,
        'function' : com_buyfood,
        'cost' : 12
    },
    32: {
        'name' : '資金援助',
        'turn_expend' : False,
        'function' : com_moneyaid,
        'cost' : 100
    },
    33: {
        'name' : '食料援助',
        'turn_expend' : False,
        'function' : com_foodaid,
        'cost' : 100
    },
    34: {
        'name' : '誘致活動',
        'turn_expend' : True,
        'function' : com_propaganda,
        'cost' : 1000
    },
    39: {
        'name' : '島の放棄',
        'turn_expend' : True,
        'function' : com_giveup,
        'cost' : 0
    },
    40: {
        'name' : 'ミサイル発射',
        'turn_expend' : True,
        'function' : com_missile,
        'cost' : 20
    },
    41: {
        'name' : 'PPミサイル発射',
        'turn_expend' : True,
        'function' : com_ppmissile,
        'cost' : 50
    },
    42: {
        'name' : 'STミサイル発射',
        'turn_expend' : True,
        'function' : com_stmissile,
        'cost' : 50
    },
    43: {
        'name' : '陸地破壊弾発射',
        'turn_expend' : True,
        'function' : com_ldmissile,
        'cost' : 5
    },
    50: {
        'name' : '怪獣派遣',
        'turn_expend' : True,
        'function' : com_sendmonster,
        'cost' : 3000
    },
    51: {
        'name' : '記念碑発射',
        'turn_expend' : True,
        'function' : com_launchmonument,
        'cost' : 9999
    },
}