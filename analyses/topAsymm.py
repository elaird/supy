import os,topAsymmShell,steps,calculables,samples,plotter,utils,organizer
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
            ]+topAsymmShell.topAsymmShell.cleanupSteps(pars)+[ 
            steps.Histos.value("%sTriggeringPt%s"%lepton, 200,0,200),
            steps.Filter.value("%sTriggeringPt%s"%lepton, min = lPtMin),
            
            steps.Histos.value(obj["sumPt"],50,0,1500),
            #steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            
            ]+topAsymmShell.topAsymmShell.selectionSteps(pars) +[
            steps.Filter.label("selection complete"),
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            steps.Top.discriminateNonTop(pars),     steps.Other.assertNotYetCalculated("TopReconstruction"),
            #steps.Filter.label('dNonQQ'),  steps.Top.discriminateQQbar(('fitTop','')),
            steps.Top.Asymmetry(('fitTop','')),
            steps.Top.kinFitLook("fitTopRecoIndex"),
            
            #steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            #]+([steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets2"])] \
            #   if tuple(sorted(pars["nJets2"].values()))!=tuple(sorted(pars["nJets"].values())) else [])+[
            #steps.Top.discriminateNonTop(pars),
            #steps.Top.kinFitLook("fitTopRecoIndex"),
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
                      "muon": (specify(names = ["SingleMu.Run2011A-PR-v4.FJ.Burt5",
                                                "SingleMu.Run2011A-PR-v4.FJ.Burt4",
                                                "SingleMu.Run2011A-PR-v4.FJ.Burt3",
                                                "SingleMu.Run2011A-PR-v4.FJ.Burt2",
                                                "SingleMu.Run2011A-PR-v4.FJ.Burt1",
                                                "SingleMu.Run2011A-May10-v1.FJ.Burt",
                                                ])+#, nFilesMax = 1, nEventsMax = 1000)+
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
            return (specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kBlue, weights = "wNonQQbar") +
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kGreen, weights = calculables.Top.wTopAsym(-0.4) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kGreen, weights = calculables.Top.wTopAsym(-0.3) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kGreen, weights = calculables.Top.wTopAsym(-0.2) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kGreen, weights = calculables.Top.wTopAsym(-0.1) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kOrange, weights = calculables.Top.wTopAsym(0) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kRed, weights = calculables.Top.wTopAsym(0.1) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kRed, weights = calculables.Top.wTopAsym(0.2) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kRed, weights = calculables.Top.wTopAsym(0.3) )+
                    specify(names = "tt_tauola_fj", effectiveLumi = None, color = r.kRed, weights = calculables.Top.wTopAsym(0.4) )+
                    [])

        def ewk(eL, skimp=True) :
            EWK = {}
            EWK["electron"] = specify( names = "w_enu_fj", effectiveLumi = eL, color = 28)
            EWK["muon"] = specify( names = "w_munu_fj", effectiveLumi = eL, color = 28)
            EWK["other"] = specify( names = "w_taunu_fj", effectiveLumi = eL, color = r.kYellow-3)
            if skimp : return EWK[pars["lepton"]["name"]]+specify( names = "w_jets_fj_mg", effectiveLumi = None, color = 28 )
            return sum(EWK.values(),[])

        eL = 2000 # 1/pb
        return  ( data() +
                  qcd_py6(eL) +
                  ewk(eL) +
                  ttbar_py(eL) +
                  [])

    def concludeAll(self) :
        super(topAsymm,self).concludeAll()
        self.meldNorm()
        self.meldWpartitions()

    def meldNorm(self, dist = "dphiLnu") :
        meldSamples = {"top_muon_pf" : ["SingleMu","P00","NonQQbar"],
                       "Wlv_muon_pf" : ["SingleMu"],
                       "QCD_muon_pf" : ["SingleMu"]}
        signal = ()
        templates = []
        
        organizers = [organizer.organizer(tag, [s for s in self.sampleSpecs(tag) if any(item in s['name'] for item in meldSamples[tag])])
                      for tag in [p['tag'] for p in self.readyConfs]]
        for org,color in zip(organizers,[r.kBlack,r.kRed,r.kBlue]) :
            org.mergeSamples(targetSpec = {"name":"t#bar{t}", "color":r.kViolet}, sources=["tt_tauola_fj.wNonQQbar","tt_tauola_fj.wTopAsymP00"])
            org.mergeSamples(targetSpec = {"name":"Data 2011", "color":color, "markerStyle":(20 if "top" in org.tag else 1)}, allWithPrefix="SingleMu")

            iData = org.indexOfSampleWithName("Data 2011")
            before = next(org.indicesOfStep("label","selection complete"))
            distTup = org.steps[next(iter(filter(lambda i: before<i, org.indicesOfStepsWithKey(dist))))][dist]
            data = [distTup[iData].GetBinContent(i) for i in range(distTup[iData].GetNbinsX()+2)]
            if "top" in org.tag :
                signal = data
                iTT = org.indexOfSampleWithName("t#bar{t}")
                templates.append([distTup[iTT].GetBinContent(i) for i in range(distTup[iTT].GetNbinsX()+2)])
                print "t#bar{t}"
            else :
                templates.append(data)
                print org.tag
            org.scale(toPdf=True)

        import fractions
        cs = fractions.componentSolver(signal, templates, 1e4)
        fractions.printComponentSolver(cs,decimals=4)
        stuff = fractions.drawComponentSolver(cs)
        stuff[0].Print("fractions.eps")
            
        melded = organizer.organizer.meld(organizers = organizers)
        pl = plotter.plotter(melded,
                             psFileName = self.psFileName(melded.tag),
                             doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             ).plotAll()

    def meldWpartitions(self) :
        samples = {"top_muon_pf" : ["w_"],
                   "Wlv_muon_pf" : ["w_","SingleMu"],
                   "QCD_muon_pf" : []}
        organizers = [organizer.organizer(tag, [s for s in self.sampleSpecs(tag) if any(item in s['name'] for item in samples[tag])])
                      for tag in [p['tag'] for p in self.readyConfs]]
        for org in organizers :
            org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
            org.mergeSamples(targetSpec = {"name":"w_mg", "color":r.kRed if "Wlv" in org.tag else r.kBlue, "markerStyle": 22}, sources = ["w_jets_fj_mg"])
            org.mergeSamples(targetSpec = {"name":"w_py", "color":r.kRed if "Wlv" in org.tag else r.kBlue}, sources = ["w_munu_fj"])
            org.drop("w_py")
            org.scale(toPdf=True)

        melded = organizer.organizer.meld("wpartitions",filter(lambda o: o.samples, organizers))
        pl = plotter.plotter(melded,
                             psFileName = self.psFileName(melded.tag),
                             doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             ).plotAll()


    def conclude(self,pars) :
        org = self.organizer(pars)
        for suf in ["N40","N20","N10","P10","P20","P40"] : org.drop('tt_tauola_fj.wTopAsym%s'%suf)
        org.drop("w_munu_fj")
        org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}", "color":r.kViolet}, sources=["tt_tauola_fj.wNonQQbar","tt_tauola_fj.wTopAsymP00"])
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.N30", "color":r.kRed}, sources = ["tt_tauola_fj.wTopAsymN30","tt_tauola_fj.wNonQQbar"][:1])
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.P30", "color":r.kGreen}, sources = ["tt_tauola_fj.wTopAsymP30","tt_tauola_fj.wNonQQbar"][:1])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+2}, sources = ["qcd_py6","w_munu_fj","t#bar{t}","w_jets_fj_mg"], keepSources = True)
        org.scale()
        
        #plot
        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag+"_log"),
                             pegMinimum = 0.01,
                             samplesForRatios = ("Data 2011","standard_model"),
                             sampleLabelsForRatios = ("data","s.m."),
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             detailedCalculables = True,
                             ).plotAll()

        pl = plotter.plotter(org, psFileName = self.psFileName(org.tag+"_nolog"),
                             doLog = False,
                             samplesForRatios = ("Data 2011","standard_model"),
                             sampleLabelsForRatios = ("data","s.m."),
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             detailedCalculables = True,
                             ).plotAll()

        #self.optimizeCut(org,signal = "t#bar{t}", background = "standard_model", var = "TopRatherThanWProbability")
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
        
            
        
