#!/bin/bash

for i in `seq 1 6`; do
  # Executes agents asynchronous
  ./agent.py i &
  # Print process id of every agent in order that you can kill them
  echo $!
done