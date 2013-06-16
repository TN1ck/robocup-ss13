#!/bin/bash

for i in `seq 1 6`; do
  # Executes agents asynchronously
  ./agent.py $i &
  # Print process id of every agent in order that you can kill them
  echo $! >> .kill_info
  sleep 1s
done