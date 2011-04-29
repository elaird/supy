from wrappedChain import *
import calculables,math,utils,fitKinematic

######################################
class genTopNuP4(wrappedChain.calculable) :
    def __init__(self) :
        self.empty = utils.LorentzV()
    def update(self,ignored) :
        self.value = self.empty
        if self.source['isRealData'] : return
        for index,pdg,mother in zip( range(len(self.source['genPdgId'])),
                                     self.source['genPdgId'],
                                     self.source['genMotherPdgId'] ) :
            if abs(mother) == 24 and abs(pdg) in [12,14] :
                self.value = self.source['genP4'][index]
                return
######################################
class genTopTTbar(wrappedChain.calculable) :
    def update(self,ignored) :
        self.value = tuple(list(self.source['genPdgId']).index(i) for i in [6,-6]) if \
                     (not self.source['isRealData']) and \
                     all([id in self.source['genPdgId'] for id in [-6,6]]) else ()
######################################
class genTTbarIndices(wrappedChain.calculable) :
    def update(self,ignored) :
        ids = [i for i in self.source['genPdgId']]
        mom = self.source['genMotherIndex']
        self.value = dict([(name, ids.index(i)) for name,i in [('t',6),
                                                               ('tbar',-6),
                                                               ('wplus',24),
                                                               ('wminus',-24)
                                                               ]])
        self.value.update(dict([ (w+"Child",filter(lambda i: mom[i]==self.value[w],range(len(ids)))) for w in ['wplus','wminus','t','tbar']]))
        self.value['b'] = list(set(self.value['tChild']) - set(['24']))[0]
        self.value['bbar'] = list(set(self.value['tbarChild']) - set(['-24']))[0]
        self.value['lplus'] = max([None]+filter(lambda i: ids[i] in [-11,-13],self.value['wplusChild']))
        self.value['lminus'] = max([None]+filter(lambda i: ids[i] in [11,13],self.value['wminusChild']))
######################################
class genTopTTbarPtOverSumPt(wrappedChain.calculable) :
    def update(self,ignored) :
        self.value = self.source['genTopTTbarSumP4'].Pt() / self.source['genTopTTbarSumPt']
######################################
class genTopDeltaPhittbar(wrappedChain.calculable) :
    def update(self,ignored) :
        p4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = r.Math.VectorUtil.DeltaPhi(p4[ttbar[0]], p4[ttbar[1]]) if ttbar else None
######################################
class genTopDeltaYttbar(wrappedChain.calculable) :
    def update(self,ignored) :
        p4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = p4[ttbar[0]].Rapidity() - p4[ttbar[1]].Rapidity() if ttbar else None
######################################
class genTopDeltaAbsYttbar(wrappedChain.calculable) :
    def update(self,ignored) :
        p4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = abs(p4[ttbar[0]].Rapidity()) - abs(p4[ttbar[1]].Rapidity()) if ttbar else None
######################################
class genTopTTbarSumP4(wrappedChain.calculable) :
    def update(self,ignored) :
        genP4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = genP4[ttbar[0]] + genP4[ttbar[1]]
######################################
class genTopTTbarSumPt(wrappedChain.calculable) :
    def update(self,ignored) :
        genP4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = genP4[ttbar[0]].Pt() + genP4[ttbar[1]].Pt()
######################################
class CosThetaStar(wrappedChain.calculable) :
    def __init__(self,TTbarIndex) :
        self.TTbarIndex = TTbarIndex
    def update(self,ignored) :
        qqbar = self.source['genQQbar']
        genP4 = self.source['genP4']
        boost = r.Math.BoostZ( self.source['genTopTTbarSumP4'].BoostToCM().z())
        iTop = self.source['genTopTTbar'][self.TTbarIndex]
        iAxis = qqbar[0] if qqbar else self.source['genIndexStrongerParton']

        self.value = r.Math.VectorUtil.CosTheta(boost(genP4[iTop]),genP4[iAxis]) *( 1 if self.TTbarIndex else -1)
######################################
class genTopCosThetaStar(CosThetaStar) :
    def __init__(self) : super(genTopCosThetaStar,self).__init__(0)
class genTopCosThetaStarBar(CosThetaStar) :
    def __init__(self) : super(genTopCosThetaStarBar,self).__init__(1)
class genTopCosThetaStarAvg(wrappedChain.calculable) :
    def update(self,ignored) :
        x,y = tuple(self.source['genTopCosThetaStar%s'%suf] for suf in ['','Bar'])
        sign = 1 if x>0 else -1
        self.value = sign - sign*math.sqrt((x-sign)*(y-sign))
######################################
class genTopAlpha(wrappedChain.calculable) :
    m2 = 172**2
    def update(self,ignored) :
        x = 4*self.m2/ (self.source['genTopTTbarSumP4'].E())**2
        self.value = max(0,(1-x)/(1+x))
######################################
__f0__ = 0.6
__R__ = 0.04
######################################
class genTopBeta(wrappedChain.calculable) :
    def update(self, ignored) :
        self.value = self.source['genTopCosThetaStarAvg'] * math.sqrt(min(__f0__,self.source['genTopAlpha']))
######################################
class genTopBeta2(wrappedChain.calculable) :
    def update(self, ignored) :
        self.value = self.source['genTopCosThetaStarAvg'] * math.sqrt(self.source['genTopAlpha'])
######################################
class wTopAsym(wrappedChain.calculable) :
    def __init__(self,rPrime,totalEff=None) :
        self.rPrime = rPrime
        self.R = __R__
        self.epsilon = 1.
        self.epsilon = 1. / max( self.weight(math.sqrt(__f0__),__f0__),
                                 self.weight(-math.sqrt(__f0__),__f0__))

        assert self.epsilon <= 1.
        assert totalEff < self.epsilon
        if 0 < totalEff : self.epsilon = totalEff
        
    def weight(self,beta,alpha) :
        base = 3 * (1+beta*beta) / (6+2.*alpha)
        return (base+beta*self.rPrime) / (base+beta*self.R)
    
    def update(self,ignored) :
        self.value = None if not self.source['genQQbar'] else self.weight(self.source['genTopBeta'],
                                                                          min(__f0__,self.source['genTopAlpha']))
class wTopAsymN30(wTopAsym) :
    def __init__(self) : super(wTopAsymN30,self).__init__(-0.30)
class wTopAsymN20(wTopAsym) :
    def __init__(self) : super(wTopAsymN20,self).__init__(-0.20)
class wTopAsymN15(wTopAsym) :
    def __init__(self) : super(wTopAsymN15,self).__init__(-0.15)
class wTopAsymN10(wTopAsym) :
    def __init__(self) : super(wTopAsymN10,self).__init__(-0.10)
class wTopAsymN05(wTopAsym) :
    def __init__(self) : super(wTopAsymN05,self).__init__(-0.05)
class wTopAsymP00(wTopAsym) :
    def __init__(self) : super(wTopAsymP00,self).__init__(0.00)
class wTopAsymP05(wTopAsym) :
    def __init__(self) : super(wTopAsymP05,self).__init__(0.05)
class wTopAsymP10(wTopAsym) :
    def __init__(self) : super(wTopAsymP10,self).__init__(0.10)
class wTopAsymP15(wTopAsym) :
    def __init__(self) : super(wTopAsymP15,self).__init__(0.15)
class wTopAsymP20(wTopAsym) :
    def __init__(self) : super(wTopAsymP20,self).__init__(0.20)
class wTopAsymP30(wTopAsym) :
    def __init__(self) : super(wTopAsymP30,self).__init__(0.30)
######################################
class mixedSumP4(wrappedChain.calculable) :
    def __init__(self, transverse = None, longitudinal = None) :
        self.trans = transverse
        self.longi = longitudinal
        self.moreName = "transvers: %s ; longitudinal: %s" % (transverse,longitudinal)
        self.value = utils.LorentzV()
    def update(self,ignored) :
        trans = self.source[self.trans]
        longi = self.source[self.longi]
        f = trans.pt() / longi.pt()
        self.value.SetPxPyPzE(-trans.px(),-trans.py(), f*longi.pz(), f*longi.E())
#####################################
class SemileptonicTopIndex(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","IndicesNonIso"])
        self.moreName = "Just indices[0] or indicesNonIso[0] for now."

    def update(self,ignored) :
        indices = self.source[self.Indices]
        nonIso = self.source[self.IndicesNonIso]
        self.value = indices[0] if indices else nonIso[0] if nonIso else None
#####################################
class TopReconstruction(wrappedChain.calculable) :
    def __init__(self, collection, jets, SumP4) :
        self.fixes = collection
        self.stash(["SemileptonicTopIndex","P4","Charge"])
        self.stash(["CorrectedP4","IndicesBtagged","Indices","Resolution","CovariantResolution2"],jets)
        self.SumP4 = SumP4

    def reconstruct(self, iBhad, iQQ, iBlep, zPlus) :
        iLep = self.source[self.SemileptonicTopIndex]
        charge = self.source[self.Charge][iLep]
        iHad = tuple([iBhad] + iQQ)
        if iHad not in self.hadronicFitCache :
            hadP4 = [self.source[self.CorrectedP4][i] for i in iHad]
            hadRes = [self.source[self.Resolution][i] for i in iHad]
            if len(iQQ) == 1 : hadP4.append(utils.LorentzV()); hadRes.append(1.0)
            self.hadronicFitCache[iHad] = fitKinematic.minuitHadronicTop(hadP4, hadRes)

        hadronicFit = self.hadronicFitCache[iHad]
        hadTopP4 = sum(hadronicFit.J.fitted, utils.LorentzV())
        
        sumP4 = self.source[self.SumP4] - sum(hadronicFit.J.raw,utils.LorentzV()) + hadTopP4
        lepP4 = self.source[self.P4][iLep]

        iUnusedJets = list(set(range(len(self.source[self.CorrectedP4])))-set(list(iHad)+[iBlep]))
        nuErr = sum([self.source[self.CovariantResolution2][i] for i in iUnusedJets], calculables.Jet.CovariantResolution2.matrix())

        leptonicFit = fitKinematic.minuitLeptonicTop(self.source[self.CorrectedP4][iBlep],
                                                     self.source[self.Resolution][iBlep],
                                                     lepP4, -sumP4.x(), -sumP4.y(),
                                                     nuErr, zPlus = zPlus )

        lepTopP4 = leptonicFit.mu.P4 + leptonicFit.nu.fitted + leptonicFit.B.fitted
        topP4 = lepTopP4 if charge > 0 else hadTopP4
        tbarP4= hadTopP4 if charge > 0 else lepTopP4
        
        return {"nu"   : leptonicFit.nu.fitted,
                "lep"  : leptonicFit.mu.P4,
                "lepB" : leptonicFit.B.fitted,
                "lepW" : leptonicFit.mu.P4 + leptonicFit.nu.fitted,
                "hadB" : hadronicFit.J.fitted[0],
                "hadP" : hadronicFit.J.fitted[1],
                "hadQ" : hadronicFit.J.fitted[2],
                "hadW" : hadronicFit.J.fitted[1] + hadronicFit.J.fitted[2],
                "lepTopP4" : lepTopP4,
                "hadTopP4" : hadTopP4,
                "chi2" : hadronicFit.chi2() + leptonicFit.chi2(),
                "top"  : topP4,
                "tbar" : tbarP4,
                "sumP4": sumP4,
                "residuals" : {"lepB":leptonicFit.residuals.B,
                               "lepS":leptonicFit.residuals.S,
                               "lepL":leptonicFit.residuals.L,
                               "lepT":leptonicFit.residuals.T,
                               "hadB":hadronicFit.J.residuals[0],
                               "hadP":hadronicFit.J.residuals[1],
                               "hadQ":hadronicFit.J.residuals[2],
                               "hadW":hadronicFit.W.residual,
                               "hadT":hadronicFit.T.residual
                               }
                }

    def update(self,ignored) :
        self.hadronicFitCache = {}

        bIndices = set(self.source[self.IndicesBtagged][:3]) #consider the top 3 tags as possible b candidates
        allIndices = set(self.source[self.Indices])
        recos = []
        
        for iBLep in bIndices :
            for iBHad in (bIndices-set([iBLep])) :
                iOther = list(allIndices - set([iBLep,iBHad]))
                for iP in iOther :
                    for iQ in iOther[iOther.index(iP)+1:] :
                        pts = [self.source[self.CorrectedP4][i].pt() for i in [iBLep,iBHad,iP,iQ]]
                        if max(pts[:2])<min(pts[2:]) : continue # probability that neither of the two leading in pT is a b-jet is only 7%
                        if sum(pts[1:])<100 : continue # probability that the sumPt of hadronic side jets is less that 100 is only 4%
                        for zPlus in [0,1] :
                            recos.append( self.reconstruct(iBHad,[iP,iQ],iBLep, zPlus))
        if not recos:
            bIndices = self.source[self.IndicesBtagged][:2]
            indices = filter(lambda i: i not in bIndices, self.source[self.Indices])[:2]
            recos = [ self.reconstruct( bIndices[not bLep], indices, bIndices[bLep], zPlus) for bLep in [0,1] for zPlus in [0,1] ]
        self.value = sorted( recos,  key = lambda x: x["chi2"] )
#####################################
class NeutrinoP4(wrappedChain.calculable) :
    def __init__(self, collection) :
        self.fixes = collection
        self.stash(["TopReconstruction"])
    def update(self,ignored) :
        self.value = self.source[self.TopReconstruction][0]["nu"]
#####################################
class SumP4Nu(wrappedChain.calculable) :
    def name(self) : return self.SumP4 + "Nu"
    def __init__(self, collection, SumP4) :
        self.SumP4 = SumP4
        self.stash(["NeutrinoP4"],collection)
    def update(self,ignored) :
        self.value = self.source[self.NeutrinoP4] + self.source[self.SumP4]
######################################
class SignedRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None, SumP4 = None) :
        self.fixes = collection
        self.SumP4 = SumP4
        self.stash(["SemileptonicTopIndex","P4","Charge"])
        self.moreName = "sign(y_sum) * q_lep * y_lep"
    def update(self,ignored) :
        index = self.source[self.SemileptonicTopIndex]
        self.value = None if index is None else \
                     (1 if self.source[self.SumP4].Rapidity()>0 else -1)*self.source[self.Charge][index]*self.source[self.P4][index].Rapidity()
#####################################
class RelativeRapidity(wrappedChain.calculable) :
    def name(self) : return "%s%s"%self.fixes + self.__class__.__name__ + self.SumP4
    def __init__(self, collection = None, SumP4 = None) :
        self.fixes = collection
        self.SumP4 = SumP4
        self.stash(["SemileptonicTopIndex","P4","Charge"])
        self.moreName = "sign(y_sum) * q_lep * (y_lep-y_sum); %s%s; %s"%(collection+(SumP4,))

    def update(self,ignored) :
        index = self.source[self.SemileptonicTopIndex]
        if index is None: self.value=None; return

        y_sum = self.source[self.SumP4].Rapidity()
        y_lep = self.source[self.P4][index].Rapidity()
        q_lep = self.source[self.Charge][index]
        
        self.value = (1 if y_sum>0 else -1) * q_lep * (y_lep-y_sum)
######################################
class TTbarDeltaAbsY(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["TopReconstruction"])

    def update(self,ignored) :
        reco = self.source[self.TopReconstruction][0]
        self.value = abs(reco['top'].Rapidity()) - abs(reco['tbar'].Rapidity())
######################################
class TTbarSignedDeltaY(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["TopReconstruction"])

    def update(self,ignored) :
        reco = self.source[self.TopReconstruction][0]
        sign = 1 if reco['sumP4'].Eta() > 0 else -1
        self.value = sign * (reco['top'].Rapidity() - reco['tbar'].Rapidity())
######################################
class TTbarMHTOverHT(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["TopReconstruction"])

    def update(self,ignored) :
        reco = self.source[self.TopReconstruction][0]
        sumP4 = reco['top'] + reco['tbar']
        sumPt = reco['top'].Pt() + reco['tbar'].Pt()
        self.value = sumP4.Pt() / sumPt
