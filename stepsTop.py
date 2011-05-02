import copy,array,os,collections,math
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class Asymmetry(analysisStep) :
    def __init__(self, collection) :
        self.collection = collection
        for item in ["LeptonCharge","SignedLeptonRapidity","RelativeLeptonRapidity",
                     "DeltaAbsY","DeltaY","PtOverSumPt","Beta"] :
            setattr(self,item,("%s"+item+"%s")%collection)
        self.bins = 31

    def uponAcceptance(self,ev) :
        for charge in ["",["Negative","Positive"][max(0,ev[self.LeptonCharge])]] :
            self.book.fill(ev[self.SignedLeptonRapidity], "leptonSignedY"+charge, self.bins,-5,5, title = "%s;leptonSignedY;events / bin"%charge)
            self.book.fill(ev[self.RelativeLeptonRapidity], "leptonRelativeY"+charge, self.bins,-5,5, title = "%s;#Delta y;events / bin"%charge)

        
        self.book.fill( ev[self.DeltaAbsY],   'ttbarDeltaAbsY',    31, -4, 4, title = ';#Delta|Y|_{ttbar};events / bin' )
        self.book.fill( ev[self.DeltaY],      'ttbarSignedDeltaY', 31, -4, 4, title = ';sumP4dir * #Delta Y_{ttbar};events / bin' )
        self.book.fill( ev[self.PtOverSumPt], 'ttbarPtOverSumPt',    30,  0, 1, title = ';ttbar MHT/HT;events / bin')
        self.book.fill( ev[self.Beta],        'ttbarBeta',  21, -math.sqrt(2), math.sqrt(2), title = ';#beta_{ttbar};events / bin')
#####################################
class kinFitLook(analysisStep) :
    def uponAcceptance(self,ev) :
        topReco = ev["TopReconstruction"]
        residuals = topReco[0]["residuals"]
        lepTopM = topReco[0]['lepTopP4'].M()
        hadTopM = topReco[0]['hadTopP4'].M()
        lepWM = topReco[0]['lepW'].M()
        hadWM = topReco[0]['hadW'].M()

        for name,val in residuals.iteritems() :
            self.book.fill(val, "topKinFit_residual_%s"%name, 100,-5,5, title = ";residual %s;events / bin"%name)
        self.book.fill((residuals["hadP"],residuals["hadQ"]), "topKinFit_residual_had_PQ", (100,100),(-5,-5),(5,5), title = ';residual hadP;residual hadQ;events / bin')
        self.book.fill((residuals["lepS"],residuals["lepL"]), "topKinFit_residual_lep_SL", (100,100),(-5,-5),(5,5), title = ';residual lepS;residual lepL;events / bin')

        self.book.fill( lepWM, "wMassLepFit", 75, 0, 150, title = ';fit mass_{W} (leptonic);events / bin')
        self.book.fill( hadWM, "wMassHadFit", 75, 0, 150, title = ';fit mass_{W} (hadronic);events / bin')
        self.book.fill( lepTopM, "topMassLepFit", 100,0,300, title = ";fit mass_{top} (leptonic);events / bin" )
        self.book.fill( hadTopM, "topMassHadFit", 100,0,300, title = ";fit mass_{top} (hadronic);events / bin" )
        self.book.fill( (lepTopM, hadTopM), "lepM_vs_hadM", (100,100),(0,0),(300,300),
                        title = ";fit mass_{top} (leptonic); fit mass_{top} (hadronic);events / bin",)

        hadX2 = math.log(1+topReco[0]['hadChi2'])
        lepX2 = math.log(1+topReco[0]['lepChi2'])
        bound = ("_bound" if topReco[0]['lepBound'] else "_unbound")
        self.book.fill( math.log(1+topReco[0]['chi2']), "topRecoLogChi2", 50, 0 , 10, title = ';ttbar kin. fit log(1+#chi^{2});events / bin')
        self.book.fill( hadX2, "topRecoLogHadChi2", 50, 0 , 10, title = ';ttbar kin. fit log(1+#chi^{2}_{had});events / bin')
        self.book.fill( lepX2, "topRecoLogLepChi2", 50, 0 , 10, title = ';ttbar kin. fit log(1+#chi^{2}_{lep});events / bin')
        self.book.fill( lepX2, "topRecoLogLepChi2"+bound, 50, 0 , 10, title = ';ttbar kin. fit log(1+#chi^{2}_{lep});events / bin')
        self.book.fill( (lepX2,hadX2), "topRecoVsLogX2", (50,50),(0,0),(10,10), title = ";log(1+#chi^{2}_{lep});log(1+#chi^{2}_{had});events / bin" )

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
            for sumP4 in ['genSumP4','genTopSumP4','mixedSumP4','mixedSumP4Nu'][:4 if self.withNu else 3 if self.withLepton else 2] :
                self.book.fill( qdir * ev[sumP4].pz(), "qdir_%s_pz"%sumP4, 100,-3000,3000, title = ';qdir * %s.pz;events/bin'%sumP4)
                self.book.fill( qdir * ev[sumP4].Eta(), "qdir_%s_eta"%sumP4, 100,-10,10, title = ';qdir * %s.eta;events/bin'%sumP4)
        
#####################################
class discriminateQQbar(analysisStep) :
    def __init__(self, collection) :
        for item in ['DeltaPhi','PtOverSumPt','SumP4'] :
            setattr(self,item,('%s'+item+'%s')%collection)
        
    @staticmethod
    def phiMod(phi) : return phi + 2*math.pi*int(phi<0)

    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return

        dphi = self.phiMod(ev[self.DeltaPhi])

        ### dphi is highly correlated with PtAsym and/or PtOverSumPt, but they are mostly uncorrelated to alpha
        #self.book.fill( (dphi,ev['genTopPtAsymttbar']), 'corrDphiPtAsym', (51,51), (0,-1),(2*math.pi,1), title=';dphi;ptasymm;events / bin' )
        #self.book.fill( (dphi,ev['genTopAlpha']), 'corrDphiAlpha', (51,10), (0,0),(2*math.pi,1), title=';dphi;#alpha;events / bin' )
        #self.book.fill( (ev['genTopTTbarPtOverSumPt'],ev['genTopAlpha']), 'corrPtAsymAlpha', (50,10), (0,0),(1,1), title=';(t+tbar)_{pt}/(t_{pt}+tbar_{pt});#alpha;events / bin' )

        self.book.fill( dphi, self.DeltaPhi, 51,0,2*math.pi, title = ';#Delta #phi_{ttbar};events / bin')
        self.book.fill( ev[self.PtOverSumPt], self.PtOverSumPt, 50,0,1, title = ';(t+tbar)_{pt}/(t_{pt}+tbar_{pt});events / bin')
        sumP4 = ev[self.SumP4]
        self.book.fill( abs(sumP4.Rapidity()), self.SumP4+'AbsRapidity', 50,0,3, title = ';y_{ttbar};events / bin')
        self.book.fill( abs(sumP4.Eta()), self.SumP4+'AbsEta', 40,0,10, title = ';|#eta_{ttbar}|;events / bin')
        self.book.fill( abs(sumP4.Pz()), self.SumP4+'AbsPz', 50,0,3000, title = ';|pz|_{ttbar};events / bin')
        
#####################################
class mcTruthAcceptance(analysisStep) :
    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return

        indices = ev['genTTbarIndices']
        if not bool(indices['lplus'])^bool(indices['lminus']) : return
        lep = ev['genP4'][max(indices['lplus'],indices['lminus'])]
        iJets = [indices['b'],indices['bbar']] + indices['wplusChild' if indices['lminus'] else 'wminusChild']
        jets = [ev['genP4'][i] for i in iJets]
        iBlep = indices['b'] if indices['lplus'] else indices['bbar']
        
        self.book.fill(lep.eta(),"lepEta",31,-5,5, title=';#eta_{lep};events / bin')
        self.book.fill(max([abs(p4.eta()) for p4 in jets]), 'jetEtaMax', 30,0,5, title=';jet |#eta|_{max};events / bin')
        self.book.fill(max([abs(p4.eta()) for p4 in jets[:2]]), 'jetEtaMaxB', 30,0,5, title=';b jet |#eta|_{max};events / bin')
        self.book.fill(max([abs(p4.eta()) for p4 in jets[2:]]), 'jetEtaMaxLite', 30,0,5, title=';lite jet |#eta|_{max};events / bin')

        pts = [p4.pt() for p4 in jets]
        self.book.fill(min(pts), 'jetMinPt', 50,0,100, title=';jet pT_{min};events / bin')
        self.book.fill(min(pts[:2]), 'jetMinPtB', 50,0,100, title=';b jet pT_{min};events / bin')
        self.book.fill(min(pts[2:]), 'jetMinPtLite', 50,0,100, title=';lite jet pT_{min};events / bin')

        self.book.fill( max(pts[:2]) - min(pts[2:]), "diffBigBLittleQ", 50,-50,100,title=';pT_{maxb}-pT_{minq};events / bin' )
        self.book.fill( min(pts[:2]) - max(pts[2:]), "diffLittleBBigQ", 50,-50,100,title=';pT_{minb}-pT_{maxq};events / bin' )
        self.book.fill( sum(pts[:2]) - sum(pts[2:]), "diffSumBBSumQQ", 50,-50,100,title=';sumpT_{b}-sumpT_{q};events / bin' )
        
        self.book.fill(sum(pts), 'jetSumPt', 50, 0, 800, title=';#sum pT_{top jets};events / bin')
        self.book.fill(sum(pts)-ev['genP4'][iBlep].pt(), 'jetSumPtHad', 50, 0, 500, title=';hadronic #sum pT_{top jets};events / bin')

        self.book.fill( int(max(pts)==max(pts[:2])), "maxPtJetIsBjet", 2, 0 , 1, title = ';maxPt is bjet;events / bin')
        self.book.fill( int(max(pts[:2])>min(pts[2:])), "maxPtOrNextJetIsBjet", 2, 0 , 1, title = ';maxPt or next is bjet;events / bin')
        self.book.fill( int(sum(pts[:2])>sum(pts[2:])), "sumPtBB_gt_sumPtPQ", 2, 0 , 1, title = ';sumPt of bs > sumPt of pq;events / bin')
#####################################
class mcTruthTemplates(analysisStep) :
    def uponAcceptance(self,ev) :
        if not ev['genTopTTbar'] : return

        self.book.fill(ev['genTopAlpha'],'alpha',10,0,2,title=';genTopAlpha;events / bin')
        alpha = '_alpha%02d'%int(10*ev['genTopAlpha'])

        self.book.fill(ev['genTopCosThetaStarAvg'], 'cosThetaStarAvg%s'%alpha, 20, -1, 1, title = ';cosThetaStarAvg;events / bin')

        self.book.fill(ev['genTopBeta'], 'genTopBeta', 20,-2,2, title = ";beta;events / bin")
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopCosThetaStarBar']), 'cts_v_ctsbar%s'%alpha, (100,100),(-1,-1),(1,1), title = ';costhetaQT;cosThetaQbarTbar;events/bin')
        #self.book.fill( (ev['genTopCosThetaStar'],ev['genTopAlpha']), 'cts_v_alpha', (25,25),(-1,0),(1,1), title = ';costhetaQT;#alpha;events/bin')
        #self.book.fill( (ev['genTopCosThetaStarAvg'],ev['genTopAlpha']), 'ctsavg_v_alpha', (25,25),(-1,0),(1,1), title = ';costhetaAvg;#alpha;%s events/bin')
        #self.book.fill(ev['genTopTTbarSumP4'].M(), "genttbarinvmass", 40,0,1000, title = ';ttbar invariant mass;events / bin' )
        #for i in [0,1]: self.book.fill(ev['genP4'][ev['genTopTTbar'][i]].M(), "topmass", 50, 120, 220, title = ';top mass;events / bin')
        
        qqbar = ev['genQQbar']
        genP4 = ev['genP4']
        qdir = 1 if qqbar and genP4[qqbar[0]].pz()>0 else -1
        genP4dir = 1 if ev['genSumP4'].pz() > 0 else -1
        
        self.book.fill(    qdir * ev['genTopDeltaY'], 'genTopTrueDeltaYttbar', 31,-5,5, title = ';True Signed #Delta y_{ttbar};events / bin')
        self.book.fill(genP4dir * ev['genTopDeltaY'], 'genTopMezDeltaYttbar', 31,-5,5, title = ';MEZ Signed #Delta y_{ttbar};events / bin')
        self.book.fill(        ev['genTopDeltaAbsY'], 'genTopDeltaAbsYttbar', 31,-5,5, title = ';#Delta |y|_{ttbar};events / bin')

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
