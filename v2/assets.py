from io import BytesIO
from pathlib import Path

import UnityPy

import config

def main():
    config.image_output_dirs = [config.image_output_dirs[0]]
    extract_assets()

def extract_assets(files: list[Path] | None = None) -> None:
    print('Extracting images...')

    if files is None:
        bundle_dir = Path(config.game_data_dir, 'AssetBundles_Windows')
        files = list(bundle_dir.iterdir())

    for output_dir in config.image_output_dirs:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    for file in files:
        if file.parent.name == 'AssetBundles_Windows':
            #if file.stem < '8f06fb844d662068738c48831b7424ee':
            #    continue
            if file.suffix == '.bundle':
                try:
                    extract_bundle(file)
                except Exception as e:
                    print('FAIL', file.name, repr(e))
            else:
                print('SKIP', file.name)

def extract_bundle(path: Path) -> None:
    bundle_name = path.stem
    stream = decode_bundle(path)
    bundle = UnityPy.load(stream)

    for i, reader in enumerate(bundle.objects):
        # FIXME: check type here?

        obj = None
        try:
            obj = reader.read()
        except Exception:
            print('FAIL', bundle_name, i)

        name = try_getattr(obj, reader, lambda obj: obj.name)
        path_id = try_getattr(obj, reader, lambda obj: obj.path_id)
        type_name = try_getattr(obj, reader, lambda obj: obj.type.name)

        if type_name != 'Texture2D':
            continue

        if not name:
            name = path_id

        for output_dir in config.image_output_dirs:
            path = Path(output_dir, name + '.png')
            try:
                obj.image.save(str(path))
            except Exception:
                print('FAIL', bundle_name, i, name)
                break

    print('    ' + bundle_name)

def try_getattr(*args):
    getter = args[-1]
    args = args[:-1]
    for arg in args:
        try:
            return getter(arg)
        except AttributeError:
            pass
    return None

def decode_bundle(path: Path) -> BytesIO:
    cipher_stream = path.open('rb')
    cipher_header_1 = cipher_stream.read(8)
    cipher_header_2 = cipher_stream.read(8)

    plain_stream = BytesIO()
    plain_header_1 = bytes.fromhex('556e 6974 7946 5300')
    plain_header_2 = bytes.fromhex('0000 0007 352e 782e')
    plain_stream.write(plain_header_1)
    plain_stream.write(plain_header_2)

    key1 = xor(cipher_header_1, plain_header_1)
    key2 = xor(cipher_header_2, plain_header_2)

    while True:
        cipher_word_1 = cipher_stream.read(8)
        cipher_word_2 = cipher_stream.read(8)

        if len(cipher_word_2) < 8:
            plain_word_1 = xor_tail(cipher_word_1, key1)
            plain_word_2 = xor_tail(cipher_word_2, key2)

        else:
            plain_word_1 = xor(cipher_word_1, key1)
            plain_word_2 = xor(cipher_word_2, key2)

        plain_stream.write(plain_word_1)
        plain_stream.write(plain_word_2)

        if len(cipher_word_2) < 8:
            break

        if cipher_stream.tell() >= 0x8000:
            data = cipher_stream.read()
            plain_stream.write(data)
            break

    cipher_stream.close()

    plain_stream.seek(0)
    return plain_stream

def xor(a: bytes, b: bytes) -> bytes:
    x = int.from_bytes(a, 'little')
    y = int.from_bytes(b, 'little')
    return (x ^ y).to_bytes(8, 'little')

def xor_tail(a: bytes, b: bytes) -> bytes:
    a_pad = a + bytes(8 - len(a))
    return xor(a_pad, b)[:len(a)]

if __name__ == '__main__':
    main()
