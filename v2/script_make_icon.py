from common import *

from PIL import Image, ImageDraw

assets_dir = '/mnt/c/_re/gf2/texture-240123'
output_dir = '/mnt/c/_re/gf2/icons'

def main():
    darkzone_chest_2()

def darkzone_chest_1():
    icon_path = Path(assets_dir, 'icon_DarkzoneMap_Mask6.png')

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    colors = {
        '精装补给箱': (223, 158, 0),
        '普通补给箱': (121, 104, 186),
        '粗糙补给箱': (50, 145, 171),
    }

    for name, color in colors.items():
        icon = Image.open(icon_path)
        for x in range(20, 44):
            for y in range(20, 44):
                r1, g1, b1, a = icon.getpixel((x, y))
                r2, g2, b2 = color
                r = round(r1 * r2 / 255)
                g = round(g1 * g2 / 255)
                b = round(b1 * b2 / 255)
                icon.putpixel((x, y), (r, g, b, a))
        icon.save(Path(output_dir, name + '-1.png'))

def darkzone_chest_2():
    size = 48

    #icon_path = Path(assets_dir, 'Icon_DarkzoneMap_Box.png')
    icon_path = Path(output_dir, 'Icon_DarkzoneMap_Box.png')

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    colors = {
        '精装补给箱': (223, 158, 0),
        '普通补给箱': (121, 104, 186),
        '粗糙补给箱': (50, 145, 171),
    }

    for name, color in colors.items():
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))

        draw = ImageDraw.Draw(out)
        draw.ellipse(
            (0, 0, size - 1, size - 1),
            fill='white',
        )
                #color = colors[obj['name']]
                #r = 15
                #draw.ellipse(
                #    (x - r, y - r, x + r, y + r),
                #    fill=color,
                #    outline='white',
                #    width=5
                #)

        icon = Image.open(icon_path)
        for x in range(icon.width):
            for y in range(icon.height):
                r1, g1, b1, a = icon.getpixel((x, y))
                r2, g2, b2 = color
                r = round(r1 * r2 / 255)
                g = round(g1 * g2 / 255)
                b = round(b1 * b2 / 255)
                icon.putpixel((x, y), (r, g, b, a))

        offset = (size - icon.width) // 2
        out.alpha_composite(icon, (offset, offset))

        out.save(Path(output_dir, name + '-2.png'))

if __name__ == '__main__':
    main()
