#!/usr/bin/env python3

import csv
import hashlib
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import dhash
import imagehash
from PIL import Image
from common import Const, read, write

class View:
    file_count = 0
    total_files = 0
    total_size = 0
    printed_length = 0

class Config:
    flags = "0"
    catalog_directory = ""
    catalog_file_name = ""


def is_ignored(path):
    path_str = str(path).lower()
    for exclude_keyword in Const.exclude_list:
        if exclude_keyword.lower() in path_str:
            return True
    return False


def is_included(filename):
    return True  # filename.lower().endswith(('.mov', '.avi', '.mp4', '.m4v', '.wmv', '.mpg', '.mpeg'))


def dt(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d %H.%M")


def print_progress(path, view, isSkipping):
    if view.total_size >= Const.gibi:
        size_string = "%.2f GiB" % (view.total_size / Const.gibi)
    elif view.total_size >= Const.mebi:
        size_string = "%.2f MiB" % (view.total_size / Const.mebi)
    else:
        size_string = "%.2f KiB" % (view.total_size / Const.kibi)

    spinner = " " + Const.progress[view.file_count % len(Const.progress)] + " "
    procent = view.file_count / view.total_files * 100
    out_string = "\rProgress {:.2f}%, ".format(procent) + \
        "processed {:_d}".format(view.file_count) + " files " + \
        "totaling " + size_string + spinner + \
        ("skipping " if isSkipping else "reading ") + str(path)
    if len(out_string) > 120:
        out_string = out_string[:100] + "..." + out_string[-20:]
    end_padding = view.printed_length - len(out_string)
    end_string = " " * (end_padding if end_padding > 0 else 0)
    print(out_string + end_string, end="")
    return len(out_string)


def path_filter(path):
    # populate filter criteria
    parts = path.parts
    result = {}
    result["path_part_1"] = parts[0] if len(parts) > 0 else ""
    result["path_part_2"] = parts[1] if len(parts) > 1 else ""
    result["path_part_3"] = parts[2] if len(parts) > 2 else ""
    result["path_end"] = parts[-1] if len(parts) > 0 else ""
    result["file_extension"] = path.suffix

    # populate path and file_name
    result["path"] = path.parent
    result["file_name"] = path.name

    return result

def basic_stat(info):
    result = {}

    # populate file dates
    result["modified_time"] = dt(info.st_mtime)
    result["created_time"] = dt(info.st_ctime)
    result["access_time"] = dt(info.st_atime)
    # size
    result["file_size"] = info.st_size

    return result

def md5_hash(path):
    md5_hash = hashlib.md5()
    with open(path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()


def exiftool(path):
    result = {
        Const.field_exiftool_duration: "",
        Const.field_exiftool_date: "", 
        Const.field_exiftool_content_date: ""
    }
    if path.suffix not in Const.imgs + Const.mvs:
        return result
    output = subprocess.getoutput(
        'exiftool -d "%Y.%m.%d %H.%M.%S" -Duration -ContentCreateDate -CreateDate "' + str(path) + '"')
    output = output.splitlines()
    for line in output:
        if line.startswith("Create"):
            line = re.sub("^.*: ", "", line)
            if line.startswith("19") or line.startswith("20"):
                result[Const.field_exiftool_date] = line
        elif line.startswith("Content"):
            line = re.sub("^.*: ", "", line)
            if line.startswith("19") or line.startswith("20"):
                result[Const.field_exiftool_content_date] = line
        if line.startswith("Duration"):
            line = re.sub("^.*: ", "", line)
            result[Const.field_exiftool_duration] = line
    return result


def image_average_hash(path):
    hash_size = 16
    if not path.suffix.endswith(tuple(Const.imgs)):
        return ""
    with Image.open(path) as img:
        hash = imagehash.average_hash(img, hash_size)
        return hash
    return ""


def image_difference_hash(path):
    if not path.suffix.endswith(tuple(Const.imgs)):
        return ""
    with Image.open(path) as img:
        row, col = dhash.dhash_row_col(img)
        return dhash.format_hex(row, col)

def read_configuration():
    cfg = Config()
    if len(sys.argv) != 4:
        print("Use ./catalog.py flags <dir-to-catalog> <catalog_file.csv>")
        print(
            "The flags are:\n" +
            "\t0 to just read the files\n" +
            "\t" + Const.md5_hash_flag + " for MD5\n" +
            "\t" + Const.exiftool_flag + " for exiftool\n" +
            "\t" + Const.avarage_hash_flag + " for average hash algorithm\n" +
            "\t" + Const.difference_hash_flag + " for difference hash algorithm (recommended)\n"
        )
        exit(1)

    cfg.flags = sys.argv[1]
    cfg.catalog_directory = sys.argv[2] 
    cfg.catalog_file_name = sys.argv[3]
    return cfg

def make_catalog(resolved_path, flags, old_catalog):
    catalog_paths = list(resolved_path.rglob("*"))
    catalog = []
    view = View()
    view.total_files = len(catalog_paths)
    print("Found {:_d} paths in {}.".format(view.total_files, make_elpsed_time_string(start_time)))

    for path in catalog_paths:
        relative_path = path.relative_to(resolved_path)
        view.file_count += 1
        if relative_path.is_dir() or is_ignored(relative_path) or not is_included(relative_path):
            view.printed_length = print_progress(relative_path, view, True)
            continue
        view.printed_length = print_progress(relative_path, view, False)
        fprop = {}
        try:
            info = path.stat()
            fprop.update(path_filter(path))
            new_key =  make_key(fprop, info.st_size)
            fprop.update(old_catalog.get(new_key, {}))
            fprop.update(basic_stat(info))

            view.total_size += info.st_size

            # md5 hash
            if Const.md5_hash_flag in flags and fprop.get(Const.field_md5_hash, "") == "":
                fprop[Const.field_md5_hash] = md5_hash(relative_path)
            # get date using exiftool
            shouldUpdateExif = fprop.get(Const.field_exiftool_duration, "") == "" and \
                fprop.get(Const.field_exiftool_date, "") == "" and \
                fprop.get(Const.field_exiftool_content_date, "") == ""
            if Const.exiftool_flag in flags and shouldUpdateExif:
                exiftool_result = exiftool(relative_path)
                fprop.update(exiftool_result)
            # image average hash
            if Const.avarage_hash_flag in flags and fprop.get(Const.field_image_average_hash, "") == "":
                fprop[Const.field_image_average_hash] = image_average_hash(relative_path)
            # image_difference_hash
            if Const.difference_hash_flag in flags and fprop.get(Const.field_image_difference_hash, "") == "":
                fprop[Const.field_image_difference_hash] = image_difference_hash(
                    relative_path)

            # add to catalog
            catalog.append(fprop)
        except KeyboardInterrupt:
            exit(1)
        except:
            if Const.debug not in flags:
                print("\nError ", sys.exc_info()[0], " occurred.")
                continue
            else:
                traceback.print_exc()
                exit(1)
    print("\n")
    
    return catalog

def make_key(file_attrs, size):
    return str(file_attrs[Const.field_path]) + file_attrs[Const.field_file_name] + str(size)

def make_old_catalog_hash(file):
    old_catalog_hash = {}
    if os.path.isfile(file):
        print("There already is a {} catalog. It will be updated with new values.".format(file))
        old_catalog = read(file)
        for file_attrs in old_catalog:
            key = make_key(file_attrs, file_attrs[Const.field_file_size])
            old_catalog_hash[key] = file_attrs
    return old_catalog_hash

def merge(old_hash, new):
    if len(old_hash) == 0:
        return new
    else:
        return new

def make_elpsed_time_string(start_time):
    time_total = time.time() - start_time
    time_minutes = int(time_total / 60)
    time_seconds = int(time_total % 60)
    mili_seconds = int(time_total * 1000)
    if time_minutes > 0:
        return("{}m {}s".format(time_minutes, time_seconds))
    elif time_seconds > 0:
        return("{}s".format(time_seconds))
    else:
        return("{}ms".format(mili_seconds))

# === START === #

start_time = time.time()
config = read_configuration()
old_catalog_hash = make_old_catalog_hash(config.catalog_file_name)
resolved_path = Path(config.catalog_directory).expanduser().resolve()
print("Reading {}".format(resolved_path))
new_catalog = make_catalog(resolved_path, config.flags, old_catalog_hash)

# writing to csv file
resolved_output_path = Path(config.catalog_file_name).expanduser().resolve()
write(resolved_output_path, new_catalog)

# done in ...
print("Done in " + make_elpsed_time_string(start_time))