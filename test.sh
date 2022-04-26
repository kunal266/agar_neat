#!/bin/bash

files=$(ls checkpoints_1/done)
for file in $files; do
    if [[ ($file =~ .*.pkl) ]]; 
    then echo $file ; WINNER_FILE_NAME=$file python3 main.py 0 0 0 ./checkpoints_1/history/$file
    fi
done
