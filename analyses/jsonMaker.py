#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

a=analysis.analysis(name = "jsonMaker",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = [ steps.progressPrinter(2,300),
                                    steps.jsonMaker("/vols/cms02/%s/tmp/"%os.environ["USER"]),
                                    ],
                    listOfCalculables = calculables.zeroArgs(),
                    listOfSamples = [samples.specify(name = "JetMET.Run2010A")],
                    listOfSampleDictionaries = [samples.jetmet],

                    mainTree=("lumiTree","tree"),
                    otherTreesToKeepWhenSkimming=[],
                    )

a.loop( nCores = 6 )
