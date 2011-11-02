from core.analysis import analysis
import math,steps,calculables,samples,ROOT as r

class triggerWeight(analysis) :
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
        return (calculables.zeroArgs() +
                calculables.fromCollections(calculables.Muon,[pars["muon"]]) +
                [calculables.Muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.Muon.IndicesTriggering( pars['muon'] ),
                 calculables.Vertex.ID(),
                 calculables.Vertex.Indices(),
                 calculables.Other.abbreviation( "nVertexRatio", "nvr" ),
                 calculables.Other.abbreviation('muonTriggerWeightPF','tw')
                 ])

    def listOfSteps(self,pars) :
        return [
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Filter.multiplicity("vertexIndices",min=1),
            steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.Trigger.physicsDeclaredFilter(),
            steps.Filter.monster(),
            steps.Filter.hbheNoise(),
            calculables.Trigger.TriggerWeight(samples = ['SingleMu.Run2011A-PR-v4.FJ.Burt.tw','SingleMu.Run2011A-May10-v1.FJ.Burt.tw'],
                                              triggers = zip(*pars['triggers'])[0], thresholds = zip(*pars['triggers'])[1]),
            calculables.Other.Ratio("nVertex", binning = (15,-0.5,14.5), thisSample = pars['baseSample'],
                                    target = ("SingleMu",[]), groups = [('qcd_py6',[]),('w_jets_fj_mg',[]),('tt_tauola_fj_mg',[])]),
            steps.Histos.value("%sCombinedRelativeIso%s"%pars['muon'], 100, 0, 1, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.absEta("%sP4%s"%pars['muon'], 200,0,2.2, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.phi("%sP4%s"%pars['muon'], 200,-math.pi,math.pi, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.generic(("%sP4%s"%pars['muon'],"%sTriggeringIndex%s"%pars['muon']),
                                 (100,100),(0,-math.pi),(2.2,math.pi), title = ";mu |eta|;mu phi;events / bin",
                                 funcString = "lambda x: (abs(x[0][x[1]].eta()),x[0][x[1]].phi())" ),

            steps.Filter.value("%sTriggeringPt%s"%pars['muon'], min = 35, max = 45),

            steps.Histos.pt("%sP4%s"%pars['muon'], 500,30,50, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.value("%sCombinedRelativeIso%s"%pars['muon'], 100, 0, 1, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.absEta("%sP4%s"%pars['muon'], 200,0,2.2, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.phi("%sP4%s"%pars['muon'], 200,-math.pi,math.pi, "%sIndicesTriggering%s"%pars['muon'], index=0),
            steps.Histos.generic(("%sP4%s"%pars['muon'],"%sTriggeringIndex%s"%pars['muon']),
                                 (100,100),(0,-math.pi),(2.2,math.pi), title = ";mu |eta|;mu phi;events / bin",
                                 funcString = "lambda x: (abs(x[0][x[1]].eta()),x[0][x[1]].phi())" ),
            ]
            
    def listOfSampleDictionaries(self) : return [samples.Muon.muon,samples.MC.mc]

    def listOfSamples(self,params) :
        return ( samples.specify( names = ['SingleMu.Run2011A-PR-v4.FJ.Burt', 
                                           'SingleMu.Run2011A-May10-v1.FJ.Burt'], weights = 'tw') +
                 samples.specify( names = ['qcd_py6fjmu_pt_15_20',
                                           'qcd_py6fjmu_pt_20_30',
                                           'qcd_py6fjmu_pt_30_50',
                                           'qcd_py6fjmu_pt_50_80',
                                           'qcd_py6fjmu_pt_80_120',
                                           'qcd_py6fjmu_pt_120_150',
                                           'qcd_py6fjmu_pt_150',
                                           'w_jets_fj_mg',
                                           'tt_tauola_fj_mg'
                                           ], weights = ['tw','nvr'] , effectiveLumi = 300))
    
    def conclude(self,pars) :
        from core.plotter import plotter
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"SingleMu","color":r.kBlack,"markerStyle":20}, allWithPrefix="SingleMu")
        org.mergeSamples(targetSpec = {"name":"qcd", "color":r.kBlue}, allWithPrefix="qcd")
        org.mergeSamples(targetSpec = {"name":"w_jets","color":r.kRed}, allWithPrefix="w_jets")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}","color":r.kViolet}, allWithPrefix="tt_tauola_fj_mg")
        org.mergeSamples(targetSpec = {"name":"s.m.", "color":r.kGreen+3}, keepSources = True, sources = ['qcd','w_jets','t#bar{t}'])
        org.scale()

        kwargs = { "blackList":["lumiHisto","xsHisto","nJobsHisto","muonTriggerWeightPF"],
                   "samplesForRatios":("SingleMu","s.m.") if "s.m." in [ss['name'] for ss in org.samples] else ("","")}

        plotter(org, psFileName = self.psFileName(org.tag+'_log'),   doLog = True,  **kwargs).plotAll()
        plotter(org, psFileName = self.psFileName(org.tag+'_nolog'), doLog = False, **kwargs).plotAll()
