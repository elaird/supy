#!/usr/bin/env python

import os,analysis,utils,calculables,steps,samples,organizer

photon = ("photon","Pat")

class photonSkim(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def listOfSteps(self,params) :
        stepList=[ steps.progressPrinter(),
                   steps.multiplicityFilter("%sIndices%s"%photon, nMin = 1),
                   steps.skimmer(),
                   ]
        return stepList

    def listOfCalculables(self,params) :
        return calculables.zeroArgs() +\
               calculables.fromCollections(calculables.photon,[photon]) +\
               [calculables.photon.photonIndicesPat(ptMin = 80, flagName = "photonIDNoIsoReqPat")]

    def listOfSamples(self,params) :
        from samples import specify        
        return [
            specify(name = "JetMETTau.Run2010A-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "JetMET.Run2010A-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "Jet.Run2010B-Nov4ReReco_v1.RECO.Burt"),
            specify(name = "MultiJet.Run2010B-Nov4ReReco_v1.RECO.Burt"),

            specify(name = "v12_qcd_mg_ht_50_100"),
            specify(name = "v12_qcd_mg_ht_100_250"),
            specify(name = "v12_qcd_mg_ht_250_500"),
            specify(name = "v12_qcd_mg_ht_500_1000"),
            specify(name = "v12_qcd_mg_ht_1000_inf"),

            specify(name = "v12_g_jets_mg_pt40_100"),
            specify(name = "v12_g_jets_mg_pt100_200"),
            specify(name = "v12_g_jets_mg_pt200"),
            ]

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.photon, samples.mc]

    def conclude(self) :
        org = organizer.organizer( self.sampleSpecs() )
        utils.printSkimResults(org)
