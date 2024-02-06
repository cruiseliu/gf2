from common import *
from format_skills import format_skill_upgrade_desc

attrs = {
    'pow': '攻击',
    'shieldArmor': '防御',
    'maxHp': '生命',
    'powPercent': '攻击加成',
    'shieldArmorPercent': '防御加成',
    'maxHpPercent': '生命加成',
    'crit': '暴击',
    'critMult': '暴击伤害',
}

def main():

    for doll in Tables.GunData:
        #if doll['name'] != '闪电':
        #    continue
        print()
        print(doll['name'])

        doll_name = doll['name']
        rank = doll['rank']

        doll_id = doll['id']
        get_talents(doll_id)

        Path('wiki').mkdir(parents=True, exist_ok=True)
        Path(f'wiki/{doll_name}-talents.wiki').write_text(text)

def build_talent(key_id: int | None = None, prop_id: int | None = None) -> dict:
    talent = {}

    if key_id:
        key = Tables.TalentKeyData[key_id]
        talent['name'] = key['keyName']
        talent['icon'] = Tables.ItemData[key_id]['icon']
        skill_id = key['battleSkillId']
        if skill_id:
            talent['desc'] = Tables.BattleSkillDisplayData[skill_id]['description']

        if not prop_id and key['propertyId']:
            prop_id = key['propertyId']

    if prop_id:
        stats = dict(Tables.PropertyData[prop_id])
        stats.pop('id')
        ordered_stats = {}
        for k in attrs.keys():
            v = stats.pop(k)
            if v:
                ordered_stats[k] = v
        assert not any(stats.values()), stats
        talent['stats'] = ordered_stats

    return talent

def get_talents(doll_id: int) -> tuple[list, list, dict]:
    talents_data = Tables.SquadTalentGunData[doll_id]

    tree_ids = [int(x) for x in talents_data['traverseSquadTalentTreeId']]
    tree_data = [Tables.SquadTalentTreeData[tid] for tid in tree_ids]

    node_ids = []
    for node_data in tree_data:
        node_ids += [int(x) for x in node_data['openPoijnt']]

    nodes = [Tables.SquadTalentGroupData[str(nid)] for nid in node_ids]

    stat_nodes = []
    skill_nodes = []
    for node in nodes:
        gene_id = int(node['traverseTalentEffectGeneGroup'][0])
        gene = Tables.GroupTalentEffectGeneData[gene_id]
        if gene['itemId']:
            talent = build_talent(key_id=gene['itemId'])
            skill_nodes.append(talent)
        else:
            talent = build_talent(prop_id=gene['propertyId'])
            stat_nodes.append(talent)

    final_node = build_talent(key_id=talents_data['fullyActiveItemId'])

    return stat_nodes, skill_nodes, final_node

def format_talents(stat_nodes, skill_nodes, final_node):
    lines = []

    rank = Tables.GunData[doll_id]['rank']
    line = f'|rank={rank}'
    lines.append(line)
    icon = skill_nodes[0]['icon'].removeprefix('Skill_Chrtalent_').removesuffix('01')
    line = f'|icon={icon}'
    lines.append(line)

    for i, node in enumerate(stat_nodes):
        node_args = {}
        for j, stat in enumerate(node['stats'].items()):
            k, v = stat
            node_args[f'k{i + 1}{j + 1}'] = attrs[k]
            node_args[f'v{i + 1}{j + 1}'] = format_stat_value(k, v)
        line = ''.join(f'|{k}={v}' for k, v in node_args.items())
        lines.append(line)

    for i, node in enumerate(skill_nodes):
        node_args = {}
        node_args[f'name{i + 1}'] = node['name'].removeprefix('固键·')
        node_args[f'skill{i + 1}'] = format_skill_upgrade_desc(node['desc'])
        line = ''.join(f'|{k}={v}' for k, v in node_args.items())
        lines.append(line)

    name = final_node['name'].removeprefix('共键·')
    k, v = next(iter(final_node['stats'].items()))
    key = attrs[k]
    value = format_stat_value(k, v)
    skill = format_skill_upgrade_desc(final_node['desc'])
    line = f'|name7={name}'
    lines.append(line)
    line = f'|k7={key}|v7={value}'
    lines.append(line)
    line = f'|skill7={skill}'
    lines.append(line)

    text = '==心智螺旋==\n{{talents\n' + '\n'.join(lines) + '\n}}\n'
    return text

def format_stat_value(k, v):
    if k.endswith('Percent') or k in ['crit', 'critMult']:
        return f'{v // 10}.{v % 10}%'
    else:
        return str(v)

if __name__ == '__main__':
    main()
