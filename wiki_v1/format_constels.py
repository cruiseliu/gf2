from common import *
from format_skills import format_skill_upgrade_desc

def main():
    for doll in Tables.GunData:
        print()
        print(doll['name'])
        print()

        doll_id = doll['id']

        constel_ids = Tables.GunGradeByGradeData[doll_id]['id']
        constels = [Tables.GunGradeData.get(cid) for cid in constel_ids[1:]]

        print('{{upgrades')
        for i, constel in enumerate(constels):
            skill_id = constel['abbr'][0]
            skill = Tables.BattleSkillDisplayData[skill_id]
            name = skill['name']
            level = skill['level']
            effect = format_skill_upgrade_desc(skill['upgradeDescription'])
            print(f'|skill{i + 1}={name}|level{i + 1}={level}')
            print(f'|desc{i + 1}={effect}')
            #print(name, level, effect)
            #formatted_constels.append({
            #    'name': '椎体·' + ('一二三四五六')[i],
            #    'effect': skill['upgradeDescription'],
            #    'skill_name': skill['name'],
            #})
        print('}}')
        #constels = formatted_constels

main()
