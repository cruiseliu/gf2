from common import *

def main():
    for doll in Tables.GunData:
        print(doll['id'], doll['name'])
        format_doll_skill_details(doll['name'])

def format_doll_skill_details(doll: str | int) -> str:
    skills, constels, talents = get_doll_skills_info(doll)

    details = []
    for skill in skills:
        details.append(format_skill_detail(skill, constels, talents))

    text = '===详细说明===\n\n' + '\n\n'.join(details) + '\n'
    Path('wiki').mkdir(parents=True, exist_ok=True)
    Path(f'wiki/{doll}-skill-detail.wiki').write_text(text)
    return text

def format_skill_detail(skill: dict, constels: list[dict], talents: list[dict]) -> str:
    args = {}
    args['name'] = skill['name']
    args['icon'] = skill['icon']
    args['tag'] = skill['tag']

    types = [skill['ammo_type'], skill['elem_type']]
    types = [t for t in types if t is not None]
    for i, type_ in enumerate(types):
        args[f'type_{i + 1}'] = type_

    args['cost'] = skill['cost']
    args['break'] = skill['break']
    args['desc'] = format_skill_desc(skill['desc'])
    args['flavor'] = skill['flavor']
    args['range_image'] = skill['range_image']
    args['range_dist'] = skill['range_dist']
    args['range_area'] = skill['range_area']

    upgrades = []
    for upgrade in (constels + talents):
        if upgrade['skill_name'] == skill['name']:
            upgrades.append({
                'name': upgrade['name'],
                'desc': format_skill_upgrade_desc(upgrade['effect']),
            })
    for i, upgrade in enumerate(upgrades):
        args[f'upgrade_name_{i + 1}'] = upgrade['name']
        args[f'upgrade_desc_{i + 1}'] = upgrade['desc']

    lines = ['{{skill_detail']
    for key, value in args.items():
        if value is not None:
            lines.append(f'|{key}={value}')
    lines.append('}}')
    return '\n'.join(lines)

def get_doll_skills_info(name_or_id: int | str) -> tuple[list[dict], list[dict], list[dict]]:
    doll = None
    for doll_ in Tables.GunData:
        if str(name_or_id) in [doll_['name'], str(doll_['id'])]:
            doll = doll_
    assert doll

    doll_id = doll['id']

    constel_ids = Tables.GunGradeByGradeData[doll_id]['id']
    constels = [Tables.GunGradeData.get(cid) for cid in constel_ids]

    if doll['name'] == '纳美西丝':
        skill_ids = [doll['skillNormalAttack']] + [10080401, 10080501, 10080701, 10080801]
    else:
        skill_ids = [doll['skillNormalAttack']] + constels[0]['abbr']
    skills = [get_skill_info(doll_id, sid) for sid in skill_ids]
    skills = [skills[0]] + sorted(skills[1:], key=(lambda skill: skill['icon'][-1]))

    formatted_constels = []
    for i, constel in enumerate(constels[1:]):
        skill_id = constel['abbr'][0]
        skill = Tables.BattleSkillDisplayData[skill_id]
        formatted_constels.append({
            'name': '椎体·' + ('一二三四五六')[i],
            'effect': skill['upgradeDescription'],
            'skill_name': skill['name'],
        })
    constels = formatted_constels

    talents = []
    for key in Tables.TalentKeyData:
        if key['gunId'] != [doll_id]:
            continue
        talents.append({
            'name': key['keyName'],
            'effect': Tables.BattleSkillDisplayData[key['battleSkillId']]['description'],
            'skill_name': get_replaced_skill_name(key['replaceId']),
        })

    return skills, constels, talents

def get_replaced_skill_name(replace_id: int) -> str | None:
    if not replace_id:
        return None
    replace = Tables.ReplaceSkillData[replace_id]
    for key, value in replace.items():
        if isinstance(value, list):
            for skill_id in value:
                return Tables.BattleSkillDisplayData[skill_id]['name']
    return None

def get_skill_info(doll_id, skill_id: int) -> list[str]:
    data = Tables.BattleSkillData[skill_id]
    display = Tables.BattleSkillDisplayData[skill_id]

    desc = display['description']

    cost = None
    if data['cdTime']:
        cost = '冷却回合：' + str(data['cdTime'])
    if data['potentialCost']:
        cost = '导染消耗：' + str(data['potentialCost'])

    break_damage = None
    for effect in data['result'].split(';'):
        values = effect.split(',')
        if values[0] == '2':
            break_damage = '稳态伤害：' + values[1]

    range_param = display['rangeDisplayParam'] or data['skillRangeParam']
    shape = display['shapeDisplay'] or data['shape']
    shape_param = display['shapeDisplayParam'] or data['shapeParam']

    dist = ''
    if range_param:
        value = int(range_param.split(',')[0])
        dist = str(round(value / 100))
    elif data['skillRange'] == 8:
        dist = 'inf'

    area = ''
    if shape_param:
        value = int(shape_param.split(',')[0])
        area = str(round(value / 100))
        if shape == 2:
            area = f'{area}x{area}'
        if shape == 7:
            area = '--'
    elif shape == 8:
        area = 'inf'

    special_skills = [
        #'领域压制',
        '多重编译',
    ]

    if display['name'] in special_skills:
        range_image = 'range-' + display['name']
    elif not area:
        range_image = 'range-' + (dist or '0')
    elif shape == 5:
        range_image = 'range-' + area + 'l'
    elif shape == 7:
        range_image = 'range-s' + shape_param
    else:
        range_image = 'range-' + (dist or '0') + '-' + area

    if not dist:
        dist = '自身'
    dist = dist.replace('inf', '全图')
    if not area:
        area = '目标'
    area = area.replace('x', ' × ')
    area = area.replace('inf', '全图')

    ammo_type = None
    if data['weaponTag']:
        bullet = data['weaponTag']
        if bullet == 1:
            weapon = Tables.GunData[doll_id]['weaponType']
            weapon_to_bullet = {
                1: 2,
                2: 2,
                3: 8,
                4: 4,
                5: 8,
                6: 32,
                7: 16,
            }
            bullet = weapon_to_bullet[weapon]
        bullet_name = {
            2: '轻型弹',
            4: '中型弹',
            8: '重型弹',
            16: '近战',
            32: '霰弹',
        }
        ammo_type = bullet_name[bullet]

    elem_type = None
    if data['elementTag']:
        element_name = {
            1: '燃烧',
            4: '酸蚀',
            5: '浊刻',
        }
        elem_type = element_name[data['elementTag']]

    return {
        'icon': display['icon'],
        'name': display['name'],
        'desc': desc,
        'cost': cost,
        'break': break_damage,
        'tag': display['skillTag'],
        'flavor': display['descriptionLiterary'],
        'range_image': range_image,
        'range_dist': dist,
        'range_area': area,
        'ammo_type': ammo_type,
        'elem_type': elem_type,
    }

def get_skill_upgrade_info(skill_id: int) -> str:
    display = Tables.BattleSkillDisplayData[skill_id]
    return format_skill_desc(display['upgradeDescription'])

def format_skill_desc(desc: str) -> str:
    buffs = load_table('BattleBuffPerformData', key='name')
    special_buffs = [
        '行动支援',
        '反击',
        '暗流',
        '支援增幅I',
        '支援增幅II',
        '伏击',
        '临机支援',
    ]
    for keyword, pattern in find_keywords(desc).items():
        if keyword in buffs or keyword in special_buffs:
            desc = desc.replace(pattern, '{{' + keyword + '}}')
    return replace_colors(desc)

def format_skill_upgrade_desc(desc: str) -> str:
    lines = desc.split('\n')
    for line in lines[1:]:
        assert line.startswith('<color=#3487e0>'), line
    return format_skill_desc(lines[0])

if __name__ == '__main__':
    main()
