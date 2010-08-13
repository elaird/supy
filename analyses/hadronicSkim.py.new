#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

def makeSteps() :
    jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]
    stepList=[ steps.progressPrinter(2,300),
               steps.hltFilter("HLT_Jet50U"),
               steps.leadingUnCorrJetPtSelector(jetAlgoList,100.0),
               steps.techBitFilter([0],True),
               steps.physicsDeclared(),
               steps.vertexRequirementFilter(5.0,15.0),
               steps.monsterEventFilter(10,0.25),
               steps.skimmer("/vols/cms02/%s/"%os.environ["USER"]),
               ]
    return stepList

def makeCalculables() :
    return calculables.zeroArgs()

def makeSamples() :
    from samples import specify
    return [specify(name = "MinimumBias.Commissioning10-SD_JetMETTau-Jun14thSkim_v1.RECO.Bryn" ),
            specify(name = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn"                     ),
            specify(name = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn"                     ),
            specify(name = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn"                        ),
            specify(name = "JetMETTau.Run2010A-PromptReco-v4.RECO.Loukas"                      ),
            specify(name = "JetMET.Run2010A-PromptReco-v4.RECO.Loukas"                         ),
            ]
    
a=analysis.analysis(name = "hadronicSkim",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables(),
                    listOfSamples = makeSamples(),
                    listOfSampleDictionaries = [samples.jetmet,samples.mc]
                    )

a.loop( nCores = 6 )
