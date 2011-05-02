#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class eventSkim(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(2,300),
                   steps.Other.runLsEventFilter("/home/hep/elaird1/78_bryn_sync/events.txt"),
                   #steps.Other.runLsEventFilter("/home/hep/elaird1/75_rob_sync/v1/robs_events/ht300.txt"),
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
        return specify(names = ["HT.Run2011A-PromptReco-v1.AOD.Georgia","HT.Run2011A-PromptReco-v1.AOD.Henning","HT.Run2011A-PromptReco-v2.AOD.Arlo"] )

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
