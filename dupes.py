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

def dupes_catalog(catalog, headers_criteria, existing_key_values, max_dupes=2):
    catalog_with_duplicates = []
    for file_attrs in catalog:
        key = ""
        for header in headers_criteria:
            key += file_attrs.get(header, "")
        value = existing_key_values.get(key, 0)
        if value >= max_dupes:
            file_attrs["dupe_count"] = value
            file_attrs["org_full_path"] = existing_key_values.get(key+"file", "")
            catalog_with_duplicates.append(file_attrs)
    return catalog_with_duplicates

# === START === #

if len(sys.argv) != 4:
    print(f"Use ./dupes.py <header1,header2,...> <master_catalog.csv> <incoming_catalog.csv, it will output 'master_catalog.{Const.duplicates}.csv' and 'incoming_catalog.{Const.duplicates}.csv'")
    exit(1)

headers = sys.argv[1].split(",")
master_catalog_file = sys.argv[2]
incoming_catalog_file = sys.argv[3]

master_catalog = read(master_catalog_file)
incoming_catalog = read(incoming_catalog_file)

master_kv = {}
incoming_unique_catalog = []
incoming_duplicates_catalog = []

for master_file_attrs in master_catalog:
    key = ""
    for header in headers:
        key += master_file_attrs[header]
    master_kv[key] = master_kv.get(key, 0) + 1
    master_kv[key+"file"] = master_file_attrs["path"] + "/" + master_file_attrs["file_name"]

master_catalog_with_duplicates = dupes_catalog(master_catalog, headers, master_kv)
master_duplicates_file = append_suffix(master_catalog_file, Const.duplicates)
write(master_duplicates_file, master_catalog_with_duplicates)

incoming_catalog_with_duplicates = dupes_catalog(incoming_catalog, headers, master_kv, 1)
incoming_duplicates_file = append_suffix(incoming_catalog_file, Const.duplicates)
write(incoming_duplicates_file, incoming_catalog_with_duplicates)
