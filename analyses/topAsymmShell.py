from core.analysis import analysis
import samples,calculables,steps

class topAsymmShell(analysis) :

    def parameters(self) :
        def mutriggers() :
            ptv = {
                #3:(3,4),
                #5:(3,4,5,6),
                #8:(1,2,3,4),
                12:(1,2,3,4,5),
                15:(2,3,4,5,6),
                20:(1,2,3,4,5),
                24:(1,2,3,4,5),
                30:(1,2,3,4,5),
                40:(1,2,3),
                #100:(1,2,3),
                }
            return sum([[("HLT_Mu%d_v%d"%(pt,v),pt+1) for v in vs] for pt,vs in sorted(ptv.iteritems())],[])
        
        objects = self.vary()
        fields =                           [ "jet",               "met",           "sumP4",    "sumPt",       "muon",         "electron",         "photon",         "muonsInJets"]
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",       "pfSumP4",  "metSumEtPF",  ("muon","PF"),  ("electron","PF"),  ("photon","Pat"),  True]))
        #objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),  "metP4AK5TypeII", "xcSumP4", "xcSumPt",     ("muon","Pat"), ("electron","Pat"), ("photon","Pat"),  False]))

        leptons = self.vary()
        fieldsLepton    =                            ["name","ptMin", "etaMax",              "isoVar", "triggers"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     20,     2.1, "CombinedRelativeIso",   mutriggers()]))
        #leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,       9,         "IsoCombined", ("FIX","ME")]))
        
        bVar = "NTrkHiEff" # "TrkCountingHighEffBJetTags"
        bCut = {"normal"   : {"index":1, "min":2.0},
                "inverted" : {"index":1, "max":2.0}}
        lIso = {"normal":  {"N":1, "indices":"Indices"},
                "inverted":{"N":0, "indices":"IndicesNonIso"}}
        
        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  {"min":4,"max":None},
                 "nJets2" : {"min":4,"max":None},
                 "bVar" : bVar,
                 "selection" : self.vary({"top" : {"bCut":bCut["normal"],  "lIso":lIso["normal"]},
                                          #"Wlv" : {"bCut":bCut["inverted"],"lIso":lIso["normal"]},
                                          "QCD" : {"bCut":bCut["normal"],  "lIso":lIso["inverted"]}
                                          })
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
            calculables.Muon.IndicesTriggering(obj["muon"]),
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
            calculables.Other.lowestUnPrescaledTrigger(zip(*pars["lepton"]["triggers"])[0]),

            calculables.Top.mixedSumP4(transverse = obj["met"], longitudinal = obj["sumP4"]),
            calculables.Other.pt("mixedSumP4"),
            calculables.Top.SemileptonicTopIndex(lepton),            
            calculables.Top.fitTopLeptonCharge(lepton),
            calculables.Top.TopReconstruction(lepton,obj["jet"],"mixedSumP4"),
            
            calculables.Other.Mt(lepton,"mixedSumP4", allowNonIso=True, isSumP4=True),
            calculables.Muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"]),
            calculables.Other.PtSorted(obj['muon']),
            calculables.Other.Covariance(('met','PF')),
            calculables.Other.abbreviation( "TrkCountingHighEffBJetTags", "NTrkHiEff", fixes = calculables.Jet.xcStrip(obj['jet']) ),
            calculables.Other.abbreviation( "nVertexRatio", "nvr" ),
            calculables.Other.abbreviation('muonTriggerWeightPF','tw'),
            calculables.Jet.pt( obj['jet'], index = 0, Btagged = True ),
            calculables.Jet.absEta( obj['jet'], index = 3, Btagged = False)
            ]
        outList += calculables.fromCollections(calculables.Top,[('genTop',""),('fitTop',"")])
        outList.append( calculables.Top.TopComboQQBBLikelihood(pars['objects']['jet'], pars['bVar']))
        outList.append( calculables.Top.OtherJetsLikelihood(pars['objects']['jet'], pars['bVar']))
        outList.append( calculables.Top.TopRatherThanWProbability(priorTop=0.5) )
        return outList

    def listOfSampleDictionaries(self) :
        return [samples.MC.mc, samples.Muon.muon]
    

    @staticmethod
    def dataCleanupSteps(pars) :
        obj = pars['objects']
        return ([
            steps.Filter.hbheNoise(),
            steps.Trigger.physicsDeclaredFilter(),
            steps.Filter.monster(),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.Trigger.hltPrescaleHistogrammer(zip(*pars['lepton']['triggers'])[0]),
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            steps.Histos.multiplicity("vertexIndices", max=15),
            steps.Histos.value("%sPtSorted%s"%obj['muon'], 2,-0.5,1.5),
            steps.Filter.multiplicity("vertexIndices",min=1),
            ])

    @staticmethod
    def xcleanSteps(pars) :
        obj = pars['objects']
        return ([
            steps.Filter.multiplicity(s, max = 0) for s in ["%sIndices%s"%obj["photon"],
                                                            "%sIndicesUnmatched%s"%obj["photon"],
                                                            "%sIndices%s"%(obj["electron" if pars["lepton"]["name"]=="muon" else "muon"]),
                                                            "%sIndicesUnmatched%s"%obj["electron"],
                                                            "%sIndicesOther%s"%obj["muon"],
                                                            ]]+[
            steps.Jet.forwardFailedJetVeto( obj["jet"], ptAbove = 50, etaAbove = 3.5),
            steps.Jet.uniquelyMatchedNonisoMuons(obj["jet"]),
            ])

    @staticmethod
    def selectionSteps(pars, withPlots = True) :
        obj = pars["objects"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        lEtaMax = pars["lepton"]["etaMax"]
        lIsoIndices = ("%s"+pars["selection"]["lIso"]["indices"]+"%s")%lepton

        topTag = pars['tag'].replace("Wlv","top").replace("QCD","top")
        selections = (
            [steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
             steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets"]),
             
             steps.Histos.pt("mixedSumP4",100,0,300),
             steps.Filter.pt("mixedSumP4",min=20),
             
             topAsymmShell.lepIso(1,pars),
             steps.Filter.multiplicity("%sIndices%s"%lepton, max = 1), # drell-yann rejection
             topAsymmShell.lepIso(0,pars),

             steps.Filter.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, max = 1.0, indices = lIsoIndices, index = 0),
             steps.Filter.multiplicity("%sIndices%s"%lepton, min=pars["selection"]["lIso"]["N"],max=pars["selection"]["lIso"]["N"]),
             steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = lIsoIndices, index = 0),
             steps.Filter.absEta("%sP4%s"%lepton, max = lEtaMax, indices = lIsoIndices, index = 0),
             
             ]+[steps.Histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = i) for i in range(3)]+[
            calculables.Jet.ProbabilityGivenBQN(obj["jet"], pars['bVar'], binning=(64,-1,15), samples = pars['topBsamples'], tag = topTag),
            steps.Histos.value("TopRatherThanWProbability", 100,0,1),
            #steps.Filter.value("TopRatherThanWProbability", min = 0.2),
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1, min = 0.0),
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], **pars["selection"]["bCut"]),
            ])
        return [s for s in selections if withPlots or s.isSelector or issubclass(type(s),calculables.secondary)]

    @staticmethod
    def lepIso(index,pars) :
        lepton = pars["objects"][pars["lepton"]["name"]]
        return steps.Histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 55,0,1.1, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=index)
