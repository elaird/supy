export VO_CMS_SW_DIR=/sharesoft/cmssw
export SCRAM_ARCH=slc5_amd64_gcc434
. $VO_CMS_SW_DIR/cmsset_default.sh
. /sharesoft2/osg/ce/setup.sh

cd /sharesoft/cmssw/slc5_amd64_gcc434/cms/cmssw-patch/CMSSW_4_2_8_patch7 && eval `scram runtime -sh` && cd - >& /dev/null

#INSERT_BATCH_SETUP
