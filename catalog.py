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
from common import Const, read, write

class View:
    file_count = 0
    total_size = 0
    printed_length = 0

class Config:
    flags = "0"
    catalog_directory = ""
    catalog_file_name = ""


def is_ignored(filename):
    filename = filename.lower()
    for exclude_keyword in Const.exclude_list:
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
    return datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d %H.%M")


def print_progress(file_path, file_name, view):
    if view.total_size >= Const.gibi:
        size_string = "%.2f GiB" % (view.total_size / Const.gibi)
    elif view.total_size >= Const.mebi:
        size_string = "%.2f MiB" % (view.total_size / Const.mebi)
    else:
        size_string = "%.2f KiB" % (view.total_size / Const.kibi)

    spinner = " " + Const.progress[view.file_count % len(Const.progress)] + " "
    out_string = "\rFound {:,d}".format(view.file_count) + " files " + \
        "totaling " + size_string + spinner + \
        "reading " + file_path + "/" + file_name
    if len(out_string) > 120:
        out_string = out_string[:100] + "..." + out_string[-20:]
    end_padding = view.printed_length - len(out_string)
    end_string = " " * (end_padding if end_padding > 0 else 0)
    print(out_string + end_string, end="")
    return len(out_string)


def md5_hash(filename):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()


def exiftool(filename):
    output = subprocess.getoutput(
        'exiftool -d "%Y.%m.%d %H.%M.%S" -Duration -ContentCreateDate -CreateDate "' + filename + '"')
    output = output.splitlines()
    result = {
        "exiftool_duration": "",
        "exiftool_date": "", 
        "exiftool_content_date": ""
    }
    for line in output:
        if line.startswith("Create"):
            line = re.sub("^.*: ", "", line)
            if line.startswith("19") or line.startswith("20"):
                result["exiftool_date"] = line
        elif line.startswith("Content"):
            line = re.sub("^.*: ", "", line)
            if line.startswith("19") or line.startswith("20"):
                result["exiftool_content_date"] = line
        if line.startswith("Duration"):
            line = re.sub("^.*: ", "", line)
            result["exiftool_duration"] = line
    return result


def image_average_hash(filename):
    hash_size = 16
    if not filename.lower().endswith(tuple(Const.imgs)):
        return ""
    with Image.open(filename) as img:
        hash = imagehash.average_hash(img, hash_size)
        return hash
    return ""


def image_difference_hash(filename):
    if not filename.lower().endswith(tuple(Const.imgs)):
        return ""
    with Image.open(filename) as img:
        row, col = dhash.dhash_row_col(img)
        return dhash.format_hex(row, col)

def read_configuration():
    cfg = Config()
    if len(sys.argv) != 4:
        print("Use ./catalog.py flags <dir-to-catalog> <catalog_file.csv>")
        print(
            "The flags are:\n" +
            "\t 0 to just read the files" +
            "\t" + Const.md5_hash_flag + " for MD5\n" +
            "\t" + Const.exiftool_flag + " for exiftool\n" +
            "\t" + Const.avarage_hash_flag + " for average hash algorithm\n" +
            "\t" + Const.difference_hash_flag + " for difference hash algorithm (recommended)\n"
        )
        exit(1)

    cfg.flags = sys.argv[1]
    cfg.catalog_directory = sys.argv[2] 
    if cfg.catalog_directory.endswith('/'):
        cfg.catalog_directory = cfg.catalog_directory[:-1]
    cfg.catalog_file_name = sys.argv[3]
    return cfg

def make_catalog(directory, flags):
    catalog_paths = list(Path(directory).rglob("*"))

    catalog = []
    view = View()

    for path in catalog_paths:
        path_parent = str(path.parent)
        file_name = str(path.name)
        file_with_path = path_parent + "/" + file_name
        path_parent_short = remove_prefix(path_parent, config.catalog_directory)
        path_parent_short = re.sub("^[./]+", "", path_parent_short)
        if path.is_dir() or is_ignored(file_with_path) or not is_included(file_with_path):
            continue
        view.file_count += 1
        fprop = {}
        try:
            info = path.stat()
            # populate filter criteria
            view.printed_length = print_progress(path_parent_short, file_name, view)
            paths = path_parent_short.split("/")
            fprop["path_part_1"] = paths[0] if len(paths) > 0 else ""
            fprop["path_part_2"] = paths[1] if len(paths) > 1 else ""
            fprop["path_part_3"] = paths[2] if len(paths) > 2 else ""
            fprop["path_end"] = paths[-1] if len(paths) > 0 else ""
            fprop["file_extension"] = file_name.split(".")[-1].lower()

            # populate path and file_name
            fprop["path"] = path_parent_short
            fprop["file_name"] = file_name

            # populate file dates
            fprop["modified_time"] = dt(info.st_mtime)
            fprop["created_time"] = dt(info.st_ctime)
            fprop["access_time"] = dt(info.st_atime)
            # size
            fprop["file_size"] = info.st_size
            view.total_size += info.st_size

            # md5 hash
            if Const.md5_hash_flag in flags:
                fprop["md5_hash"] = md5_hash(file_with_path)
            # get date using exiftool
            if Const.exiftool_flag in flags:
                exiftool_result = exiftool(file_with_path)
                fprop.update(exiftool_result)
            # image average hash
            if Const.avarage_hash_flag in flags:
                fprop["image_average_hash"] = image_average_hash(file_with_path)
            # image_difference_hash
            if Const.difference_hash_flag in flags:
                fprop["image_difference_hash"] = image_difference_hash(
                    file_with_path)

            # add to catalog
            catalog.append(fprop)
        except KeyboardInterrupt:
            exit(1)
        except:
            print("\nError ", sys.exc_info()[0], " occurred.")
            continue
    print("\n")
    
    return catalog

def make_key(file_attrs):
    return file_attrs["path"] + "/" + file_attrs["file_name"] + ":" + file_attrs["file_size"]

def make_old_catalog_hash(file):
    old_catalog_hash = {}
    if os.path.isfile(file):
        print("There already is a {} catalog. It will be updated with new values.".format(file))
        old_catalog = read(file)
        for file_attrs in old_catalog:
            key = make_key(file_attrs)
            old_catalog_hash[key] = file_attrs
    return old_catalog_hash

def merge(old_hash, new):
    if len(old_hash) == 0:
        return new
    else:
        return new

# === START === #

start_time = time.time()
config = read_configuration()
old_catalog_hash = make_old_catalog_hash(config.catalog_file_name)
print("Reading {}/{}".format(os.getcwd(), config.catalog_directory))
new_catalog = make_catalog(config.catalog_directory, config.flags)
catalog = merge(old_catalog_hash, new_catalog)

# writing to csv file
write(config.catalog_file_name, catalog)

# done in ...
time_total = time.time() - start_time
time_minutes = int(time_total / 60)
time_seconds = int(time_total % 60)
mili_seconds = int(time_total * 1000)
if time_minutes > 0:
    print("Done in {}m {}s".format(time_minutes, time_seconds))
elif time_seconds > 0:
    print("Done in {}s".format(time_seconds))
else:
    print("Done in {}ms".format(mili_seconds))
