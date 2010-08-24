#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class hadronicLook(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        objects = {}
        fields =                              [ "jet",             "met",            "muon",        "electron",        "photon",       "rechit"]
        objects["caloAK5"] = dict(zip(fields, [("ak5Jet","Pat"),   "metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ]))
       #objects["jptAK5"]  = dict(zip(fields, [("ak5JetJPT","Pat"),"metP4TC",       ("muon","Pat"),("electron","Pat"),("photon","Pat"), "Calo" ]))
       #objects["pfAK5"]   = dict(zip(fields, [("ak5JetPF","Pat"), "metP4PF",       ("muon","PF"), ("electron","PF"), ("photon","Pat"), "PF"   ]))

        return { "objects": objects,
                 "nJetsMinMax" : dict([  ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None))  ] [0:1] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 #"jesAbs":  [1.0,1.1,0.9]               [:],
                 #"jesRel":  0,
                 }

    def listOfCalculables(self,params) :
        _jet =  params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]

        return calculables.zeroArgs() +\
               calculables.fromCollections("calculablesJet",[_jet]) +\
               calculables.fromCollections("calculablesLepton",[_muon]) +\
               [ #calculables.xcJet( _jet,  gamma = _photon, gammaDR = 0.5, muon = _muon, muonDR = 0.5),
                 calculables.jetIndices( _jet, ptMin = 20.0, etaMax = 3.0, flagName = params["jetId"]),
                 calculables.PFJetIDloose( _jet, fNeutralEmMax = 1.0, fChargedEmMax = 1.0, fNeutralHadMax = 1.0, fChargedHadMin = 0.0, nChargedMin = 0),
                 calculables.jetSumP4( _jet, scaleFactor = 1.0),
                 calculables.deltaPhiStar( _jet, ptMin = 50.0),
                 calculables.muonIndices( _muon, ptMin = 20, combinedRelIsoMax = 0.15),
                 calculables.photonIndicesPat(  ptMin = 20, flagName="photonIDLoosePat")]

    def listOfSteps(self,params) :
        _jet  = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        
        outList=[
            steps.progressPrinter(),
            steps.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),

            steps.jetPtSelector(_jet,100.0,0),
            steps.leadingUnCorrJetPtSelector( [_jet],100.0 ),
            steps.hltFilter("HLT_Jet50U"),
            steps.vertexRequirementFilter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(),
            steps.hbheNoiseFilter(),
            steps.hltPrescaleHistogrammer(["HLT_Jet50U","HLT_HT100U","HLT_MET45"]),       

            steps.histogrammer("%sIndices%s"%_jet,10,-0.5,9.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.histogrammer("%sIndicesOther%s"%_jet,10,-0.5,9.5, title=";number of %s%s above p_{T}#semicolon failing ID or #eta;events / bin"%_jet,
                               funcString="lambda x:len(x)"),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),

            steps.histogrammer("%sSumPt%s"%_jet,50,0,1500, title = ";H_{T} (GeV) from %s%s p_{T}s;events / bin"%_jet),
            steps.variableGreaterFilter(350.0,"%sSumPt%s"%_jet),

            steps.passFilter("singleJetPlots"),
            steps.cleanJetPtHistogrammer(_jet),
            steps.passFilter("jetSumPlots"), 
            steps.cleanJetHtMhtHistogrammer(_jet),
            steps.passFilter("kinematicPlots"), 
            steps.alphaHistogrammer(_jet),
            
            steps.variableGreaterFilter(0.55,"%sAlphaT%s"%_jet),

            steps.histogrammer("%sIndices%s"%_muon,10,-0.5,9.5,title="; N muons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),
            steps.histogrammer("%sIndices%s"%_photon,10,-0.5,9.5,title="; N photons ;events / bin", funcString = "lambda x: len(x)"),
            steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            
            #steps.skimmer(),
            #steps.eventPrinter(),
            #steps.jetPrinter(_jet),
            #steps.htMhtPrinter(_jet),
            #steps.nJetAlphaTPrinter(_jet)
            #steps.genParticlePrinter(minPt=10.0,minStatus=3),

            #steps.displayer(jets = _jet,
            #                muons = _muon,
            #                met       = params["objects"]["met"],
            #                electrons = params["objects"]["electron"],
            #                photons   = params["objects"]["photon"],                            
            #                recHits   = params["objects"]["rechit"],recHitPtThreshold=1.0,#GeV
            #                scale = 200.0),#GeV
            
            ]
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self) :
        from samples import specify
        return [  specify(name = "JetMET_skim",           nFilesMax = -1, color = r.kBlack   , markerStyle = 20),
                ##specify(name = "qcd_mg_ht_250_500_old", nFilesMax = -1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt30",           nFilesMax = -1, color = r.kBlue    ),
                  specify(name = "qcd_py_pt80",           nFilesMax = -1, color = r.kBlue    ),
                  specify(name = "qcd_py_pt170",          nFilesMax = -1, color = r.kBlue    ),
                  specify(name = "qcd_py_pt300",          nFilesMax = -1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt470",          nFilesMax = -1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt800",          nFilesMax = -1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt1400",         nFilesMax = -1, color = r.kBlue    ),

                  #specify(name = "qcd_mg_ht_50_100",      nFilesMax = -1, color = r.kBlue    ),
                  #specify(name = "qcd_mg_ht_100_250",     nFilesMax = -1, color = r.kBlue    ),
                  #specify(name = "qcd_mg_ht_250_500",     nFilesMax = -1, color = r.kBlue    ),
                  #specify(name = "qcd_mg_ht_500_1000",    nFilesMax = -1, color = r.kBlue    ),
                  #specify(name = "qcd_mg_ht_1000_inf",    nFilesMax = -1, color = r.kBlue    ),
                  
                  specify(name = "tt_tauola_mg",          nFilesMax =  3, color = r.kOrange  ),
                  specify(name = "g_jets_mg_pt40_100",    nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "z_inv_mg_skim",         nFilesMax = -1, color = r.kMagenta ),
                  specify(name = "z_jets_mg_skim",        nFilesMax = -1, color = r.kYellow-3),
                  specify(name = "w_jets_mg_skim",        nFilesMax = -1, color = 28         ),
                  specify(name = "lm0",                   nFilesMax = -1, color = r.kRed     ),
                  specify(name = "lm1",                   nFilesMax = -1, color = r.kRed+1   ),
                  ]

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"g_jets_mg",     "color":r.kGreen},   sources = ["g_jets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
            org.mergeSamples(targetSpec = {"name":"qcd_py"   ,     "color":r.kBlue},    sources = ["qcd_py_pt%d"%i      for i in [80,170,300] ])
            #org.mergeSamples(targetSpec = {"name":"qcd_mg", "color":r.kBlue},sources = ["qcd_mg_ht_%s"%bin for bin in ["50_100","100_250","250_500","500_1000","1000_inf"] ])
            org.mergeSamples(targetSpec = {"name":"standard_model","color":r.kGreen+3},
                             sources = ["g_jets_mg","qcd_py","tt_tauola_mg","z_inv_mg_skim","z_jets_mg_skim","w_jets_mg_skim"], keepSources = True )
                             #sources = ["g_jets_mg","qcd_mg","tt_tauola_mg","z_inv_mg_skim","z_jets_mg_skim","w_jets_mg_skim"], keepSources = True )
            org.scale()

            #other
            import deltaPhiLook
            d = deltaPhiLook.deltaPhiLooker(org,tag)
            d.go()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("JetMET_skim","standard_model"),
                                 sampleLabelsForRatios=("data","s.m."),
                                 )
            pl.plotAll()

            #import statMan
            #statMan.go(a.organizeHistograms(),
            #           dataSampleName="JetMETTau.Run2010A",
            #           mcSampleName="standard_model",
            #           moneyPlotName="ak5JetPat_alphaT_vs_Ht_ge2jets",
            #           xCut=0.51,yCut=330.0)
