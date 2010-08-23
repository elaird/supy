#!/usr/bin/env python

import os
import analysis,steps,calculables,samples,organizer,plotter
import ROOT as r

class alphatEtaDependence(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

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
            steps.variableGreaterFilter(250.0,"%sSumPt%s"%_jet),
            #steps.multiplicityFilter("%sIndices%s"%_photon, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%_muon, nMax = 0),

            steps.alphatEtaDependence(_jet)
            ]
        return stepList
        

    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.jetmet]

    def listOfSamples(self) :
        from samples import specify
        return [  specify(name = "g_jets_mg_pt40_100",    nFilesMax = 6, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt100_200",   nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "g_jets_mg_pt200",       nFilesMax = -1, color = r.kGreen   ),
                  specify(name = "z_inv_mg_skim",         nFilesMax = -1,  color = r.kMagenta ),
                  ]

    def conclude(self) :
        for configId, tag in enumerate(self.sideBySideAnalysisTags()) :
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"g_jets_mg", "color":r.kGreen},
                             sources = ["g_jets_mg_pt%s"%bin for bin in ["40_100","100_200","200"] ])
            org.scale(100)

            pl = plotter.plotter(org, psFileName = self.psFileName(tag))
            pl.plotAll()

            def drawCut(hist,cut) :
                line = r.TLine(cut,0,cut,hist.GetMaximum())
                line.SetLineColor(r.kBlue)
                line.SetLineStyle(r.kDashed)
                r.SetOwnership( line, False )
                line.Draw("same")
            def drawOne() :
                one = r.TF1("one","1",0,5)
                one.SetLineColor(r.kRed)
                one.SetLineStyle(r.kDashed)
                one.SetLineWidth(1)
                r.SetOwnership(one,False)
                one.Draw("same")

            import utils
            r.gStyle.SetOptStat(0)
            c = r.TCanvas("c","",800,1000)
            outDir = self.outputDirectory(configId)+"/"
            for s in org.samples : c.Print(outDir+s["name"]+".ps[")
            for key in sorted(org.selections[-1]):
                if key == "counts" : continue
                for hist,sample in zip(org.selections[-1][key],org.samples) :
                    if not hist : continue
                    ctr = hist.ProjectionX(hist.GetName()+"_ctr",0,2)
                    fwd = hist.ProjectionX(hist.GetName()+"_fwd",3)
                    if min(ctr.GetEntries(),fwd.GetEntries()) < 10: continue

                    leg = r.TLegend(0.52,0.7,0.9,0.9);
                    ctr.Scale(1/ctr.Integral());  ctr.SetLineColor(r.kBlack);  ctr.SetMarkerColor(r.kBlack); leg.AddEntry(ctr,"Central","lp")
                    fwd.Scale(1/fwd.Integral());  fwd.SetLineColor(r.kRed);    fwd.SetMarkerColor(r.kRed); leg.AddEntry(fwd,"Forward","lp")
                    ratio = utils.ratioHistogram(fwd,ctr)

                    m = 2*max(fwd.GetMaximum(),ctr.GetMaximum())
                    fwd.SetMaximum(m)
                    ctr.SetMaximum(m)
                    ratio.SetMinimum(0); ratio.SetMaximum(2)

                    boson,jets,pt = key.split("_"); boson = boson[:-6]; pt = 20*int(pt[2:])
                    fwd.SetTitle("%s, pt %d-%d GeV;%s #alpha_{T}"%(boson,pt,pt+20,jets))
                    ctr.SetTitle("%s, pt %d-%d GeV;%s #alpha_{T}"%(boson,pt,pt+20,jets))
                    ratio.SetTitle("fwd/ctr")

                    c.Clear(); c.Divide(1,2); 
                    c.cd(1).SetLogy(); ctr.Draw(); fwd.Draw("same"); drawCut(ctr,0.55); leg.Draw()
                    c.cd(2); ratio.Draw(); drawOne(); drawCut(ratio,0.55)
                    c.Print(outDir+sample["name"]+".ps")

            for s in org.samples :
                fileName = outDir+s["name"]+".ps]"
                c.Print(fileName)
                fileNamePDF = fileName.replace(".ps]",".pdf")
                os.system("ps2pdf "+fileName[:-1] + " " + fileNamePDF)
                print fileNamePDF, "has been printed."
