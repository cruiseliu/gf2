from __future__ import annotations

from common import *

max_level = 60

Property: TypeAlias = dict[str, int]

class Stats(TypedDict):
    atk: int
    atk_base: int
    atk_up: int

    dfn: int
    dfn_base: int
    dfn_up: int

    hp: int
    hp_base: int
    hp_up: int

    crit: int
    crit_dmg: int

    move: int
    shield: int


def get_doll_stats(doll: int | dict, level: int = max_level) -> Stats:
    prop = _get_doll_prop(doll, level)
    return _prop_to_stats(prop)


def _get_doll_prop(doll: int | dict, level: int) -> Property:
    doll_id, doll = _find_doll(doll)
    base_prop = Tables.PropertyData[doll['propertyId']]
    level_prop_id = Tables.GunLevelExpData[level]['propertyId']
    return _apply_level(base_prop, level_prop_id)

def _apply_level(base_prop: Property, level_prop: int | Property) -> Property:
    if isinstance(level_prop, int):
        level_prop = Tables.PropertyData[level_prop]
    prop = {}
    for key in base_prop.keys():
        if key != 'id':
            prop[key] = math.ceil(base_prop[key] * level_prop[key] / 1000)
    return prop


def _find_doll(doll_or_id: int | dict) -> tuple[int, dict]:
    if isinstance(doll_or_id, int):
        doll_id = doll_or_id
    else:
        doll_id = doll_or_id['id']
    return doll_id, Tables.GunData[doll_id]

def _prop_to_stats(prop: Property) -> Stats:
    return {
        'atk': math.ceil(prop['pow'] * (1 + prop['powPercent'] / 1000)),
        'atk_base': prop['pow'],
        'atk_up': prop['powPercent'],

        'dfn': math.ceil(prop['shieldArmor'] * (1 + prop['shieldArmorPercent'] / 1000)),
        'dfn_base': prop['shieldArmor'],
        'dfn_up': prop['shieldArmorPercent'],

        'hp': math.ceil(prop['maxHp'] * (1 + prop['maxHpPercent'] / 1000)),
        'hp_base': prop['maxHp'],
        'hp_up': prop['maxHpPercent'],

        'crit': prop['crit'],
        'crit_dmg': prop['critMult'],

        'move': prop['maxAp'] // 100,
        'shield': prop['maxWillValue'],
    }

def _trim_prop(prop: dict) -> dict:
    return {k: v for k, v in prop.items() if v and k != 'id'}

if __name__ == '__main__':
    pass
