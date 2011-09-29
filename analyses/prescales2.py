from core.analysis import analysis
import os,steps,calculables,samples,samples.Muon,ROOT as r

class prescales2(analysis) :
    def mutriggers(self) :
        ptv = {   #3:(3,4),
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

    def parameters(self) :
        return {"muon" : ("muon","PF"),
                "triggers": self.mutriggers()
                }
    
    def listOfCalculables(self,pars) :
        from calculables import Muon,Other,Vertex
        return (calculables.zeroArgs() +
                calculables.fromCollections(calculables.Muon,[pars["muon"]]) +
                [Muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 Muon.TriggeringIndex(pars['muon'], ptMin = 10),
                 Other.lowestUnPrescaledTrigger(zip(*pars["triggers"])[0]),
                 Vertex.ID(),
                 Vertex.Indices(),
                 ])

    def listOfSteps(self,pars) :
        from steps import Print, Filter, Trigger, Histos, Other
        return [
            Print.progressPrinter(),
            Filter.multiplicity("vertexIndices",min=1),
            Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            Trigger.physicsDeclaredFilter(),
            Filter.monster(),
            Filter.hbheNoise(),
            Filter.value("%sTriggeringPt%s"%pars["muon"],min=10),
            Trigger.prescaleLumiEpochs(pars['triggers']),
            Trigger.anyTrigger(zip(*pars['triggers'])[0]),
            Histos.value("%sTriggeringPt%s"%pars["muon"],100,0,200),
            Trigger.hltPrescaleHistogrammer(zip(*pars["triggers"])[0]),
            Trigger.lowestUnPrescaledTriggerHistogrammer(),
            Trigger.lowestUnPrescaledTriggerFilter(),
            Histos.value("%sTriggeringPt%s"%pars["muon"],100,0,200),
            ]+[ Trigger.prescaleScan(trig,ptMin,"%sTriggeringPt%s"%pars['muon']) for trig,ptMin in pars['triggers']]+[
            Filter.value( "%sTriggeringPt%s"%pars['muon'],min = 31)]

    def listOfSampleDictionaries(self) : return [samples.Muon.muon]

    def listOfSamples(self,params) :
        return ( samples.specify( names = "SingleMu.Run2011A-PR-v4.FJ.Burt5", color = r.kViolet) +
                 samples.specify( names = "SingleMu.Run2011A-PR-v4.FJ.Burt4", color = r.kOrange) +
                 samples.specify( names = "SingleMu.Run2011A-PR-v4.FJ.Burt3", color = r.kBlack) +
                 samples.specify( names = "SingleMu.Run2011A-PR-v4.FJ.Burt2", color = r.kGreen) +
                 samples.specify( names = "SingleMu.Run2011A-PR-v4.FJ.Burt1", color = r.kRed) +
                 samples.specify( names = "SingleMu.Run2011A-May10-v1.FJ.Burt", color = r.kBlue) )
    
    def conclude(self,pars) :
        import re
        org = self.organizer(pars)
        black = sum([[hist for hist in step if re.match(r"HLT_Mu\d*_v\d*_p\d*",hist)] for step in org.steps],[])

        
        args = {"blackList":["lumiHisto","xsHisto","nJobsHisto"] + black,
                "detailedCalculables" : True }

        from core.plotter import plotter
        plotter(org, psFileName = self.psFileName(org.tag+"unmerged"), **args ).plotAll()
        plotter(org, psFileName = self.psFileName(org.tag+"unmerged_nolog"), doLog=False, **args ).plotAll()
        org.mergeSamples(targetSpec = {"name":"SingleMu","color":r.kRed}, allWithPrefix="SingleMu")
        plotter(org, psFileName = self.psFileName(org.tag), **args ).plotAll()
        self.printPrescales(org)

                
    def printPrescales(self,org) :
        with open('output.txt','w') as file :
            print >> file, "\t     ptMin\t    prescale  observed\t\tN pass"
            for step in org.steps :
                if step.name != "prescaleScan" : continue
                for hist in sorted(step,key = lambda h: int(h.split("_")[3][1:])) :
                    if not step[hist][0].GetBinContent(2) : continue
                    label =''.join(part.strip('p').rjust(8) for part in hist.split('_'))
                    listed = int(hist.split("_")[3][1:])
                    observed = step[hist][0].GetEntries() / step[hist][0].GetBinContent(2)
                    print >> file, label, ("%.1f" % observed).ljust(10), ("%.1f"%(observed/listed)).rjust(7), ("%d"%step[hist][0].GetBinContent(2)).rjust(20)

