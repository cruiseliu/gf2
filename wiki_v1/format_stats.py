from common import *
from format_talents import get_talents

max_level = 60

def main():
    for doll in Tables.GunData:
        #print(doll['name'])
        format_doll_stats(doll)

def format_doll_stats(doll):
    level_stats, final_stats = get_doll_stats(doll['id'])

    lines = []
    arg_keys = [
        'weapon',
        'atk', 'atk_base', 'atk_buff',
        'def', 'def_base', 'def_buff',
        'hp', 'hp_base', 'hp_buff',
        'posture',
        'crit',
        'critdmg',
        'move',
    ]
    for i, stats in enumerate(final_stats):
        args = []
        for stat in stats:
            if isinstance(stat, tuple):
                args += stat
            else:
                args.append(stat)
        args = [str(a) for a in args]
        for k, v in zip(arg_keys, args):
            lines.append(f'|{k}{i + 1}={v}')
    table1 = '{{stats_max|\n' + '\n'.join(lines) + '\n}}\n'

    lines = []
    for stats in level_stats:
        stats = [str(s) for s in stats]
        if stats[0] == '增域':
            line = '!' + '!!'.join(stats)
        else:
            line = '|' + '||'.join(stats)
        lines.append(line)
    table2 = '{{stats_level_header}}\n' + '\n|-\n'.join(lines) + '\n|}\n'

    doll_name = doll['name']
    text = table1 + '\n' + table2
    #Path('wiki').mkdir(parents=True, exist_ok=True)
    #Path(f'wiki/{doll_name}-stats.wiki').write_text(text)
    return text

def get_doll_stats(doll_id):
    doll = Tables.GunData[doll_id]

    group = Tables.GunClassByGunClassGroupIdData[doll['gunClass']]
    classes = [Tables.GunClassData[cid] for cid in group['id']]

    base_prop = Tables.PropertyData[doll['propertyId']]
    #print(base_prop)

    break_stats = [0, 0, 0]
    stats = None

    attrs = ['pow', 'shieldArmor', 'maxHp']
    per_level_stats = []

    for level in range(1, max_level + 1):
        prop_id = Tables.GunLevelExpData[level]['propertyId']
        level_prop = Tables.PropertyData[prop_id]

        stats = list(break_stats)

        for i, attr in enumerate(attrs):
            stats[i] += math.ceil(base_prop[attr] * level_prop[attr] / 1000)

        per_level_stats.append([level] + stats)
        #print_attrs(level, stats)

        if level == classes[0]['gunLevelMax']:
            classes = classes[1:]
            if classes:
                break_prop = Tables.PropertyData[classes[0]['propertyId']]
                for i, attr in enumerate(attrs):
                    break_stats[i] += break_prop[attr]
                    stats[i] += break_prop[attr]
                per_level_stats.append(['增域'] + stats)
                #print_attrs('增域', stats)

    doll_prop = dict(base_prop)
    for i, attr in enumerate(attrs):
        doll_prop[attr] = stats[i]

    stat_talents, skill_talents, final_talent = get_talents(doll_id)
    talents = stat_talents + [final_talent]
    for talent in talents:
        for k, v in talent['stats'].items():
            doll_prop[k] += v
    doll_prop['powPercent'] += 120
    doll_prop['shieldArmorPercent'] += 120
    doll_prop['maxHpPercent'] += 120

    weapon_ids = doll['weaponPrivateShow']
    if doll['name'] == '克罗丽科':
        weapon_ids = [11007]

    battle_pass_weapons = {
        1: 10001,
        2: 10002,
        3: 10003,
        4: 10004,
        7: 10005,
        5: 10006,
        6: 10007,
    }
    if doll['rank'] == 4:
        weapon_ids.append(battle_pass_weapons[doll['weaponType']])

    final_stats = []

    weapons = [Tables.GunWeaponData[wid] for wid in weapon_ids]
    weapons = [w for w in weapons if w['rank'] > 3]
    weapons = sorted(weapons, key=(lambda w: w['rank']))

    for weapon in weapons:
        prop = dict(doll_prop)
        weapon_prop = get_weapon_prop(weapon['id'], max_level)
        for k, v in weapon_prop.items():
            prop[k] += v

        final_stats.append([weapon['name']] + format_prop(prop))

    return per_level_stats, final_stats

def get_weapon_prop(weapon_id, level):
    weapon = Tables.GunWeaponData[weapon_id]
    base_prop = Tables.PropertyData[weapon['propertyId']]

    level_id = level * 100 + weapon['rank']
    level_data = Tables.GunWeaponExpData[level_id]
    assert level_data['level'] == level
    assert level_data['rank'] == weapon['rank']
    level_prop = Tables.PropertyData[level_data['propertyId']]

    prop = {}
    for k in base_prop.keys():
        if k != 'id':
            prop[k] = math.ceil(base_prop[k] * level_prop[k] / 1000)
    return prop

def format_prop(prop):
    return [
        calc_percent(prop, 'pow'),
        calc_percent(prop, 'shieldArmor'),
        calc_percent(prop, 'maxHp'),
        prop['maxWillValue'],
        format_percent(prop['crit']),
        format_percent(prop['critMult']),
        prop['maxAp'] // 100,
    ]

def calc_percent(prop, attr):
    return (
        math.ceil(prop[attr] * (1 + prop[attr + 'Percent'] / 1000)),
        prop[attr],
        format_percent(prop[attr + 'Percent']),
    )

def format_percent(x):
    return f'{x // 10}.{x % 10}'.removesuffix('.0') + '%'


def strip_dict(d):
    return {k: v for k, v in d.items() if v}

def main2():
    for weapon in Tables.GunWeaponData:
        if weapon['name'] != '金石奏':
            continue
        prop = get_weapon_stats(weapon['id'], max_level)
        print(strip_dict(prop))

#        base_prop = Tables.PropertyData[doll['propertyId']]
#        #print(base_prop)
#
#        break_stats = [0, 0, 0]
#        stats = None
#
#        attrs = ['pow', 'shieldArmor', 'maxHp']
#
#        for level in range(1, 61):
#            prop_id = Tables.GunLevelExpData[level]['propertyId']
#            level_prop = Tables.PropertyData[prop_id]
#
#            stats = list(break_stats)
#
#            for i, attr in enumerate(attrs):
#                stats[i] += math.ceil(base_prop[attr] * level_prop[attr] / 1000)


def print_attrs(level, stats):
    #print('|-')
    line = f'|{level}||{stats[0]}||{stats[1]}||{stats[2]}'
    if level == '增域':
        line = line.replace('|', '!')
    #print(line)

if __name__ == '__main__':
    main()
