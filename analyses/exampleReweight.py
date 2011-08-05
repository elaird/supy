import os,math,ROOT as r
import analysis,samples,secondaryCalculable

class Ratio(secondaryCalculable.secondaryCalculable) :
    def __init__(self, var=None, binning=(0,0,0), thisSample = None, targetPrefix = None, groupPrefixes = []) :
        self.fixes = (var,"")
        self.defaultValue = 1.0
        self.groups = [targetPrefix] + groupPrefixes
        self.thisGroup = next((gp for gp in self.groups if gp in thisSample),None)
        for item in ["var","binning","groupPrefixes"] : setattr(self,item,eval(item))

    def setup(self,*_) :
        name = 'unweighted'+self.var
        hists = self.fromCache( [self.groups[0], self.thisGroup], [name])
        source = hists[self.thisGroup][name]
        self.weights = hists[self.groups[0]][name]
        if source and self.weights :
            self.weights.Scale(1./self.weights.Integral(0,self.weights.GetNbinsX()+1))
            source.Scale(1./source.Integral(0,source.GetNbinsX()+1))
            self.weights.Divide(source)
        else : self.weights = None
        
    def uponAcceptance(self,eventVars) :
        myWeight = eventVars[self.name]
        value = eventVars[self.var]
        self.book.fill( value, "unweighted"+self.var, *self.binning, w = 1, title = ";%s;events / bin"%self.var )
        self.book.fill( value, "myweighted"+self.var, *self.binning, w = myWeight, title = ";%s;events / bin"%self.var)
        self.book.fill( value, self.var, *self.binning, title = ";%s;events / bin"%self.var )
        self.book.fill(math.log(myWeight), "logMyWeight", 40, -5, 5, w = 1, title = ";log(%s);events / bin"%self.name)

    def update(self, ignored) :
        self.value = self.defaultValue if not self.weights else self.weights.GetBinContent(self.weights.FindFixBin(self.source[self.var]))

    def organize(self,org) :
        [org.mergeSamples( targetSpec = {"name":pre}, allWithPrefix=pre) for pre in self.groups]

class exampleReweight(analysis.analysis) :
    def parameters(self) : return {}

    def listOfSteps(self,pars) :
        import steps
        return [ steps.Print.progressPrinter(),
                 steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
                 steps.Histos.multiplicity("vertexIndices",max=15),
                 steps.Filter.multiplicity("vertexIndices",min=1),
                 steps.Filter.pt("muonP4PF", min = 25, indices = "muonIndicesPF", index=0),
                 steps.Histos.multiplicity("vertexIndices",max=15),
                 Ratio("nVertex", binning = (15,-0.5,14.5), targetPrefix = "SingleMu", groupPrefixes = ['qcd_mg','qcd_py6'], thisSample = pars['baseSample']),
                 steps.Histos.multiplicity("vertexIndices",max=15),
                 ]
    
    def listOfCalculables(self,pars) :
        import calculables
        muon = ("muon","PF")
        return ( calculables.zeroArgs() +
                 calculables.fromCollections(calculables.Muon, [muon]) +
                 [ calculables.Muon.Indices( muon, ptMin = 10, combinedRelIsoMax = 0.15),
                   calculables.Vertex.ID(),
                   calculables.Vertex.Indices(),
                   ] )

    def listOfSampleDictionaries(self) : return [samples.mc,samples.muon]

    def listOfSamples(self,pars) :
        def qcd_py6_mu(eL) :
            q6 = [0,5,15,20,30,50,80,120,150,None]
            iCut = q6.index(15)
            return samples.specify( effectiveLumi = eL, color = r.kOrange, weights = "nVertexRatio",
                                    names = ["qcd_py6fjmu_pt_%s"%("%d_%d"%(low,high) if high else "%d"%low) for low,high in zip(q6[:-1],q6[1:])[iCut:]] )

        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000][1:]]
            return samples.specify( effectiveLumi = eL, color = r.kBlue, weights = "nVertexRatio",
                                    names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])

        return (samples.specify(names="SingleMu.Run2011A-PR-v4.FJ.Burt4") +
                qcd_mg(100) +
                qcd_py6_mu(100) +
                [])
                
    def conclude(self,pars) :
        import plotter
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"qcd_mg", "color":r.kBlue}, allWithPrefix="qcd_mg")
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kRed}, allWithPrefix="qcd_py6")
        org.scale(100)
        plotter.plotter( org,
                         psFileName = self.psFileName(org.tag),
                         blackList = ["lumiHisto","xsHisto","xsPostWeightsHisto","nJobsHisto","genpthat"],
                         detailedCalculables = True,
                         ).plotAll()


