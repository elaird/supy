#####################################
from stepsOther import *
from stepsJet import *
from stepsTrigger import *
from stepsPhoton import *
from stepsPrint import *
from stepsGen import *
from stepsXclean import *
#####################################
def adjustStepsForMc(inSteps) :
    dummyBX=bxFilter([])
    dummyPhysDecl=physicsDeclared()
    dummyTechBit0=techBitFilter([0],True)
    dummyDisplayer=displayer()
    dummyHltFilter=hltFilter("")
    dummyHbheNoiseFilter=hbheNoiseFilter()
    outSteps=[]
    for step in inSteps :
        disable = False
        #determine whether to disable
        if type(step) in [hltFilter,       #temporary hack
                          hltFilterList,   #temporary hack
                          lowestUnPrescaledTrigger, #temporary hack
                          hbheNoiseFilter, #temporary hack
                          bxFilter,
                          physicsDeclared] : disable = True
        if step.moreName == dummyTechBit0.moreName : disable = True
        outSteps.append(copy.deepcopy(step))
        if disable : outSteps[-1].disable()

        #turn on gen stuff
        if type(step) == displayer : outSteps[-1].switchGenOn()
    return outSteps
#####################################
def adjustStepsForData(inSteps) :
    outSteps=[]
    for step in inSteps :
        disable = False
        #determine whether to disable
        if type(step) == histogrammer and "genpthat" in step.var : disable = True
        if type(step) == genMotherHistogrammer : disable = True
        if type(step) == photonPurityPlots : disable = True
        outSteps.append(copy.deepcopy(step))
        if disable : outSteps[-1].disable()        
    return outSteps
#####################################
def insertPtHatFilter(inSteps,value) :
    inSteps.insert(0,ptHatFilter(value))
    inSteps[0].ignore()
#####################################
