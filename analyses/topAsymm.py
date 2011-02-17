#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class topAsymm(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                           [ "jet",            "met",            "muon",       "electron",        "photon",        "muonsInJets"]
        objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),"metP4AK5TypeII",("muon","Pat"),("electron","Pat"),("photon","Pat"), False]))
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"),"metP4PF",    ("muon","PF"),("electron","PF"),("photon","Pat"),   True]))

        leptons = {}
        fieldsLepton    =                            ["name","ptMin",              "isoVar", "triggerList"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     20, "CombinedRelativeIso", ("HLT_Mu9","HLT_Mu15_v1")]))
        leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,         "IsoCombined", ("FIX","ME")]))
        
        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  [{"min":3,"max":None}],
                 "lepCharge" : {#"pos":{"min":1},
                                #"neg":{"max":-1},
                                "":{}
                                },
                 "btagAndCut" : ("TrkCountingHighEffBJetTags",2.3) #Best guess at TCHEL
                 }

    def listOfCalculables(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += calculables.fromCollections(calculables.Jet, [obj["jet"]])
        outList += [
            calculables.Jet.IndicesBtagged(obj["jet"],pars["btagAndCut"][0]),
            calculables.Jet.Indices(      obj["jet"],      ptMin = 30, etaMax = 3.0, flagName = "JetIDloose"),
            calculables.Muon.Indices(     obj["muon"],     ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.Photon.photonIndicesPat(           ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),

            calculables.Jet.SumP4(obj["jet"]),
            calculables.Jet.MhtOverMet(obj["jet"], obj["met"]),
            calculables.Jet.deadEcalDR(obj["jet"], minNXtals = 10),

            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.xcJet(obj["jet"], applyResidualCorrectionsToData = False,
                                     gamma    = obj["photon"],      gammaDR = 0.5,
                                     electron = obj["electron"], electronDR = 0.5,
                                     muon     = obj["muon"],         muonDR = 0.5, correctForMuons = not obj["muonsInJets"]),
            calculables.XClean.SumP4(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),

            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            calculables.Other.lowestUnPrescaledTrigger(pars["lepton"]["triggerList"]),

            calculables.Other.SemileptonicTopIndex(lepton),
            calculables.Other.NeutrinoPz(lepton,"xcSumP4"),
            calculables.Other.NeutrinoP4P(lepton,"xcSumP4"),
            calculables.Other.NeutrinoP4M(lepton,"xcSumP4"),
            calculables.Other.SumP4NuP(lepton,"xcSumP4"),
            calculables.Other.SumP4NuM(lepton,"xcSumP4"),
            calculables.Other.SignedRapidity(lepton,"xcSumP4"),
            calculables.Other.RelativeRapidity(lepton,"xcSumP4"),
            calculables.Other.RelativeRapidity(lepton,"xcSumP4NuP"),
            calculables.Other.RelativeRapidity(lepton,"xcSumP4NuM"),
            
            calculables.Other.Mt(lepton,"%sNeutrinoP4P%s"%lepton),
            calculables.Muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"])
            ]
        return outList
    
    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        btag = ("%s"+pars["btagAndCut"][0]+"%s")%calculables.Jet.xcStrip(obj["jet"])
        bCut = pars["btagAndCut"][1]

        return [
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
            steps.Filter.multiplicity("vertexIndices",min=1),
            steps.Filter.monster(),
            steps.Filter.hbheNoise(),
            steps.Trigger.techBitFilter([0],True),
            steps.Trigger.physicsDeclared(),            
            #steps.Trigger.lowestUnPrescaledTrigger(), #FIXME ele
            ]+[
            steps.Filter.multiplicity(s, max = 0) for s in ["%sIndicesOther%s"%obj["jet"],
                                                            "%sIndicesOther%s"%obj["muon"],
                                                            "%sIndicesUnmatched%s"%obj["electron"],
                                                            "%sIndicesUnmatched%s"%obj["photon"],
                                                            "%sIndices%s"%(obj["electron" if pars["lepton"]["name"]=="muon" else "muon"]),
                                                            "%sIndices%s"%obj["photon"]]
            ]+[
            steps.Jet.uniquelyMatchedNonisoMuons(obj["jet"]),

            steps.Other.compareMissing(["xcSumP4",obj["met"]]),
            
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets"]),

            steps.Histos.multiplicity("%sIndicesModified%s"%obj["jet"]),
            steps.Histos.value("%sNMuonsMatched%s"%obj["jet"], 10,-0.5,9.5, indices = "%sIndices%s"%obj["jet"]),
            steps.Other.iterHistogrammer(("%sNmuon%s"%calculables.Jet.xcStrip(obj["jet"]),"%sNMuonsMatched%s"%obj["jet"]),
                                         (6,6),(-0.5,-0.5),(5.5,5.5), title = ";Nmuon;NMuonsMatched;events / bin"),
            steps.Other.compareMissing(["xcSumP4",obj["met"]]),
            steps.Filter.pt("xcSumP4",min=20),
            
            steps.Histos.multiplicity("%sIndices%s"%lepton),
            steps.Histos.multiplicity("%sIndicesNonIso%s"%lepton),
            steps.Histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 60,0,0.6, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=0),
            steps.Histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 60,0,0.6, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=1),

            #invert isolation requirement here
            #steps.Filter.multiplicity("%sIndices%s"%lepton, max = 0),
            steps.Filter.multiplicity("%sIndices%s"%lepton, min = 1, max = 1),
            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndices%s"%lepton, index = 0),
            steps.Filter.value("%sCharge%s"%lepton, indices = "%sIndices%s"%lepton, index = 0, **pars['lepCharge']),

            steps.Histos.value(btag, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 0),
            steps.Histos.value(btag, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1),
            steps.Histos.value(btag, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),
            steps.Histos.generic( (btag,"%sIndicesBtagged%s"%obj["jet"]), (60,60),(0,0),(30,30),
                                  title = ";btag0;btag1; events / bin",
                                  funcString = "lambda x: (x[0][x[1][0]],x[0][x[1][1]])"),
            steps.Histos.generic( (btag,"%sIndicesBtagged%s"%obj["jet"]), 50,0,50,
                                  title = ";btag0 * btag1; events / bin",
                                  funcString = "lambda x: x[0][x[1][0]] * x[0][x[1][1]]", suffix="_product"),
            
            steps.Filter.value(btag, min=bCut, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1),
            
            steps.Histos.value("%sSignedRapidity%s"%lepton, 31,-5,5),
            steps.Histos.value("%s%s"%lepton+"RelativeRapidityxcSumP4", 31,-5,5, xtitle = "#Delta y"),
            steps.Histos.value("%sMt%s"%lepton+"%sNeutrinoP4P%s"%lepton, 30,0,180, xtitle = "M_{T}"),

            #steps.Histos.generic(("%s%s"%lepton+"RelativeRapidityxcSumP4NuM","%s%s"%lepton+"RelativeRapidityxcSumP4NuP"),
            #                     (101,101), (-5,-5), (5,5), title = ";#Delta y #nu_{-};#Delta y #nu_{+};events / bin",
            #                     funcString = "lambda x: (x[0],x[1])"),

            #steps.Histos.generic(("%sNeutrinoPz%s"%lepton,"%sNeutrinoPz%s"%lepton),(100,100),(-1500,-500),(500,1500),
            #                     title=";#nu_{-} p_{z} (GeV);#nu_{+} p_{z} (GeV);events / bin", funcString = "lambda x: (x[0][0],x[0][1])"),
            
            steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            steps.Filter.value(btag, max=bCut, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),

            steps.Histos.generic(("%sIndicesBtagged%s"%obj["jet"],"%sCorrectedP4%s"%obj["jet"]),
                                 30,0,180, title=";M_{2-light};events / bin",
                                 funcString="lambda x: (x[1][x[0][2]] + x[1][x[0][3]]).M()"),

            #steps.Other.productGreaterFilter(0,["%s%s"%lepton+"RelativeRapidityxcSumP4NuM","%s%s"%lepton+"RelativeRapidityxcSumP4NuP"]),
            #steps.Other.histogrammer("%sSignedRapidity%s"%lepton, 51, -5, 5, title = ";y_lep*q_lep*sign(boost);events / bin"),
            #steps.Other.histogrammer("%s%s"%lepton+"RelativeRapidityxcSumP4", 51, -5, 5, title = ";#Delta y;events / bin"),
            #steps.Other.histogrammer(("%s%s"%lepton+"RelativeRapidityxcSumP4NuM","%s%s"%lepton+"RelativeRapidityxcSumP4NuP"),
            #                         (101,101), (-5,-5), (5,5), title = ";#Delta y #nu_{-};#Delta y #nu_{+};events / bin",
            #                         funcString = "lambda x: (x[0],x[1])"),
            #steps.Other.histogrammer("%sMt%s"%lepton+"%sNeutrinoP4P%s"%lepton,50,0,200, title = ";M_{T};events / bin"),
            #
            #steps.Other.histogrammer(("xcSumP4NuM","xcSumP4NuP"),(75,75),(-1500,-1500),(1500,1500),
            #                         funcString = "lambda x:(x[0].pz(),x[1].pz())", title = ";xcSumP4NuM.pz;xcSumP4NuP.pz;events / bin")
            
            ]
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.muon, samples.electron]

    def listOfSamples(self,pars) :
        from samples import specify
        def data() :
            names = { "electron": [#"EG.2010A_skim",
                                   "Electron.Run2010B_skim"
                                   ],
                      "muon": ["Mu.Run2010A_skim",
                               "Mu.Run2010B_skim"
                               ] }
            return specify( #nFilesMax = 1, nEventsMax = 40000,
                            names = names[pars["lepton"]["name"]])

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q6.index(15)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py6_pt_%dto%d"%t)[:None if t[1] else -3] for t in zip(q6,q6[1:]+[0])[iCut:]] )
        def qcd_py8(eL) :
            q8 = [0,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q8.index(50)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py8_pt%dto%d"%t)[:None if t[1] else -3] for t in zip(q8,q8[1:]+[0])[iCut:]] )
        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["v12_qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])
        def ttbar_mg(eL) :
            return specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kOrange)

        def ewk(eL, skimp=True) :
            EWK = {}
            EWK["electron"] = specify( names = "w_enu", effectiveLumi = eL, color = 28)
            EWK["muon"] = specify( names = "w_munu", effectiveLumi = eL, color = 28)
            EWK["other"] = specify( names = "w_taunu", effectiveLumi = eL, color = r.kYellow-3)
            if skimp :
                return EWK[pars["lepton"]["name"]]
            return sum(EWK.values(),[])

        eL = 400 # 1/pb
        return  ( data() +
                  qcd_py6(eL) +
                  ttbar_mg(eL) +
                  ewk(eL)
                  )

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"Data 2010", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Mu.Run2010")
            org.mergeSamples(targetSpec = {"name":"Data 2010", "color":r.kBlack, "markerStyle":20}, sources=["EG.2010A_skim","Electron.Run2010B_skim"])
            org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
            org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3},
                             sources = ["qcd_py6","w_enu","w_munu","w_taunu","tt_tauola_mg_v12"], keepSources = True)
            org.scale()
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios = ("Data 2010","standard_model"),
                                 sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 #doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 #pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()

