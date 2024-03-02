import assets
import checksum
import tables

def main():
    files = checksum.filter_updated_files()
    tables.decode_tables(files)
    assets.extract_assets(files)

if __name__ == '__main__':
    main()
