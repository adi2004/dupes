#! /bin/bash

rsync -av . /Volumes/photo/incoming/test --exclude={'@*','.git/'} 

