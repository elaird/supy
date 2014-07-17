export SCRAM_ARCH=slc5_amd64_gcc434
source /vols/cms/grid/setup.sh
export LD_PRELOAD=""
#cd /vols/sl5_exp_software/cms/${SCRAM_ARCH}/cms/cmssw/CMSSW_4_2_8/src && eval `scram runtime -sh` && cd - >& /dev/null 
#cd /vols/sl5_exp_software/cms/slc5_amd64_gcc434/cms/cmssw-patch/CMSSW_4_4_3_patch1 && eval `scram runtime -sh` && cd - >& /dev/null 
#cd /home/hep/bbetchar/work/CMSSW_5_0_1_patch3/src && eval `scram runtime -sh` && cd - >& /dev/null # vanilla + HEAD of RecoLuminosity/LumiDB (Sun Feb 26 19:29:00 EST 2012) for pixel lumi
cd /home/hep/bbetchar/work/CMSSW_4_4_3_patch1/src && eval `scram runtime -sh` && cd - >& /dev/null # vanilla + HEAD of RecoLuminosity/LumiDB (Mon Mar 5 13:50:00 EST 2012) for pixel lumi
export FRONTIER_FORCERELOAD=long # part of pixel lumi

#INSERT_BATCH_SETUP
