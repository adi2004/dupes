#!/usr/bin/env python3

import csv
import sys
import os
from common import Const, read, write, append_suffix

# takes 2 inputs and outputs 2 cvs files -> one with unique files, and the other with duplicates

def dupes_catalog(catalog, headers_criteria, existing_key_values, max_dupes=2):
    catalog_with_duplicates = []
    for file_attrs in catalog:
        key = ""
        for header in headers_criteria:
            key += file_attrs.get(header, "")
        if len(key) == 0:
            continue
        duplicate_files = existing_key_values.get(key, [])
        if len(duplicate_files) >= max_dupes:
            file_attrs["dupe_count"] = len(duplicate_files)
            duplicate_files[0]["cmd"] = ""
            catalog_with_duplicates.append(file_attrs)
    return catalog_with_duplicates

# === START === #

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print(f"Use ./dupes.py <header1,header2,...> <master_catalog.csv> <incoming_catalog.csv>, it will output 'master_catalog.{Const.duplicates}.csv' and 'incoming_catalog.{Const.duplicates}.csv'")
    exit(1)

headers = sys.argv[1].split(",")
master_catalog_file = sys.argv[2]
master_catalog = read(master_catalog_file)

# create a dictionary where on the key is the duplication criteria, and the value is an array with the file attributes
master_kv = {}
for master_file_attrs in master_catalog:
    key = ""
    for header in headers:
        key += master_file_attrs.get(header, "")
    dupes = master_kv.get(key, []) + [master_file_attrs]
    dupes.sort(key=lambda k: k['modified_time'], reverse=True)
    dupes.sort(key=lambda k: int(k['file_size']), reverse=True)
    for dupe in dupes:
        dupe_path = '"dupes/' + dupe["path"] + '"'
        dupe["cmd"] = 'mkdir -p ' + dupe_path + ' && mv "' + dupe["path"] + "/" + dupe["file_name"] + '" ' + dupe_path
    master_kv[key] = dupes

master_catalog_with_duplicates = dupes_catalog(master_catalog, headers, master_kv)
master_duplicates_file = append_suffix(master_catalog_file, Const.duplicates)
master_catalog_with_duplicates.sort(key=lambda k: k['modified_time'], reverse=True)
master_catalog_with_duplicates.sort(key=lambda k: int(k['file_size']), reverse=True)
if 'md5_hash' in master_catalog_with_duplicates:
    master_catalog_with_duplicates.sort(key=lambda k: k['md5_hash'])
write(master_duplicates_file, master_catalog_with_duplicates)

# find duplicates in the second catalog if they exist in the first catalog
if len(sys.argv) == 4:
    incoming_catalog_file = sys.argv[3]
    incoming_catalog = read(incoming_catalog_file)
    incoming_catalog_with_duplicates = dupes_catalog(incoming_catalog, headers, master_kv, 1)
    incoming_duplicates_file = append_suffix(incoming_catalog_file, Const.duplicates)
    write(incoming_duplicates_file, incoming_catalog_with_duplicates)
