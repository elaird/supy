import samples,calculables,steps,os,math,ROOT as r
from core.analysis import analysis

class exampleReweight(analysis) :

    def listOfSteps(self,pars) :
        import calculables.Other
        from steps import Print,Other,Histos,Filter
        return [ Print.progressPrinter(),
                 Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
                 Histos.multiplicity("vertexIndices",max=15),
                 Filter.multiplicity("vertexIndices",min=1),
                 Filter.pt("muonP4PF", min = 25, indices = "muonIndicesPF", index=0),
                 Histos.multiplicity("vertexIndices",max=15),
                 calculables.Other.Ratio("nVertex", binning = (15,-0.5,14.5), thisSample = pars['baseSample'],
                                         target = ("SingleMu",[]), groups = [('qcd_mg',[]),('qcd_py6',[])],
                                         ),
                 Histos.multiplicity("vertexIndices",max=15),
                 ]
    
    def listOfCalculables(self,pars) :
        from calculables import Muon,Vertex
        muon = ("muon","PF")
        return ( calculables.zeroArgs() +
                 calculables.fromCollections(calculables.Muon, [muon]) +
                 [ Muon.Indices( muon, ptMin = 10, combinedRelIsoMax = 0.15),
                   Vertex.ID(),
                   Vertex.Indices(),
                   ] )

    def listOfSampleDictionaries(self) :
        from samples import MC,Muon
        return [MC.mc,Muon.muon]

    def listOfSamples(self,pars) :
        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000][1:]]
            return samples.specify( effectiveLumi = eL, weights = "nVertexRatio",
                                    names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])
        def qcd_py6_mu(eL) :
            q6 = [0,5,15,20,30,50,80,120,150,None]
            iCut = q6.index(15)
            return samples.specify( effectiveLumi = eL, weights = "nVertexRatio",
                                    names = ["qcd_py6fjmu_pt_%s"%("%d_%d"%(low,high) if high else "%d"%low)
                                             for low,high in zip(q6[:-1],q6[1:])[iCut:]] )
        return (samples.specify(names="SingleMu.Run2011A-PR-v4.FJ.Burt4") +
                qcd_mg(100) +
                qcd_py6_mu(100) +
                [])
                
    def conclude(self,pars) :
        from core import plotter
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"qcd_mg", "color":r.kBlue}, allWithPrefix="qcd_mg")
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kRed}, allWithPrefix="qcd_py6")
        org.scale()
        plotter.plotter( org,
                         psFileName = self.psFileName(org.tag),
                         blackList = ["lumiHisto","xsHisto","xsPostWeightsHisto","nJobsHisto","genpthat"],
                         detailedCalculables = True,
                         ).plotAll()
        
