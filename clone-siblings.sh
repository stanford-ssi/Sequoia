#!/bin/bash
for dir in avionics gnc software structures systems ; do
    git clone https://github.com/stanford-ssi/sequoia-$dir.git ../$dir
done