# Purpose
Find and remove duplicate files.

# Workflow
1. I need to know what files are on a CD, directory, remote folder
2. I need to delete duplicate files and images
3. I should be able to say how a file is marked as duplicate
4. When new files are added to a directory, I should know about them

I keep my files in one storage.

I want to manually add new files from some remote directory, to my storage, but some files are aready there so I should spot them.

On the remote drive some changes can occur, maybe some files are added, modifyed or deleted, I want to take the new files.

Needs also exiftool.

# Operations

catalog.py
   - catalogs the files in a directory and outputs them to a csv file. Also calculates hashes.
dupes.py 
   - find duplicate files in a csv files based on the given columns as a criteria
   - find files that are in an incoming catalog based on a master catalog using user criteria (i.e. same md5 hash or other form of hash)
prune.py
   - prune a catalog (remove files that do not exist anymore)
# Improvements Ideeas

   - merge 2 catalogs togheter (needed to skip recalculating hashes). 2 file are the same based on criteria or based on path. the existing and new fields are taken from second catalog and put in the first
   - create some sort of UI or CLI
   - add tests