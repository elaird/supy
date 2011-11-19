from core.analysis import analysis
import steps,calculables,samples

class topAsymmTemplates(analysis) :
    def parameters(self) :
        return {"effectiveLumi" : None,
                "generator" : self.vary({"compare":["_mg",""],
                                         "mg":"_mg",
                                         "pythia":""
                                         }),
                }

    def listOfCalculables(self, pars) :
        return ( calculables.zeroArgs() +
                 calculables.fromCollections(calculables.Top,[('genTop',""),('fitTop',"")]) +
                 [ calculables.Vertex.ID(),
                   calculables.Vertex.Indices(),
                   ]
                 )
    
    def listOfSteps(self, pars) :
        return [steps.Print.progressPrinter(),
                #steps.Gen.topPrinter(),
                steps.Gen.genParticlePrinter()
                #steps.Filter.label("all"),         steps.Top.mcTruthTemplates(),
                #steps.Filter.OR([steps.Filter.value('genTTbarIndices',min=0,index='lplus'),
                #                 steps.Filter.value('genTTbarIndices',min=0,index='lminus')]),
                #steps.Top.mcTruthTemplates(),
                #steps.Filter.label("acceptance"),        steps.Top.mcTruthAcceptance(),
                #steps.Filter.label("discriminateQQbar"), steps.Top.discriminateQQbar(('genTop','')),
                #steps.Filter.label("q direction"),       steps.Top.mcTruthQDir(),
                ]
    
    def listOfSampleDictionaries(self) : return [samples.MC.mc]

    def listOfSamples(self,pars) :
        import ROOT as r
        eL = pars["effectiveLumi"]

        if type(pars["generator"]) is list :
            suffixColor = zip(pars["generator"],[r.kBlack,r.kRed])
            return sum([samples.specify(names = "tt_tauola_fj%s"%suf, effectiveLumi = eL, color = col ) for suf,col in suffixColor],[])
            #return sum([samples.specify(names = "tt_tauola_fj%s"%suf, effectiveLumi = eL, color = col, weights = "wQQbar" ) for suf,col in suffixColor],[])
            #return sum([samples.specify(names = "tt_tauola_fj%s"%suf, effectiveLumi = eL, color = col, weights = ["wQQbar","TwoToTwo"] ) for suf,col in suffixColor],[])

        sample = "tt_tauola_fj%s"%pars["generator"]
        asymms = [(r.kBlue, -0.3),
                  (r.kGreen, 0.0),
                  (r.kRed,   0.3)]
        R_sm = -0.05 if pars['generator'] == "mg" else 0.0
        return (
            #samples.specify( names = sample, effectiveLumi = 500, color = r.kBlack,     weights = calculables.Gen.wNonQQbar()) +
            #samples.specify( names = sample, effectiveLumi = eL, color = r.kRed,       weights = calculables.Gen.wQQbar()) +
            sum([samples.specify(names = sample, effectiveLumi = eL, color = col, weights = calculables.Top.wTopAsym(R,R_sm=R_sm)) for col,R in asymms],[]) +
            [])
    
    def conclude(self,pars) :
        org = self.organizer(pars)
        org.scale(toPdf=True)

        self.signalChi2(org,("tt_tauola_fj_mg.wTopAsymN30","tt_tauola_fj_mg.wTopAsymP30"), org.keysMatching(["genTopBeta",
                                                                                                             "genTopDeltaAbsYttbar",
                                                                                                             "genTopTrue",
                                                                                                             "genTopMez"
                                                                                                             ]))
        from core import plotter
        pl = plotter.plotter(org,
                             psFileName = self.psFileName(org.tag),
                             doLog = False,
                             pegMinimum = 0.1,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             ).plotAll()


    def signalChi2(self,org, samples,hists) :
        iZero,iOne = tuple([org.indexOfSampleWithName(i) for i in samples])
        if iZero is None  or iOne is None : return
        for sel in org.steps :
            print "\n\n%s:%s"%sel.nameTitle
            print '-'*20
            for hist in hists :
                if hist not in sel : continue
                zero = sel[hist][iZero]
                one = sel[hist][iOne]
                print hist.ljust(35), ('%.1f'%zero.Chi2Test(one,"WWOFUFCHI2")).rjust(10)
