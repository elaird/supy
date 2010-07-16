#!/usr/bin/env python

import analysis

a=analysis.analysis(name="example",
                    outputDir="/vols/cms02/elaird1/tmp/"
                    )

a.addSampleSpec(sampleName="Example_Skimmed_900_GeV_Data",
                listName="jetKineSteps",
                isMc=False,
                nEvents=-1)

a.addSampleSpec(sampleName="Example_Skimmed_900_GeV_MC",
                listName="jetKineSteps",
                isMc=True,
                nEvents=-1)

a.go(loop=True,
     plot=True,
     profile=False,
     nCores=1,
     splitJobsByInputFile=False
     )
