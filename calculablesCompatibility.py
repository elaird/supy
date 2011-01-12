from wrappedChain import *
import calculables
##############################
class deadEcalRegionsFromFile(wrappedChain.calculable) :
    def __init__(self) :
        self.trigPrims = r.std.vector(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double')))()
        self.nBadXtals = r.std.vector("int")()
        self.maxStatus = r.std.vector("int")()
        inFile=open("deadRegionList.txt")
        for line in inFile :
            if line[0]=="#" : continue
            fieldList = line.split()
            eta  = float(fieldList[0])
            phi  = float(fieldList[1])
            nBad = int(fieldList[4])
            self.trigPrims.push_back(r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,eta,phi,0.0))
            self.nBadXtals.push_back(nBad)
            self.maxStatus.push_back(14)
        inFile.close()

    def update(self,ignored) :
        self.value={}
        self.value["trigPrims"] = self.trigPrims
        self.value["nBadXtals"] = self.nBadXtals
        self.value["maxStatus"] = self.maxStatus
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
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["trigPrims"]
class ecalDeadTowerNBadXtals(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["nBadXtals"]
class ecalDeadTowerMaxStatus(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["maxStatus"]
##############################
class hcalDeadChannelP4(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["p4"]
class hcalDeadChannelStatus(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["status"]
##############################
class logErrorTooManyClusters(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class logErrorTooManySeeds(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
##############################
class beamHaloCSCLooseHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloCSCTightHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloEcalLooseHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloEcalTightHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloGlobalLooseHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloGlobalTightHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloHcalLooseHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloHcalTightHaloId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
##############################
class isRealData(wrappedChain.calculable) :
    def isFake(self) : return True    
    def update(self,ignored) : self.value = not ("genpthat" in self.source)
##############################
