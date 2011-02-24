#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class WPolSkim(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(2,300),
                   steps.Other.runLsEventFilter("/home/hep/elaird1/58_wpol_events/v2/38_Run_event_ls.txt"),
                   #steps.Other.runLsEventFilter("/home/hep/elaird1/58_wpol_events/v2/38_misRun_event_ls.txt"),
                   #steps.Other.runLsEventFilter("/home/hep/elaird1/58_wpol_events/v2/39_Run_event_ls.txt"),
                   #steps.Other.runLsEventFilter("/home/hep/elaird1/58_wpol_events/v2/39_misRun_event_ls.txt"),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return specify(names = "wpol_38" )

    def listOfSampleDictionaries(self) :
        return [samples.wpol]
