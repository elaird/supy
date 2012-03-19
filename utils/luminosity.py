#!/usr/bin/env python

import sys,os,tempfile,configuration
import __init__ as utils

try:
    from RecoLuminosity.LumiDB import lumiCalcAPI,sessionManager,lumiCorrections
except:
    pass

def recordedInvMicrobarns(json) :
    jsonALT = dict([(int(run),sum([range(begin,end+1) for begin,end in lumis],[])) for run,lumis in json.items()])

    session = sessionManager.sessionManager("frontier://LumiCalc/CMS_LUMI_PROD").openSession( cpp2sqltype = [('unsigned int','NUMBER(10)'),('unsigned long long','NUMBER(20)')])
    session.transaction().start(True)
    lumidata = lumiCalcAPI.lumiForRange( session.nominalSchema(),
                                         jsonALT,
                                         norm = 1.0,
                                         finecorrections = lumiCorrections.pixelcorrectionsForRange(session.nominalSchema(),jsonALT.keys()),
                                         lumitype='PIXEL',
                                         branchName='DATA')
    return sum( sum(data[6] for data in lumis) for run,lumis in lumidata.iteritems() if lumis)

def recordedInvMicrobarnsShotgun(jsons, cores = 2, cacheDir = './' ) :
    pickles = ["%s/%d.pickle"%(cacheDir,hash(str(sorted([(key,val) for key,val in json.iteritems()])))) for json in jsons]
    def worker(pickle, json) :
        if not os.path.exists(pickle) : utils.writePickle(pickle, recordedInvMicrobarns(json))
    utils.operateOnListUsingQueue(cores, utils.qWorker(worker), zip(pickles,jsons))
    return [utils.readPickle(pickle) for pickle in pickles ]

if __name__=='__main__' :
    print
    if len(sys.argv)<2 : print 'Pass list of "{json}" and/or filenames as argument'; sys.exit(0)

    def output(arg) :
        json = eval(arg if '{' in arg else open(arg).readline())
        lumi = recordedInvMicrobarns(json)
        print "%.4f/pb in %s"%(lumi/1e6,arg)
        print
    utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(output), [(a,) for a in sys.argv[1:]])
