#####################################
from stepsOther import *
from stepsJet import *
from stepsTrigger import *
from stepsPhoton import *
from stepsPrint import *
from stepsGen import *
#####################################
def removeStepsForMc(inSteps) :
    dummyBX=bxFilter([])
    dummyPhysDecl=physicsDeclared()
    dummyTechBit0=techBitFilter([0],True)
    dummyDisplayer=displayer()
    dummyHltFilter=hltFilter("")
    dummyHbheNoiseFilter=hbheNoiseFilter()
    outSteps=[]
    for step in inSteps :
        #remove inapplicable steps
        if step.__doc__==dummyHltFilter.__doc__ : continue #temporary hack
        if step.__doc__==dummyHbheNoiseFilter.__doc__ : continue #temporary hack
        if step.__doc__==dummyBX.__doc__ : continue
        if step.__doc__==dummyPhysDecl.__doc__ : continue
        if step.moreName==dummyTechBit0.moreName : continue
        outSteps.append(copy.deepcopy(step))

        #turn on gen stuff
        if step.__doc__==dummyDisplayer.__doc__ : outSteps[-1].switchGenOn()
    return outSteps
#####################################
def removeStepsForData(inSteps) :
    dummyPtHatHistogrammer=ptHatHistogrammer()
    outSteps=[]
    for step in inSteps :
        #remove inapplicable steps
        if step.__doc__==dummyPtHatHistogrammer.__doc__ : continue
        outSteps.append(copy.deepcopy(step))
    return outSteps
#####################################
def insertPtHatFilter(inSteps,value) :
    inSteps.insert(0,ptHatFilter(value))
#####################################
