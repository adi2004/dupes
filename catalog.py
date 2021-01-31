#!/usr/bin/env python3

import csv
import hashlib
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import dhash
import imagehash
from PIL import Image

if len(sys.argv) != 3:
    print("Use ./catalog.py <dir-to-catalog> <catalog-file.csv")
    exit(1)

exclude_list = [".git", "@eaDir", "backup", "incoming"]
include_list = ['.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg']


class Const:
    gibi = 1024 * 1024 * 1024
    mebi = 1024 * 1024
    kibi = 1024

def is_ignored(filename):
    for exclude_keyword in exclude_list:
        if exclude_keyword.lower() in filename:
            return True
    return False


def is_included(filename):
    return True  # filename.lower().endswith(('.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg'))


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def dt(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d %H.%M.%S")


def md5_hash(filename):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()


def exiftool_date(filename):
    date_output = subprocess.getoutput(
        'exiftool -CreateDate "{}"'.format(file_with_path))
    date_trimmed = re.sub("^.*: ", "", date_output)
    date_trimmed = re.sub(":", ".", date_trimmed)
    if date_trimmed.startswith("20") or date_trimmed.startswith("19"):
        return date_trimmed
    return ""


def exiftool_duration(filename):
    if not filename.lower().endswith(('.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg')):
        return ""
    date_output = subprocess.getoutput(
        'exiftool -Duration "{}"'.format(file_with_path))
    date_trimmed = re.sub("^.*: ", "", date_output)
    return date_trimmed


def image_average_hash(filename):
    hash_size = 16
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return ""
    with Image.open(filename) as img:
        hash = imagehash.average_hash(img, hash_size)
        return hash
    return ""


def image_difference_hash(filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return ""
    with Image.open(filename) as img:
        row, col = dhash.dhash_row_col(img)
        return dhash.format_hex(row, col)


def movie_hash(filename):
    if not filename.lower().endswith(('.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg')):
        return ""


def write(file, catalog):
    if len(catalog) == 0:
        print("Nothing to write...")
    print("Writing to {}".format(file))
    with open(file, 'w') as file_handler:
        # creating a csv dict writer object
        writer = csv.DictWriter(
            file_handler, fieldnames=list(catalog[0].keys()))

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(catalog)


start_time = time.time()
catalog_directory = sys.argv[1]
catalog_file_name = sys.argv[2]
print("Reading {}/{}".format(os.getcwd(), catalog_directory))

catalog_paths = list(Path(catalog_directory).rglob("*"))

catalog = []

file_count = 0
total_size = 0
progress = ["|", "/", "-", "|", "\\"]
for path in catalog_paths:
    path_parent = str(path.parent)
    file_name = str(path.name)
    file_with_path = path_parent + "/" + file_name
    if path.is_dir() or is_ignored(file_with_path) or not is_included(file_with_path):
        continue
    file_count += 1
    fprop = {}
    try:
        info = path.stat()
        # populate filter criteria
        path_parent = remove_prefix(path_parent, catalog_directory)
        path_parent = re.sub("^[./]+", "", path_parent)
        if total_size >= Const.gibi:
            size_string = "%.2f GiB" % (total_size / Const.gibi)
        elif total_size >= Const.mebi:
            size_string = "%.2f MiB" % (total_size / Const.mebi)
        else:
            size_string = "%.2f KiB" % (total_size / Const.kibi)
        print("Found {} files totaling {} {} reading {}"
            .format(file_count, size_string, progress[file_count % 5], file_with_path[0:120] + " " * 60), 
            end="\r")
        paths = path_parent.split("/")
        fprop["path_part_1"] = paths[0] if len(paths) > 0 else ""
        fprop["path_part_2"] = paths[1] if len(paths) > 1 else ""
        fprop["path_part_3"] = paths[2] if len(paths) > 2 else ""
        fprop["path_end"] = paths[-1] if len(paths) > 0 else ""
        fprop["file_extension"] = file_name.split(".")[-1].lower()

        # populate path and file_name
        fprop["path"] = path_parent
        fprop["file_name"] = file_name

        # populate file dates
        fprop["modified_time"] = dt(info.st_mtime)
        fprop["created_time"] = dt(info.st_ctime)
        fprop["access_time"] = dt(info.st_atime)

        # size
        fprop["file_size"] = info.st_size
        total_size += info.st_size
        # md5 hash
        fprop["md5_hash"] = md5_hash(file_with_path)
        # get date using exiftool
        fprop["exiftool_date"] = exiftool_date(file_with_path)
        # get muvie duration using exiftool
        fprop["exiftool_duration"] = exiftool_duration(file_with_path)
        # image average hash
        fprop["image_average_hash"] = image_average_hash(file_with_path)
        # image_difference_hash
        fprop["image_difference_hash"] = image_difference_hash(file_with_path)

        # add to catalog
        catalog.append(fprop)
    except KeyboardInterrupt:
        exit(1)
    except:
        print("\nGot it!", sys.exc_info()[0], "occurred.\n")
        continue

print("\n")

# writing to csv file
write(catalog_file_name, catalog)

time_total = time.time() - start_time
time_minutes = int(time_total / 60)
time_seconds = int(time_total % 60)
print("Done in {}m {}s".format(time_minutes, time_seconds))
