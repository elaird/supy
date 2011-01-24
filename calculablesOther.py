from wrappedChain import *
import calculables,math
#####################################
class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry
#####################################
class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry
#####################################
class chain_access(wrappedChain.calculable) :
    def name(self) : return "chain"
    def update(self,ignored) : self.value = self.source._wrappedChain__chain
#####################################
class crock(wrappedChain.calculable) :
    def update(self,localEntry) : self.value = {}
#####################################
class ecalDeadTowerIsBarrel(wrappedChain.calculable) :
    def update(self,ignored) : self.value = map( self.isBarrel, self.source["ecalDeadTowerTrigPrimP4"] )
    def isBarrel(self, p4) : return abs(p4.eta()) < 1.48
#####################################
class lowestUnPrescaledTrigger(wrappedChain.calculable) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.cached = dict()
        self.moreName = "lowest unprescaled of "+','.join(self.sortedListOfPaths).replace("HLT_","")
        
    def update(self, ignored) :
        key = (self.source["run"],self.source["lumiSection"])
        if key not in self.cached :
            self.cached[key] = None
            for path in self.sortedListOfPaths :
                if self.source["prescaled"][path]==1 :
                    self.cached[key] = path
                    break
        self.value = self.cached[key]
##############################
class Mt(wrappedChain.calculable) :
    def name(self) :
        return "%sMt%s%s"%(self.fixes[0], self.fixes[1], self.met)
    
    def __init__(self, collection = None, met = None, byHand = True ) :
        self.met = met
        self.fixes = collection
        self.stash(["Indices","P4"])
        self.byHand = byHand
        self.moreName = "%s%s, %s, byHand=%d"%(collection[0], collection[1], met, byHand)

    def update(self, ignored) :
        if not len(self.Indices) :
            self.value= -1.0
            return
        lep = self.source[self.P4][self.source[self.Indices][0]]
        met = self.source[self.met]

        if self.byHand :
            self.value = math.sqrt( 2.0*lep.pt()*met.pt()*(1.0 - math.cos(r.Math.VectorUtil.DeltaPhi(lep, met))) )
        else :
            self.value = (lep+met).Mt()
#####################################
class SemileptonicTopIndex(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices"])
        self.moreName = "Just indices[0] for now."

    def update(self,ignored) :
        indices = self.source[self.Indices]
        self.value = indices[0] if indices else None
#####################################
class RelativeRapidity(wrappedChain.calculable) :
    def __init__(self, collection = None, MissingP4 = None) :
        self.fixes = collection
        self.stash(["SemileptonicTopIndex","P4","Charge"])
        self.MissingP4 = MissingP4
        self.moreName = "- sign(y_miss) * q_mu * (y_miss+y_mu); %s%s; %s"%(collection+(MissingP4,))

    def update(self,ignored) :
        index = self.source[self.SemileptonicTopIndex]
        if index is None: self.value=None; return

        y_miss = self.source[self.MissingP4].rapidity()
        y_mu = self.source[self.P4][index].rapidity()
        q_mu = self.source[self.Charge][index]
        
        self.value = (-1 if y_miss>0 else 1) * q_mu * (y_miss + y_mu)
#####################################
class NuetrinoPz(wrappedChain.calculable) :
    def __init__(self, collection = None, MissingP4 = None) :
        self.fixes = collection
        self.stash(["SemileptonicTopIndex","P4"])
        self.MissingP4 = MissingP4
        self.moreName = "neutrinoPz; given SemileptonicTopIndex in %s%s; %s"%(collection+(MissingP4,))
        self.Wmass2 = 80**2 # GeV
        
    def update(self,ignored) :
        self.value = None
        
        index = self.source[self.SemileptonicTopIndex]
        if index is None: return

        mu4 = self.source[self.P4][index]
        nu4 = self.source[self.MissingP4]
        W4 = mu4 + nu4

        muZ = mu4.z()
        muE = mu4.E()
        muT2 = mu4.Perp2()
        nuT2 = nu4.Perp2()
        WT2 = W4.Perp2()

        P = self.Wmass2 + WT2 - muT2 - nuT2

        discriminant = muZ**2 + 4*muT2*(1-(4*muE*muE*nuT2)/(P**2))
        if discriminant < 0: return
        
        sqrtD = math.sqrt(discriminant)
        factor = 0.5*P/muT2
        self.value = (factor * (muZ-sqrtD),
                      factor * (muZ+sqrtD))

