#!/usr/bin/env python

import os,topAsymmShell,steps,calculables,samples,plotter,utils
import ROOT as r

class topAsymm(topAsymmShell.topAsymmShell) :

    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        lEtaMax = pars["lepton"]["etaMax"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])
        
        return ([
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
            steps.Filter.absEta("%sP4%s"%lepton, max = lEtaMax, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
            ]+topAsymmShell.topAsymmShell.cleanupSteps(pars)+[ 
            
            steps.Histos.value(obj["sumPt"],50,0,1500),
            #steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            
            ]+topAsymmShell.topAsymmShell.selectionSteps(pars) +[
            steps.Filter.label("selection complete"),
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            steps.Top.discriminateNonTop(pars),     steps.Other.assertNotYetCalculated("TopReconstruction"),
            #steps.Filter.label('dNonQQ'),  steps.Top.discriminateQQbar(('fitTop','')),
            #steps.Top.Asymmetry(('fitTop','')),
            
            #steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            #]+([steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets2"])] \
            #   if tuple(sorted(pars["nJets2"].values()))!=tuple(sorted(pars["nJets"].values())) else [])+[
            #steps.Filter.label('kinfit'),  steps.Top.kinFitLook("fitTopRecoIndex"),
            #steps.Top.discriminateNonTop(pars),
            #steps.Top.Asymmetry(('fitTop','')),
            #steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            #steps.Filter.value(bVar, max=2.0, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),
            #steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            #steps.Filter.value("fitTopPtOverSumPt", max=0.2),
            #steps.Top.Asymmetry(('fitTop','')),
            
            ])
    
    def listOfSamples(self,pars) :
        from samples import specify
        def data() :
            names = { "electron": ["SingleElectron.Run2011A-PromptReco-v1.Burt"],
                      "muon": (specify(names = ["SingleMu.Run2011A-PR-v4.FJ.Burt_skim",
                                                "SingleMu.Run2011A-May10-v1.FJ.Burt_skim"
                                                ])+#, nFilesMax = 1, nEventsMax = 1000)+
                               #specify(names="SingleMu.Run2011A-PR-v2.Alex_1muskim", nEventsMax = 2000, weights = jw, overrideLumi = 12.27) +
                               #specify(names="SingleMu.Run2011A-PR-v2.Robin1", weights = jw, overrideLumi = 87.31) +
                               #specify(names="SingleMu.Run2011A-PR-v2.Robin2", weights = jw, overrideLumi = 79.34) +
                               #specify(names="SingleMu.Run2011A-PR-v2.Alex", weights = jw,   overrideLumi = 12.27) +
                               #specify(names="SingleMu.Run2011A-PR-v2.Burt", weights = jw, overrideLumi = 0.68) +
                               []) }
            return names[pars["lepton"]["name"]]

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800,None]
            iCut = q6.index(15)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["qcd_py6fj_pt_%s"%("%d_%d"%(low,high) if high else "%d"%low) for low,high in zip(q6[:-1],q6[1:])[iCut:]] )
        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000][1:]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])
        def ttbar_mg(eL) :
            intrinsicR = -0.05
            return (specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kBlue,  weights = "wNonQQbar") +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kRed,  weights = "wQQbar") +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kOrange,   weights = calculables.Top.wTopAsym(-0.30, intrinsicR = intrinsicR)) +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kYellow-3, weights = calculables.Top.wTopAsym( 0.00, intrinsicR = intrinsicR)) +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kRed,      weights = calculables.Top.wTopAsym( 0.30, intrinsicR = intrinsicR)) +
                    [])

        def ttbar_py(eL) :
            return (specify(names = "tt_tauola_fj", effectiveLumi = eL, color = r.kBlue, weights = "wNonQQbar") +
                    specify(names = "tt_tauola_fj", effectiveLumi = eL, color = r.kGreen, weights = calculables.Top.wTopAsym(-0.3) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = eL, color = r.kOrange, weights = calculables.Top.wTopAsym(0) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = eL, color = r.kRed, weights = calculables.Top.wTopAsym(0.3) )+
                    [])

        def ewk(eL, skimp=True) :
            #return specify( names = "w_jets_mg", effectiveLumi = eL, color = 28 )
            EWK = {}
            EWK["electron"] = specify( names = "w_enu_fj", effectiveLumi = eL, color = 28)
            EWK["muon"] = specify( names = "w_munu_fj", effectiveLumi = eL, color = 28)
            EWK["other"] = specify( names = "w_taunu_fj", effectiveLumi = eL, color = r.kYellow-3)
            if skimp : return EWK[pars["lepton"]["name"]]
            return sum(EWK.values(),[])

        eL = 2000 # 1/pb
        return  ( data() +
                  qcd_py6(eL) +
                  ewk(eL) +
                  ttbar_py(eL) +
                  [])

    def conclude(self,pars) :
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}", "color":r.kBlue+1}, sources=["tt_tauola_fj.wNonQQbar","tt_tauola_fj.wTopAsymP00"])
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.N30", "color":r.kRed}, sources = ["tt_tauola_fj.wTopAsymN30","tt_tauola_fj.wNonQQbar"][:1])
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.P30", "color":r.kGreen}, sources = ["tt_tauola_fj.wTopAsymP30","tt_tauola_fj.wNonQQbar"][:1])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+2}, sources = ["qcd_py6","w_munu_fj","t#bar{t}"], keepSources = True)
        org.scale()#toPdf=True)
        
        #plot
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             samplesForRatios = ("Data 2011","standard_model"),
                             sampleLabelsForRatios = ("data","s.m."),
                             #whiteList = ["lowestUnPrescaledTrigger"],
                             #doLog = False,
                             #compactOutput = True,
                             #noSci = True,
                             pegMinimum = 0.01,
                             detailedCalculables = True,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             )
        pl.plotAll()

        self.optimizeCut(org,signal = "t#bar{t}", background = "standard_model", var = "TopRatherThanWProbability")
        #org.printFormattedCalculablesGraph()
        #with open("topAsymm.gv","write") as file : print>>file, org.calculablesDotFile

    def optimizeCut(org, signal = "", background = "", var = "", FOM = lambda s,b: s/math.sqrt(s+b) ) :
        
        iSignal = org.indexOfSampleWithName(signal)
        iBack = org.indexOfSampleWithName(background)
        iStep = next( org.indicesOfStepsWithKey(var) )

        sHist = org.steps[iStep][var][iSignal]
        bHist = org.steps[iStep][var][iBack]
        bins = sHist.GetNbins()+2
        S = [sHist.GetBinContent(i) for i in range(bins)]
        B = [bHist.GetBinContent(i) for i in range(bins)]
        

        mDist = bHist.Clone("%s_fom"%var)
        mDist.Reset()
        iSeed = max((FOM(s,b),i) for i,s,b in zip(range(bins),S,B))[1]

        iL = iR = iSeed
        
            
        
