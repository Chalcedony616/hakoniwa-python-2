// ミサイル基地と海底基地のレベルを算出する関数
const get_missile_base_level = (landvalue) => {
    if (landvalue < 20) return 1;
    if (landvalue < 60) return 2;
    if (landvalue < 120) return 3;
    if (landvalue < 200) return 4;
    return 5;
};

const get_sea_base_level = (landvalue) => {
    if (landvalue < 50) return 1;
    if (landvalue < 200) return 2;
    return 3;
};

// 記念碑のリストを出力する関数
const get_monument_name = (landvalue) => {
    if (landvalue == 1) return '平和記念碑';
    if (landvalue == 2) return '戦いの碑';
    return 'モノリス'
}

const terrainData = {
    0: {
        name: '海',
        imageList: ['/images/sea.gif'],
        touristImage: (landvalue) => terrainData[0].imageList[0],
        developmentImage: (landvalue) => terrainData[0].imageList[0],
        isLand: false,
        touristTooltip: '海',
        developmentTooltip: '海',
    },
    1: {
        name: '浅瀬',
        imageList: ['/images/shallows.gif'],
        touristImage: (landvalue) => terrainData[1].imageList[0],
        developmentImage: (landvalue) => terrainData[1].imageList[0],
        isLand: false,
        touristTooltip: '浅瀬',
        developmentTooltip: '浅瀬',
    },
    2: {
        name: '荒地',
        imageList: ['/images/wastes.gif', '/images/crater.gif'],
        touristImage: (landvalue) => landvalue === 1 ? terrainData[2].imageList[1] : terrainData[2].imageList[0],
        developmentImage: (landvalue) => landvalue === 1 ? terrainData[2].imageList[1] : terrainData[2].imageList[0],
        isLand: true,
        touristTooltip: '荒地',
        developmentTooltip: '荒地',
    },
    3: {
        name: '平地',
        imageList: ['/images/plains.gif'],
        touristImage: (landvalue) => terrainData[3].imageList[0],
        developmentImage: (landvalue) => terrainData[3].imageList[0],
        isLand: true,
        touristTooltip: '平地',
        developmentTooltip: '平地',
    },
    4: {
        name: '森',
        imageList: ['/images/forest.gif'],
        touristImage: (landvalue) => terrainData[4].imageList[0],
        developmentImage: (landvalue) => terrainData[4].imageList[0],
        isLand: true,
        touristTooltip: '森',
        developmentTooltip: (landvalue) => `森　本数：${landvalue * 100}本`,
    },
    5: {
        name: '山',
        imageList: ['/images/mountain.gif'],
        touristImage: (landvalue) => terrainData[5].imageList[0],
        developmentImage: (landvalue) => terrainData[5].imageList[0],
        isLand: true,
        touristTooltip: '山',
        developmentTooltip: '山',
    },
    10: {
        name: '村',
        imageList: ['/images/village.gif'],
        touristImage: (landvalue) => terrainData[10].imageList[0],
        developmentImage: (landvalue) => terrainData[10].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `村　人口：${landvalue * 100}人`,
        developmentTooltip: (landvalue) => `村　人口：${landvalue * 100}人`,
    },
    11: {
        name: '町',
        imageList: ['/images/town.gif'],
        touristImage: (landvalue) => terrainData[11].imageList[0],
        developmentImage: (landvalue) => terrainData[11].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `町　人口：${landvalue * 100}人`,
        developmentTooltip: (landvalue) => `町　人口：${landvalue * 100}人`,
    },
    12: {
        name: '都市',
        imageList: ['/images/city.gif'],
        touristImage: (landvalue) => terrainData[12].imageList[0],
        developmentImage: (landvalue) => terrainData[12].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `都市　人口：${landvalue * 100}人`,
        developmentTooltip: (landvalue) => `都市　人口：${landvalue * 100}人`,
    },
    20: {
        name: '農場',
        imageList: ['/images/farm.gif'],
        touristImage: (landvalue) => terrainData[20].imageList[0],
        developmentImage: (landvalue) => terrainData[20].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `農場：${landvalue * 100}人規模`,
        developmentTooltip: (landvalue) => `農場：${landvalue * 100}人規模`,
    },
    21: {
        name: '工場',
        imageList: ['/images/factory.gif'],
        touristImage: (landvalue) => terrainData[21].imageList[0],
        developmentImage: (landvalue) => terrainData[21].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `工場：${landvalue * 100}人規模`,
        developmentTooltip: (landvalue) => `工場：${landvalue * 100}人規模`,
    },
    22: {
        name: '採掘場',
        imageList: ['/images/mine.gif'],
        touristImage: (landvalue) => terrainData[22].imageList[0],
        developmentImage: (landvalue) => terrainData[22].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `採掘場：${landvalue * 100}人規模`,
        developmentTooltip: (landvalue) => `採掘場：${landvalue * 100}人規模`,
    },
    30: {
        name: 'ミサイル基地',
        imageList: ['/images/forest.gif', '/images/missile.gif'],
        touristImage: (landvalue) => terrainData[30].imageList[0],
        developmentImage: (landvalue) => terrainData[30].imageList[1],
        isLand: true,
        touristTooltip: '森',
        developmentTooltip: (landvalue) => {
            const level = get_missile_base_level(landvalue);
            return `ミサイル基地　レベル：${level}　経験値：${landvalue}`;
        },
    },
    31: {
        name: '防衛施設',
        imageList: ['/images/defense.gif'],
        touristImage: (landvalue) => terrainData[31].imageList[0],
        developmentImage: (landvalue) => terrainData[31].imageList[0],
        isLand: true,
        touristTooltip: '防衛施設',
        developmentTooltip: '防衛施設',
    },
    32: {
        name: 'ハリボテ',
        imageList: ['/images/defense.gif'],
        touristImage: (landvalue) => terrainData[32].imageList[0],
        developmentImage: (landvalue) => terrainData[32].imageList[0],
        isLand: true,
        touristTooltip: '防衛施設',
        developmentTooltip: 'ハリボテ',
    },
    33: {
        name: '海底基地',
        imageList: ['/images/sea.gif', '/images/seamissile.gif'],
        touristImage: (landvalue) => terrainData[33].imageList[0],
        developmentImage: (landvalue) => terrainData[33].imageList[1],
        isLand: true,
        touristTooltip: '海',
        developmentTooltip: (landvalue) => {
            const level = get_sea_base_level(landvalue);
            return `海底基地　レベル：${level}　経験値：${landvalue}`;
        },
    },
    40: {
        name: '海底油田',
        imageList: ['/images/oilfield.gif'],
        touristImage: (landvalue) => terrainData[40].imageList[0],
        developmentImage: (landvalue) => terrainData[40].imageList[0],
        isLand: true,
        touristTooltip: '海底油田',
        developmentTooltip: '海底油田',
    },
    50: {
        name: '記念碑',
        imageList: ['/images/monument0.gif'],
        touristImage: (landvalue) => {
            const image = terrainData[50].imageList[0]
            return image;
        },
        developmentImage: (landvalue) => {
            const image = terrainData[50].imageList[0]
            return image;
        },
        isLand: true,
        touristTooltip: (landvalue) => {
            const tooltip = get_monument_name(landvalue);
            return tooltip;
        },
        developmentTooltip: (landvalue) => {
            const tooltip = get_monument_name(landvalue);
            return tooltip;
        },
    },
    70: {
        name: '怪獣（いのら）',
        imageList: ['/images/monster0.gif'],
        touristImage: (landvalue) => terrainData[70].imageList[0],
        developmentImage: (landvalue) => terrainData[70].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣いのら　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣いのら　体力：${landvalue}`,
    },
    71: {
        name: '怪獣（レッドいのら）',
        imageList: ['/images/monster1.gif'],
        touristImage: (landvalue) => terrainData[71].imageList[0],
        developmentImage: (landvalue) => terrainData[71].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣レッドいのら　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣レッドいのら　体力：${landvalue}`,
    },
    72: {
        name: '怪獣（ダークいのら）',
        imageList: ['/images/monster2.gif'],
        touristImage: (landvalue) => terrainData[72].imageList[0],
        developmentImage: (landvalue) => terrainData[72].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣ダークいのら　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣ダークいのら　体力：${landvalue}`,
    },
    73: {
        name: '怪獣（キングいのら）',
        imageList: ['/images/monster3.gif'],
        touristImage: (landvalue) => terrainData[73].imageList[0],
        developmentImage: (landvalue) => terrainData[73].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣キングいのら　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣キングいのら　体力：${landvalue}`,
    },
    75: {
        name: '怪獣（サンジラ）',
        imageList: ['/images/monster5.gif'],
        touristImage: (landvalue) => terrainData[75].imageList[0],
        developmentImage: (landvalue) => terrainData[75].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣サンジラ　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣サンジラ　体力：${landvalue}`,
    },    
    76: {
        name: '怪獣（クジラ）',
        imageList: ['/images/monster6.gif'],
        touristImage: (landvalue) => terrainData[76].imageList[0],
        developmentImage: (landvalue) => terrainData[76].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣クジラ　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣クジラ　体力：${landvalue}`,
    },
    77: {
        name: '怪獣（メカいのら）',
        imageList: ['/images/monster7.gif'],
        touristImage: (landvalue) => terrainData[77].imageList[0],
        developmentImage: (landvalue) => terrainData[77].imageList[0],
        touristTooltip: (landvalue) => `怪獣メカいのら　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣メカいのら　体力：${landvalue}`,
    },
    78: {
        name: '怪獣（いのらゴースト）',
        imageList: ['/images/monster8.gif'],
        touristImage: (landvalue) => terrainData[78].imageList[0],
        developmentImage: (landvalue) => terrainData[78].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣いのらゴースト　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣いのらゴースト　体力：${landvalue}`,
    },
    79: {
        name: '怪獣（サンジラ）（硬化中）',
        imageList: ['/images/monster4.gif'],
        touristImage: (landvalue) => terrainData[79].imageList[0],
        developmentImage: (landvalue) => terrainData[79].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣サンジラ（硬化）　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣サンジラ（硬化）　体力：${landvalue}`,
    },
    80: {
        name: '怪獣（クジラ）（硬化中）',
        imageList: ['/images/monster4.gif'],
        touristImage: (landvalue) => terrainData[80].imageList[0],
        developmentImage: (landvalue) => terrainData[80].imageList[0],
        isLand: true,
        touristTooltip: (landvalue) => `怪獣クジラ（硬化）　体力：${landvalue}`,
        developmentTooltip: (landvalue) => `怪獣クジラ（硬化）　体力：${landvalue}`,
    },
};

export default terrainData;
