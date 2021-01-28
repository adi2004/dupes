import csv
import sys

master_catalog_file = sys.argv[1]
incoming_catalog_file = sys.argv[2]

def read(file):
    catalog = []
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            catalog.append(row)
    return catalog

master_catalog = read(master_catalog_file)
incoming_catalog = read(incoming_catalog_file)

incoming_unique_catalog = []
duplicates_catalog = []

for incoming_file_attributes in incoming_catalog:
    is_duplicate = False
    for master_file_attributes in master_catalog:
        if incoming_file_attributes['md5_hash'] == master_file_attributes['md5_hash']:
            print(master_file_attributes['file_name'])
            incoming_file_attributes['is_duplicate'] += master_file_attributes['path'] + "/" + master_file_attributes['file_name']
            incoming_file_attributes['command'] += "rm -v \"" + incoming_file_attributes['path'] + "/" + incoming_file_attributes['file_name'] + "\""
            duplicates_catalog.append(incoming_file_attributes)
            is_duplicate = True
            break
    if not is_duplicate:
        incoming_unique_catalog.append(incoming_file_attributes)


duplicates = "duplicates.csv"
fields = ["path_part_1", "path_part_2", "path_part_3",'file_extension',
    "path", "file_name",
    'modified_time',
    'file_size',
    'md5_hash', 'exiftool_time',
    'is_duplicate', 'command']
with open(duplicates, 'w') as duplicates_file_handler: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(duplicates_file_handler, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(duplicates_catalog) 

incoming_unique = "incoming_unique.csv"
with open(incoming_unique, 'w') as duplicates_file_handler: 
    # creating a csv dict writer object 
    writer = csv.DictWriter(duplicates_file_handler, fieldnames = fields) 
      
    # writing headers (field names) 
    writer.writeheader() 
      
    # writing data rows 
    writer.writerows(incoming_unique_catalog) 