#!/usr/bin/env python

import analysis

a=analysis.analysis(name="metPasSkim",
                    outputDir="/vols/cms02/elaird1/tmp/"
                    )

#a.addSampleSpec(sampleName="JetMETTau.Run2010A-Jun9thReReco_v1.RECO",
#                listName="metPasFilter",
#                isMc=False,
#                nEvents=-1)
#
#a.addSampleSpec(sampleName="MinimumBias.Commissioning10-SD_JetMETTau-Jun9thSkim_v1.RECO",
#                listName="metPasFilter",
#                isMc=False,
#                nEvents=-1)
#
#a.addSampleSpec(sampleName="QCD_Pt-15_7TeV-pythia8.Summer10-START36_V10_SP10-v1.GEN-SIM-RECODEBUG",
#                listName="metPasFilter",
#                isMc=False,
#                nEvents=-1)

a.addSampleSpec(sampleName="JetMETTau.Run2010A-Jul6thReReco_v1.RECO",
                listName="metPasFilter",
                isMc=False,
                nEvents=-1)

#a.addSampleSpec(sampleName="QCD_Pt30.Summer10-START36_V9_S09-v1.GEN-SIM-RECODEBUG",
#                listName="metPasFilter",
#                isMc=True,
#                nEvents=-1)

a.go(loop=True,
     plot=False,
     profile=False,
     nCores=6,
     splitJobsByInputFile=True
     )
