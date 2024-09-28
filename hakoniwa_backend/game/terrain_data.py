# 地形データに関する辞書
TERRAIN_LIST = {
    0: {
        'name' : '海',
        'is_land' : False,
        'preparable' : False,
        'buildable' : False
    },
    1: {
        'name' : '浅瀬',
        'is_land' : False,
        'preparable' : False,
        'buildable' : False
    },
    2: {
        'name' : '荒地',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    3: {
        'name' : '平地',
        'is_land' : True,
        'preparable' : True,
        'buildable' : True
    },
    4: {
        'name' : '森',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    5: {
        'name' : '山',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False
    },
    10: {
        'name' : '村',
        'is_land' : True,
        'preparable' : True,
        'buildable' : True
    },
    11: {
        'name' : '町',
        'is_land' : True,
        'preparable' : True,
        'buildable' : True
    },
    12: {
        'name' : '都市',
        'is_land' : True,
        'preparable' : True,
        'buildable' : True
    },
    20: {
        'name' : '農場',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    21: {
        'name' : '工場',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    22: {
        'name' : '採掘場',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False
    },
    30: {
        'name' : 'ミサイル基地',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    31: {
        'name' : '防衛施設',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    32: {
        'name' : 'ハリボテ',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    33: {
        'name' : '海底基地',
        'is_land' : False,
        'preparable' : False,
        'buildable' : False
    },
    40: {
        'name' : '海底油田',
        'is_land' : False,
        'preparable' : False,
        'buildable' : False
    },
    50: {
        'name' : '記念碑',
        'is_land' : True,
        'preparable' : True,
        'buildable' : False
    },
    70: {
        'name' : '怪獣（いのら）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 10, # 本来は 5
        'value' : 400
    },
    71: {
        'name' : '怪獣（レッドいのら）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 20, # 本来は12
        'value' : 1000
    },
    72: {
        'name' : '怪獣（ダークいのら）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 30, # 本来は15
        'value' : 800
    },
    73: {
        'name' : '怪獣（キングいのら）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 50, # 本来は30
        'value' : 2000
    },
    75: {
        'name' : '怪獣（サンジラ）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 15, # 本来は7
        'value' : 500
    },
    76: {
        'name' : '怪獣（クジラ）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 40, # 本来は20
        'value' : 1500
    },
    77: {
        'name' : '怪獣（メカいのら）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 5, # 本来のまま
        'value' : 0
    },
    78: {
        'name' : '怪獣（いのらゴースト）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False,
        'exp' : 15, # 本来は10
        'value' : 300
    },
    79: {
        'name' : '怪獣（サンジラ）（硬化中）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False
    },
    80: {
        'name' : '怪獣（クジラ）（硬化中）',
        'is_land' : True,
        'preparable' : False,
        'buildable' : False
    },
}