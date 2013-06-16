#!/bin/bash

for i in `cat .kill_info`; do
  kill -INT $i
done

rm .kill_info