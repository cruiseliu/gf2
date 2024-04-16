from datetime import datetime
import getpass
from pathlib import Path
import sys

# general config

game_install_dir = Path('D:/Program Files/GF2Exilium')

game_data_dir = Path(game_install_dir, 'GF2 Game/GF2_Exilium_Data/LocalCache/Data')

output_dir = Path(__file__).parents[1]

table_output_dirs = [output_dir / 'tables']
image_output_dirs = [output_dir / 'image']
media_output_dirs = [output_dir / 'media']

# my personal config

_personal = (getpass.getuser() == 'lz')

if _personal:
    if sys.platform == 'linux':
        game_data_dir = Path('/mnt/c/_prog/gf2/GF2 Game/GF2_Exilium_Data/LocalCache/Data')
        gf2_output_dir = Path('/mnt/c/_re/gf2')
    else:
        game_data_dir = Path('C:/_prog/gf2/GF2 Game/GF2_Exilium_Data/LocalCache/Data')
        gf2_output_dir = Path('C:/_re/gf2')

    game_version = datetime.now().strftime('%y%m%d')
    version_output_dir = gf2_output_dir / game_version

    table_output_dirs = [
        gf2_output_dir / 'tables',
        version_output_dir / 'tables',
    ]

    image_output_dirs = [
        gf2_output_dir / 'image',
        version_output_dir / 'image'
    ]

    image_output_dirs.append(version_output_dir / 'image')

    #lua_output_dirs = output_dir.parents[1] / 'lua'
