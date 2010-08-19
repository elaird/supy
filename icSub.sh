#!/bin/bash

Q="hep.q"
export X509_USER_PROXY=/home/hep/$USER/.MyProxy
qsub  -q $Q $1
