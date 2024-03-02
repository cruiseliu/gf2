import json
from pathlib import Path
import zlib

import config

def filter_updated_files() -> list[Path]:
    cur_checksum = get_checksum()
    prev_checksum = detect_previous_checksum()

    if prev_checksum is not None:
        print('Comparing checksum...')
        rel_paths = []

        for path, cur in cur_checksum.items():
            prev = prev_checksum.pop(path, None)
            if cur != prev:
                if prev is None:
                    print('[new]', path)
                else:
                    print('[updated]', path)
                rel_paths.append(path)

        for path in prev_checksum.keys():
            print('[removed]', path)

    else:
        rel_paths = cur_checksum.keys()

    return [Path(config.game_data_dir, path) for path in rel_paths]

def get_checksum() -> dict[str, str]:
    # todo: use Version_D.txt ?

    try:
        text = Path(config.version_output_dir, 'crc32.json').read_text()
        return json.loads(text)
    except Exception:
        pass

    return calc_checksum()

def calc_checksum() -> dict[str, str]:
    print('Calculating checksum...')
    file_hash = {}

    files = Path(config.game_data_dir).rglob('*')
    for file in sorted(files):
        rel = file.relative_to(config.game_data_dir)
        if rel.parts[0].endswith('_BrowserProfile'):
            continue
        if file.is_dir():
            print('   ', rel)
            continue
        hash_ = zlib.crc32(file.read_bytes())
        file_hash[rel.as_posix()] = f'{hash_:08x}'

    text = json.dumps(file_hash, indent=4, ensure_ascii=False)

    checksum_file = Path(config.version_output_dir, 'crc32.json')  # FIXME
    checksum_file.parent.mkdir(parents=True, exist_ok=True)
    checksum_file.write_text(text)

    return file_hash

def detect_previous_checksum() -> dict[str, str] | None:
    version = None
    checksum = None

    for dir_ in Path(config.version_output_dir).parent.iterdir():
        if version is not None and dir_.name < version:
            continue
        if dir_.name == config.game_version:
            continue

        try:
            content = (dir_ / 'crc32.json').read_text()
            checksum = json.loads(content)
            version = dir_.name
        except Exception:
            pass

    if checksum is not None:
        print('Found previous version:', version)
    return checksum

if __name__ == '__main__':
    filter_updated_files()
