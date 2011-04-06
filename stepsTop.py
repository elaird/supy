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
    def __init__(self,withNu=False) :
        self.withNu = withNu
    def uponAcceptance(self,ev) :
        if ev['isRealData'] : return
        genSumPz = ev['genSumP4'].pz()
        for sumP4 in ['genTopNuP4','genTopTTbarSumP4','mixedSumP4','mixedSumP4Nu'][:4 if self.withNu else 3] :
            self.book.fill( (genSumPz, ev[sumP4].pz()), "genSumP4_%s_pz"%sumP4, (100,100),(-3000,-3000),(3000,3000),
                            title = ";genSumP4 pz;%s pz;events/bin"%sumP4)

        qqbar = ev['genQQbar']
        if qqbar :
            qdir = 1 if ev['genP4'][qqbar[0]].pz()>0 else -1
            for sumP4 in ['genSumP4','mixedSumP4','mixedSumP4Nu'][:3 if self.withNu else 2] :
                self.book.fill( qdir * ev[sumP4].pz(), "qdir_%s_pz"%sumP4, 100,-3000,3000, title = ';qdir * %s.pz;events/bin'%sumP4)
        
#####################################
class mcTruth(analysisStep) :
    def __init__(self,lepton) :

        pass

    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return
        suf = '_QQbar' if ev['genQQbar'] else '_NonQQbar'
        self.book.fill(ev['genTopAlpha'],'alpha%s'%suf,10,0,1,title=';genTopAlpha;events / bin')
        alpha = '_alpha%d'%int(10*ev['genTopAlpha'])

        #self.book.fill(ev['genTopCosThetaStar'], 'cosThetaStar%s%s'%(suf,alpha), 20, -1, 1, title = ';cosThetaStar;events / bin')
        self.book.fill(ev['genTopCosThetaStarAvg'], 'cosThetaStarAvg%s%s'%(suf,alpha), 20, -1, 1, title = ';cosThetaStarAvg;events / bin')

        self.book.fill(ev['genTopBeta'], 'genTopBeta%s'%suf, 20,-1,1, title = ";beta;events / bin")
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopCosThetaStarBar']), 'cts_v_ctsbar%s%s'%(suf,alpha), (100,100),(-1,-1),(1,1), title = ';costhetaQT;cosThetaQbarTbar;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopAlpha']), 'cts_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaQT;#alpha;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStarAvg'],ev['genTopAlpha']), 'ctsavg_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaAvg;#alpha;%s events/bin'%suf)
