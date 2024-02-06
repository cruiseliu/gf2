from common import *

def main():
    for doll in sort_dolls():
        print(doll['name'])
        print()

        print('===皮肤===')
        print('{{costumes')
        for i, costume_id in enumerate(doll['costumeReplace']):
            costume = Tables.ClothesData[costume_id]
            print(f'|name{i + 1}=' + costume['name'])
            if i > 0:
                print(f'|source{i + 1}=')
            print(f'|image{i + 1}=Img_ChrSkinPic_' + costume['code'])
            print(f'|desc{i + 1}=' + costume['description'])
        print('}}')

        print()

if __name__ == '__main__':
    main()
