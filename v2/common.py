__all__ = [
    'Tables',
    'find_keywords',
    'load_table',
    'replace_colors',

    'Fraction',
    'Path',
    'defaultdict',
    'json',
    'math',
]

from collections import defaultdict
from fractions import Fraction
import functools
import json
import math
from pathlib import Path
import re

tables_dir = Path(__file__).parents[1] / 'tables'

@functools.cache
def load_table(name: str, key: str | None = None) -> dict:
    text = (tables_dir / f'{name}.json').read_text()
    data = json.loads(text)['data']
    if key is None:
        key = next(iter(data[0].keys()))
    dict_ = {item[key]: item for item in data}
    return _Table(dict_)

class _Table(dict):
    def __iter__(self):
        return iter(super().values())

class _TableLoader:
    def __getattr__(self, key: str) -> dict:
        return load_table(key)

Tables = _TableLoader()

def replace_colors(text: str) -> str:
    text = re.sub(
        r'<color=#([0-9a-fA-F]{6})>',
        r'{{color|\1|',
        text
    )
    return text.replace('</color>', '}}')

def find_keywords(text: str) -> dict[str, str]:
    r = r'<color=#3487e0>(.+?)</color>'
    return {match.group(1): match.group(0) for match in re.finditer(r, text)}
