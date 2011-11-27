#!/usr/bin/env python

import sys,os,tempfile
from supy import configuration,sites,utils
sys.path.extend([sites.info(key="CMSSW_lumi")])

try:
    from RecoLuminosity.LumiDB import lumiQueryAPI,inputFilesetParser
except: pass

def jsonToIFP(json) :
    with tempfile.NamedTemporaryFile() as file :
        print >> file, str(json).replace("'",'"')
        file.flush()
        return inputFilesetParser.inputFilesetParser(file.name)

def recordedInvMicrobarns(json) :
    pars = lumiQueryAPI.ParametersObject()
    pars.noWarnings  = True
    pars.norm        = 1.0
    pars.lumiversion = '0001'
    pars.beammode    = 'STABLE BEAMS'

    session,svc =  lumiQueryAPI.setupSession( connectString = 'frontier://LumiCalc/CMS_LUMI_PROD',
                                              parameters = pars, siteconfpath = None, debug = False)
    lumidata =  lumiQueryAPI.recordedLumiForRange (session, pars, jsonToIFP(json))    
    return sum(lumiQueryAPI.calculateTotalRecorded(dataperRun[2]) for dataperRun in lumidata if dataperRun[1])

def recordedInvMicrobarnsShotgun(jsons, cores = 2, cacheDir = './' ) :
    pickles = ["%s/%d.pickle"%(cacheDir,hash(str(sorted([(key,val) for key,val in json.iteritems()])))) for json in jsons]
    def worker(pickle, json) :
        if not os.path.exists(pickle) : utils.writePickle(pickle, recordedInvMicrobarns(json))
    utils.operateOnListUsingQueue(cores, utils.qWorker(worker), zip(pickles,jsons))
    return [utils.readPickle(pickle) for pickle in pickles ]

if __name__=='__main__' :
    print
    from supy import utils
    if len(sys.argv)<2 : print 'Pass list of "{json}" and/or filenames as argument'; sys.exit(0)

    def output(arg) :
        json = eval(arg if '{' in arg else open(arg).readline())
        lumi = recordedInvMicrobarns(json)
        print "%.4f/pb in %s"%(lumi/1e6,arg)
        print
    utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(output), [(a,) for a in sys.argv[1:]])
