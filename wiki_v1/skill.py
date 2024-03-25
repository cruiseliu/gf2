from common import *

range_infinity = 999

class Skill(TypedDict):
    name: str
    icon: str

    tags: list[str]
    ammo_type: str | None
    elem_type: str | None

    desc: str
    flavor: str

    cd: int | None
    cost: int | None
    shield_damage: int | None

    range_image: str
    range_dist: int
    range_area: int


def get_doll_skills(doll: int | dict) -> list[Skill]:
    doll_id, doll = _find_doll(doll)

    upgrade_ids = Tables.GunGradeByGradeData[doll_id]['id']
    upgrade_0 = Tables.GunGradeData[upgrade_ids[0]]
    skill_ids = [doll['skillNormalAttack']] + upgrade_0['abbr']

    skills = [Tables.BattleSkillDisplayData[sid] for sid in skill_ids]

    skills = sorted(skills, key=(lambda skill: (skill['descriptionType'], skill['icon'][-1])))

    return [_get_skill_info(doll, skill['id']) for skill in skills]

def _get_skill_info(doll: int | dict, skill_id: int) -> Skill:
    data = Tables.BattleSkillData[skill_id]
    display = Tables.BattleSkillDisplayData[skill_id]

    name = display['name']
    icon = display['icon']

    tags = display['skillTag'].split(' / ')

    ammo_type = None
    if data['weaponTag']:
        if data['weaponTag'] == 1:
            ammo_id = _get_doll_ammo_id(doll)
        else:
            ammo_id = data['weaponTag']
        ammo_type = Tables.LanguageWeaponElementData[ammo_id]['name']

    elem_type = None
    if data['elementType']:
        elem_type = Tables.LanguageElementData[data['elementTag']]['name']

    desc = display['description']
    flavor = display['descriptionLiterary']

    cd = data['cdTime']
    cost = data['potentialCost']

    shield_damage = None
    for effect in data['result'].split(';'):
        values = effect.split(',')
        if values[0] == '2':
            shield_damage = values[1]
            break

    range_image, range_dist, range_area = _get_range(data, display)

    return {
        'name': name,
        'icon': icon,
        'tags': tags,
        'ammo_type': ammo_type,
        'elem_type': elem_type,
        'desc': desc,
        'flavor': flavor,
        'cd': cd,
        'cost': cost,
        'shield_damage': shield_damage,
        'range_image': range_image,
        'range_dist': range_dist,
        'range_area': range_area,
    }


def _get_range(data: dict, display: dict) -> tuple[str, int, int]:
    range_param = display['rangeDisplayParam'] or data['skillRangeParam']
    shape = display['shapeDisplay'] or data['shape']
    shape_param = display['shapeDisplayParam'] or data['shapeParam']

    dist = 0
    if range_param:
        value = int(range_param.split(',')[0])
        dist = round(value / 100)
    elif data['skillRange'] == 8:
        dist = range_infinity

    area = 0
    if shape_param:
        value = int(shape_param.split(',')[0])
        area = round(value / 100)
    elif shape == 8:
        area = range_infinity

    return '', dist, area

def _get_doll_ammo_id(doll: int | dict) -> int:
    ...
 
def _sort_skill_ids(skill_ids: list[int]):
    skills = [Tables.BattleSkillDisplayData[sid] for sid in skill_ids]
    skills = sorted(skills, key=(lambda skill: (skill['descriptionType'], skill['icon'][-1])))
    return [skill['id'] for skill in skills]


def _find_doll(doll_or_id: int | dict) -> tuple[int, dict]:
    if isinstance(doll_or_id, int):
        doll_id = doll_or_id
    else:
        doll_id = doll_or_id['id']
    return doll_id, Tables.GunData[doll_id]
