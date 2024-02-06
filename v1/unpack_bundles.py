from datetime import datetime
import json
from pathlib import Path

import UnityPy

from_dir = 'c:/_re/gf2/assetbundles-240201'
to_dir = 'c:/_re/gf2/assets-240201'
log_path = Path(to_dir, 'log.txt')
#log_path = Path(__file__).parents[1] / 'assets-log.txt'

log_path.parent.mkdir(parents=True, exist_ok=True)
log_stream = open(log_path, 'a')

def main() -> None:
    log_stream.write(f'### {datetime.now()} ###\n')

    for bundle in sorted(Path(from_dir).iterdir()):
        print(bundle.stem)
        try:
            unpack_bundle(bundle.stem)
        except Exception:
            log_stream.write(f'[FAIL] {bundle.stem}\n')

def unpack_bundle(bundle_name: str) -> None:
    Path(to_dir, bundle_name).mkdir(parents=True, exist_ok=True)

    bundle_path = Path(from_dir, bundle_name + '.bundle')
    bundle = UnityPy.load(str(bundle_path))

    for i, reader in enumerate(bundle.objects):
        obj = None
        try:
            obj = reader.read()
        except Exception:
            print('FAIL', bundle_name, i)

        name = try_getattr(obj, reader, lambda obj: obj.name)
        path_id = try_getattr(obj, reader, lambda obj: obj.path_id)
        type_name = try_getattr(obj, reader, lambda obj: obj.type.name)
        size = try_getattr(obj, reader, lambda obj: obj.byte_size)

        path_id = path_id.to_bytes(8, signed=True).hex()

        log_stream.write(f'{bundle_name} {i} {path_id} {name or "(noname)"} {type_name} {size}\n')
        if obj is None:
            log_stream.write(f'[FAIL] {bundle_name} {i} (read)\n')
            continue

        if name:
            file_name = name.replace('/', '|') + ' #' + path_id
        else:
            file_name = path_id

        if type_name == 'MonoBehaviour':
            try:
                path = Path(to_dir, bundle_name, file_name + '.json')
                tree = reader.read_typetree()
                text = json.dumps(
                    tree,
                    ensure_ascii=False,
                    indent=4, 
                    default=(lambda obj: f'<{type(obj).__module__}.{type(obj).__name__}>')
                )
                path.write_text(text)
            except Exception:
                print('FAIL', bundle_name, i, file_name, type_name)
                log_stream.write(f'[FAIL] {bundle_name} {i} json\n')
                continue

        if type_name == 'TextAsset':
            path = Path(to_dir, bundle_name, file_name + '.txt')
            path.write_bytes(obj.script)

        if type_name == 'Sprite' or type_name == 'Texture2D':
            try:
                path = Path(to_dir, bundle_name, file_name + '.png')
                obj.image.save(str(path))
            except Exception:
                print('FAIL', bundle_name, i, file_name, type_name)
                log_stream.write(f'[FAIL] {bundle_name} {i} image\n')
                continue

    log_stream.flush()

def try_getattr(*args):
    getter = args[-1]
    args = args[:-1]
    for arg in args:
        try:
            return getter(arg)
        except AttributeError:
            pass
    return None

main()
