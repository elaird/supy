#!/bin/bash

# 'bqueues -u $USER' gives you a list of queues that you can use.
Q="8nh"
bsub -q $Q $1
