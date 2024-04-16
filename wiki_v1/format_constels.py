from common import *
from format_skills import format_skill_upgrade_desc

def main():
    for doll in sort_dolls():
        format_constels(doll)

def format_constels(doll):
    doll_id = doll['id']

    constel_ids = Tables.GunGradeByGradeData[doll_id]['id']
    constels = [Tables.GunGradeData.get(cid) for cid in constel_ids[1:]]

    lines = []
    lines.append('{{upgrades')
    for i, constel in enumerate(constels):
        skill_id = constel['abbr'][0]
        skill = Tables.BattleSkillDisplayData[skill_id]
        name = skill['name']
        level = skill['level']
        effect = format_skill_upgrade_desc(skill['upgradeDescription'])
        lines.append(f'|skill{i + 1}={name}|level{i + 1}={level}')
        lines.append(f'|desc{i + 1}={effect}')
        #print(name, level, effect)
        #formatted_constels.append({
        #    'name': '椎体·' + ('一二三四五六')[i],
        #    'effect': skill['upgradeDescription'],
        #    'skill_name': skill['name'],
        #})
    lines.append('}}')
    #constels = formatted_constels
    return lines

main()
