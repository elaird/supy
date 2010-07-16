#!/usr/bin/env python

import analysis

a=analysis.analysis(name="example",
                    outputDir="/tmp/"
                    )

a.addSampleSpec(sampleName="Example_Skimmed_900_GeV_Data",
                listName="jetKineSteps",
                isMc=False,
                nEvents=-1)

a.addSampleSpec(sampleName="Example_Skimmed_900_GeV_MC",
                listName="jetKineSteps",
                isMc=True,
                nEvents=100)

a.go(loop=True,                  #loop over events and make root files containing histograms
     plot=True,                  #make a pdf file with plots from the histograms created above
     profile=False,              #profile the code
     nCores=1,                   #use multiple cores to process samples in parallel
     splitJobsByInputFile=False  #process all input files (rather than just samples) in parallel
     )
