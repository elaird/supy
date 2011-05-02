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
        outList += [calculables.Top.wTopAsym(i) for i in [-0.3,0,0.3]]
        outList += calculables.fromCollections(calculables.Top,[('genTop',""),('fitTop',"")])
        return outList
    
    def listOfSteps(self, pars) :
        return [steps.Print.progressPrinter(),
                steps.Filter.label("all"),         steps.Top.mcTruthTemplates(),
                steps.Filter.OR([steps.Filter.value('genTTbarIndices',min=0,index='lplus'),
                                 steps.Filter.value('genTTbarIndices',min=0,index='lminus')]),
                steps.Top.mcTruthTemplates(),
                steps.Filter.label("acceptance"),        steps.Top.mcTruthAcceptance(),
                steps.Filter.label("discriminateQQbar"), steps.Top.mcTruthDiscriminateQQbar(),
                steps.Filter.label("q direction"),       steps.Top.mcTruthQDir(),
                ]
    
    def listOfSampleDictionaries(self) : return [samples.mc]

    def listOfSamples(self,pars) :
        from samples import specify
        eL = pars["effectiveLumi"]

        if type(pars["sample"]) is list :
            return (specify( names = "tt_tauola_%s"%pars["sample"][0], effectiveLumi = eL) +
                    specify( names = "tt_tauola_%s"%pars["sample"][1], effectiveLumi = eL, color = r.kRed) )

        sample = "tt_tauola_%s"%pars["sample"]
        return (
            specify( names = sample, effectiveLumi = eL, color = r.kBlack,     weightName = "wNonQQbar") +
            #specify( names = sample, effectiveLumi = eL, color = r.kRed,     weightName = "wQQbar") +
            specify( names = sample, effectiveLumi = eL, color = r.kBlue,      weightName = "wTopAsymN30") +
            #specify( names = sample, effectiveLumi = eL, color = r.kBlue,      weightName = "wTopAsymN20") +
            #specify( names = sample, effectiveLumi = eL, color = r.kGreen+3,   weightName = "wTopAsymN10") +
            specify( names = sample, effectiveLumi = eL, color = r.kGreen,     weightName = "wTopAsymP00") +
            #specify( names = sample, effectiveLumi = eL, color = r.kYellow-3,  weightName = "wTopAsymP10") +
            #specify( names = sample, effectiveLumi = eL, color = r.kOrange,    weightName = "wTopAsymP20") +
            specify( names = sample, effectiveLumi = eL, color = r.kRed,       weightName = "wTopAsymP30") +
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
