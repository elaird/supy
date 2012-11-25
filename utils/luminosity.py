#!/usr/bin/env python

import supy
import sys,os,tempfile,configuration
import __init__ as utils

def cvsEnv() :
    return '\n'.join(['export CVSROOT=$USER@cmscvs.cern.ch:/cvs_server/repositories/CMSSW',
                      'export CVS_RSH=ssh',
                      '. /vols/cms/grid/setup.sh'
                      ])

def lumiEnv(initialize=True) :
    return ". %s/%s %s %s"%(supy.whereami(),
                            supy.sites.lumiEnvScript(),
                            supy.sites.info(key='globalOutputDir'),
                            'true' if initialize else 'false')

def recordedInvMicrobarns(json, initialize=True) :
    with tempfile.NamedTemporaryFile('w') as jsonFile :
        print >> jsonFile, str(json).replace("'",'"')
        jsonFile.flush()
        csvFileName = jsonFile.name + '.csv'
        commands = [cvsEnv(),
                    lumiEnv(initialize),
                    'lumiCalc2.py overview -i %s -o %s > /dev/null'%(jsonFile.name,csvFileName)]
        os.system('\n'.join(commands))
    
    if not json : return 0.0
    with open(csvFileName) as f :
        os.remove(csvFileName)
        return sum([float(l.split(',')[-1]) for l in f.readlines(100000) if l[:3]!='Run'])
    
def recordedInvMicrobarnsShotgun(jsons, cores = 2, cacheDir = './' ) :
    os.system('\n'.join([cvsEnv(),lumiEnv(True)]))
    pickles = ["%s/%d.pickle"%(cacheDir,hash(str(sorted([(key,val) for key,val in json.iteritems()])))) for json in jsons]
    def worker(pickle, json) :
        if not os.path.exists(pickle) : utils.writePickle(pickle, recordedInvMicrobarns(json))
    utils.operateOnListUsingQueue(cores, utils.qWorker(worker), zip(pickles,jsons))
    return [utils.readPickle(pickle) for pickle in pickles ]

if __name__=='__main__' :
    print
    if len(sys.argv)<2 : print 'Pass list of "{json}" and/or filenames as argument'; sys.exit(0)
    os.system('\n'.join([cvsEnv(),lumiEnv(True)]))
    
    def output(arg) :
        json = eval(arg if '{' in arg else open(arg).readline())
        lumi = recordedInvMicrobarns(json,False)
        print "%.4f/pb in %s"%(lumi/1e6,arg)
        print
    utils.operateOnListUsingQueue(configuration.nCoresDefault(), utils.qWorker(output), [(a,) for a in sys.argv[1:]])
