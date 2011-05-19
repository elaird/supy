#!/usr/bin/env python

import os,topAsymmShell,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class topAsymm(topAsymmShell.topAsymmShell) :

    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])
        
        return ([
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),

            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
            ]+topAsymmShell.topAsymmShell.cleanupSteps(pars)+[ #]+sum([[step,topAsymmShell.topAsymmShell.lepIso(0,pars)][:1] for step in topAsymmShell.topAsymmShell.cleanupSteps(pars)],[])+[
            
            steps.Histos.value(obj["sumPt"],50,0,1000),
            steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            
            ]+topAsymmShell.topAsymmShell.selectionSteps(pars) +[
            
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            steps.Filter.label('dNonTop'), steps.Top.discriminateNonTop(pars),     steps.Other.assertNotYetCalculated("TopReconstruction"),
            #steps.Filter.label('dNonQQ'),  steps.Top.discriminateQQbar(('fitTop','')),
            #steps.Filter.label('kinfit'),  steps.Top.kinFitLook("fitTopRecoIndex"),
            steps.Filter.label('signal'),  steps.Top.Asymmetry(('fitTop','')),
            
            #steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            #steps.Filter.value(bVar, max=2.0, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),
            steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            #steps.Filter.value("fitTopPtOverSumPt", max=0.2),
            steps.Top.Asymmetry(('fitTop','')),
            
            ])
    
    def listOfSamples(self,pars) :
        from samples import specify
        def data() :
            jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-163869_7TeV_PromptReco_Collisions11_JSON.txt", acceptFutureRuns = False) #193/pb
            names = { "electron": ["SingleElectron.Run2011A-PromptReco-v1.Burt"],
                      "muon": (specify(names="SingleMu.Run2011A-PR-v2.Robin1", weights = jw, overrideLumi = 87.31) +
                               specify(names="SingleMu.Run2011A-PR-v2.Robin2", weights = jw, overrideLumi = 79.34) +
                               specify(names="SingleMu.Run2011A-PR-v2.Alex", weights = jw,   overrideLumi = 12.27) +
                               #specify(names="SingleMu.Run2011A-PR-v2.Burt", weights = jw, overrideLumi = 0.68) +
                               []) }
            return names[pars["lepton"]["name"]]

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q6.index(15)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py6_pt_%dto%d"%t)[:None if t[1] else -3] for t in zip(q6,q6[1:]+[0])[iCut:]] )
        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000][1:]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])
        def ttbar_mg(eL) :
            intrinsicR = -0.05
            return (specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kBlack)+#,  weights = calculables.Gen.wNonQQbar()) +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kOrange,   weights = calculables.Top.wTopAsym(-0.30, intrinsicR = intrinsicR)) +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kYellow-3, weights = calculables.Top.wTopAsym( 0.00, intrinsicR = intrinsicR)) +
                    #specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kRed,      weights = calculables.Top.wTopAsym( 0.30, intrinsicR = intrinsicR)) +
                    [])

        def ewk(eL, skimp=True) :
            return specify( names = "w_jets_mg", effectiveLumi = eL, color = 28 )
            EWK = {}
            EWK["electron"] = specify( names = "w_enu", effectiveLumi = eL, color = 28)
            EWK["muon"] = specify( names = "w_munu", effectiveLumi = eL, color = 28)
            EWK["other"] = specify( names = "w_taunu", effectiveLumi = eL, color = r.kYellow-3)
            if skimp :
                return EWK[pars["lepton"]["name"]]
            return sum(EWK.values(),[])

        eL = 500 # 1/pb
        return  ( data() +
                  qcd_mg(eL) +
                  ewk(eL) +
                  ttbar_mg(eL) +
                  [])

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
            org.mergeSamples(targetSpec = {"name":"qcd_mg", "color":r.kBlue}, allWithPrefix="qcd_mg")
            #org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
            #org.mergeSamples(targetSpec = {"name":"topN30", "color":r.kRed}, sources = ["tt_tauola_mg.wTopAsymN30","tt_tauola_mg.wNonQQbar"], keepSources = True)
            #org.mergeSamples(targetSpec = {"name":"topP30", "color":r.kGreen}, sources = ["tt_tauola_mg.wTopAsymP30","tt_tauola_mg.wNonQQbar"])
            #org.drop("qcd_mg")
            org.drop("tt_tauola_mg.wTopAsymP00")
            org.drop("tt_tauola_mg.wTopAsymN30")
            org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3},
                             sources = ["qcd_mg", "qcd_py6","w_jets_mg", "w_enu","w_munu","w_taunu","tt_tauola_mg"], keepSources = True)
            org.scale()#toPdf=True)
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios = ("Data 2011","standard_model"),
                                 sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 #doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 #pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()

