#!/usr/bin/env python

import os
import analysis,utils,calculables,steps,samples,organizer,plotter
import ROOT as r

class triggerTurnOn(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/vols/cms02/%s/tmp/"%os.environ["USER"]

    def parameters(self) :
        jettypes = ["ak5Jet","ak5JetJPT","ak5JetPF"]
        params = {"jets": dict(zip(jettypes,zip(jettypes,3*["Pat"]))),
                  "minJets": {"ge1":1,"ge2":2},
                  "trig1":"HLT_Jet70U",
                  "trig2":"HLT_Jet100U"
                  }
        return params

    def listOfSteps(self,conf) :
        jets = conf["jets"]
        return [ steps.progressPrinter(),
                 steps.techBitFilter([0],True),
                 steps.physicsDeclared(),
                 steps.vertexRequirementFilter(),
                 steps.monsterEventFilter(),
                 steps.hbheNoiseFilter(),
                 steps.multiplicityFilter("%sIndices%s"%jets, nMin = conf["minJets"]),
                 steps.multiplicityFilter("%sIndicesOther%s"%jets, nMax = 0),
                 steps.hltFilter(conf["trig1"]),
                 steps.histogrammer("%sLeadingPt%s"%jets,100,0,300, title=";Leading Jet p_{T};events / bin"),
                 steps.hltFilter(conf["trig2"]),
                 steps.histogrammer("%sLeadingPt%s"%jets,100,0,300, title=";Leading Jet p_{T};events / bin") ]
    
    def listOfCalculables(self,config) :
        jets = config["jets"]
        calcs =  calculables.zeroArgs()
        calcs += calculables.fromCollections("calculablesJet",[jets])
        calcs += [ calculables.jetIndices( jets, ptMin = 20., etaMax = 3.0, flagName = "JetIDloose")]
        return calcs

    def listOfSampleDictionaries(self) : return [samples.jetmet]

    def listOfDataSampleNames(self) :
        return ["JetMETTau.Run2010A-Jun14thReReco_v2.RECO.Bryn"    ,
                "JetMETTau.Run2010A-Jul16thReReco-v1.RECO.Bryn"    ,
                "JetMETTau.Run2010A-PromptReco-v4.RECO.Bryn"       ,
                "JetMET.Run2010A-PromptReco-v4.RECO.Bryn"          ,
                "JetMET.Run2010A-PromptReco-v4.RECO.Bryn2"         ]

    def listOfSamples(self,params) :
        from samples import specify
        return [specify(name) for name in self.listOfDataSampleNames()]

    def conclude(self) :
        from collections import defaultdict
        turnOns = defaultdict(list)
        configs = defaultdict(list)
        for conf in self.configurations() :
            org = organizer.organizer( self.sampleSpecs(conf['tag']) )
            org.mergeSamples(targetSpec = {"name":"jetmet","color":r.kBlack}, sources = self.listOfDataSampleNames() )
            org.scale()

            plotName = "%sLeadingPt%s"%conf["jets"]
            sel1,sel2 = tuple(filter(lambda y: y.name=="hltFilter" and y.title in [conf["trig1"],conf["trig2"]], org.selections))
            def binomialDivide(before,after) :
                hist = before.Clone("turnOn_%s_%s_%s"%(conf["trig2"],conf["trig1"],plotName))
                hist.Divide(after,before,1,1,"B") #binomial errors
                hist.SetTitle(";Leading Jet p_{T};P( %s | %s )"%(conf["trig2"].replace("HLT_",""),
                                                                 conf["trig1"].replace("HLT_","")))
                return hist
            sel2["turnOn"] = tuple(map(binomialDivide, sel1[plotName],sel2[plotName]))
            plotter.plotter( org,psFileName = self.psFileName()[:-3]+conf['tag']+".ps").plotAll()

            label = conf['tag'].replace(conf['jets'][0],"")
            turnOns[label].append(sel2["turnOn"])
            configs[label].append(conf)

        #######################
        r.gStyle.SetOptStat(0)
        c = r.TCanvas("c","",800,600)
        c.SetGridx()
        c.SetGridy()
        for label in turnOns.keys() :
            leg = r.TLegend(0.15,0.6,0.4,0.87)
            
            same = ""
            colors = [r.kGreen,r.kRed, r.kBlue,r.kYellow,r.kOrange,r.kGray][:len(turnOns[label])]
            for i in range(len(turnOns[label])) :
                hist = turnOns[label][i][0]
                hist.UseCurrentStyle()
                hist.SetLineColor(colors[i])
                leg.AddEntry(hist,"%s%s"%configs[label][i]["jets"])
                hist.SetMinimum(0)
                hist.SetMaximum(1.05)
                hist.Draw(same)
                same = "same"
            leg.Draw()

            outName = self.psFileName()[:-3]+label+"_allJets.eps"
            c.Print(outName)
            
            outPdfName = outName.replace(".eps",".pdf")
            os.system("epstopdf "+outName)
            os.system("rm "+outName)
            print "The output file \""+outPdfName+"\" has been written."


