#!/usr/bin/env python3

import sys
import os
from common import read, write, Const, append_suffix

if len(sys.argv) != 3:
    print("Use ./prune.py <dir-to-catalog> <catalog_file.csv>")
    exit(1)

catalog_directory = sys.argv[1]
catalog_file_name = sys.argv[2]

print("Reading {}/{}".format(os.getcwd(), catalog_file_name))

catalog = read(catalog_file_name)
catalog_pruned = []

for file in catalog:
    full_path = os.path.join(catalog_directory, file["path"], file["file_name"])
    if os.path.exists(full_path):
        catalog_pruned.append(file)
    else:
        print(full_path + " was pruned")

catalog_pruned_file_name = append_suffix(catalog_file_name, Const.pruned)
write(catalog_pruned_file_name, catalog_pruned)