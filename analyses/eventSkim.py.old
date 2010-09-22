#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class eventSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(2,300),
                   steps.runLsEventFilter("/home/hep/elaird1/markusEvents.txt"),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return [specify(name = "JetMET_skim")]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
