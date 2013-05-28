#!/bin/bash

for i in `cat .kill_info`; do
  kill $i
done

rm .kill_info