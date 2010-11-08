from wrappedChain import *
import calculables

class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry

class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry

class chain_access(wrappedChain.calculable) :
    def name(self) : return "chain"
    def update(self,ignored) : self.value = self.source._wrappedChain__chain

class crock(wrappedChain.calculable) :
    def update(self,localEntry) : self.value = {}
##############################
class deadEcalRegionsFromFile(wrappedChain.calculable) :
    def __init__(self) :
        self.trigPrims = r.std.vector(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double')))()
        self.nBadXtals = r.std.vector("int")()
        inFile=open("deadRegionList.txt")
        for line in inFile :
            if line[0]=="#" : continue
            fieldList = line.split()
            eta  = float(fieldList[0])
            phi  = float(fieldList[1])
            nBad = int(fieldList[4])
            self.trigPrims.push_back(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,eta,phi,0.0))
            self.nBadXtals.push_back(nBad)
        inFile.close()

    def update(self,ignored) :
        self.value={}
        self.value["trigPrims"] = self.trigPrims
        self.value["nBadXtals"] = self.nBadXtals
##############################
class deadHcalChannelsFromFile(wrappedChain.calculable) :
    def __init__(self) :
        self.p4s = r.std.vector(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double')))()
        self.status = r.std.vector("int")()
        inFile = open("hcalDeadChannels.txt")
        for line in inFile :
            if line[0]=="#" : continue
            fieldList = line.split()
            if not len(fieldList) : continue
            eta    = float(fieldList[0])
            phi    = float(fieldList[1])
            status = int(fieldList[2])
            self.p4s.push_back(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0, eta, phi, 0.0))
            self.status.push_back(status)
        inFile.close()

    def update(self,ignored) :
        self.value={}
        self.value["p4"] = self.p4s
        self.value["status"] = self.status
##############################
class ecalDeadTowerTrigPrimP4(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["trigPrims"]
        
class ecalDeadTowerNBadXtals(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["nBadXtals"]

class ecalDeadTowerIsBarrel(wrappedChain.calculable) :
    def update(self,ignored) : self.value = map( self.isBarrel, self.source["ecalDeadTowerTrigPrimP4"] )
    def isBarrel(self, p4) : return abs(p4.eta()) < 1.48
##############################                        
class hcalDeadChannelP4(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["p4"]

class hcalDeadChannelStatus(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["status"]
##############################                        
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
        
class vertexIndicesOther(calculables.indicesOther) :
    def __init__(self) :
        super(vertexIndicesOther, self).__init__(("vertex",""))
        self.moreName = "pass sumPtMin; fail ID"

class vertexSumPt(wrappedChain.calculable) :
    def __init__(self) :
        self.sumPts = r.std.vector('double')()
        for i in range(100) :
            self.sumPts.push_back(-100.0)
            
    def update(self, ignored) :
        self.value = self.sumPts

class vertexSumP3(wrappedChain.calculable) :
    def __init__(self) :
        self.sumP3s = r.std.vector(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double')))()

    def update(self, ignored) :
        self.value = self.sumP3s
