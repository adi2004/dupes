#!/usr/bin/env python3

import subprocess
import sys
import re

file = sys.argv[1]

output = subprocess.getoutput(
    'exiftool -d "%Y.%m.%d %H.%M.%S" -Duration -ContentCreateDate -CreateDate "' + file + '"')
output = output.splitlines()
for line in output:
    print(line)
    if line.startswith("Duration"):
        line = re.sub("^.*: ", "", line)
        print("SAVE:" + line + "/")
    elif line.startswith("Content"):
        line = re.sub("^.*: ", "", line)
        if line.startswith("19") or line.startswith("20"):
            print("SAVE:" + line + "/")
    elif line.startswith("Create"):
        line = re.sub("^.*: ", "", line)
        if line.startswith("19") or line.startswith("20"):
            print("SAVE:" + line + "/")
