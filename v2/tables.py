import json
from pathlib import Path

import proto

import config
import declarations

def decode_tables(files: list[Path] | None = None) -> None:
    print('Decoding tables...')
    if files is None:
        abs_files = Path(config.game_data_dir, 'Table').iterdir()
        files = [f.relative_to(config.game_data_dir) for f in abs_files]

    Path(config.tables_output_dir).mkdir(parents=True, exist_ok=True)

    string_table = decode_table('LangPackageTableCnData', strings=None)
    strings = {int(s['id']): s['content'] for s in string_table}

    for file in files:
        if file.parts[0] != 'Table':
            continue
        elif file.suffix != '.bytes':
            print('SKIP', file.name)
        elif file.stem != 'LangPackageTableCnData':
            decode_table(file.stem, strings)

def decode_table(table_name: str, strings: dict[int, str] | None) -> dict | None:
    from_path = Path(config.game_data_dir, f'Table/{table_name}.bytes')
    to_path = Path(config.tables_output_dir, f'{table_name}.json')

    data = from_path.read_bytes()
    header_len = int.from_bytes(data[:4], 'little')

    try:
        DataClass = getattr(declarations, table_name)
    except AttributeError:
        return None

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
        print('[FAIL]', table_name)
        return None

    table_obj = DataTableClass.to_dict(table_msg)

    primary_key = None
    for msg, obj in zip(table_msg.data, table_obj['data']):
        keys = list(obj.keys())
        if primary_key is None:
            primary_key = keys[0]
        for key in keys:
            field = getattr(msg, key)
            if isinstance(field, declarations.LanguageStringData) and strings is not None:
                obj[key] = strings[int(field.id)]
            if isinstance(field, declarations.KvSortUintData):
                # we don't really care the order
                # sort them for easier diff
                obj[key] = dict(sorted(zip(field.key, field.value)))

    if isinstance(table_obj['data'][0][primary_key], (int, str)):
        table_obj['data'] = sorted(table_obj['data'], key=(lambda obj: obj[primary_key]))

    s = json.dumps(table_obj, indent=4, ensure_ascii=False)
    to_path.write_text(s)

    print('    ' + table_name)
    return table_obj['data']

if __name__ == '__main__':
    decode_tables()