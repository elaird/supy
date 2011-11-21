#!/bin/bash

Q="hepshort.q"
#Q="hepmedium.q"
#Q="heplong.q"

#hepshort.q :  1 hour,  352 cores
#hepmedium.q : 6 hours, 124 cores
#heplong.q :  72 hours,  60 cores

export X509_USER_PROXY=/home/hep/$USER/.MyProxy
qsub -q $Q $1
