from common import *
from format_skills import get_doll_skills_info
from format_stats import get_doll_stats

def main():
    for doll in sort_dolls():
        #if doll['name'] != '闪电':
        #    continue

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

        print()
        print(doll['name'])
        print()

        print('==角色==')
        print('===信息===')
        print('{{doll_info')
        print('|code=' + doll['code'])
        print('|name=' + doll['name'])
        print('|nickname=')
        print('|class=' + Tables.GunDutyData[doll['duty']]['name'])
        print('|weapon=' + Tables.GunWeaponTypeData[doll['weaponType']]['name'])
        print('|quality=' + str(doll['rank']))
        print('|pool=常驻')
        print('|move=' + str(move))
        print('|range=' + str(range_))
        print('|attack_type=' + types)
        print('|weak_type=' + weak)
        print('|cv_cn=' + char['cvCn'])
        print('|cv_jp=' + char['cvJp'])
        print('|doll_type=' + char['bodyId'])
        print('|weapon_type=' + char['brand'])
        print('|affiliation=' + char['belong'])
        print('|desc=' + char['charInfo'].replace('', ''))
        print('|color=' + char['color'][:6])
        print('}}')

        #desc = char['charInfo']
        #print(desc[-19])
        #print(desc[-18])
        #print(desc[-17])
        #print(desc[-16])

main()
