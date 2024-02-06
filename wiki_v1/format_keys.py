from common import *
from format_skills import format_skill_upgrade_desc
from format_talents import build_talent, format_stat_value

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
    keys = [key for key in Tables.TalentKeyData if key['talentKeyType'] == 2]
    keys = sorted(keys, key=(lambda key: -Tables.ItemData[key['talentKeyId']]['rank']))
    for key in keys:
        key_id = key['talentKeyId']
        data = build_talent(key_id)
        print('|-')
        print('|[[Image:Game:' + data['icon'] + '.png|96px]]')
        print('|' + Tables.ItemData[key_id]['name'])

        stat_keys = []
        stat_values = []
        for k, v in data['stats'].items():
            stat_keys.append(attrs[k])
            stat_values.append(format_stat_value(k, v))
        stat_k = '<br>'.join(stat_keys)
        stat_v = '+' + '<br>+'.join(stat_values)
        print('|{{attr|' + stat_k + '|' + stat_v + '}}')

        if data.get('desc'):
            print('|' + format_skill_upgrade_desc(data['desc']))

        print('|')

if __name__ == '__main__':
    main()
