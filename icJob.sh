export SCRAM_ARCH=slc5_amd64_gcc434
source /vols/cms/grid/setup.sh
export LD_PRELOAD=""
cd /vols/sl5_exp_software/cms/${SCRAM_ARCH}/cms/cmssw/CMSSW_4_1_3/src && eval `scram runtime -sh` && cd - >& /dev/null
#export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
