#!/bin/bash
DIR=$1 
DO_SETUP=$2

. /vols/cms/grid/setup.sh
#from https://twiki.cern.ch/twiki/bin/viewauth/CMS/LumiCalc
WD=$PWD
cd $DIR
REL=CMSSW_5_0_1
TAG=V04-01-09
PKG=RecoLuminosity/LumiDB

if $DO_SETUP; then
    scramv1 p CMSSW $REL
fi

cd $REL/src
eval `scram runtime -sh`

if $DO_SETUP; then
    cvs co  -r $TAG $PKG
    cd $PKG
    scramv1 b
fi

cd $WD
