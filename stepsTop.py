import copy,array,os,collections,math
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
        pass
        #for charge in ["",["Negative","Positive"][max(0,eV[self.charge][eV[self.index]])]] :
        #    self.book.fill(eV[self.signedY], self.signedY+charge, self.bins,-5,5, title = "%s;%s;events / bin"%(charge,self.signedY))
        #    self.book.fill(eV[self.relY], self.relY+charge, self.bins,-5,5, title = "%s;#Delta y;events / bin"%charge)

        topReco = eV[self.TopReco]
        #lepTopM = topReco[0]['lepTopP4'].M()
        #self.book.fill( lepTopM, "bestLepTopM", 100,0,300, title = ";best leptonic top mass;events / bin" )
        #self.book.fill( (lepTopM, topReco[0]['hadTopP4'].M()), "lepM_vs_hadM", (100,100),(0,0),(300,300),
        #                title = ";best leptonic top mass; corresponding hadronic top mass;events / bin",)
        #self.book.fill( topReco[1]['lepTopP4'].M(), "secondBestLepTopM", 100,0,300, title = ";2nd best leptonic top mass;events / bin" )
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
            for sumP4 in ['genSumP4','genTopTTbarSumP4','mixedSumP4','mixedSumP4Nu'][:4 if self.withNu else 3 if self.withLepton else 2] :
                self.book.fill( qdir * ev[sumP4].pz(), "qdir_%s_pz"%sumP4, 100,-3000,3000, title = ';qdir * %s.pz;events/bin'%sumP4)
                self.book.fill( qdir * ev[sumP4].Eta(), "qdir_%s_eta"%sumP4, 100,-10,10, title = ';qdir * %s.eta;events/bin'%sumP4)
        
#####################################
class mcTruthDiscriminateQQbar(analysisStep) :
    def __init__(self, qqbar = None) :
        self.qqbar = qqbar

    @staticmethod
    def phiMod(phi) : return phi + 2*math.pi*int(phi<0)

    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return
        if self.qqbar!=None and self.qqbar!=bool(ev['genQQbar']) : return

        suf = '' if self.qqbar==None else '_QQbar' if ev['genQQbar'] else '_NonQQbar'
        dphi = self.phiMod(ev['genTopDeltaPhittbar'])

        ### dphi is highly correlated with PtAsym and/or PtOverSumPt, but they are mostly uncorrelated to alpha
        #self.book.fill( (dphi,ev['genTopPtAsymttbar']), 'corrDphiPtAsym', (51,51), (0,-1),(2*math.pi,1), title=';dphi;ptasymm;events / bin' )
        #self.book.fill( (dphi,ev['genTopAlpha']), 'corrDphiAlpha', (51,10), (0,0),(2*math.pi,1), title=';dphi;#alpha;events / bin' )
        #self.book.fill( (ev['genTopTTbarPtOverSumPt'],ev['genTopAlpha']), 'corrPtAsymAlpha'+suf, (50,10), (0,0),(1,1), title=';(t+tbar)_{pt}/(t_{pt}+tbar_{pt});#alpha;events / bin' )

        self.book.fill( dphi, 'genTopDeltaPhittbar'+suf, 51,0,2*math.pi, title = ';#Delta #phi_{ttbar};events / bin')
        self.book.fill( ev['genTopTTbarPtOverSumPt'], 'ttbarPtOverSumPt'+suf, 50,0,1, title = ';(t+tbar)_{pt}/(t_{pt}+tbar_{pt});events / bin')

        self.book.fill(ev['genTopAlpha'],'alpha'+suf,10,0,1,title=';genTopAlpha;events / bin')

        self.book.fill( ev['genTopTTbarSumP4'].Rapidity(), 'ttbarRapidity'+suf, 51,-3,3, title = ';y_{ttbar};events / bin')
        self.book.fill( ev['genTopTTbarSumP4'].Eta(), 'ttbarEta'+suf, 81,-10,10, title = ';#eta_{ttbar};events / bin')
        self.book.fill( ev['genTopTTbarSumP4'].Pz(), 'ttbarPz'+suf, 51,-3000,3000, title = ';pz_{ttbar};events / bin')
        
#####################################
class mcTruthAcceptance(analysisStep) :
    def __init__(self, qqbar = None) :
        self.qqbar = qqbar
    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return
        if self.qqbar is not None and bool(ev['genQQbar']) != self.qqbar : return
        suf = '' if self.qqbar is None else '_QQbar' if ev['genQQbar'] else '_NonQQbar'

        indices = ev['genTTbarIndices']
        if not bool(indices['lplus'])^bool(indices['lminus']) : return
        lep = ev['genP4'][max(indices['lplus'],indices['lminus'])]
        iJets = [indices['b'],indices['bbar']] + indices['wplusChild' if indices['lminus'] else 'wminusChild']
        jets = [ev['genP4'][i] for i in iJets]
        
        self.book.fill(lep.eta(),"lepEta"+suf,31,-5,5, title=';#eta_{lep};events / bin')
        self.book.fill(max([abs(p4.eta()) for p4 in jets]), 'jetEtaMax'+suf, 30,0,5, title=';jet |#eta|_{max};events / bin')
        self.book.fill(min([p4.pt() for p4 in jets]), 'jetMinPt'+suf, 50,0,100, title=';jet pT_{min};events / bin')

#####################################
class mcTruthTemplates(analysisStep) :
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
        self.book.fill(ev['genTopBeta2'], 'genTopBeta2%s'%suf, 20,-1,1, title = ";beta;events / bin")
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopCosThetaStarBar']), 'cts_v_ctsbar%s%s'%(suf,alpha), (100,100),(-1,-1),(1,1), title = ';costhetaQT;cosThetaQbarTbar;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopAlpha']), 'cts_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaQT;#alpha;%s events/bin'%suf)
        #self.book.fill( (ev['genTopCosThetaStarAvg'],ev['genTopAlpha']), 'ctsavg_v_alpha%s'%suf, (25,25),(-1,0),(1,1), title = ';costhetaAvg;#alpha;%s events/bin'%suf)
        #self.book.fill(ev['genTopTTbarSumP4'].M(), "genttbarinvmass", 40,0,1000, title = ';ttbar invariant mass;events / bin' )
        #for i in [0,1]: self.book.fill(ev['genP4'][ev['genTopTTbar'][i]].M(), "topmass", 50, 120, 220, title = ';top mass;events / bin')
        
        qqbar = ev['genQQbar']
        genP4 = ev['genP4']
        qdir = 1 if qqbar and genP4[qqbar[0]].pz()>0 else -1
        genP4dir = 1 if ev['genSumP4'].pz() > 0 else -1
        
        self.book.fill(    qdir * ev['genTopDeltaYttbar'], 'genTopTrueDeltaYttbar', 31,-5,5, title = ';True Signed #Delta y_{ttbar};events / bin')
        self.book.fill(genP4dir * ev['genTopDeltaYttbar'], 'genTopMezDeltaYttbar', 31,-5,5, title = ';MEZ Signed #Delta y_{ttbar};events / bin')
        self.book.fill(        ev['genTopDeltaAbsYttbar'], 'genTopDeltaAbsYttbar', 31,-5,5, title = ';#Delta |y|_{ttbar};events / bin')

        indices = ev['genTTbarIndices']
        if indices['lplus'] and indices['lminus'] :
            dy = genP4[indices['lplus']].Rapidity() - genP4[indices['lminus']].Rapidity()
            self.book.fill(    qdir * dy, "genTopTrueDeltaYll", 31,-5,5, title = ';True Signed #Delta y_{ll};events / bin')
            self.book.fill(genP4dir * dy, "genTopMezDeltaYll", 31,-5,5, title = ';MEZ Signed #Delta y_{ll};events / bin')
        elif indices['lplus'] or indices['lminus'] :
            Q = 1 if indices['lplus'] else -1
            lRapidity = genP4[max(indices['lplus'],indices['lminus'])].Rapidity()
            dy = (lRapidity - ev['genSumP4'].Rapidity())
            for suf in ['','Positive' if Q>0 else 'Negative'] :
                self.book.fill(    qdir * Q * dy, "genTopTrueDeltaYlmiss"+suf, 31,-5,5, title = '%s;True Signed #Delta y_{lmiss};events / bin'%suf)
                self.book.fill(genP4dir * Q * dy, "genTopMezDeltaYlmiss"+suf, 31,-5,5, title = '%s;MEZ Signed #Delta y_{lmiss};events / bin'%suf)
                self.book.fill(    qdir * Q * lRapidity, "genTopTrueLRapidity"+suf, 31,-5,5, title = "%s;True Signed y_l;events / bin"%suf)
                self.book.fill(genP4dir * Q * lRapidity, "genTopMezLRapidity"+suf, 31,-5,5, title = "%s;MEZ Signed y_l;events / bin"%suf)
