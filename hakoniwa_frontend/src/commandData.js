const commandData = {
    0: {
        name: '資金繰り',
        turnExpend: true,
        description: '資金繰り',
        description_q: '資金繰り',
        category: 'operation',
        costdescription: '無料'
    },
    1: {
        name: '整地',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で整地`,
        description_q: ({coordinates}) => `(${coordinates})で整地`,
        category: 'development',
        costdescription: '5億円'
    },
    2: {
        name: '地ならし',
        turnExpend: false,
        description: ({coordinates}) => `(${coordinates})で地ならし`,
        description_q: ({coordinates}) => `(${coordinates})で地ならし`,
        category: 'development',
        costdescription: '100億円'
    },
    3: {
        name: '埋め立て',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で埋め立て`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で埋め立て（${quantity}回）`,
        category: 'development',
        costdescription: '150億円'
    },
    4: {
        name: '掘削',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で掘削`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で掘削（数量${quantity}）`,
        category: 'development',
        costdescription: '200億円'
    },
    5: {
        name: '伐採',
        turnExpend: false,
        description: ({coordinates}) => `(${coordinates})で伐採`,
        description_q: ({coordinates}) => `(${coordinates})で伐採`,
        category: 'development',
        costdescription: '無料'
    },
    6: {
        name: '植林',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で植林`,
        description_q: ({coordinates}) => `(${coordinates})で植林`,
        category: 'development',
        costdescription: '50億円'
    },
    10: {
        name: '農場整備',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で農場整備`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で農場整備（${quantity}回）`,
        category: 'construction',
        costdescription: '20億円'
    },
    11: {
        name: '工場建設',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で工場建設`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で工場建設（${quantity}回）`,
        category: 'construction',
        costdescription: '100億円'
    },
    12: {
        name: '採掘場整備',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で採掘場整備`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で採掘場整備（${quantity}回）`,
        category: 'construction',
        costdescription: '300億円'
    },
    20: {
        name: 'ミサイル基地建設',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})でミサイル基地建設`,
        description_q: ({coordinates}) => `(${coordinates})でミサイル基地建設`,
        category: 'construction',
        costdescription: '300億円'
    },
    21: {
        name: '防衛施設建設',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で防衛施設建設`,
        description_q: ({coordinates}) => `(${coordinates})で防衛施設建設`,
        category: 'construction',
        costdescription: '1000億円'
    },
    22: {
        name: '海底基地建設',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で海底基地建設`,
        description_q: ({coordinates}) => `(${coordinates})で海底基地建設`,
        category: 'construction',
        costdescription: '8000億円'
    },
    23: {
        name: 'ハリボテ設置',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})でハリボテ設置`,
        description_q: ({coordinates}) => `(${coordinates})でハリボテ設置`,
        category: 'construction',
        costdescription: '1億円'
    },
    24: {
        name: '記念碑建設',
        turnExpend: true,
        description: ({coordinates}) => `(${coordinates})で記念碑建設（数量0）`,
        description_q: ({coordinates, quantity}) => `(${coordinates})で記念碑建設（数量${quantity}）`,
        category: 'construction',
        costdescription: '9999億円'
    },
    30: {
        name: '食料輸出',
        turnExpend: false,
        description: `食料輸出（100万トン）`,
        description_q: ({quantity}) => `食料輸出（${quantity}万トン）`,
        category: 'operation',
        costdescription: '1万トンあたり8億円'
    },
    31: {
        name: '食料輸入',
        turnExpend: false,
        description: `食料輸入（100万トン）`,
        description_q: ({quantity}) => `食料輸入（${quantity}万トン）`,
        category: 'operation',
        costdescription: '1万トンあたり12億円'
    },
    32: {
        name: '資金援助',
        turnExpend: false,
        description: ({target_island}) => `${target_island}へ資金援助（10000億円）`,
        description_q: ({target_island, quantity}) => `${target_island}へ資金援助（${quantity * 100}億円）`,
        category: 'operation',
        costdescription: '数量×100億円'
    },
    33: {
        name: '食料援助',
        turnExpend: false,
        description: ({target_island}) => `${target_island}へ食料援助（100万トン）`,
        description_q: ({target_island, quantity}) => `${target_island}へ食料援助（${quantity}万トン）`,
        category: 'operation',
        costdescription: '数量×1万トン'
    },
    34: {
        name: '誘致活動',
        turnExpend: true,
        description: `誘致活動`,
        description_q: ({quantity}) => `誘致活動（${quantity}回）`,
        category: 'operation',
        costdescription: '1000億円'
    },
    39: {
        name: '島の放棄',
        turnExpend: true,
        description: `島の放棄`,
        description_q: `島の放棄`,
        category: 'operation',
        costdescription: 'あなたの島のすべて'
    },
    40: {
        name: 'ミサイル発射',
        turnExpend: true,
        description: ({target_island, coordinates}) => `${target_island}(${coordinates})へミサイル発射（無制限）`,
        description_q: ({target_island, coordinates, quantity}) => `${target_island}(${coordinates})へミサイル発射（${quantity}発）`,
        category: 'attack',
        costdescription: '1発20億円'
    },
    41: {
        name: 'PPミサイル発射',
        turnExpend: true,
        description: ({target_island, coordinates}) => `${target_island}(${coordinates})へPPミサイル発射（無制限）`,
        description_q: ({target_island, coordinates, quantity}) => `${target_island}(${coordinates})へPPミサイル発射（${quantity}発）`,
        category: 'attack',
        costdescription: '1発50億円'
    },
    42: {
        name: 'STミサイル発射',
        turnExpend: true,
        description: ({target_island, coordinates}) => `${target_island}(${coordinates})へSTミサイル発射（無制限）`,
        description_q: ({target_island, coordinates, quantity}) => `${target_island}(${coordinates})へSTミサイル発射（${quantity}発）`,
        category: 'attack',
        costdescription: '1発50億円'
    },
    43: {
        name: '陸地破壊弾発射',
        turnExpend: true,
        description: ({target_island, coordinates}) => `${target_island}(${coordinates})へ陸地破壊弾発射（無制限）`,
        description_q: ({target_island, coordinates, quantity}) => `${target_island}(${coordinates})へ陸地破壊弾発射（${quantity}発）`,
        category: 'attack',
        costdescription: '1発100億円'
    },
    50: {
        name: '怪獣派遣',
        turnExpend: true,
        description: ({target_island}) => `${target_island}へ怪獣派遣`,
        description_q: ({target_island}) => `${target_island}へ怪獣派遣`,
        category: 'attack',
        costdescription: '3000億円'
    },
    51: {
        name: '記念碑発射',
        turnExpend: true,
        description: ({coordinates, target_island}) => `(${coordinates})の記念碑を${target_island}へ発射`,
        description_q: ({coordinates, target_island}) => `(${coordinates})の記念碑を${target_island}へ発射`,
        category: 'attack',
        costdescription: '9999億円'
    },
};

export default commandData;
