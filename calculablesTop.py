from wrappedChain import *
import calculables,math,utils,fitKinematic,operator
######################################
class TopP4Calculable(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4'])
######################################
######################################
class SumP4(TopP4Calculable) :
    def update(self,ignored) :
        self.value = self.source[self.P4]['t'] + self.source[self.P4]['tbar']
######################################
class SumPt(TopP4Calculable) :
    def update(self,ignored) :
        self.value = self.source[self.P4]['t'].pt() + self.source[self.P4]['tbar'].pt()
######################################
class PtOverSumPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SumP4','SumPt'])
    def update(self,ignored) :
        self.value = self.source[self.SumP4].pt() / self.source[self.SumPt]
######################################
class BoostZ(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SumP4'])
    def update(self,ignored) :
        self.value = r.Math.BoostZ( self.source[self.SumP4].BoostToCM().z())
######################################
class DeltaPhi(TopP4Calculable) :
    def update(self,ignored) :
        self.value = r.Math.VectorUtil.DeltaPhi(self.source[self.P4]['t'], self.source[self.P4]['tbar'])
######################################
class DeltaY(TopP4Calculable) :
    def update(self,ignored) :
        self.value = self.source[self.P4]['t'].Rapidity() - self.source[self.P4]['tbar'].Rapidity()
######################################
class DeltaAbsY(TopP4Calculable) :
    def update(self,ignored) :
        self.value = abs(self.source[self.P4]['t'].Rapidity()) - abs(self.source[self.P4]['tbar'].Rapidity())
######################################
class WqqDeltaR(TopP4Calculable) :
    def update(self,ignored) :
        self.value = r.Math.VectorUtil.DeltaR(self.source[self.P4]['p'],self.source[self.P4]['q'])
######################################
class SignedLeptonRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4',"LeptonCharge"])
    def update(self,ignored) :
        p4 = self.source[self.P4]
        charge = self.source[self.LeptonCharge]
        self.value = (1 if p4['quark'].z()>0 else -1) * charge * p4['lepton'].Rapidity()
#####################################
class RelativeLeptonRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["SumP4","P4","LeptonCharge"])
        self.moreName = "sign(y_sum) * q_lep * (y_lep-y_sum); %s%s; %s"%(collection+(SumP4,))

    def update(self,ignored) :
        q_lep = self.source[self.LeptonCharge]
        y_lep = self.source[self.P4]['lepton'].Rapidity()
        y_sum = self.source[self.SumP4].Rapidity()
        
        self.value = (1 if y_sum>0 else -1) * q_lep * (y_lep-y_sum)
#####################################
class Alpha(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SumP4'])
        self.FourMtop2 = 4 * 172**2
    def update(self,ignored) :
        x = self.FourMtop2 / self.source[self.SumP4].M2()
        self.value = 2 * max(0,(1-x)/(1+x))
######################################
class Beta(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Alpha','CosThetaStarAvg'])
    def update(self, ignored) :
        self.value = self.source[self.CosThetaStarAvg] * math.sqrt(self.source[self.Alpha])
######################################
class __CosThetaStar__(wrappedChain.calculable) :
    def __init__(self, collection = None, topKey = 't') :
        self.fixes = collection
        self.stash(['BoostZ','P4'])
        self.TopKey = topKey
    def update(self,ignored) :
        p4 = self.source[self.P4] 
        boost = self.source[self.BoostZ]
        sign = ( 1 if self.TopKey=='t' else -1)
        self.value = sign * r.Math.VectorUtil.CosTheta( self.source[self.BoostZ](p4[self.TopKey]),  p4['quark'] ) 
######################################
class CosThetaStar(__CosThetaStar__) :
    def __init__(self, collection = None) : super(CosThetaStar,self).__init__(collection, 't')
class CosThetaStarBar(__CosThetaStar__) :
    def __init__(self, collection = None) : super(CosThetaStarBar,self).__init__(collection, 'tbar')
class CosThetaStarAvg(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['CosThetaStar','CosThetaStarBar'])
    def update(self,ignored) :
        star = self.source[self.CosThetaStar]
        bar =  self.source[self.CosThetaStarBar]
        sign = 1 if star>0 else -1
        self.value = sign - sign*math.sqrt((star-sign)*(bar-sign))
######################################
######################################
######################################

class genTopP4(wrappedChain.calculable) :
    def update(self,ignored) :
        indices = self.source['genTTbarIndices']
        p4 = self.source['genP4']
        qqbar = self.source['genQQbar']
        self.value = { 't':p4[indices['t']],
                       'tbar':p4[indices['tbar']],
                       'quark':p4[qqbar[0] if qqbar else self.source['genIndexStrongerParton']],
                       'lepton': p4[indices['lplus']] if indices['lplus'] else p4[indices['lminus']] if indices['lminus'] else None,
                       'p' : p4[indices['q'][0]] if indices['q'] else None,
                       'q' : p4[indices['q'][1]] if len(indices['q'])>1 else None
                       }
class genTopLeptonCharge(wrappedChain.calculable) :
    def update(self,ignored) : self.value = (1 if self.source['genTTbarIndices']['lplus'] else \
                                             -1 if self.source['genTTbarIndices']['lminus'] else 0)
        
class fitTopP4(wrappedChain.calculable) :
    def update(self,ignored) :
        reco = self.source["TopReconstruction"][0]
        t = reco['top']
        tbar = reco['tbar']
        q_z = 0.5*(t+tbar).z()
        self.value = {'t':t,
                      'tbar':tbar,
                      'quark': utils.LorentzV().SetPxPyPzE(0,0,q_z,abs(q_z)),
                      'lepton': reco['lep'],
                      'p' : reco['hadP'],
                      'q' : reco['hadQ']}
class fitTopLeptonCharge(wrappedChain.calculable) :
    def __init__(self, lepton) :
        self.lepton = lepton
    def update(self,ignored) :
        self.value = self.source["%sCharge%s"%self.lepton][self.source["%sSemileptonicTopIndex%s"%self.lepton]]


######################################
######################################
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
        self.value['q'] = ((self.value['wplusChild'] if not self.value['lplus'] else []) +
                            (self.value['wminusChild'] if not self.value['lminus'] else []))
        nus = filter(lambda i: abs(ids[i]) in [12,14], self.value['wplusChild']+self.value['wminusChild'])
        self.value['nu'] = nus[0] if nus else None
######################################
class genTopSemiLeptonicWithinAcceptance(wrappedChain.calculable) :
    def __init__(self, jetPtMin = None, jetAbsEtaMax = None, lepPtMin = None, lepAbsEtaMax = None) :
        for item in ['jetPtMin','jetAbsEtaMax','lepPtMin','lepAbsEtaMax'] : setattr(self,item,eval(item))
        self.moreName = 'jetPt>%0.1f; jet|eta|<%0.1f; lepPt>%0.1f; lep|eta|<%0.1f'%(jetPtMin,jetAbsEtaMax,lepPtMin,lepAbsEtaMax)
    def update(self,ignored) :
        self.value = False
        indices = self.source['genTTbarIndices']
        if not bool(indices['lplus'])^bool(indices['lminus']) : return
        iLep = max(indices['lplus'],indices['lminus'])
        genP4 = self.source["genP4"]
        if genP4[iLep].pt() < self.lepPtMin : return
        if abs(genP4[iLep].eta()) > self.lepAbsEtaMax : return
        for iJet in ( indices['q'] + [indices['b'],indices['bbar']] ) :
            if genP4[iJet].pt() < self.jetPtMin : return
            if abs(genP4[iJet].eta()) > self.jetAbsEtaMax : return
        self.value = True
######################################
class genTopSemiLeptonicAccepted(wrappedChain.calculable) :
    def __init__(self,jets) :
        self.indicesGenB = "%sIndicesGenB%s"%jets
        self.indicesGenWqq = "%sIndicesGenWqq%s"%jets
    def update(self,ignored) :
        self.value = len(self.source[self.indicesGenB]) is 2 is len(self.source[self.indicesGenWqq])
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
    def __init__(self, lepton, jets, SumP4) :
        self.stash(["SemileptonicTopIndex","P4","Charge"],lepton)
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
                "lepBound" : "phi" in leptonicFit.fitted,
                "hadB" : hadronicFit.J.fitted[0],
                "hadP" : hadronicFit.J.fitted[1],
                "hadQ" : hadronicFit.J.fitted[2],
                "hadW" : hadronicFit.J.fitted[1] + hadronicFit.J.fitted[2],
                "lepTopP4" : lepTopP4,
                "hadTopP4" : hadTopP4,
                "hadChi2" : hadronicFit.chi2(),
                "lepChi2" : leptonicFit.chi2(),
                "chi2" : hadronicFit.chi2() + leptonicFit.chi2(),
                "top"  : topP4,
                "tbar" : tbarP4,
                "sumP4": sumP4,
                "iBhad": iBhad,
                "iBlep": iBlep,
                "iQQ": iQQ,
                "probability" : self.source["TopComboProbability"][tuple(sorted([iBhad,iBlep])+sorted(iQQ))],
                "sigmaL" : 1.0 / math.sqrt(leptonicFit.nu.invSigmaL2),
                "sigmaS" : 1.0 / math.sqrt(leptonicFit.nu.invSigmaS2),
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
        topProbability = self.source["TopComboProbability"]
        maxTopProbability = self.source["TopComboMaxProbability"]
        self.hadronicFitCache = {}

        #bIndices = set(self.source[self.IndicesBtagged][:3]) #consider the top 3 tags as possible b candidates
        bIndices = set(self.source[self.IndicesBtagged][:4]) #consider the top 3 tags as possible b candidates
        allIndices = set(self.source[self.Indices])
        recos = []
        
        for iBLep in bIndices :
            for iBHad in (bIndices-set([iBLep])) :
                iOther = list(allIndices - set([iBLep,iBHad]))
                for iP in iOther :
                    for iQ in iOther[iOther.index(iP)+1:] :
                        pts = [self.source[self.CorrectedP4][i].pt() for i in [iBLep,iBHad,iP,iQ]]
                        #if max(pts[:2])<min(pts[2:]) : continue # probability that neither of the two leading in pT is a b-jet is only 7%
                        #if sum(pts[1:])<100 : continue # probability that the sumPt of hadronic side jets is less that 100 is only 4%
                        for zPlus in [0,1] :
                            hadKey = tuple(sorted([iBHad,iBLep]) + sorted([iP,iQ]))
                            if topProbability[hadKey] < 0.01 : continue
                            recos.append( self.reconstruct(iBHad,[iP,iQ],iBLep, zPlus))
        if not recos:
            bIndices = self.source[self.IndicesBtagged][:2]
            indices = filter(lambda i: i not in bIndices, self.source[self.Indices])[:2]
            recos = [ self.reconstruct( bIndices[not bLep], indices, bIndices[bLep], zPlus) for bLep in [0,1] for zPlus in [0,1] ]
        self.value = sorted( recos,  key = lambda x: x["chi2"]*(1-x["probability"])**2 )


######################################
class lepDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored):
        indices = self.source['genTTbarIndices']
        genLep = self.source['genP4'][max(indices['lplus'],indices['lminus'])]
        self.value = [r.Math.VectorUtil.DeltaR(genLep,reco['lep']) for reco in self.source['TopReconstruction']]
class nuDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored):
        genNu = self.source['genP4'][self.source['genTTbarIndices']['nu']]
        self.value = [r.Math.VectorUtil.DeltaR(genNu,reco['nu']) for reco in self.source['TopReconstruction']]
class bLepDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored):
        indices = self.source['genTTbarIndices']
        genLepB = self.source['genP4'][indices['b'] if indices['lplus'] else indices['bbar']]
        self.value = [r.Math.VectorUtil.DeltaR(genLepB,reco['lepB']) for reco in self.source['TopReconstruction']]
class bHadDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored):
        indices = self.source['genTTbarIndices']
        genHadB = self.source['genP4'][indices['bbar'] if indices['lplus'] else indices['b']]
        self.value = [r.Math.VectorUtil.DeltaR(genHadB,reco['hadB']) for reco in self.source['TopReconstruction']]
class pqDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored):
        PQ = tuple([self.source['genP4'][self.source['genTTbarIndices']['q'][i]] for i in range(2)])
        self.value= [min([ tuple(sorted([r.Math.VectorUtil.DeltaR(*t) for t in [(reco['hadP'],PQ[i]),(reco['hadQ'],PQ[j])]])) for i,j in [(0,1),(1,0)]])\
                     for reco in self.source['TopReconstruction']]
class qDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,ignored): self.value = [pq[1] for pq in self.source['pqDeltaRTopRecoGen']]
######################################
class fitTopRecoIndex(wrappedChain.calculable) :
    value = 0
    def update(self,ignored) : pass
class genTopRecoIndex(wrappedChain.calculable) :
    def __init__(self,rMax = 0.6, rMaxNu = 1.0) :
        for item in ['lep','bLep','bHad','q'] : setattr(self,"rMax"+item, rMax )
        self.rMaxnu = rMaxNu
        self.moreName = "deltaR[lep,b,b,q,q] <%0.1f; deltaRnum<%0.1f"%(rMax,rMaxNu)
    def update(self,ignored) :
        self.value = None
        if not self.source['genTopSemiLeptonicWithinAcceptance'] : return        
        indices = range(len(self.source['TopReconstruction']))
        iPass = list(reduce(lambda A,B: A.intersection(B),
                            [set(filter(lambda i: self.source['%sDeltaRTopRecoGen'%s][i]<getattr(self,"rMax%s"%s),indices)) for s in ['lep','nu','bLep','bHad','q']]))
        if len(iPass) > 1 : iPass.sort( key = lambda i: sum([self.source['%sDeltaRTopRecoGen'%s][i] for s in ['lep','nu','bLep','bHad','q']]))
        if len(iPass) : self.value = iPass[0]
######################################
class wTopAsym(wrappedChain.calculable) :
    def __init__(self, rPrime, totalEff = None, intrinsicR = 0) :
        self.fixes = ("",("N" if rPrime < 0 else "P") + "%02d"%(100*abs(rPrime)))
        self.rPrime = rPrime
        self.R = intrinsicR
        self.epsilon = 1.
        self.epsilon = 1. / max( self.weight(math.sqrt(2),2),
                                 self.weight(-math.sqrt(2),2))

        assert self.epsilon <= 1.
        assert totalEff < self.epsilon
        if 0 < totalEff : self.epsilon = totalEff
        
    def weight(self,beta,alpha) :
        base = 3 * (1+beta*beta) / (6+2.*alpha)
        return (base+beta*self.rPrime) / (base+beta*self.R)
    
    def update(self,ignored) :
        self.value = None if not self.source['genQQbar'] else self.weight(self.source['genTopBeta'],
                                                                          self.source['genTopAlpha'])
######################################
class TopComboLikelihood(wrappedChain.calculable) :
    def __init__(self, jets = None, tag = None) :
        self.stash(["Indices"],jets)
        self.B = ("%sTagProbabilityB_"+tag+"%s") % jets
        self.Q = ("%sTagProbabilityQ_"+tag+"%s") % jets
        self.N = ("%sTagProbabilityN_"+tag+"%s") % jets

    def update(self,ignored) :
        self.value = {}
        indices = self.source[self.Indices]
        B = self.source[self.B]
        Q = self.source[self.Q]
        N = self.source[self.N]

        for i in range(len(indices)) :
            for j in range(len(indices))[i+1:] :
                for m in range(len(indices)) :
                    if m in [i,j] : continue
                    for n in range(len(indices))[m+1:] :
                        if n in [i,j] : continue
                        other = filter(lambda k: k not in [i,j,m,n], indices)
                        self.value[tuple([indices[k] for k in [i,j,m,n]])] = reduce(operator.mul, [B[i],B[j],Q[m],Q[n]]+[N[k] for k in other] )
######################################
class TopComboProbability(wrappedChain.calculable) :
    def update(self,ignored) :
        likelihoods = self.source['TopComboLikelihood']
        sumL = sum(likelihoods.values())
        self.value = {}
        for key,val in likelihoods.iteritems() : self.value[key] = val / sumL
        return
######################################
class TopComboMaxProbability(wrappedChain.calculable) :
    def update(self,ignored) : self.value = max(self.source["TopComboProbability"].values())
######################################
class WComboLikelihood(wrappedChain.calculable) :
    def __init__(self, jets = None, tag = None) :
        self.stash(["Indices"],jets)
        self.Q = ("%sTagProbabilityQ_"+tag+"%s") % jets
        self.N = ("%sTagProbabilityN_"+tag+"%s") % jets

    def update(self,ignored) :
        self.value = {}
        indices = self.source[self.Indices]
        Q = self.source[self.Q]
        N = self.source[self.N]

        for i in range(len(indices)) :
            for j in range(len(indices))[i+1:] :
                other = filte(lambda k : k not in [i,j], indices)
                self.value[tuple([i,j])] = reduce(operator.mul, [Q[i],Q[j]]+[N[k] for k in other])
######################################
class TopRatherThanWProbability(wrappedChain.calculable) :
    def __init__(self, priorTop = 0.5) : self.priorTop = priorTop

    def update(self,ignored) :
        topL = self.source["TopComboLikelihood"]
        wL = self.source["WComboLikelihood"]
        
