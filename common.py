import csv
import os

class Const:
    gibi = 1024 * 1024 * 1024
    mebi = 1024 * 1024
    kibi = 1024
    progress = ["|", "/", "-", "\\"] 
    imgs = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    mvs = ['.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg']

    exclude_list = [".git", "@eaDir", "backup", "incoming", ".vscode", ".unotes", "__pycache__"] # case insensitive
    include_list = ['.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg']

    md5_hash_flag = "5"
    exiftool_flag = "e"
    avarage_hash_flag = "a"
    difference_hash_flag = "d" # recommended

    duplicates = "dplc"
    pruned = "prnd"

def append_suffix(file, suffix):
    name = os.path.splitext(file)[0]
    extension = os.path.splitext(file)[1]
    return name + "." + suffix + extension

def read(file):
    catalog = []
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            catalog.append(row)
    return catalog

def write(file, catalog):
    if len(catalog) == 0:
        print("Nothing to write...")
        return
    print("Writing to {}".format(file))
    with open(file, 'w') as file_handler:
        # creating a csv dict writer object
        writer = csv.DictWriter(
            file_handler, fieldnames=list(catalog[0].keys()))

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(catalog)