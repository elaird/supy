from wrappedChain import *
import calculables,math,utils,fitKinematic,operator,itertools,numpy as np
######################################
class TopP4Calculable(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4'])
######################################
######################################
class DeltaPhiLNu(TopP4Calculable) :
    def update(self,_) : self.value = abs(r.Math.VectorUtil.DeltaPhi(self.source[self.P4]['lepton'],self.source[self.P4]['sumP4']))
######################################
class LeptonPt(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['lepton'].pt()
######################################
class NuPt(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['neutrino'].pt()
######################################
class MET(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['sumP4'].pt()
######################################
class RawHadWmass(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['rawW'].M()
######################################
class Key(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['key']
######################################
class Chi2(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['chi2']
######################################
class HadChi2(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['hadChi2']
######################################
class SumP4(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['t'] + self.source[self.P4]['tbar']
######################################
class SumPt(TopP4Calculable) :
    def update(self,_) : self.value = self.source[self.P4]['t'].pt() + self.source[self.P4]['tbar'].pt()
######################################
class Pt(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(['SumP4'])
    def update(self,_) : self.value = self.source[self.SumP4].pt()
######################################
class PtOverSumPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Pt','SumPt'])
    def update(self,_) : self.value = self.source[self.Pt] / self.source[self.SumPt]
######################################
class BoostZ(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SumP4'])
    def update(self,_) :
        self.value = r.Math.BoostZ( self.source[self.SumP4].BoostToCM().z())
######################################
class BoostZAlt(TopP4Calculable) :
    def update(self,_) :
        t,tbar = tuple(self.source[self.P4][i] for i in ['t','tbar'])
        pt = t.pt()
        ptbar = tbar.pt()
        self.value = r.Math.BoostZ( - (t.z()/pt + tbar.z()/ptbar) / (t.E()/pt + tbar.E()/ptbar) )
######################################
class DeltaPhi(TopP4Calculable) :
    def update(self,_) :
        self.value = r.Math.VectorUtil.DeltaPhi(self.source[self.P4]['t'], self.source[self.P4]['tbar'])
######################################
class WqqDeltaR(TopP4Calculable) :
    def update(self,_) :
        self.value = r.Math.VectorUtil.DeltaR(self.source[self.P4]['p'],self.source[self.P4]['q'])
######################################
class DeltaAbsYttbar(TopP4Calculable) :
    def update(self,_) :
        self.value = abs(self.source[self.P4]['t'].Rapidity()) - abs(self.source[self.P4]['tbar'].Rapidity())
######################################
class DeltaYttbar(TopP4Calculable) :
    def update(self,_) :
        self.value = self.source[self.P4]['t'].Rapidity() - self.source[self.P4]['tbar'].Rapidity()
######################################
class DirectedDeltaYttbar(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['DeltaYttbar','SignQuarkZ'])
    def update(self,_) :
        self.value = self.source[self.SignQuarkZ] * self.source[self.DeltaYttbar]
######################################
class DirectedDeltaYLHadt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SignQuarkZ','P4','LeptonCharge'])
    def update(self,_) :
        p4 = self.source[self.P4]
        qLep = self.source[self.LeptonCharge]
        self.value = self.source[self.SignQuarkZ] * qLep * (p4['lepton'].Rapidity() - p4['t' if qLep<0 else 'tbar'].Rapidity())
######################################
class SignedLeptonRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4',"LeptonCharge","SignQuarkZ"])
    def update(self,_) :
        self.value = (self.source[self.SignQuarkZ] *
                      self.source[self.LeptonCharge] *
                      self.source[self.P4]['lepton'].Rapidity() )
#####################################
class RelativeLeptonRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["SumP4","P4","LeptonCharge"])
        self.moreName = "sign(y_sum) * q_lep * (y_lep-y_sum); %s%s; %s"%(collection+(SumP4,))

    def update(self,_) :
        q_lep = self.source[self.LeptonCharge]
        y_lep = self.source[self.P4]['lepton'].Rapidity()
        y_sum = self.source[self.SumP4].Rapidity()
        
        self.value = (1 if y_sum>0 else -1) * q_lep * (y_lep-y_sum)
#####################################
class DirectedLTopRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4','SignQuarkZ','LeptonCharge'])
    def update(self,_) :
        lepQ = self.source[self.LeptonCharge]
        top = self.source[self.P4]['t' if lepQ>0 else 'tbar']
        self.value = self.source[self.SignQuarkZ] * top.Rapidity()
######################################
class DirectedHTopRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4','SignQuarkZ','LeptonCharge'])
    def update(self,_) :
        lepQ = self.source[self.LeptonCharge]
        top = self.source[self.P4]['t' if lepQ<0 else 'tbar']
        self.value = self.source[self.SignQuarkZ] * top.Rapidity()
######################################
class SignQuarkZ(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['P4'])
    def update(self,_) :
        self.value = 1 if self.source[self.P4]['quark'].z() > 0 else -1
#####################################
class Alpha(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['SumP4'])
        self.FourMtop2 = 4 * 172**2
    def update(self,_) :
        x = self.FourMtop2 / self.source[self.SumP4].M2()
        self.value = 2 * max(0,(1-x)/(1+x))
######################################
class Beta(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Alpha','CosThetaStarAvg'])
    def update(self, _) :
        self.value = self.source[self.CosThetaStarAvg] * math.sqrt(self.source[self.Alpha])
######################################
class __CosThetaStar__(wrappedChain.calculable) :
    def __init__(self, collection = None, topKey = 't', boostz = "BoostZ") :
        self.fixes = collection
        self.stash(['P4'])
        self.boostz = ("%s"+boostz+"%s")%collection
        self.TopKey = topKey
    def update(self,_) :
        p4 = self.source[self.P4] 
        sign = ( 1 if self.TopKey=='t' else -1)
        self.value = sign * r.Math.VectorUtil.CosTheta( self.source[self.boostz](p4[self.TopKey]),  p4['quark'] ) 
######################################
class CosThetaStarAlt(__CosThetaStar__) :
    def __init__(self, collection = None) : super(CosThetaStarAlt,self).__init__(collection,'t','BoostZAlt')
class CosThetaStar(__CosThetaStar__) :
    def __init__(self, collection = None) : super(CosThetaStar,self).__init__(collection, 't')
class CosThetaStarBar(__CosThetaStar__) :
    def __init__(self, collection = None) : super(CosThetaStarBar,self).__init__(collection, 'tbar')
class CosThetaStarAvg(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['CosThetaStar','CosThetaStarBar'])
    def update(self,_) :
        star = self.source[self.CosThetaStar]
        bar =  self.source[self.CosThetaStarBar]
        sign = 1 if star>0 else -1
        self.value = sign - sign*math.sqrt((star-sign)*(bar-sign))
class CosThetaStarAngle(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['CosThetaStar','CosThetaStarBar'])
    def update(self,_) :
        self.value = math.atan2(abs(self.source[self.CosThetaStar]),abs(self.source[self.CosThetaStarBar])) # on [0:pi/2]
######################################
######################################
class CosHelicityThetaL(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['BoostZAlt','P4','LeptonCharge'])
    def update(self,_) :
        lepQ = self.source[self.LeptonCharge]
        p4 = self.source[self.P4]
        boost1 = self.source[self.BoostZAlt]
        top = boost1(p4['t' if lepQ>0 else 'tbar'])
        beta = top.BoostToCM()
        boost2 = r.Math.Boost(beta.x(), beta.y(), beta.z())
        self.value = r.Math.VectorUtil.CosTheta( top, boost2(boost1(p4['lepton'])))
######################################
class CosHelicityThetaQ(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['BoostZAlt','P4','LeptonCharge'])
    def update(self,_) :
        lepQ = self.source[self.LeptonCharge]
        p4 = self.source[self.P4]
        boost1 = self.source[self.BoostZAlt]
        top = boost1(p4['t' if lepQ<0 else 'tbar'])
        beta = top.BoostToCM()
        boost2 = r.Math.Boost(beta.x(), beta.y(), beta.z())
        self.value = r.Math.VectorUtil.CosTheta( top, boost2(boost1(p4['q'])))
######################################
######################################

class genTopP4(wrappedChain.calculable) :
    def update(self,_) :
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
    def update(self,_) : self.value = (1 if self.source['genTTbarIndices']['lplus'] else \
                                             -1 if self.source['genTTbarIndices']['lminus'] else 0)
        
class fitTopP4(wrappedChain.calculable) :
    def update(self,_) :
        reco = self.source["TopReconstruction"][0]
        t = reco['top']
        tbar = reco['tbar']
        q_z = 0.5*(t+tbar).z()
        self.value = {'t':t,
                      'tbar':tbar,
                      'quark': utils.LorentzV().SetPxPyPzE(0,0,q_z,abs(q_z)),
                      'lepton': reco['lep'],
                      'neutrino' : reco['nu'],
                      'p' : reco['hadP'],
                      'q' : reco['hadQ'],
                      'rawW': reco['hadWraw'],
                      'sumP4':reco['sumP4'],
                      'key': reco['key'],
                      'chi2': reco['chi2'],
                      'hadChi2': reco['hadChi2'],
                      }
class fitTopLeptonCharge(wrappedChain.calculable) :
    def __init__(self, lepton) :
        self.lepton = lepton
    def update(self,_) :
        self.value = self.source["%sCharge%s"%self.lepton][self.source["%sSemileptonicTopIndex%s"%self.lepton]]


######################################
######################################
######################################



class genTopTTbar(wrappedChain.calculable) :
    def update(self,_) :
        self.value = tuple(list(self.source['genPdgId']).index(i) for i in [6,-6]) if \
                     (not self.source['isRealData']) and \
                     all([id in self.source['genPdgId'] for id in [-6,6]]) else ()
######################################
class genTTbarIndices(wrappedChain.calculable) :
    def update(self,_) :
        ids = [i for i in self.source['genPdgId']]
        mom = self.source['genMotherIndex']
        self.value = dict([(name, ids.index(i)) for name,i in [('t',6),
                                                               ('tbar',-6),
                                                               ('wplus',24),
                                                               ('wminus',-24)
                                                               ]])
        self.value.update(dict([ (w+"Child",filter(lambda i: mom[i]==self.value[w],range(len(ids)))) for w in ['wplus','wminus','t','tbar']]))
        self.value['b'] = next(i for i in self.value['tChild'] if abs(ids[i])!=24)
        self.value['bbar'] = next(i for i in self.value['tbarChild'] if abs(ids[i])!=24)
        self.value['lplus'] = next((i for i in self.value['wplusChild'] if ids[i] in [-11,-13]),None)
        self.value['lminus'] = next((i for i in self.value['wminusChild'] if ids[i] in [11,13]),None)
        self.value['q'] = ((self.value['wplusChild'] if not self.value['lplus'] else []) +
                            (self.value['wminusChild'] if not self.value['lminus'] else []))
        self.value['nu'] = next((i for i in (self.value['wplusChild']+self.value['wminusChild']) if abs(ids[i]) in [12,14]),None)
######################################
class genTopSemiLeptonicWithinAcceptance(wrappedChain.calculable) :
    def __init__(self, jetPtMin = None, jetAbsEtaMax = None, lepPtMin = None, lepAbsEtaMax = None) :
        for item in ['jetPtMin','jetAbsEtaMax','lepPtMin','lepAbsEtaMax'] : setattr(self,item,eval(item))
        self.moreName = 'jetPt>%0.1f; jet|eta|<%0.1f; lepPt>%0.1f; lep|eta|<%0.1f'%(jetPtMin,jetAbsEtaMax,lepPtMin,lepAbsEtaMax)
    def update(self,_) :
        self.value = False
        if not self.source["genTopTTbar"] : return
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
    def update(self,_) :
        self.value = len(self.source[self.indicesGenB]) is 2 is len(self.source[self.indicesGenWqq])
######################################
class mixedSumP4(wrappedChain.calculable) :
    def __init__(self, transverse = None, longitudinal = None) :
        self.trans = transverse
        self.longi = longitudinal
        self.moreName = "transvers: %s ; longitudinal: %s" % (transverse,longitudinal)
        self.value = utils.LorentzV()
    def update(self,_) :
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

    def update(self,_) :
        indices = self.source[self.Indices]
        nonIso = self.source[self.IndicesNonIso]
        self.value = indices[0] if indices else nonIso[0] if nonIso else None
#####################################
class TopReconstruction(wrappedChain.calculable) :
    def __init__(self, lepton, jets, SumP4) :
        self.stash(["SemileptonicTopIndex","P4","Charge"],lepton)
        self.stash(["CorrectedP4","IndicesBtagged","Indices","Resolution","CovariantResolution2","ComboPQBDeltaRawMassWTop"],jets)
        self.SumP4 = SumP4
        theta = math.pi/6
        self.ellipseR = np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta), math.cos(theta)]])

    def update(self,_) :
        epsilon = 1e-7
        p4 = self.source[self.CorrectedP4]
        resolution = self.source[self.Resolution]
        covRes2 = self.source[self.CovariantResolution2]
        comboDRawMass = self.source[self.ComboPQBDeltaRawMassWTop]
        topP = self.source["TopComboQQBBProbability"]
        maxP = self.source["TopComboQQBBMaxProbability"]
        lepQ = self.source[self.Charge][self.source[self.SemileptonicTopIndex]]
        lepP4 = self.source[self.P4][self.source[self.SemileptonicTopIndex]]
        
        indices = self.source[self.Indices]
        bIndices = self.source[self.IndicesBtagged][:5] #consider only the first few b-tagged jets as possible b-candidates
        recos = []        
        for iPQH in itertools.permutations(indices,3) :
            if iPQH[0]>iPQH[1] : continue
            if iPQH[2] not in bIndices : continue
            if np.dot(*(2*[self.ellipseR.dot(comboDRawMass[iPQH]) / [35,70]])) > 1 : continue # elliptical window on raw masses

            hadFit = fitKinematic.leastsqHadronicTop(*zip(*((p4[i], resolution[i]) for i in iPQH)))
            sumP4 = self.source[self.SumP4] - hadFit.rawT + hadFit.fitT
            nuErr = self.source["metCovariancePF"] - sum( covRes2[i] for i in iPQH )
            nuXY = -np.array([sumP4.x(), sumP4.y()])

            for iL in bIndices :
                if iL in iPQH : continue
                iPQHL = iPQH+(iL,)
                iQQBB = iPQHL[:2]+tuple(sorted(iPQHL[2:]))
                for zPlus in [0,1] :
                    lepFit = fitKinematic.leastsqLeptonicTop( p4[iL], resolution[iL], lepP4, nuXY, nuErr-covRes2[iL], zPlus = zPlus )
                    recos.append( {"nu"   : lepFit.fitNu,       "hadP" : hadFit.fitJ[0],
                                   "lep"  : lepFit.mu,          "hadQ" : hadFit.fitJ[1],
                                   "lepB" : lepFit.fitB,        "hadB" : hadFit.fitJ[2],
                                   "lepW" : lepFit.fitW,        "hadW" : hadFit.fitW,   
                                   "lepTopP4" : lepFit.fitT,    "hadTopP4": hadFit.fitT,
                                   "lepChi2" : lepFit.chi2,     "hadChi2" : hadFit.chi2,
                                   "chi2" : hadFit.chi2 + lepFit.chi2,
                                   "probability" : max(epsilon,topP[iQQBB]),
                                   "key" : hadFit.chi2 + lepFit.chi2 - 2*math.log(max(epsilon,topP[iQQBB])),

                                   "top"  : lepFit.fitT if lepQ > 0 else hadFit.fitT,
                                   "tbar" : hadFit.fitT if lepQ > 0 else lepFit.fitT,

                                   "iPQHL": iPQHL,
                                   "lepCharge": lepQ,           "hadTraw" : hadFit.rawT,
                                   "lepBound" : lepFit.bound,   "hadWraw" : hadFit.rawW,
                                   "sumP4": sumP4,
                                   "residuals" : dict( zip(["lep"+i for i in "BSLT"],  lepFit.residualsBSLT ) +
                                                       zip(["had"+i for i in "PQBWT"], hadFit.residualsPQBWT ) )
                                   })
                if 0.01 > r.Math.VectorUtil.DeltaR(recos[-2]['nu'],recos[-1]['nu']) :
                    recos.pop(max(-1,-2, key = lambda i: recos[i]['lepChi2']))
                    
        self.value = sorted( recos,  key = lambda x: x["key"] )
        
######################################
class lepDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_):
        indices = self.source['genTTbarIndices']
        genLep = self.source['genP4'][max(indices['lplus'],indices['lminus'])]
        self.value = [r.Math.VectorUtil.DeltaR(genLep,reco['lep']) for reco in self.source['TopReconstruction']]
class nuDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_):
        genNu = self.source['genP4'][self.source['genTTbarIndices']['nu']]
        self.value = [r.Math.VectorUtil.DeltaR(genNu,reco['nu']) for reco in self.source['TopReconstruction']]
class bLepDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_):
        indices = self.source['genTTbarIndices']
        genLepB = self.source['genP4'][indices['b'] if indices['lplus'] else indices['bbar']]
        self.value = [r.Math.VectorUtil.DeltaR(genLepB,reco['lepB']) for reco in self.source['TopReconstruction']]
class bHadDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_):
        indices = self.source['genTTbarIndices']
        genHadB = self.source['genP4'][indices['bbar'] if indices['lplus'] else indices['b']]
        self.value = [r.Math.VectorUtil.DeltaR(genHadB,reco['hadB']) for reco in self.source['TopReconstruction']]
class pqDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_):
        PQ = tuple([self.source['genP4'][self.source['genTTbarIndices']['q'][i]] for i in range(2)])
        self.value= [min([ tuple(sorted([r.Math.VectorUtil.DeltaR(*t) for t in [(reco['hadP'],PQ[i]),(reco['hadQ'],PQ[j])]])) for i,j in [(0,1),(1,0)]])\
                     for reco in self.source['TopReconstruction']]
class qDeltaRTopRecoGen(wrappedChain.calculable) :
    def update(self,_): self.value = [pq[1] for pq in self.source['pqDeltaRTopRecoGen']]
######################################
class fitTopRecoIndex(wrappedChain.calculable) :
    value = 0
    def update(self,_) : pass
class genTopRecoIndex(wrappedChain.calculable) :
    def __init__(self,rMax = 0.6, rMaxNu = 10.0) :
        for item in ['lep','bLep','bHad','q'] : setattr(self,"rMax"+item, rMax )
        self.rMaxnu = rMaxNu
        self.moreName = "deltaR[lep,b,b,q,q] <%0.1f; deltaRnum<%0.1f"%(rMax,rMaxNu)
    def update(self,_) :
        self.value = None
        if self.source['isRealData'] : return
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
    
    def update(self,_) :
        self.value = None if not self.source['genQQbar'] else self.weight(self.source['genTopBeta'],
                                                                          self.source['genTopAlpha'])
######################################
class TopComboQQBBLikelihood(wrappedChain.calculable) :
    def __init__(self, jets = None, tag = None) :
        self.tagProbabilityGivenBQN = ('%s'+tag+'ProbabilityGivenBQN%s')%jets
        self.stash(["Indices"],jets)

    def update(self,_) :
        indices = self.source[self.Indices]
        B,Q,N = zip(*self.source[self.tagProbabilityGivenBQN])
        self.value = {}
        for iPQHL in itertools.permutations(indices,4) :
            if iPQHL[0]>iPQHL[1] : continue
            if iPQHL[2]>iPQHL[3] : continue
            self.value[iPQHL] = reduce(operator.mul, ([Q[i] for i in iPQHL[:2]] +
                                                      [B[i] for i in iPQHL[2:]]  +
                                                      [N[k] for k in indices if k not in iPQHL]) )
######################################
class TopComboQQBBProbability(wrappedChain.calculable) :
    def update(self,_) :
        likelihoods = self.source['TopComboQQBBLikelihood']
        sumL = max(1e-20,sum(likelihoods.values()))
        self.value = dict([(key,val/sumL) for key,val in likelihoods.iteritems()])
######################################
class TopComboQQBBMaxProbability(wrappedChain.calculable) :
    def update(self,_) : self.value = max(self.source["TopComboQQBBProbability"].values())
######################################
class OtherJetsLikelihood(wrappedChain.calculable) :
    def __init__(self, jets = None, tag = None) :
        self.tagProbabilityGivenBQN = ('%s'+tag+'ProbabilityGivenBQN%s')%jets
        self.stash(["Indices"],jets)

    def update(self,_) :
        indices = self.source[self.Indices]
        B,Q,N = zip(*self.source[self.tagProbabilityGivenBQN])
        self.value = reduce(operator.mul, [N[k] for k in indices])
######################################
class TopRatherThanWProbability(wrappedChain.calculable) :
    def __init__(self, priorTop = 0.05) :
        self.priorTop = priorTop
        self.invPriorTopMinusOne =  ( 1.0 / priorTop  - 1)
        self.moreName = "priorTop = %0.3f"%priorTop
        
    def update(self,_) :
        topLikes = self.source["TopComboQQBBLikelihood"]
        if not topLikes : self.value = self.priorTop; return
        topL = sum(topLikes.values()) / float(len(topLikes))
        wL = self.source["OtherJetsLikelihood"]
        denom = (topL + wL * self.invPriorTopMinusOne)
        self.value = (topL / denom) if denom else self.priorTop
######################################
