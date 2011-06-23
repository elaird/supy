import sys,os,tempfile
import configuration
sys.path.extend([configuration.siteInfo(key="CMSSW_lumi")])

from RecoLuminosity.LumiDB import lumiQueryAPI,inputFilesetParser

def jsonToIFP(json) :
    with tempfile.NamedTemporaryFile() as file :
        print >> file, str(json).replace("'",'"')
        file.flush()
        ifp = inputFilesetParser.inputFilesetParser(file.name)
    return ifp

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
