#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples

class hadronicSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        jetAlgoList=[("ak5Jet"+jetType,"Pat") for jetType in ["","PF","JPT"]]
        stepList=[ steps.progressPrinter(2,300),
                   steps.hltFilter("HLT_Jet50U"),
                   steps.leadingUnCorrJetPtSelector(jetAlgoList,100.0),
                   steps.techBitFilter([0],True),
                   steps.physicsDeclared(),
                   steps.vertexRequirementFilter(),
                   steps.monsterEventFilter(),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self) :
        from samples import specify
        return [#specify(name = "MinimumBias.Commissioning10-SD_JetMETTau-Jun14thSkim_v1.RECO.Bryn" ),
                #specify(name = "JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn"                     ),
                #specify(name = "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn"                     ),
                #specify(name = "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn"                        ),
                #specify(name = "JetMETTau.Run2010A-PromptReco-v4.RECO.Loukas"                      ),
                #specify(name = "JetMET.Run2010A-PromptReco-v4.RECO.Loukas"                         ),
                #specify(name = "JetMET.Run2010A-PromptReco-v4.RECO.Martyn"                         ),
                specify(name = "JetMET.Run2010A-PromptReco-v4.RECO.Bryn"                           ),

                #specify(name = "z_inv_mg"    ),
                #specify(name = "z_jets_mg"   ),
                #specify(name = "w_jets_mg"   ),
                ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet,samples.mc]
