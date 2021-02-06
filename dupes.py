#!/usr/bin/env python3.8

import csv
import sys
import os

# takes 2 inputs and outputs 2 cvs files -> one with unique files, and the other with duplicates
class Const:
    files_separator = "/"
    duplicates = "dupe"
    incoming_unique = "uniq"

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
    print("Writing to {}".format(file))
    with open(file, 'w') as file_handler:
        # creating a csv dict writer object
        writer = csv.DictWriter(
            file_handler, fieldnames=list(catalog[0].keys()))

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(catalog)

def append_suffix(file, suffix):
    name = os.path.splitext(file)[0]
    extension = os.path.splitext(file)[1]
    return name + "." + suffix + extension

# === START === #

if len(sys.argv) != 3:
    print(f"Use ./dupes.py <header1,header2,...> <master_catalog.csv> <incoming_catalog.csv, it will output 'master_catalog.{Const.duplicates}.csv' and '{Const.incoming_unique}'")
    exit(1)

headers = sys.argv[1].split(",")
master_catalog_file = sys.argv[2]
# incoming_catalog_file = sys.argv[3]

master_catalog = read(master_catalog_file)
# incoming_catalog = read(incoming_catalog_file)

master_kv = {}
incoming_unique_catalog = []
incoming_duplicates_catalog = []


for master_file_attrs in master_catalog:
    key = ""
    for header in headers:
        key += master_file_attrs[header]
    value = master_kv.get(key, "")
    if len(value) > 0:
        value += Const.files_separator
    value += master_file_attrs["file_name"]
    master_kv[key] = value

master_catalog_with_duplicates = []
for master_file_attrs in master_catalog:
    key = ""
    for header in headers:
        key += master_file_attrs[header]
    value = master_kv.get(key, "")
    if Const.files_separator in value:
        master_file_attrs["is_dupe"] = value
        master_catalog_with_duplicates.append(master_file_attrs)

master_duplicates_file = append_suffix(master_catalog_file, Const.duplicates)
write(master_duplicates_file, master_catalog_with_duplicates)

# print(master_kv)
# write("master_kv.csv", [{"md5": "","file":""}, master_kv])

# for incoming_file_attributes in incoming_catalog:

#     is_duplicate = False
#     for master_file_attributes in master_catalog:
#         if incoming_file_attributes['md5_hash'] == master_file_attributes['md5_hash']:
#             print(master_file_attributes['file_name'])
#             incoming_file_attributes['is_duplicate'] += master_file_attributes['path'] + "/" + master_file_attributes['file_name']
#             incoming_file_attributes['command'] += "rm -v \"" + incoming_file_attributes['path'] + "/" + incoming_file_attributes['file_name'] + "\""
#             incoming_duplicates_catalog.append(incoming_file_attributes)
#             is_duplicate = True
#             break
#     if not is_duplicate:
#         incoming_unique_catalog.append(incoming_file_attributes)

# write(Const.duplicates, incoming_duplicates_catalog)
# write(Const.incoming_unique, incoming_unique_catalog)