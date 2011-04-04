import copy,array,os,collections
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class label(analysisStep) :
    def __init__(self,title) : self.moreName = title
    def select(self,eventVars) : return True
#####################################
class multiplicity(analysisStep) :
    def __init__(self,var, min = 0, max = None ) :
        self.moreName = "%d <= %s"%(min,var) + (" <= %d" % max if max!=None else "")
        self.var = var
        self.min = min
        self.max = max if max!=None else 1e6
    def select(self,eventVars) :
        return self.min <= len(eventVars[self.var]) <= self.max
#####################################
class value(analysisStep) :
    def __init__(self, var, min = None, max = None, indices = "", index = None) :
        for item in ["var","min","max","indices","index"] : setattr(self,item,eval(item))
        self.moreName = ( ("%.1f<="%min if min is not None else "") + var +
                          ("[i[%s]]" % str(index) if index is not None else "") + self.wrapName() + 
                          ("<=%.1f"%max if max is not None else "") +
                          ("; %s"%indices if indices else ""))

    def select(self,eventVars) :
        val = eventVars[self.var] if self.index==None else \
              eventVars[self.var][self.index] if not self.indices else \
              eventVars[self.var][eventVars[self.indices][self.index]] if self.index<len(eventVars[self.indices]) else None
        if val is None : return False
        val = self.wrap(val)
        return self.min <= val and ((self.max is None) or val <= self.max)

    def wrapName(self) : return ""
    def wrap(self,val) : return val
#####################################
class pt(value) :
    def wrapName(self) : return ".pt"
    def wrap(self,val) : return val.pt()
class absPz(value) :
    def wrapName(self) : return ".absPz"
    def wrap(self,val) : return abs(val.pz())
class eta(value) :
    def wrapName(self) : return ".eta"
    def wrap(self,val) : return val.eta()
class absEta(value) :
    def wrapName(self) : return ".absEta"
    def wrap(self,val) : return abs(val.eta())
#####################################
class OR(analysisStep) :
    def __init__(self, listOfSelectorSteps = []) :
        self.steps = listOfSelectorSteps
        self.moreName = '|'.join(["%s:%s"%(step.name(),step.moreName) for step in self.steps])
    def select(self,eventVars) :
        for step in self.steps :
            if step.select(eventVars) : return True
        return False
#####################################
class product(analysisStep) :
    def __init__(self, variables, min, max):
        for item in ["variables","min","max"] : setattr(self,item,eval(item))
        self.threshold = threshold
        self.variables = variables
        self.moreName = "%s>=%.3f %s" % ("*".join(variables),threshold,suffix)

    def select (self,eventVars) :
        product = 1
        for var in self.variables : product *= eventVars[var]
        return product >= self.threshold
#####################################
class runLsEvent(analysisStep) :
    def __init__(self, fileName) :
        self.moreName = "run:ls:event in %s"%fileName
        file = open(fileName)
        self.tuples = [ eval("(%s,%s,%s)"%tuple(line.replace("\n","").split(":"))) for line in file]
        file.close()

    def select (self,eventVars) :
        return (eventVars["run"], eventVars["lumiSection"], eventVars["event"]) in self.tuples
#####################################
class run(analysisStep) :
    def __init__(self,runs,acceptRatherThanReject) :
        self.runs = runs
        self.accept = acceptRatherThanReject

        self.moreName = "run%s in list %s" % ( ("" if self.accept else " not"),str(runs) )
        
    def select (self,eventVars) :
        return not ((eventVars["run"] in self.runs) ^ self.accept)
#####################################
class hbheNoise(analysisStep) :
    def __init__(self, invert = False) :
        self.invert = invert

    def select (self,eventVars) :
        return eventVars["hbheNoiseFilterResult"]^self.invert
#####################################
class monster(analysisStep) :
    def __init__(self,maxNumTracks=10,minGoodTrackFraction=0.25) :
        self.maxNumTracks=maxNumTracks
        self.minGoodTrackFraction=minGoodTrackFraction

        self.moreName = "<=%d tracks or >%.2f good fraction" % (maxNumTracks, minGoodTrackFraction)

    def select (self,eventVars) :
        nTracks = sum(map(eventVars.__getitem__, ["tracksNEtaLT0p9AllTracks",
                                                  "tracksNEta0p9to1p5AllTracks",
                                                  "tracksNEtaGT1p5AllTracks"]))
        nGoodTracks = sum(map(eventVars.__getitem__, ["tracksNEtaLT0p9HighPurityTracks",
                                                      "tracksNEta0p9to1p5HighPurityTracks",
                                                      "tracksNEtaGT1p5HighPurityTracks"]))
        return (nTracks <= self.maxNumTracks or nGoodTracks > self.minGoodTrackFraction*nTracks)
#####################################
class bx(analysisStep) :
    def __init__(self,bxList) :
        self.bxList = bxList
        self.moreName = "[%s]" % ",".join(bxList)

    def select (self,eventVars) :
        return eventVars["bunch"] in self.bxList
#####################################
class deadHcal(analysisStep) :
    def __init__(self, jets = None, extraName = "", dR = None, dPhiStarCut = None, nXtalThreshold = None) :
        for item in ["jets","dR","dPhiStarCut"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStar%s%s"%(self.jets[0],self.jets[1],extraName)
        self.badJet = r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,0.0,0.0,0.0)
        self.moreName = "%s%s; dR>%5.3f when deltaPhiStar<%5.3f"%(self.jets[0], self.jets[1], self.dR, self.dPhiStarCut)
        
    def select(self, eventVars) :
        d = eventVars[self.dps]
        index = d["DeltaPhiStarJetIndex"]
        if d["DeltaPhiStar"]>self.dPhiStarCut :
            return True
        jet = eventVars["%sCorrectedP4%s"%self.jets].at(index)
        self.badJet.SetCoordinates(jet.pt(),jet.eta(),jet.phi(),jet.E())
        for channel in eventVars["hcalDeadChannelP4"] :
            if r.Math.VectorUtil.DeltaR(self.badJet,channel) < self.dR :
                return False
        return True
#####################################
class deadEcalIncludingPhotons(analysisStep) :
    def __init__(self, jets = None, extraName = "", photons = None, dR = None, dPhiStarCut = None, nXtalThreshold = None) :
        for item in ["jets","photons","dR","dPhiStarCut","nXtalThreshold"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStarIncludingPhotons%s%s"%(self.jets[0],self.jets[1],extraName)
        self.badThing = r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,0.0,0.0,0.0)
        self.moreName = "%s%s; %s%s; dR>%5.3f when deltaPhiStar<%5.3f and nXtal>%d"%(self.jets[0], self.jets[1],
                                                                                     self.photons[0], self.photons[1],
                                                                                     self.dR, self.dPhiStarCut, self.nXtalThreshold)
        
    def select(self, eventVars) :
        d = eventVars[self.dps]
        if d["DeltaPhiStar"]>self.dPhiStarCut :
            return True

        jetIndex = d["DeltaPhiStarJetIndex"]
        photonIndex = d["DeltaPhiStarPhotonIndex"]
        if jetIndex!=None :
            thing = eventVars["%sCorrectedP4%s"%self.jets].at(jetIndex)
        elif photonIndex!=None :
            thing = eventVars["%sP4%s"%self.photons].at(photonIndex)

        self.badThing.SetCoordinates(thing.pt(),thing.eta(),thing.phi(),thing.E())
        for iRegion,region in enumerate(eventVars["ecalDeadTowerTrigPrimP4"]) :
            if eventVars["ecalDeadTowerNBadXtals"].at(iRegion)<self.nXtalThreshold : continue
            if r.Math.VectorUtil.DeltaR(self.badThing,region) < self.dR :
                return False
        return True
#####################################
