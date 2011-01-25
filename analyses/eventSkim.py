#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class eventSkim(analysis.analysis) :
    def listOfSteps(self,params) :
        stepList=[ steps.Print.progressPrinter(2,300),
                   steps.Other.runLsEventFilter("/home/hep/elaird1/colin.txt"),
                   steps.Other.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return [
            specify(name = "Run2010B_MJ_skim5",         ),
            specify(name = "Run2010B_MJ_skim4",         ),
            specify(name = "Run2010B_MJ_skim3",         ),
            specify(name = "Run2010B_MJ_skim2",         ),
            specify(name = "Run2010B_MJ_skim",          ),
            specify(name = "Run2010B_J_skim2",          ),
            specify(name = "Run2010B_J_skim",           ),
            specify(name = "Run2010A_JM_skim",          ),
            specify(name = "Run2010A_JMT_skim",         ),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
