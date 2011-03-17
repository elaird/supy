from wrappedChain import *
import calculables,utils,math

######################################
class genTopNuP4(wrappedChain.calculable) :
    def __init__(self) :
        self.empty = r.std.vector(type(utils.LorentzV())).value_type()
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
class genTopTTbarSumP4(wrappedChain.calculable) :
    def update(self,ignored) :
        genP4 = self.source['genP4']
        ttbar = self.source['genTopTTbar']
        self.value = genP4[ttbar[0]] + genP4[ttbar[1]]
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
    def update(self,ignored) : self.value = 0.5 * (self.source['genTopCosThetaStar']+self.source['genTopCosThetaStarBar'])
######################################
class genTTbar(wrappedChain.calculable) :
    def update(self,ignored) :
        self.value = {}

        indexT = ids.index(6)
        indexTbar = ids.index(-6)
        indexWplus = ids.index(24)
        indexWminus = ids.index(-24)
        indexB = ids.index(5)
        indexBbar = ids.index(-5)
######################################
######################################
class mixedSumP4(wrappedChain.calculable) :
    def __init__(self, transverse = None, longitudinal = None) :
        self.trans = transverse
        self.longi = longitudinal
        self.moreName = "transvers: %s ; longitudinal: %s" % (transverse,longitudinal)
        self.value = r.std.vector(type(utils.LorentzV())).value_type()
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
class NeutrinoPz(wrappedChain.calculable) :
    def __init__(self, collection = None, SumP4 = None) :
        self.fixes = collection
        self.stash(["SemileptonicTopIndex","P4"])
        self.SumP4 = SumP4
        self.moreName = "neutrinoPz; given SemileptonicTopIndex in %s%s; %s"%(collection+(SumP4,))
        self.Wmass2 = 80.4**2 # GeV
        
    def update(self,ignored) :
        self.value = None
        
        index = self.source[self.SemileptonicTopIndex]
        if index is None: return

        lep4 = self.source[self.P4][index]
        negNu4 = self.source[self.SumP4]
        W4 = lep4 - negNu4

        lepZ = lep4.z()
        lepE = lep4.E()
        lepT2 = lep4.Perp2()
        nuT2 = negNu4.Perp2()
        WT2 = W4.Perp2()

        P = self.Wmass2 + WT2 - lepT2 - nuT2

        determinant = lepZ**2 + 4*lepT2*(1-(4*lepE*lepE*nuT2)/(P**2))
        if determinant < 0:
            #return           # option A
            determinant = 0   # option B
        
        sqrtD = math.sqrt(determinant)
        factor = 0.5*P/lepT2
        self.value = (factor * (lepZ-sqrtD),
                      factor * (lepZ+sqrtD))
#####################################
class NeutrinoP4Solution(wrappedChain.calculable) :
    def __init__(self, collection, SumP4, solutionPz) :
        self.fixes = collection
        self.stash(["NeutrinoPz"])
        self.SumP4 = SumP4
        self.solutionPz = 1 if solutionPz>0 else 0

    def update(self,ignored) :
        self.value = None
        pzMinusPlus = self.source[self.NeutrinoPz]
        if not pzMinusPlus : return
        sum = self.source[self.SumP4]
        px,py,pz = -sum.px(),-sum.py(),pzMinusPlus[self.solutionPz]
        self.value = type(self.source[self.SumP4])().SetPxPyPzE(px,py,pz,math.sqrt(px**2+py**2+pz**2))
class NeutrinoP4P(NeutrinoP4Solution) :
    def __init__(self, collection = None, SumP4 = None) : super(NeutrinoP4P,self).__init__(collection,SumP4,+1)
class NeutrinoP4M(NeutrinoP4Solution) :
    def __init__(self, collection = None, SumP4 = None) : super(NeutrinoP4M,self).__init__(collection,SumP4,-1)
######################################
class TopReconstruction(wrappedChain.calculable) :
    def __init__(self, collection, jets) :
        self.massTop = 172 #GeV
        self.fixes = collection
        self.stash(["SemileptonicTopIndex","P4","NeutrinoP4P","NeutrinoP4M"])
        self.stash(["CorrectedP4","IndicesBtagged","Indices"],jets)

    def update(self,ignored) :
        indices = self.source[self.Indices]
        bIndices = self.source[self.IndicesBtagged][:2]
        jetP4s = self.source[self.CorrectedP4]
        lepP4 = self.source[self.P4][self.source[self.SemileptonicTopIndex]]
        nuP4s = [self.source[self.NeutrinoP4P],self.source[self.NeutrinoP4M]]
        self.value = sorted([ { "nuP4" : nuP4,
                                "lepTopBIndex" : iJet,
                                "lepTopP4" : nuP4+lepP4+jetP4s[iJet],
                                "hadTopP4" : sum([jetP4s[i] for i in (set(indices)-set([iJet]))], r.std.vector(type(utils.LorentzV())).value_type()),
                                "hadTopBIndex" : filter(lambda i: i!=iJet, bIndices)[0] } for nuP4 in nuP4s for iJet in bIndices],
                            key = lambda x: abs(self.massTop - x["lepTopP4"].M()) )
#####################################
class NeutrinoP4(wrappedChain.calculable) :
    def __init__(self, collection) :
        self.fixes = collection
        self.stash(["TopReconstruction"])
    def update(self,ignored) :
        self.value = self.source[self.TopReconstruction][0]["nuP4"]
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
