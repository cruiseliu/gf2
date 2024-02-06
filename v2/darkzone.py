from common import *

from PIL import Image, ImageDraw

assets_dir = Path('/mnt/c/_re/gf2/texture-240123')
icons_dir = Path('/mnt/c/_re/gf2/icons')
output_dir = Path('/mnt/c/_re/gf2/maps')

def main():
    output_dir.mkdir(parents=True, exist_ok=True)

    colors = {
        '精装补给箱': (223, 158, 0),
        '普通补给箱': (121, 104, 186),
        '粗糙补给箱': (50, 145, 171),
    }

    for map_ in Tables.DarkzoneMapV2Data:
        map_id = map_['id']

        minimap = Tables.DarkzoneMinimapV2Data.get(map_['minimapId'])
        if not minimap:
            continue

        bg_path = Path(assets_dir, minimap['background'] + '.png')
        if not bg_path.exists():
            continue

        image = Image.open(bg_path)
        if image.size == (1024, 1024):
            scaled = image.resize((2048, 2048), Image.Resampling.NEAREST)
            for x in range(1024):
                for y in range(1024):
                    p = image.getpixel((x, y))
                    scaled.putpixel((x * 2, y * 2), p)
                    scaled.putpixel((x * 2, y * 2 + 1), p)
                    scaled.putpixel((x * 2 + 1, y * 2), p)
                    scaled.putpixel((x * 2 + 1, y * 2 + 1), p)
            image = scaled
        if image.size != (2048, 2048):
            image.close()
            continue

        draw = ImageDraw.Draw(image)

        print(map_['id'], map_['name'])

        offset_x, offset_y = minimap['darkzoneMapOffset']
        scale = minimap['darkzoneMapScale']

        icons = []

        for interact in map_['interactData']:
            depot = Tables.DzIobjDepotData[interact]
            obj = Tables.DzIobjMainData[depot['id']]

            x, z, y = [int(x) for x in depot['position'].split(',')]

            x = (x / 100 + offset_x) * scale
            y = 2047 - (y / 100 + offset_y) * scale

            if '补给箱' in obj['name']:
                #color = colors[obj['name']]
                #r = 15
                #draw.ellipse(
                #    (x - r, y - r, x + r, y + r),
                #    fill=color,
                #    outline='white',
                #    width=5
                #)
                icon_path = Path(icons_dir, obj['name'] + '-2.png')
                #icon_image = Image.open(icon_path)
                #x = round(x - icon_image.width / 2)
                #y = round(y - icon_image.height / 2)
                priority = 1
                icons.append((icon_path, x, y, priority))
                #image.alpha_composite(icon_image, (x, y))

            elif obj['isShowOnMinimap']:
                icon_data = Tables.DarkzoneMinimapIconData[obj['isShowOnMinimap']]
                icon_path = Path(assets_dir, icon_data['icon'] + '.png')
                #icon_image = Image.open(icon_path)
                #x = round(x - icon_image.width / 2)
                #y = round(y - icon_image.height / 2)
                priority = 0
                icons.append((icon_path, x, y, priority))
                #image.alpha_composite(icon_image, (x, y))

        icons = sorted(icons, key=(lambda icon: icon[-1]))
        for icon_path, x, y, _priority in icons:
            icon = Image.open(icon_path)
            x = round(x - icon.width / 2)
            y = round(y - icon.width / 2)
            image.alpha_composite(icon, (x, y))

        output_path = Path(output_dir, str(map_id) + '-' + map_['name'] + '.png')
        image.save(output_path)

main()
