export SCRAM_ARCH=slc5_amd64_gcc434
source /vols/cms/grid/setup.sh
export LD_PRELOAD=""
cd /home/hep/bbetchar/work/CMSSW_5_0_1_patch3/src && eval `scram runtime -sh` && cd - >& /dev/null # vanilla + HEAD of RecoLuminosity/LumiDB (Sun Feb 26 19:29:00 EST 2012) for pixel lumi
export FRONTIER_FORCERELOAD=long # part of pixel lumi
#export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
