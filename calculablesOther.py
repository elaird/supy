from wrappedChain import *

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

class ecalDeadTowerTrigPrimP4(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["trigPrims"]
        
class ecalDeadTowerNBadXtals(wrappedChain.calculable) :
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["nBadXtals"]
