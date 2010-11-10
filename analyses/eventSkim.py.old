#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class eventSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(2,300),
                   steps.runLsEventFilter("/home/hep/elaird1/38_tanja_events/v2/tanjas14.txt"),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        return [#specify(name = "Run2010B_MJ_skim4",         ),
                #specify(name = "Run2010B_MJ_skim3",         ),
                #specify(name = "Run2010B_MJ_skim2",         ),
                #specify(name = "Run2010B_MJ_skim",          ),
                #specify(name = "Run2010B_J_skim2",          ),
                #specify(name = "Run2010B_J_skim",           ),
                #specify(name = "Run2010A_JM_skim",          ),
                #specify(name = "Run2010A_JMT_skim",         ),
                 specify(name = "2010_data_calo_skim",       ),
                #specify(name = "2010_data_pf_skim",         ),
                ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
