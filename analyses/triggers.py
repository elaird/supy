from core.analysis import analysis
import os,steps,calculables,samples,ROOT as r

class triggers(analysis) :
    def parameters(self) :
        return { "muon" : self.vary({"pf" : ("muon","PF"), "pat" : ("muon","Pat")}),
                 "electron":("electron","PF") }
    
    def listOfCalculables(self, pars) :
        from calculables import Muon,Electron,Other
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [pars["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [pars["electron"]])
        outList +=[Muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                   Muon.IndicesAnyIsoIsoOrder(pars['muon'], "CombinedRelativeIso"),
                   Muon.LeadingIsoAny(pars['muon'], ptMin = 18, iso = "CombinedRelativeIso"),
                   Electron.Indices( pars["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
                   Other.PtSorted(pars['muon'])
                   ]
        
        return outList
    
    def listOfSteps(self, pars) :
        from steps import Print, Histos, Trigger, Filter
        return (
            [Print.progressPrinter(),
             Histos.value("%sPtSorted%s"%pars['muon'], 2,0,1),
             #Filter.absEta("%sP4%s"%pars['muon'], max = 2.1, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             Trigger.triggerScan( pattern = r"HLT_Mu\d*_v\d", prescaleRequirement = "prescale==1", tag = "Mu"),
             Trigger.triggerScan( pattern = r"HLT_Mu\d*_v\d", prescaleRequirement = "True", tag = "MuAll"),
             #Trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
             #Trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
             #Trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
             Trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (100,0,50), "HLT_Mu30_v3",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #Trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (80,0,40), "HLT_Mu30_v4",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #Filter.pt("%sP4%s"%pars['muon'], min = 18, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             #Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v10",["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v9" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #Trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v8" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #Trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (50,0,25), "HLT_Mu15_v1",["HLT_Mu%d"%d for d in [9,7,5,3]]),
             Filter.multiplicity("%sPt%s"%pars['muon'], min = 2),
             Histos.value("%sPtSorted%s"%pars['muon'], 2,0,1),
             ])
    
    def listOfSampleDictionaries(self) :
        from samples import Muon,JetMET,Electron
        return [Muon.muon,JetMET.jetmet,Electron.electron]

    def listOfSamples(self,pars) :
        return ( samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt5", color = r.kOrange) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt4", color = r.kViolet) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt3", color = r.kBlue,) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt2", color = r.kGreen) +
                 samples.specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt1", color = r.kBlack) +
                 samples.specify(names = "SingleMu.Run2011A-May10-v1.FJ.Burt", color = r.kRed ) +
                 [])
        

    def conclude(self,conf) :
        org = self.organizer(conf)
        #org.mergeSamples(targetSpec = {"name":"SingleMu", "color":r.kBlack}, allWithPrefix="SingleMu")
        #org.scale()
        
        from core.plotter import plotter
        plotter(org,
                psFileName = self.psFileName(org.tag),
                #samplesForRatios = ("2010 Data","standard_model"),
                #sampleLabelsForRatios = ("data","s.m."),
                #whiteList = ["lowestUnPrescaledTrigger"],
                #doLog = False,
                #compactOutput = True,
                #noSci = True,
                #pegMinimum = 0.1,
                blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                ).plotAll()
