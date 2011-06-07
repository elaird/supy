#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils,math
import ROOT as r

class topAsymmTemplates(analysis.analysis) :
    def parameters(self) :
        return {"sample" : {#"compare":["mg","pythia"],
                            "mg":"mg",
                            #"pythia":"pythia"
                            },
                "effectiveLumi" : None# 100
                }

    def listOfCalculables(self, pars) :
        outList  = calculables.zeroArgs()
        outList += [
            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            ]
        outList += calculables.fromCollections(calculables.Top,[('genTop',""),('fitTop',"")])
        return outList
    
    def listOfSteps(self, pars) :
        return [steps.Print.progressPrinter(),
                steps.Filter.label("all"),         steps.Top.mcTruthTemplates(),
                steps.Filter.OR([steps.Filter.value('genTTbarIndices',min=0,index='lplus'),
                                 steps.Filter.value('genTTbarIndices',min=0,index='lminus')]),
                steps.Top.mcTruthTemplates(),
                steps.Filter.label("acceptance"),        steps.Top.mcTruthAcceptance(),
                steps.Filter.label("discriminateQQbar"), steps.Top.discriminateQQbar(('genTop','')),
                steps.Filter.label("q direction"),       steps.Top.mcTruthQDir(),
                ]
    
    def listOfSampleDictionaries(self) : return [samples.mc]

    def listOfSamples(self,pars) :
        from samples import specify
        eL = pars["effectiveLumi"]

        if type(pars["sample"]) is list :
            suffixColor = zip(pars["sample"],[r.kBlack,r.kRed])
            return sum([specify(names = "tt_tauola_%s"%suf, effectiveLumi = eL, color = col) for suf,col in suffixColor],[])

        sample = "tt_tauola_%s"%pars["sample"]
        asymms = [(r.kBlue, -0.3),
                  (r.kGreen, 0.0),
                  (r.kRed,   0.3)]
        intrinsicR = -0.05 if pars['sample'] == "mg" else 0.0
        return (
            #specify( names = sample, effectiveLumi = 500, color = r.kBlack,     weights = calculables.Gen.wNonQQbar()) +
            #specify( names = sample, effectiveLumi = eL, color = r.kRed,       weights = calculables.Gen.wQQbar()) +
            sum([specify(names = sample, effectiveLumi = eL, color = col, weights = calculables.Top.wTopAsym(A,intrinsicR=intrinsicR)) for col,A in asymms],[]) +
            [])
    
    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.scale(toPdf=True)

            self.signalChi2(org,("tt_tauola_mg.wTopAsymN30","tt_tauola_mg.wTopAsymP30"), org.keysMatching(["genTopBeta",
                                                                                                           "genTopDeltaAbsYttbar",
                                                                                                           "genTopTrue",
                                                                                                           "genTopMez"
                                                                                                           ]))
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()


    def signalChi2(self,org, samples,hists) :
        iZero,iOne = tuple([org.indexOfSampleWithName(i) for i in samples])
        if iZero is None  or iOne is None : return
        for sel in org.selections :
            print "\n\n%s:%s"%sel.nameTitle
            print '-'*20
            for hist in hists :
                if hist not in sel : continue
                zero = sel[hist][iZero]
                one = sel[hist][iOne]
                print hist.ljust(35), ('%.1f'%zero.Chi2Test(one,"WWOFUFCHI2")).rjust(10)
