from wrappedChain import *
import calculables,math

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
