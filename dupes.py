# import os

# with os.scandir() as dir_entries:
#     for entry in dir_entries:
#         info = entry.stat()
#         print(info.st_mtime)

import sys
from pathlib import Path
from datetime import datetime
import hashlib 

def dt(timestamp):
    return datetime.fromtimestamp(timestamp).isoformat()

def hash(filename):
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

result = list(Path(sys.argv[1]).rglob("*"))
# print(result)
hash_list = set(())
print(f"path,fname,mtime,ctime,atime,size,md5,dupe")
for path in result: #Path('.').iterdir():
    if path.is_dir():
        continue
    pathString = f"{path.parent}"
    if ".git" in pathString:
        continue
    if "@eaDir" in pathString:
        continue
    info = path.stat()
    file_path = f"{path.parent}/{path.name}"
    md5_hash = hash(file_path)
    dupe = md5_hash in hash_list
    command = ""
    if dupe:
        command = f'echo rm "{file_path}"'
    print(f"{path.parent},{path.name},{dt(info.st_mtime)},"+
    f"{dt(info.st_ctime)},{dt(info.st_atime)},{info.st_size},"+
    f"{md5_hash},{dupe},{command}")
    hash_list.add(md5_hash)