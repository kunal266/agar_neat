#!/bin/bash

# USAGE: <IS_TRAIN> <NUM_GENERATIONS> <NUM_SERVERS> <CONT_TRAIN> <CHECKPOINT_FILE_NAME>
python3 main.py 1 100 3 ./checkpoints_1/checkpoint-72
# python3 main.py 1 500 7

# echo "y" | docker container prune
