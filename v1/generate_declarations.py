from collections import defaultdict
from pathlib import Path

ce_symbol_path = Path(__file__).parent / 'ce.txt'
declaration_py_path = Path(__file__).parent / 'declarations.py'

nested_types = [
    'GF2.Data.LanguageStringData',
    'GF2.Data.KvSortUintData',
]

def main() -> None:
    lines = Path(ce_symbol_path).read_text().split('\n')

    cur_dll = None
    cur_class = None
    cur_section = None

    class_fields = defaultdict(list)

    for line in lines:
        if not line:
            continue

        indent = 0
        while line[indent] == '\t':
            indent += 1
        line = line[indent:]

        if indent == 1:
            addr, dll = line.split(' : ')
            cur_dll = dll
            continue

        if indent > 1 and cur_dll != 'StaticTable.dll':
            continue

        if indent == 2:
            addr, cls = line.split(' : ')
            cur_class = cls
            continue

        if indent > 2:
            is_data_class = cur_class.startswith('GF2.Data.') and cur_class.endswith('Data')
            if not is_data_class:
                continue

        if indent == 3:
            cur_section = line
            continue

        if indent == 4 and cur_section == 'fields':
            addr, field = line.split(' : ', 1)
            class_fields[cur_class].append(field)

    decl_py = 'import proto'

    for cls in nested_types:
        decl_py += '\n\n' + generate_class_declaration(cls, class_fields[cls])
    for cls, fields in class_fields.items():
        if cls not in nested_types:
            decl_py += '\n\n' + generate_class_declaration(cls, fields)

    Path(declaration_py_path).write_text(decl_py + '\n')

def generate_class_declaration(cls: str, fields: list[str]) -> str:
    lines = []

    cls = cls.removeprefix('GF2.Data.')
    lines.append(f'class {cls}(proto.Message):')

    number = 0
    for field in fields:
        name, type_ = field.removesuffix(')').split(' (type: ')

        if not name.endswith('_'):
            continue
        number += 1
        name = name.removesuffix('_')

        if type_.startswith('Google.Protobuf.Collections.'):
            container, args = type_.removesuffix('>').split('<')
            args = args.split(',')

            field_class = 'proto.' + container.removeprefix('Google.Protobuf.Collections.')
            type_ = ', '.join(cs_to_pb_type(arg) for arg in args)

        else:
            field_class = 'proto.Field'
            type_ = cs_to_pb_type(type_)

        lines.append(f'    {name} = {field_class}({type_}, number={number})')

    if len(lines) == 1:
        lines.append('    pass')

    return '\n'.join(lines)

def cs_to_pb_type(cs_type: str) -> str:
    ns, type_ = cs_type.rsplit('.', 1)

    if ns == 'GF2.Data':
        if cs_type in nested_types:
            return type_
        if type_.endswith('Type') or type_ in ['GridEffectTpye', 'RogueStageMode']:
            return 'proto.INT32'  # enum

    if ns == 'System':
        if type_ == 'Boolean':
            return 'proto.BOOL'
        else:
            return 'proto.' + type_.upper()

    raise ValueError(f'Unknown type {cs_type}')

main()
