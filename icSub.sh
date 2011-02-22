#!/bin/bash

Q="hepshort.q"
#Q="hepmedium.q"
#Q="heplong.q"

export X509_USER_PROXY=/home/hep/$USER/.MyProxy
qsub  -q $Q $1
