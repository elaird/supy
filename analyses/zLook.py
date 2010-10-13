#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class zLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit", "muonsInJets", "jetPtMin"] 
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"), "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ,    False,        50.0]))
        #objects["pfAK5"]   = dict(zip(fields, [("ak5JetPF","Pat"), "metP4PF",     ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"  ,     True ,        50.0]))

        return { "objects": objects,
                 "nJetsMinMax" :      dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)) ]                     [0:1] ),
                 "photonId" :         dict([ ("photonLoose","photonIDLooseFromTwikiPat"), ("photonTight","photonIDTightFromTwikiPat")] [0:1] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 "etRatherThanPt" : [True,False]        [0],
                 }

    def listOfCalculables(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _electron = params["objects"]["electron"]
        _photon = params["objects"]["photon"]
        _jetPtMin = params["objects"]["jetPtMin"]
        _etRatherThanPt = params["etRatherThanPt"]
        _met = params["objects"]["met"]
        _correctForMuons = not params["objects"]["muonsInJets"]

        lowPtThreshold = 30.0
        lowPtName = "lowPt"
        
        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesMuon",[_muon]) +\
               calculables.fromCollections("calculablesElectron",[_electron]) +\
               calculables.fromCollections("calculablesPhoton",[_photon]) +\
               [ calculables.xcJet( _jet,
                                    gamma = _photon,
                                    gammaDR = 0.5,
                                    muon = _muon,
                                    muonDR = 0.5,
                                    correctForMuons = _correctForMuons,
                                    electron = _electron, electronDR = 0.5
                                    ),
                 calculables.jetIndices( _jet, _jetPtMin,      etaMax = 3.0, flagName = params["jetId"]),
                 calculables.jetIndices( _jet, lowPtThreshold, etaMax = 3.0, flagName = params["jetId"], extraName = lowPtName),
                 calculables.muonIndices( _muon, ptMin = 20, combinedRelIsoMax = 0.15),
                 calculables.electronIndices( _electron, ptMin = 20, simpleEleID = "95", useCombinedIso = True),
                 calculables.photonIndicesPat(  ptMin = 20, flagName = params["photonId"]),
                 calculables.genIndices( pdgs = [22], label = "Photon", status = [1]),
                 calculables.genPhotonCategory(label = "Photon"),
                 #calculables.indicesUnmatched(collection = _photon, xcjets = _jet, DR = 0.5),
                 #calculables.indicesUnmatched(collection = _electron, xcjets = _jet, DR = 0.5)
                 ] \
                 + [ calculables.jetSumP4(_jet, mcScaleFactor = 1.0),
                     calculables.deltaPhiStar(_jet, ptMin = lowPtThreshold, extraName = lowPtName),                     
                     calculables.deltaPseudoJet(_jet, _etRatherThanPt),
                     calculables.alphaT(_jet, _etRatherThanPt),
                     calculables.alphaTMet(_jet, _etRatherThanPt, _met) ]

    def listOfSteps(self,params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]

        outList=[
            steps.progressPrinter(),
            steps.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),

            steps.preIdJetPtSelector(_jet,100.0,0),
            steps.preIdJetPtSelector(_jet,100.0,1),
            steps.jetEtaSelector(_jet,2.5,0),
            steps.hltFilter("HLT_HT100U"),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),

            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.histogrammer("%sIndicesOther%s"%_jet,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            
            #electron, muon, photon vetoes
            steps.multiplicityFilter("%sIndices%s"%_electron, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.multiplicityFilter("%sIndicesOther%s"%_muon, nMax = 0),
            steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),

            steps.histogrammer("%sSumEt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s %s_{T}s;events / bin"%(_jet[0],_jet[1],"p" if not _etRatherThanPt else "E")),
            steps.variableGreaterFilter(250.0,"%sSumEt%s"%_jet, suffix = "GeV"),

            #many plots
            steps.passFilter("jetSumPlots"),
            steps.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            steps.passFilter("kinematicPlots"),
            steps.alphaHistogrammer(_jet, _etRatherThanPt),

            steps.variablePtGreaterFilter(140.0,"%sSumP4%s"%_jet,"GeV"),
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),
            
            #steps.skimmer(),
            #steps.eventPrinter(),
            #steps.jetPrinter(_jet),
            #steps.htMhtPrinter(_jet),
            #steps.particleP4Printer(_photon),
            #steps.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),
            #steps.genParticlePrinter(minPt=-10.0,minStatus=1),
            
            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 400.0,#GeV
            #                etRatherThanPt = _etRatherThanPt,
            #                doGenParticles = True,
            #                ),
            
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self,params) :
        from samples import specify
        outList = [specify(name = "z_inv_mg_skim_v12", nFilesMax = -1, color = r.kMagenta )]
        return outList

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org = organizer.organizer( self.sampleSpecs(tag) )
            org.scale(6.679)

            #plot all
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 )
            pl.plotAll()
