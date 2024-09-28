from pytz import timezone as pytz_timezone
from django.conf import settings

# サーバーのアドレス
SERVER_ADDRESS = settings.CORS_ALLOWED_ORIGINS[0]  # 最初のアドレスがReactのアドレスに対応している

# 更新時刻
TURN_TIME = ["00:00:00", "04:00:00", "08:00:00", "12:00:00", "16:00:00", "20:00:00"]

# 日本標準時 (JST)
JST = pytz_timezone('Asia/Tokyo')

# コマンド名に使われるタグ
TAG_COMNAME_START = '<FONT COLOR="#d08000"><B>'
TAG_COMNAME_END = '</B></FONT>'

# 数量その他に使われるボール度タグ
TAG_QUANTITY_START = '<FONT COLOR="#000000"><B>'
TAG_QUANTITY_END = '</B></FONT>'

# 極秘ログ用のタグ
TAG_CONFIDENTIAL_START = '<FONT COLOR="#000000"><B>'
TAG_CONFIDENTIAL_END = '</B></FONT>'

# 災害ログ用のタグ
TAG_DISASTER_START = '<FONT COLOR="#ff0000"><B>'
TAG_DISASTER_END = '</B></FONT>'

# ターン数用のタグ
TAG_NUMBER_START = '<FONT COLOR="#800000"><B>'
TAG_NUMBER_END = '</B></FONT>'

# 単位
UNIT_POPULATION = '00人'
UNIT_MONEY = '億円'
UNIT_FOOD = '00トン'

# 放棄ターン
GIVEUP_ABSENT = 180

# 最大食料
MAX_FOOD_STRAGE  = 10000 # 100万トン
MAX_MONEY_STRAGE = 12000 # 1兆2000億円

# 食料の生産効率：100人当たり100トン
FOOD_PRODUCTIVITY = 1

# 資金の生産効率：100人当たり0.1億円
MONEY_PRODUCTIVITY = 0.1

# 食料消費量：100人当たり20トン
FOOD_REQUIREMENT = 0.2

# 伐採の価格：木100本あたり5億円
TREE_VALUE = 5

# 食料の輸出価格：1万トン当たり8億円
FOOD_SELL_PRICE = 0.08

# 食料の輸入価格：1万トン当たり12億円
# 実は食料輸入コマンド中ではcostで処理しているので、この変数は使ってない
FOOD_BUY_PRICE = 0.12

# 各職場に関する設定
INDUSTRY_SETTING = {
    "FARM_INITIAL"      : 100,  # 農場の初期規模：10000人
    "FARM_EXPANSION"    : 20,   # 農場整備の増設規模：2000人
    "FARM_MAXIMUM"      : 500,  # 農場の最大規模：50000人
    "FACTORY_INITIAL"   : 300,  # 工場の初期規模：30000人
    "FACTORY_EXPANSION" : 100,  # 工場建設の増設規模：10000人
    "FACTORY_MAXIMUM"   : 1000, # 工場の最大規模：100000人
    "MINE_INITIAL"      : 50,   # 採掘場の初期規模：5000人
    "MINE_EXPANSION"    : 50,   # 採掘場整備の増設規模：5000人
    "MINE_MAXIMUM"      : 2000, # 採掘場の最大規模：200000人
}

# 町系に関する設定
POPULATION_SETTING = {
    "POP_TOWN"               : 30,  # 町の基準人口：3000人
    "POP_CITY"               : 100, # 都市の基準人口：10000人
    "MAXPOP_CITY"            : 200, # 都市の最大人口：20000人
    "ADDPOP_TOWN"            : 3,   # 村、町の人口増加：100人～300人
    "ADDPOP_CITY"            : 0,   # 都市の人口増加；0人
    "ADDPOP_PROPAGANDA_TOWN" : 30,  # 誘致活動時の村、町の人口増加：100人～3000人
    "ADDPOP_PROPAGANDA_CITY" : 3,   # 誘致活動時の都市の人口増加：100人～3000人
    "ADDPOP_STARVE"          : -30, # 食料不足時の人口減少；-100人～-3000人
}

# 森の最大本数：20000本
MAXTREE = 200

# 海底油田の収益：1000億円
OILINCOME = 1000

# 海底油田の枯渇確率：1％
PROB_OILEND = 0.01

# 災害に関する設定
DISASTER_SETTING = {
    "PROB_EARTHQUAKE" : 0.005, # 地震：弱体化
    "PROB_TSUNAMI"    : 0.015, # 津波：弱体化
    "PROB_TYHOON"     : 0.020, # 台風：弱体化
    "PROB_METEO"      : 0.010, # 隕石：確率を1.5％→1.0％へ削減
    "PROB_HUGEMETRO"  : 0.002, # 巨大隕石：確率を0.5％→0.2％へ削減
    "PROB_ERUPTION"   : 0.005, # 噴火：確率を1.0％→0.5％へ削減
    "PROB_FIRE"       : 0.010, # 火災：防げるのでそのまま
    "PROB_NEXT_METEO" : 0.500, # 隕石が落ちた時に「次が落ちる」確率
    "FALLDOWN_BORDER" : 90,    # 安全限界の広さ（HEX数）
    "PROB_FALLDOWN"   : 1.000, # その広さを超えた場合の地盤沈下確率
}

PROB_MAIZO = 0.010 # 埋蔵金は災害ではないので独立

# 怪獣に関する設定
MONSTER_SETTING = {
    "MONSTER_BORDER" : [1000, 2500, 4000],           # 人口基準（怪獣レベル1、2、3）
    "MONSTER_LEVEL"  : [1, 4, 6],                    # 出現する怪獣の範囲
    "MONSTER_LIST"   : [70, 75, 71, 72, 78, 76, 73], # 怪獣のリスト
    "MONSTER_BHP"    : [1, 1, 3, 2, 1, 4, 5],        # 怪獣の基礎 HP
    "MONSTER_DHP"    : [2, 2, 2, 2, 0, 2, 2],        # 怪獣の HPの幅
    "MONSTER_WEIGHT" : [5, 5, 6, 3, 1, 5, 5],        # 出現確率の重み付け（独自設定）
    "PROB_MONSTER"   : 0.0003,                       # 単位面積当たりの出現率
    "ARTIFICIAL_MONSTER_HP" : 2                      # メカいのらの体力
}

# 賞に関する設定
PRIZE_SETTING = {
    "PROSPERITY_BORDER" : [3000, 5000, 10000],                # 繁栄賞基準人口
    "PROSPERITY_NAME"   : ["繁栄賞", "超繁栄賞", "究極繁栄賞"], # 賞の名前
    "PEACE_BORDER"      : [200, 500, 800],                    # 平和賞基準難民
    "PEACE_NAME"        : ["平和賞", "超平和賞", "究極平和賞"], # 賞の名前
    "TRAGEDY_BORDER"    : [500, 1000, 2000],                  # 災難賞基準人口減少幅
    "TRAGEDY_NAME"      : ["災難賞", "超災難賞", "究極災難賞"], # 賞の名前
    "TURNPRIZE_NAME"    : "ターン杯",                          # 賞の名前
}