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
        value = existing_key_values.get(key, 0)
        if value >= max_dupes:
            file_attrs["dupe_count"] = value
            file_attrs["org_full_path"] = existing_key_values.get(key+"org_full_path", "")
            catalog_with_duplicates.append(file_attrs)
    return catalog_with_duplicates

# === START === #

if len(sys.argv) != 4:
    print(f"Use ./dupes.py <header1,header2,...> <master_catalog.csv> <incoming_catalog.csv, it will output 'master_catalog.{Const.duplicates}.csv' and 'incoming_catalog.{Const.duplicates}.csv'")
    exit(1)

headers = sys.argv[1].split(",")
master_catalog_file = sys.argv[2]
master_catalog = read(master_catalog_file)
master_kv = {}
for master_file_attrs in master_catalog:
    key = ""
    for header in headers:
        key += master_file_attrs[header]
    master_kv[key] = master_kv.get(key, 0) + 1
    master_kv[key+"org_full_path"] = master_file_attrs["path"] + "/" + master_file_attrs["file_name"]

master_catalog_with_duplicates = dupes_catalog(master_catalog, headers, master_kv)
master_duplicates_file = append_suffix(master_catalog_file, Const.duplicates)
write(master_duplicates_file, master_catalog_with_duplicates)

incoming_catalog_file = sys.argv[3]
incoming_catalog = read(incoming_catalog_file)
incoming_catalog_with_duplicates = dupes_catalog(incoming_catalog, headers, master_kv, 1)
incoming_duplicates_file = append_suffix(incoming_catalog_file, Const.duplicates)
write(incoming_duplicates_file, incoming_catalog_with_duplicates)
