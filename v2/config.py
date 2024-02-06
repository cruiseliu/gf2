from datetime import datetime
from pathlib import Path
import sys

game_version = datetime.now().strftime('%y%m%d')

# general config

game_data_dir = Path('D:/Program Files/GF2Exilium/GF2 Game/GF2_Exilium_Data/LocalCache/Data')

output_dir = Path(__file__).parents[1] / game_version
tables_output_dir = output_dir / 'tables'
assets_output_dir = output_dir / 'assets'
media_output_dir = output_dir / 'media'

# my personal config

_personal = True

if _personal:
    if sys.platform == 'linux':
        game_data_dir = Path('/mnt/d/Program Files/GF2Exilium/GF2 Game/GF2_Exilium_Data/LocalCache/Data')
