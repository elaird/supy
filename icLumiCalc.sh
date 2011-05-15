#!/bin/bash

DIR=$1
JSONFILENAME=$2

#from https://twiki.cern.ch/twiki/bin/viewauth/CMS/LumiCalc
export SCRAM_ARCH=slc5_ia32_gcc434
REL=CMSSW_3_8_7_patch2
TAG=V02-01-03
PKG=RecoLuminosity/LumiDB

cd $DIR
scramv1 p CMSSW $REL
cd $REL/src
cvs co -r $TAG $PKG
cd $PKG
scramv1 b
eval `scram runtime -sh`
lumiCalc.py -c frontier://LumiProd/CMS_LUMI_PROD -i $JSONFILENAME overview
