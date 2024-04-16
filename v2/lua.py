import shutil
import subprocess

from common import *
import config

def decompile_lua(files: list[Path] | None = None) -> None:
    print('Decompiling lua...')

    if files is None:
        lua_dir = Path(
            config.game_data_dir,
            'ClientRes_Windows/1.0.2010/A5CFF04BAF8EAC27EF4D4716C075F344'
        )
        files = list(lua_dir.iterdir())

    #for output_dir in config.lua_output_dirs:
    #    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(config.output_dir, 'lua/luac').mkdir(parents=True, exist_ok=True)
    Path(config.output_dir, 'lua/lua').mkdir(parents=True, exist_ok=True)
    Path(config.output_dir, 'lua/named').mkdir(parents=True, exist_ok=True)

    for file in files:
        if file.parent.name == 'A5CFF04BAF8EAC27EF4D4716C075F344':
            if file.suffix == '.bytes':
                #lua_file = decompile(file)
                lua_file = Path(config.output_dir, f'lua/lua/{file.stem}.lua') 

                class_name, _requires = inspect_lua_hierarchy(lua_file)
                if class_name is None:
                    print('[FAIL]', file.stem)
                else:
                    f = Path(config.output_dir, f'lua/named/{class_name}.lua')
                    shutil.copyfile(lua_file, f)

            else:
                print('SKIP', file.name)

    #class_package = {}
    #for package in packages:
    #    class_name = package.split('.')[-1]
    #    class_package[class_name] = package

    #for class_name, file in class_file.items():
    #    if class_name in class_package:
    #        print(class_package[class_name], file.stem)
    #    else:
    #        print('?.' + class_name, file.stem)
    #for file in bad_files:
    #    print('?', file.stem)

def inspect_lua_hierarchy(file: Path) -> tuple[str | None, list[str]]:
    try:
        text = file.read_text()
    except FileNotFoundError:
        return None, []

    if not text.strip():
        return None, []

    lines = text.split('\n')

    class_name = None
    requires = []

    first_line = True

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if 'require(' in line:
            requires.append(line.split('require("')[1].removesuffix('")'))
            continue

        if class_name is None:
            if line.startswith('local '):
                line = line.removeprefix('local ')

            if ' = class(' in line:
                class_name = line.split(' = class(')[0]
                break

            if first_line and ' = {' in line:
                class_name = line.split(' = {')[0]
                break

        first_line = False

    if class_name is None:
        class_name = '_' + file.stem.lower()
    return class_name, requires

def decompile(path: Path) -> Path:
    uuid = path.stem

    data = path.read_bytes()
    data = bytearray(data)
    for i, _ in enumerate(data):
        data[i] ^= 0xff

    luac_path = Path(config.output_dir, 'lua/luac', f'{uuid}.luac')
    luac_path.write_bytes(data)

    lua_path = Path(config.output_dir, 'lua/lua', f'{uuid}.lua')

    subprocess.run(
        f'java -jar unluac.jar --output {lua_path} {luac_path}'.split()
    )

    return lua_path

if __name__ == '__main__':
    decompile_lua()
