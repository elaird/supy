from wrappedChain import *
import calculables,math

class mixedSumP4(wrappedChain.calculable) :
    def __init__(self, transverse = None, longitudinal = None) :
        self.trans = transverse
        self.longi = longitudinal
        self.moreName = "transvers: %s ; longitudinal: %s" % (transverse,longitudinal)
        self.value = r.std.vector('LorentzV').value_type()
    def update(self,ignored) :
        trans = self.source[self.trans]
        longi = self.source[self.longi]
        f = trans.pt() / longi.pt()
        self.value.SetPxPyPzE(trans.px(),trans.py(), f*longi.pz(), f*longi.E()) 
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
#####################################
class NeutrinoP4(wrappedChain.calculable) :
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
class NeutrinoP4P(NeutrinoP4) :
    def __init__(self, collection = None, SumP4 = None) : super(NeutrinoP4P,self).__init__(collection,SumP4,+1)
class NeutrinoP4M(NeutrinoP4) :
    def __init__(self, collection = None, SumP4 = None) : super(NeutrinoP4M,self).__init__(collection,SumP4,-1)
######################################
class SumP4NuX(wrappedChain.calculable) :
    def name(self) : return self.SumP4 + "Nu" + self.solutionPz
    def __init__(self, collection, SumP4, solutionPz) :
        self.NuX = ("%sNeutrinoP4"+solutionPz+"%s")%collection
        self.SumP4 = SumP4
        self.solutionPz = solutionPz
    def update(self,ignored) :
        nu = self.source[self.NuX]
        if nu : self.value = nu + self.source[self.SumP4]
        else : self.value = self.source[self.SumP4]
class SumP4NuP(SumP4NuX) :
    def __init__(self, collection = None, SumP4 = None) : super(SumP4NuP,self).__init__(collection,SumP4,"P")
class SumP4NuM(SumP4NuX) :
    def __init__(self, collection = None, SumP4 = None) : super(SumP4NuM,self).__init__(collection,SumP4,"M")
######################################
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
