from pathlib import Path

game_data_dir = Path('D:/Program Files/GF2Exilium/GF2 Game/GF2_Exilium_Data/LocalCache/Data')
from_dir = game_data_dir / 'AssetBundles_Windows'
to_dir = 'c:/_re/gf2/assetbundles-240201'

def main() -> None:
    Path(to_dir).mkdir(parents=True, exist_ok=True)
    for file in sorted(Path(from_dir).iterdir()):
        if file.suffix != '.bundle':
            print('SKIP', file.name)
        else:
            print('decoding', file.name)
            decode_asset_bundle(file.name)

def decode_asset_bundle(file_name: str) -> None:
    cipher_stream = Path(from_dir, file_name).open('rb')
    cipher_header_1 = cipher_stream.read(8)
    cipher_header_2 = cipher_stream.read(8)

    plain_stream = Path(to_dir, file_name).open('wb')
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
    plain_stream.close()

def xor(a: bytes, b: bytes) -> bytes:
    x = int.from_bytes(a, 'little')
    y = int.from_bytes(b, 'little')
    return (x ^ y).to_bytes(8, 'little')

def xor_tail(a: bytes, b: bytes) -> bytes:
    a_pad = a + bytes(8 - len(a))
    return xor(a_pad, b)[:len(a)]

main()
