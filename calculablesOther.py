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
class vertexID(wrappedChain.calculable) :
    def __init__(self, minNdof = 5.0, maxAbsZ = 24.0, maxD0 = 2.0 ) :
        for item in ["minNdof","maxAbsZ","maxD0"] : setattr(self,item,eval(item))
        self.moreName = "!fake; nd>=%.1f; |z|<=%.1f cm; d0<=%.1f cm" % (minNdof,maxAbsZ,maxD0)

    def id(self, isFake, ndof, pos) :
        return (not isFake) and \
               ndof >= self.minNdof and \
               abs(pos.Z()) <= self.maxAbsZ and \
               abs(pos.Rho()) <= self.maxD0

    def update(self,ignored) :
        self.value = map(self.id, self.source["vertexIsFake"],self.source["vertexNdof"],self.source["vertexPosition"])
#####################################
class vertexIndices(wrappedChain.calculable) :
    def __init__(self, sumPtMin = None) :
        self.sumPtMin = sumPtMin
        self.moreName = ""
        if self.sumPtMin!=None :
            self.moreName += "sumPt >=%.1f"%sumPtMin
        self.moreName += "; pass ID"
        
    def update(self,ignored) :
        sumPt = self.source["vertexSumPt"]
        id = self.source["vertexID"]
        self.value = []
        other = self.source["vertexIndicesOther"]
        for i in range(len(id)) :
            if self.sumPtMin!=None and sumPt.at(i) < self.sumPtMin : continue
            elif id[i] : self.value.append(i)
            else : other.append(i)
        self.value.sort( key = sumPt.__getitem__, reverse = True )
#####################################
class vertexIndicesOther(calculables.indicesOther) :
    def __init__(self) :
        super(vertexIndicesOther, self).__init__(("vertex",""))
        self.moreName = "pass sumPtMin; fail ID"
#####################################
class vertexSumPt(wrappedChain.calculable) :
    def __init__(self) :
        self.sumPts = r.std.vector('double')()
        for i in range(100) :
            self.sumPts.push_back(-100.0)
            
    def update(self, ignored) :
        self.value = self.sumPts
#####################################
class vertexSumP3(wrappedChain.calculable) :
    def __init__(self) :
        self.sumP3s = r.std.vector(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double')))()

    def update(self, ignored) :
        self.value = self.sumP3s
#####################################
class lowestUnPrescaledTrigger(wrappedChain.calculable) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.moreName = "lowest unprescaled of "+','.join(self.sortedListOfPaths).replace("HLT_","")
        
    def update(self, ignored) :
        self.value = None
        for path in self.sortedListOfPaths :
            if self.source["prescaled"][path]==1 :
                self.value = path
                break
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
class RelativeEta(wrappedChain.calculable) :
    def __init__(self, collection = None, MET = None) :
        self.fixes = collection
        self.stash(["Indices","P4","Charge"])
        self.MET = MET
        self.moreName = "%s%s; %s; sign(SumP4.z)*mu.eta*mu.charge"%(collection+(MET,))

    def update(self,ignored) :
        indices = self.source[self.Indices]
        if not len(indices):
            self.value=0
            return
        index = indices[0]
        met = self.source[self.MET]
        
        self.value = (1 if met.pz()>0 else -1) * self.source[self.P4][index].eta() * self.source[self.Charge][index]
#####################################
