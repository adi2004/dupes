#!/usr/bin/env python3.8

import sys
from pathlib import Path
from datetime import datetime
import time
import hashlib 
import csv
import re
import subprocess
from PIL import Image
import imagehash
import os

if len(sys.argv) != 3:
    print("Use ./catalog.py <dir-to-catalog> <catalog-file.csv")
    exit(1)

fields = [
    "path_part_1", "path_part_2", "path_part_3",'file_extension',
    "path", "file_name",
    'modified_time',
    'file_size',
    'md5_hash', 'exiftool_time', 'image_hash', 'similarity',
    'is_duplicate', 'command'
]

class FileProperties:
    path_part_1 = "" 
    path_part_2 = "" 
    path_part_3 = ""
    file_extension = ""
    path = "" 
    file_name = "" 
    modified_time = "" 
    creation_time = "" 
    access_time = "" 
    file_size = ""
    md5_hash = "" 
    exiftool_time = "" 
    image_hash = ""
    similarity = ""
    is_duplicate = "" 
    command = ""

    def asdict(self):
        return { 
            'path_part_1': self.path_part_1, 'path_part_2': self.path_part_2, 'path_part_3': self.path_part_3, 'file_extension': self.file_extension,
            'path': self.path, 'file_name': self.file_name, 
            'modified_time': self.modified_time,
            'file_size': self.file_size, 
            'md5_hash': self.md5_hash, 'exiftool_time': self.exiftool_time,  'image_hash': self.image_hash, 'similarity': self.similarity,
            'is_duplicate': self.is_duplicate, 'command': self.command}

exclude_list = [".git", "@eaDir", "backup", "incoming"]

def is_ignored(path):
    path_string = str(path.parent)
    for exclude_keyword in exclude_list:
        if exclude_keyword in path_string:
            return True
    return False

def dt(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d %H.%M.%S")

def md5_hash(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

def exiftool_date(filename):
    date_output = subprocess.getoutput('exiftool -CreateDate "{}"'.format(file_with_path))
    date_trimmed = re.sub("^.*: ", "", date_output)
    date_trimmed = re.sub(":", ".", date_trimmed)
    if date_trimmed.startswith("20") or date_trimmed.startswith("19"):
        return date_trimmed
    return ""

def image_hash(filename):
    hash_size = 8
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return ""
    with Image.open(filename) as img:
        hash = imagehash.average_hash(img, hash_size)
        return hash
    return ""

start_time = time.time()
catalog_directory = sys.argv[1]
catalog_file_name = sys.argv[2]
print("Reading {}".format(catalog_directory))

catalog_paths = list(Path(catalog_directory).rglob("*"))

catalog = []

file_count = 0
progress = ["|", "/", "-", "|", "\\"]
for path in catalog_paths:
    if path.is_dir() or is_ignored(path):
        continue
    file_count += 1
    info = path.stat()
    file_with_path = "{}/{}".format(path.parent, path.name)
    file_name = str(path.name)
    file_properties = FileProperties()
    # populate filter criteria
    path_parent = re.sub("^[./]+", "", str(path.parent))
    print("\rFound {} files {} reading from {}".format(file_count, progress[file_count % 5], path_parent[0:60] + " "*20), end="")
    paths = path_parent.split("/")
    if len(paths) > 0:
        file_properties.path_part_1 = paths[0]
    if len(paths) > 1:
        file_properties.path_part_2 = paths[1]
    if len(paths) > 2:
        file_properties.path_part_3 = paths[2]
    file_properties.file_extension = file_name.split(".")[-1] 

    # populate path and file_name
    file_properties.path =  path.parent
    file_properties.file_name = path.name

    # populate file dates
    file_properties.modified_time = dt(info.st_mtime)
    file_properties.created_time = dt(info.st_ctime)
    file_properties.access_time = dt(info.st_atime)

    # size
    file_properties.file_size = info.st_size
    # md5 hash
    file_properties.md5_hash = md5_hash(file_with_path)
    # get date using exiftool
    file_properties.exiftool_time = exiftool_date(file_with_path)
    #image hash
    file_properties.image_hash = image_hash(file_with_path)

    # add to catalog
    catalog.append(file_properties.asdict())

print("\n")

# writing to csv file 
print("Writing to {}".format(catalog_file_name))
with open(catalog_file_name, 'w') as catalog_file_handler: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(catalog_file_handler, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(catalog) 

time_total = time.time() - start_time
time_minutes = int(time_total / 60)
time_seconds = int(time_total % 60)
print("Done in {}m {}s".format(time_minutes, time_seconds))