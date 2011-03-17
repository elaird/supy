#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class variableStash(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(2,300),
                   steps.Other.collector(["susyScanM0","susyScanM12"]),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "t21")
        #return specify(names = "scan_tanbeta3_skim100")
    
    def listOfSampleDictionaries(self) :
        return [samples.mc]
