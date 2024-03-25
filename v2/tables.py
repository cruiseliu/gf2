import json
from pathlib import Path

import proto

import config
import declarations

def decode_tables(files: list[Path] | None = None) -> None:
    print('Decoding tables...')

    if files is None:
        table_dir = Path(config.game_data_dir, 'Table')
        files = list(table_dir.iterdir())

    for output_dir in config.table_output_dirs:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    string_path = Path(config.game_data_dir, 'Table/LangPackageTableCnData.bytes')
    string_table = decode_table(string_path, strings=None)
    strings = {int(s['id']): s['content'] for s in string_table}

    for file in files:
        if file.parent.name == 'Table':
            if file.stem == 'LangPackageTableCnData':
                continue
            if file.suffix == '.bytes':
                decode_table(file, strings)
            else:
                print('SKIP', file.name)

def decode_table(path: Path, strings: dict[int, str] | None) -> dict | None:
    table_name = path.stem
    data = path.read_bytes()
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

    first_obj = table_obj['data'][0]
    n = len(table_obj['data'])
    primary_key = next(iter(first_obj.keys()))
    key_used = {key: bool(value) or n <= 1 for key, value in first_obj.items()}

    for msg, obj in zip(table_msg.data, table_obj['data']):
        for key in obj.keys():
            if not key_used[key] and obj[key] != first_obj[key]:
                key_used[key] = True
            field = getattr(msg, key)
            if isinstance(field, declarations.LanguageStringData) and strings is not None:
                obj[key] = strings[int(field.id)]
            if isinstance(field, declarations.KvSortUintData):
                # we don't really care the order
                # sort them for easier diff
                obj[key] = dict(sorted(zip(field.key, field.value)))
            if type(field).__name__ == 'ScalarMapContainer':
                if field:
                    k0 = next(iter(field.keys()))
                    if isinstance(k0, int):
                        obj[key] = {int(k): v for k, v in obj[key].items()}
                    obj[key] = dict(sorted(field.items()))

    unused_keys = [key for key, used in key_used.items() if not used and key != primary_key]
    if unused_keys:
        for obj in table_obj['data']:
            for key in unused_keys:
                obj.pop(key)

    if isinstance(table_obj['data'][0][primary_key], (int, str)):
        table_obj['data'] = sorted(table_obj['data'], key=(lambda obj: obj[primary_key]))

    s = json.dumps(table_obj, indent='\t', ensure_ascii=False)
    for output_dir in config.table_output_dirs:
        path = Path(output_dir, f'{table_name}.json')
        path.write_text(s)

    print('    ' + table_name)
    return table_obj['data']

if __name__ == '__main__':
    config.table_output_dirs = [Path(__file__).parents[1] / 'tables']
    #config.table_output_dirs = [config.table_output_dirs[0]]
    decode_tables()
