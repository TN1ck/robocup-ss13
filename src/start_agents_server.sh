#!/bin/bash

rcssserver3d &

if command -v ./roboviz.sh >/dev/null 2>&1; then
  ./roboviz.sh &
else
  rcsoccersim3d &
fi

for i in `seq 1 11`; do
  # Executes agents asynchronously
  $RCAGENT/agent.py $i &
  # Print process id of every agent in order that you can kill them
  echo $! >> $RCAGENT/.kill_info
  sleep 2s
done
