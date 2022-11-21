import csv
import os

class Const:
    gibi = 1024 * 1024 * 1024
    mebi = 1024 * 1024
    kibi = 1024
    progress = ["|", "/", "-", "\\"] 
    imgs = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    mvs = ['.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg']

    exclude_list = [".git", "@eaDir", "backup", "incoming", ".vscode", ".unotes", "__pycache__", "thumbnail", ".dtrash"] # case insensitive
    include_list = ['.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg']

    md5_hash_flag = "5"
    exiftool_flag = "e"
    avarage_hash_flag = "a"
    difference_hash_flag = "d" # recommended
    debug = "D"

    duplicates = "dplc"
    pruned = "prnd"

    field_path_part_1 = "path_part_1"
    field_path_part_2 = "path_part_2"
    field_path_part_3 = "path_part_3"
    field_path_end = "path_end"
    field_file_extension = "file_extension"
    field_path = "path"
    field_file_name = "file_name"
    field_modified_time = "modified_time"
    field_created_time = "created_time"
    field_access_time = "access_time"
    field_file_size = "file_size"

    field_exiftool_duration = "exiftool_duration"
    field_exiftool_date = "exiftool_date"
    field_exiftool_content_date = "exiftool_content_date"

    field_md5_hash = "md5_hash"
    field_image_average_hash = "image_average_hash"
    field_image_difference_hash = "image_difference_hash"

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

def write(path, catalog):
    if len(catalog) == 0:
        print("Nothing to write...")
        return
    print("Writing to {}".format(path))
    with open(path, 'w') as file_handler:
        # creating a csv dict writer object
        writer = csv.DictWriter(
            file_handler, fieldnames=list(catalog[0].keys()))

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(catalog)