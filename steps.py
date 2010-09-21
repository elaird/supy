#####################################
from stepsOther import *
from stepsJet import *
from stepsTrigger import *
from stepsPhoton import *
from stepsPrint import *
from stepsGen import *
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
        if step.__doc__==dummyHltFilter.__doc__ : disable = True #temporary hack
        if step.__doc__==dummyHbheNoiseFilter.__doc__ : disable = True #temporary hack
        if step.__doc__==dummyBX.__doc__ : disable = True
        if step.__doc__==dummyPhysDecl.__doc__ : disable = True
        if step.moreName==dummyTechBit0.moreName : disable = True
        outSteps.append(copy.deepcopy(step))
        if disable : outSteps[-1].disable()

        #turn on gen stuff
        if step.__doc__==dummyDisplayer.__doc__ : outSteps[-1].switchGenOn()
    return outSteps
#####################################
def adjustStepsForData(inSteps) :
    outSteps=[]
    for step in inSteps :
        disable = False
        #determine whether to disable
        if type(step) == histogrammer and "genpthat" in step.var : disable = True
        if type(step) == genMotherHistogrammer : disable = True
        outSteps.append(copy.deepcopy(step))
        if disable : outSteps[-1].disable()        
    return outSteps
#####################################
def insertPtHatFilter(inSteps,value) :
    inSteps.insert(0,ptHatFilter(value))
    inSteps[0].ignore()
#####################################
