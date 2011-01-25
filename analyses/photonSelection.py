#!/usr/bin/env python

import os
import analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class photonSelection(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                               ["jet",                 "met",             "muon",        "electron",        "photon",         "genjet","rechit"]
        objects["caloAK5"] = dict(zip(fields, [("xcak5Jet","Pat"),   "metAK5TypeIIPat",("muon","Pat"),("electron","Pat"),("photon","Pat") , "ak5Jet", "Calo" ]))

        return { "objects": objects,
                 "nJetsMinMax" : dict([  ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None))  ] [0:1] ),
                 "jetId" :  ["JetIDloose","JetIDtight"] [0],
                 }

    def listOfCalculables(self,params) :
        _jet =  params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        
        calcs =  calculables.zeroArgs() +\
                calculables.fromCollections("calculablesJet",[_jet]) +\
                calculables.fromCollections("calculablesLepton",[_muon]) +\
                [ calculables.xcJet( _jet,  gamma = _photon, gammaDR = 0.5, 
                                     muon = _muon, muonDR = 0.5),
                  calculables.jetIndices( _jet, ptMin = 20.0, etaMax = 3.0, flagName = params["jetId"]),
                  calculables.photonIndicesPat(  ptMin = 20, flagName="photonIDLoosePat"),
                  calculables.muonIndices( _muon, ptMin = 20.0, combinedRelIsoMax = 0.15),
                  calculables.genIndices( label = "Z", pdgs = [23]),
                  ]
        return calcs

    def listOfSteps(self,params) :
        _jet = params["objects"]["jet"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        stepList = [
            steps.progressPrinter(),

            steps.jetPtSelector(_jet,100.0,0),
            steps.leadingUnCorrJetPtSelector( [_jet],100.0 ),
            steps.hltFilter("HLT_Jet50U"),
            steps.vertexRequirementFilter(5.0,24.0),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.monsterEventFilter(10,0.25),
            steps.hbheNoiseFilter(),
        
            steps.multiplicityFilter("%sIndices%s"%_jet, nMin = params["nJetsMinMax"][0], nMax = params["nJetsMinMax"][1]),
            steps.multiplicityFilter("%sIndicesOther%s"%_jet, nMax = 0),
            steps.variableGreaterFilter(350.0,"%sSumPt%s"%_jet),
            #steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),

            steps.alphaTetaDependence(_jet)

            # signal distributions for {g,Z}x{forward,mid,central}
            ]
        return stepList
        

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self) :
        from samples import specify
        return [  #specify(name = "JetMET_skim",           nFilesMax = 1, color = r.kBlack   , markerStyle = 20),
                ##specify(name = "qcd_mg_ht_250_500_old", nFilesMax = 1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt30",           nFilesMax = 1, color = r.kBlue    ),
                  #specify(name = "qcd_py_pt80",           nFilesMax = 1, color = r.kBlue    ),
                  #specify(name = "qcd_py_pt170",          nFilesMax = 1, color = r.kBlue    ),
                  #specify(name = "qcd_py_pt300",          nFilesMax = 1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt470",          nFilesMax = 1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt800",          nFilesMax = 1, color = r.kBlue    ),
                ##specify(name = "qcd_py_pt1400",         nFilesMax = 1, color = r.kBlue    ),
                  #specify(name = "tt_tauola_mg",          nFilesMax = 1, color = r.kOrange  ),
                  specify(name = "g_jets_mg_pt40_100",    nFilesMax = 1, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "z_inv_mg_skim",         nFilesMax = -1,  color = r.kMagenta ),
                  #specify(name = "z_jets_mg_skim",        nFilesMax = 1, color = r.kYellow-3),
                  #specify(name = "w_jets_mg_skim",        nFilesMax = 1, color = 28         ),
                  #specify(name = "lm0",                   nFilesMax = 1, color = r.kRed     ),
                  #specify(name = "lm1",                   nFilesMax = 1, color = r.kRed+1   ),
                  ]

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"g_jets_mg",     "color":r.kGreen},   sources = ["g_jets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
            #org.mergeSamples(targetSpec = {"name":"qcd_py"   ,     "color":r.kBlue},    sources = ["qcd_py_pt%d"%i         for i in [30,80,170,300,470,800,1400] ])
            #org.mergeSamples(targetSpec = {"name":"standard_model","color":r.kGreen+3},
            #                 sources = ["g_jets_mg","qcd_py","tt_tauola_mg","z_inv_mg_skim","z_jets_mg_skim","w_jets_mg_skim"], keepSources = True
            #                 )
            org.scale(100)

            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios=("JetMET_skim","standard_model"),
                                 sampleLabelsForRatios=("ctr","fwd"),
                                 )
            pl.plotAll()

            import utils
            c = r.TCanvas("c","",800,1000)
            for key in org.selections[-1]:
                if key == "counts" : continue
                for hist,sample in zip(org.selections[-1][key],org.samples) :
                    if not hist : continue
                    c.Clear()
                    c.Divide(1,2)
                    c.cd(1).SetLogy()
                    div = 1 if "z" in key else 2
                    ctr = hist.ProjectionX(hist.GetName()+"_ctr",0,div)
                    fwd = hist.ProjectionX(hist.GetName()+"_fwd",div+1)
                    if max(ctr.GetEntries(),fwd.GetEntries()) < 10: continue

                    ctr.Scale(1/ctr.Integral())
                    fwd.Scale(1/fwd.Integral())

                    ctr.SetLineColor(r.kBlack);  ctr.SetMarkerColor(r.kBlack)
                    fwd.SetLineColor(r.kRed);    fwd.SetMarkerColor(r.kRed)

                    leg = r.TLegend(0.52,0.7,0.9,0.9);
                    leg.AddEntry(ctr,"Central","lp")
                    leg.AddEntry(fwd,"Forward","lp")
                    m = 2*max(fwd.GetMaximum(),ctr.GetMaximum())
                    fwd.SetMaximum(m)
                    ctr.SetMaximum(m)
                    ctr.Draw("")
                    fwd.Draw("same")
                    leg.Draw()
                    c.cd(2)
                    ratio = utils.ratioHistogram(fwd,ctr)
                    ratio.SetMaximum(2)
                    one = r.TF1("one","1",0,5)
                    one.SetLineColor(r.kRed)
                    one.SetLineStyle(r.kDashed)
                    one.SetLineWidth(1)
                    ratio.Draw()
                    one.Draw("same")
                    c.Print(sample["name"]+'_'+key+"normSlice.eps")
