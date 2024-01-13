import json
from pathlib import Path

import proto

import declarations

tables_path = 'D:/Program Files/GF2Exilium/GF2 Game/GF2_Exilium_Data/LocalCache/Data/Table'
output_path = Path(__file__).parents[1] / 'tables'
fail_log_path = Path(__file__).parents[1] / 'fail-tables.txt'

fail_log_file = open(fail_log_path, 'w')

def main():
    Path(output_path).mkdir(parents=True, exist_ok=True)

    string_table = decode_table('LangPackageTableCnData', strings=None)
    strings = {int(s['id']): s['content'] for s in string_table}

    for file in Path(tables_path).iterdir():
        if file.suffix != '.bytes':
            print('SKIP', file.name)
        elif file.stem != 'LangPackageTableCnData':
            decode_table(file.stem, strings)

def decode_table(table_name: str, strings: dict[int, str] | None) -> dict | None:
    from_path = Path(tables_path) / f'{table_name}.bytes'
    to_path = Path(output_path) / f'{table_name}.json'

    data = from_path.read_bytes()
    header_len = int.from_bytes(data[:4], 'little')

    DataClass = getattr(declarations, table_name)
    DataTableClass = type(
        table_name + 'Table',
        (proto.Message,),
        {'data': proto.RepeatedField(DataClass, number=1)}
    )

    table_msg = None
    for skip_len in [1, 2, 3, 4]:
        try:
            msg = DataTableClass.deserialize(data[(header_len + skip_len):])
            if msg.data:
                table_msg = msg
                break
        except Exception:
            pass

    if table_msg is None:
        print('FAIL', table_name)
        fail_log_file.write(table_name + '\n')
        return None

    table_obj = DataTableClass.to_dict(table_msg)

    if strings:
        for msg, obj in zip(table_msg.data, table_obj['data']):
            for key in obj.keys():
                field = getattr(msg, key)
                if isinstance(field, declarations.LanguageStringData):
                    obj[key] = strings[int(field.id)]
                if isinstance(field, declarations.KvSortUintData):
                    obj[key] = {k: v for k, v in zip(field.key, field.value)}

    s = json.dumps(table_obj, indent=4, ensure_ascii=False)
    to_path.write_text(s)

    return table_obj['data']

main()
