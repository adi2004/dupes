import sys
from pathlib import Path
from datetime import datetime
import hashlib 
import csv
import re
import subprocess

fields = ["path_part_1", "path_part_2", "path_part_3",'file_extension',
    "path", "file_name",
    'modified_time',
    'file_size',
    'md5_hash', 'exiftool_time',
    'is_duplicate', 'command']

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
    is_duplicate = "" 
    command = ""

    def asdict(self):
        return { 
            'path_part_1': self.path_part_1, 'path_part_2': self.path_part_2, 'file_extension': self.file_extension,
            'path': self.path, 'file_name': self.file_name, 
            'modified_time': self.modified_time,
            'file_size': self.file_size, 
            'md5_hash': self.md5_hash, 'exiftool_time': self.exiftool_time, 
            'is_duplicate': self.is_duplicate, 'command': self.command}

exclude_list = [".git", "@eaDir", "backup", "incoming"]

def is_ignored(path):
    path_string = f"{path.parent}"
    for exclude_keyword in exclude_list:
        if exclude_keyword in path_string:
            return True
    return False

def dt(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def hash(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

catalog_directory = sys.argv[1]
catalog_file_name = sys.argv[2]
print(f"Reading {catalog_directory}")

catalog_paths = list(Path(catalog_directory).rglob("*"))

catalog = []

file_count = 0
progress = ["|", "/", "-", "|", "\\"]
for path in catalog_paths:
    if path.is_dir() or is_ignored(path):
        continue
    file_count += 1
    info = path.stat()
    file_properties = FileProperties()
    # populate filter criteria
    path_parent = re.sub("^[./]+", "", f"{path.parent}")
    print(f"Found {file_count} files {progress[file_count % 5]} reading from {path_parent[0:60]}\r", end="")
    paths = path_parent.split("/")
    if len(paths) > 0:
        file_properties.path_part_1 = paths[0]
    if len(paths) > 1:
        file_properties.path_part_2 = paths[1]
    if len(paths) > 2:
        file_properties.path_part_3 = paths[2]
    file_name = f"{path.name}"
    file_properties.file_extension = file_name.split(".")[-1] 
    # populate path and file_name
    file_properties.path =  path.parent
    file_properties.file_name = path.name
    # populate file dates
    file_properties.modified_time = dt(info.st_mtime)
    file_properties.created_time = dt(info.st_ctime)
    file_properties.access_time = dt(info.st_atime)
    # populate duplication criteria
    file_properties.file_size = info.st_size
    file_with_path = f"{path.parent}/{path.name}"
    file_properties.md5_hash = hash(file_with_path)

    # get date using exiftool
    date_output = subprocess.getoutput(f'exiftool -CreateDate "{file_with_path}"')
    date_trimmed = re.sub("^.*: ", "", date_output)
    date_trimmed = re.sub(":", ".", date_trimmed)
    if date_trimmed.startswith("20") or date_trimmed.startswith("19"):
        file_properties.exiftool_time = date_trimmed
    # add to catalog
    catalog.append(file_properties.asdict())

print("\n")

# writing to csv file 
print(f"Writing to {catalog_file_name}")
with open(catalog_file_name, 'w') as catalog_file_handler: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(catalog_file_handler, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(catalog) 

# steps: use cvs module for writing cvs file
# correctly mark files as duplicates
# write to file