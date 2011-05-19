import analysis,samples,calculables,steps

class topAsymmShell(analysis.analysis) :

    def parameters(self) :
        objects = {}
        fields =                           [ "jet",              "met",           "sumP4",                "sumPt",                 "muon",       "electron",        "photon",        "muonsInJets"]
        #objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),  "metP4AK5TypeII","xcSumP4",              "xcSumPt",               ("muon","Pat"),("electron","Pat"),("photon","Pat"), False]))
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"),"metP4PF",       "xcak5JetPFRawSumP4Pat","xcak5JetPFRawSumPtPat", ("muon","PF"),("electron","PF"),("photon","Pat"),   True]))

        leptons = {}
        fieldsLepton    =                            ["name","ptMin",              "isoVar", "triggerList"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     25, "CombinedRelativeIso", ("HLT_Mu24_v1","HLT_Mu24_v2")]))
        #leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,         "IsoCombined", ("FIX","ME")]))
        
        bVar = "TrkCountingHighEffBJetTags"
        bCut = {"normal"   : {"index":1, "min":2.0},
                "inverted" : {"index":0, "max":2.0}}
        lIso = {"normal":  {"nMaxIso":1, "indices":"Indices"},
                "inverted":{"nMaxIso":0, "indices":"IndicesNonIso"}}
        
        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  [{"min":4,"max":None}],
                 "bVar" : bVar,
                 "sample" : {"top" : {"bCut":bCut["normal"],  "lIso":lIso["normal"]},
                             "Wlv" : {"bCut":bCut["inverted"],"lIso":lIso["normal"]},
                             "QCD" : {"bCut":bCut["normal"],  "lIso":lIso["inverted"]}
                             }
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
            calculables.Jet.IndicesBtagged(obj["jet"],pars["bVar"]),
            calculables.Jet.Indices(      obj["jet"],      ptMin = 20, etaMax = 3.5, flagName = "JetIDloose"),
            calculables.Muon.Indices(     obj["muon"],     ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "80", useCombinedIso = True),
            calculables.Photon.Indices(   obj["photon"],   ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),

            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.xcJet(obj["jet"], applyResidualCorrectionsToData = False,
                                     gamma    = obj["photon"],      gammaDR = 0.5,
                                     electron = obj["electron"], electronDR = 0.5,
                                     muon     = obj["muon"],         muonDR = 0.5, correctForMuons = not obj["muonsInJets"]),
            calculables.XClean.SumP4(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),
            calculables.XClean.SumPt(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),

            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            calculables.Other.lowestUnPrescaledTrigger(pars["lepton"]["triggerList"]),

            calculables.Top.mixedSumP4(transverse = obj["met"], longitudinal = obj["sumP4"]),
            calculables.Top.SemileptonicTopIndex(lepton),            
            calculables.Top.fitTopLeptonCharge(lepton),
            calculables.Top.TopReconstruction(lepton,obj["jet"],"mixedSumP4"),
            
            calculables.Other.Mt(lepton,"mixedSumP4", allowNonIso=True, isSumP4=True),
            calculables.Muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"])
            ]
        outList += calculables.fromCollections(calculables.Top,[('genTop',""),('fitTop',"")])
        outList += [calculables.Jet.TagProbability(pars['objects']['jet'], pars['bVar'], letter) for letter in ['b','q','n']]
        outList.append( calculables.Top.TopComboLikelihood(pars['objects']['jet'], pars['bVar']))
        outList.append( calculables.Top.OtherJetsLikelihood(pars['objects']['jet'], pars['bVar']))
        outList.append( calculables.Top.TopRatherThanWProbability() )
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.muon, samples.electron]
    

    @staticmethod
    def cleanupSteps(pars) :
        obj = pars['objects']
        return ([
            steps.Filter.multiplicity("vertexIndices",min=1),
            steps.Filter.monster(),
            steps.Filter.hbheNoise(),
            #steps.Trigger.techBitFilter([0],True), #FIXME
            steps.Trigger.physicsDeclared(),            
            steps.Trigger.lowestUnPrescaledTrigger(), #FIXME ele
            ]+[
            steps.Filter.multiplicity(s, max = 0) for s in ["%sIndices%s"%obj["photon"],
                                                            "%sIndicesUnmatched%s"%obj["photon"],
                                                            "%sIndices%s"%(obj["electron" if pars["lepton"]["name"]=="muon" else "muon"]),
                                                            "%sIndicesUnmatched%s"%obj["electron"],
                                                            "%sIndicesOther%s"%obj["muon"],
                                                            ]]+[
            steps.Jet.forwardJetVeto( obj["jet"], ptAbove = 50, etaAbove = 3.5),
            steps.Jet.uniquelyMatchedNonisoMuons(obj["jet"]),
            ])

    @staticmethod
    def selectionSteps(pars, withPlots = True) :
        obj = pars["objects"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]

        selections = (
            [steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
             steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets"]),
             
             steps.Histos.pt("mixedSumP4",100,0,300),
             steps.Filter.pt("mixedSumP4",min=20),
             
             topAsymmShell.lepIso(0,pars), topAsymmShell.lepIso(1,pars),
             steps.Filter.multiplicity("%sIndices%s"%lepton, max = pars["sample"]["lIso"]["nMaxIso"]),
             steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = ("%s"+pars["sample"]["lIso"]["indices"]+"%s")%lepton, index = 0),
             
             ]+[steps.Histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = i) for i in range(3)]+[
            steps.Histos.value("TopRatherThanWProbability", 100,0,1),
            #steps.Filter.value("TopRatherThanWProbability", min = 0.02),
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1, min = 0.0),
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], **pars["sample"]["bCut"]),
            ])
        if not withPlots : selections = filter(lambda s: hasattr(s,"select"), selections)
        return selections

    @staticmethod
    def lepIso(index,pars) :
        lepton = pars["objects"][pars["lepton"]["name"]]
        return steps.Histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 60,0,0.6, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=index)
        
            
