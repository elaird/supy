import os
import analysis,utils,calculables,steps,samples,plotter,samplesMCOld
import ROOT as r

class exampleInclusive(analysis.analysis) :
    def parameters(self) :
        return {"xsPostWeights" : {"exact":True,"approx":False}}

    def listOfSteps(self,pars) :
        return [ steps.Print.progressPrinter(),
                 steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
                 ]
    
    def listOfCalculables(self,pars) : return calculables.zeroArgs()
    def listOfSampleDictionaries(self) : return [samplesMCOld.mcOld]

    def listOfSamples(self,pars) :
        return self.sampleDict.manageInclusive( samples.specify( names = ["v12_qcd_py6_pt%d"%d for d in [15,30,80,170,300,470,800,1400]],
                                                                 color = r.kBlue, effectiveLumi = 500) ,
                                                applyPostWeightXS = pars["xsPostWeights"])
    
    def conclude(self,pars) :
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="v12_qcd_py6")
        org.scale(100)
        plotter.plotter( org,
                         psFileName = self.psFileName(org.tag),
                         blackList = ["lumiHisto","xsHisto","xsPostWeightsHisto","nJobsHisto"],
                         ).plotAll()
