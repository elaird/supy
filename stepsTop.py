import copy,array,os,collections
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class Asymmetry(analysisStep) :
    def __init__(self, lepton) :
        self.charge = "%sCharge%s"%lepton
        self.index = "%sSemileptonicTopIndex%s"%lepton
        self.signedY = "%sSignedRapidity%s"%lepton
        self.relY = "%s%s"%lepton+"RelativeRapiditymixedSumP4Nu"
        self.bins = 31
        self.TopReco = "%sTopReconstruction%s"%lepton
    def uponAcceptance(self,eV) :
        for charge in ["",["Negative","Positive"][max(0,eV[self.charge][eV[self.index]])]] :
            self.book.fill(eV[self.signedY], self.signedY+charge, self.bins,-5,5, title = "%s;%s;events / bin"%(charge,self.signedY))
            self.book.fill(eV[self.relY], self.relY+charge, self.bins,-5,5, title = "%s;#Delta y;events / bin"%charge)

        topReco = eV[self.TopReco]
        lepTopM = topReco[0]['lepTopP4'].M()
        self.book.fill( lepTopM, "bestLepTopM", 100,0,300, title = ";best leptonic top mass;events / bin" )
        self.book.fill( (lepTopM, topReco[0]['hadTopP4'].M()), "lepM_vs_hadM", (100,100),(0,0),(300,300),
                        title = ";best leptonic top mass; corresponding hadronic top mass;events / bin",)
        self.book.fill( topReco[1]['lepTopP4'].M(), "secondBestLepTopM", 100,0,300, title = ";2nd best leptonic top mass;events / bin" )
        #steps.Histos.generic(("%s%s"%lepton+"RelativeRapiditymixedSumP4NuM","%s%s"%lepton+"RelativeRapiditymixedSumP4NuP"),
        #                     (101,101), (-5,-5), (5,5), title = ";#Delta y #nu_{-};#Delta y #nu_{+};events / bin",
        #                     funcString = "lambda x: (x[0],x[1])"),        
#####################################
class mcTruthQDir(analysisStep) :
    def __init__(self,withLepton = False, withNu = False) :
        self.withNu = withNu and withLepton
        self.withLepton = withLepton
        
    def uponAcceptance(self,ev) :
        if ev['isRealData'] : return
        genSumPz = ev['genSumP4'].pz()
        #for sumP4 in ['genTopNuP4','genTopTTbarSumP4','mixedSumP4','mixedSumP4Nu'][:4 if self.withNu else 3 if self.withLepton else 2] :
        #    self.book.fill( (genSumPz, ev[sumP4].pz()), "genSumP4_%s_pz"%sumP4, (100,100),(-3000,-3000),(3000,3000),
        #                    title = ";genSumP4 pz;%s pz;events/bin"%sumP4)

        qqbar = ev['genQQbar']
        if qqbar :
            qdir = 1 if ev['genP4'][qqbar[0]].pz()>0 else -1
            for sumP4 in ['genSumP4','mixedSumP4','mixedSumP4Nu'][:3 if self.withNu else 2 if self.withLepton else 1] :
                self.book.fill( qdir * ev[sumP4].pz(), "qdir_%s_pz"%sumP4, 100,-3000,3000, title = ';qdir * %s.pz;events/bin'%sumP4)
        
#####################################
class mcTruth(analysisStep) :
    def __init__(self,qqbar = None) :
        self.qqbar = qqbar

    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return
        if self.qqbar is not None and bool(ev['genQQbar']) != self.qqbar : return
        suf = '' if self.qqbar is None else '_QQbar' if ev['genQQbar'] else '_NonQQbar'

        self.book.fill(ev['genTopAlpha'],'alpha%s'%suf,10,0,1,title=';genTopAlpha;events / bin')
        alpha = '_alpha%d'%int(10*ev['genTopAlpha'])

        #self.book.fill(ev['genTopCosThetaStar'], 'cosThetaStar%s%s'%(suf,alpha), 20, -1, 1, title = ';cosThetaStar;events / bin')
        self.book.fill(ev['genTopCosThetaStarAvg'], 'cosThetaStarAvg%s%s'%(suf,alpha), 20, -1, 1, title = ';cosThetaStarAvg;events / bin')

        self.book.fill(ev['genTopBeta'], 'genTopBeta%s'%suf, 20,-1,1, title = ";beta;events / bin")
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopCosThetaStarBar']), 'cts_v_ctsbar%s%s'%(suf,alpha), (100,100),(-1,-1),(1,1), title = ';costhetaQT;cosThetaQbarTbar;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopAlpha']), 'cts_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaQT;#alpha;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStarAvg'],ev['genTopAlpha']), 'ctsavg_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaAvg;#alpha;%s events/bin'%suf)
        self.book.fill(ev['genTopTTbarSumP4'].M(), "genttbarinvmass", 40,0,1000, title = ';ttbar invariant mass;events / bin' )
        for i in [0,1]: self.book.fill(ev['genP4'][ev['genTopTTbar'][i]].M(), "topmass", 50, 120, 220, title = ';top mass;events / bin')

        
        qqbar = ev['genQQbar']
        genP4 = ev['genP4']
        qdir = 1 if qqbar and genP4[qqbar[0]].pz()>0 else -1
        genP4dir = 1 if ev['genSumP4'].pz() > 0 else -1
        
        self.book.fill(    qdir * ev['genTopDeltaYttbar'], 'genTopTruepDeltaYttbar', 31,-5,5, title = ';True Signed #Delta y_{ttbar};events / bin')
        self.book.fill(genP4dir * ev['genTopDeltaYttbar'], 'genTopMezDeltaYttbar', 31,-5,5, title = ';MEZ Signed #Delta y_{ttbar};events / bin')

        indices = ev['genTTbarIndices']
        if indices['lplus'] and indices['lminus'] :
            dy = genP4[indices['lplus']].Rapidity() - genP4[indices['lminus']].Rapidity()
            self.book.fill(    qdir * dy, "genTopTrueDeltaYll", 31,-5,5, title = ';True Signed #Delta y_{ll};evens / bin')
            self.book.fill(genP4dir * dy, "genTopMezDeltaYll", 31,-5,5, title = ';MEZ Signed #Delta y_{ll};evens / bin')
        elif indices['lplus'] or indices['lminus'] :
            dy = (1 if indices['lplus'] else -1)*(genP4[max(indices['lplus'],indices['lminus'])].Rapidity() - ev['genSumP4'].Rapidity())
            self.book.fill(    qdir * dy, "genTopTrueDeltaYlmiss", 31,-5,5, title = ';True Signed #Delta y_{lmiss};evens / bin')
            self.book.fill(genP4dir * dy, "genTopMezDeltaYlmiss", 31,-5,5, title = ';MEZ Signed #Delta y_{lmiss};evens / bin')
            
