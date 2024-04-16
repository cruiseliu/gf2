from common import *
from format_skills import get_doll_skills_info
from format_stats import get_doll_stats

def main():
    for doll in sort_dolls():
        if doll['name'] != '闪电':
            continue

def format_doll_info(doll):
    doll_id = doll['id']
    char = Tables.GunCharacterData[doll['characterId']]

    level_stats, final_stats = get_doll_stats(doll_id)
    move = final_stats[0][-1]

    skills, constels, talents = get_doll_skills_info(doll_id)
    range_ = skills[0]['range_dist']

    ammo_types = set()
    elem_types = set()
    for skill in skills:
        ammo_types.add(skill['ammo_type'])
        elem_types.add(skill['elem_type'])
    ammo_types.discard(None)
    elem_types.discard(None)
    types = sorted(ammo_types) + sorted(elem_types)
    types = '{{' + '}}<br>{{'.join(types) + '}}'

    weak_ammo = Tables.WeaponTagData[int(doll['weakWeaponTag'])]['name']
    weak_elem = Tables.LanguageElementData[int(doll['weakTag'])]['name']
    weak = '{{' + weak_ammo + '}}<br>{{' + weak_elem + '}}'

    lines = [
        '{{doll_info',
        '|code=' + doll['code'],
        '|name=' + doll['name'],
        '|nickname=',
        '|class=' + Tables.GunDutyData[doll['duty']]['name'],
        '|weapon=' + Tables.GunWeaponTypeData[doll['weaponType']]['name'],
        '|quality=' + str(doll['rank']),
        '|pool=限定（当期）',
        '|move=' + str(move),
        '|range=' + str(range_),
        '|attack_type=' + types,
        '|weak_type=' + weak,
        '|cv_cn=' + char['cvCn'],
        '|cv_jp=' + char['cvJp'],
        '|doll_type=' + char['bodyId'],
        '|weapon_type=' + char['brand'],
        '|affiliation=' + char['belong'],
        '|desc=' + char['charInfo'].replace('', ''),
        '|color=' + char['color'][:6],
        '}}',
    ]

    return lines

main()
