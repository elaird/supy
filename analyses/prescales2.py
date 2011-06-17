#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class prescales2(analysis.analysis) :
    def mutriggers(self) :
        ptv = {5:(3,),8:(1,),12:(1,),15:(2,),20:(1,),24:(1,2,3),30:(1,2,3,4),40:(1,2),100:(1,2)}
        return sum([["HLT_Mu%d_v%d"%(pt,v) for v in vs] for pt,vs in sorted(ptv.iteritems())],[])

    def parameters(self) :
        return {"muon" : ("muon","PF"),
                "triggers": self.mutriggers()
                }
    
    def listOfCalculables(self,pars) :
        return (calculables.zeroArgs() +
                calculables.fromCollections(calculables.Muon,[pars["muon"]]) +
                [calculables.Muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.Muon.TriggeringIndex(pars['muon'], ptMin = 31),
                 calculables.Other.lowestUnPrescaledTrigger(pars["triggers"]),
                 calculables.Vertex.ID(),
                 calculables.Vertex.Indices(),
                 ])

    def listOfSteps(self,pars) :
        return [
            steps.Print.progressPrinter(),
            steps.Filter.multiplicity("vertexIndices",min=1),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.Trigger.physicsDeclaredFilter(),
            steps.Filter.monster(),
            steps.Filter.hbheNoise(),
            steps.Trigger.lowestUnPrescaledTriggerHistogrammer(),
            steps.Trigger.hltPrescaleHistogrammer(pars["triggers"]),
            steps.Filter.value( "%sTriggeringIndex%s"%pars['muon'],min = 0),
            ]+[ steps.Trigger.prescaleScan(trig) for trig in pars['triggers']]

    def listOfSampleDictionaries(self) : return [samples.muon]

    def listOfSamples(self,params) :
        from samples import specify
        return ( specify(names = "SingleMu.Run2011A-PR-v4.FJ.Burt", color = r.kBlack ) +
                 specify(names = "SingleMu.Run2011A-May10-v1.FJ.Burt", color = r.kRed) +
                 []
                 )
        
    def conclude(self,pars) :
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"SingleMu"}, allWithPrefix="SingleMu")
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"]
                             )
        pl.plotAll()

        print "\t     ptMin\t    prescale  observed\t\tN pass"
        for step in org.steps :
            if step.name != "prescaleScan" : continue
            for hist in sorted(step,key = lambda h: int(h.split("_")[3][1:])) :
                    label =''.join(part.strip('p').rjust(8) for part in hist.split('_'))
                    print label, ("%.1f" % (step[hist][0].GetEntries() / step[hist][0].GetBinContent(2))).rjust(8), ("%d"%step[hist][0].GetBinContent(2)).rjust(20)
