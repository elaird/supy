from wrappedChain import *
import copy
import ROOT as r

class xcJetIndices(wrappedChain.calculable) :
    def name(self) : return self.namestr

    def __init__(self, collection) :
        self.namestr = "%sIndices%s" % collection
        self.p4sName = "%sCorrectedP4%s"% collection

    def update(self,ignored) :
        self.value = range(self.source[self.p4sName].size())
######################################
class xcJetCorrectedP4(wrappedChain.calculable) :
    def name(self) : return "xc%sCorrectedP4%s"%self.jets

    def __init__(self, collection,
                 photons   = None, photonDR   = 0,
                 electrons = None, electronDR = 0,
                 muons     = None, muonDR     = 0 ) :
        self.jets = collection
        self.other = {"photons":(photons,photonDR), "electrons":(electrons,electronDR),"muons":(muons,muonDR)}
        self.value = r.std.vector('LorentzV')()
        self.moreName = "jets,phot,elec,muon = %s,%s,%s,%s" \
                        % ("%s%s"%collection, str(photons), str(electrons), str(muons))
        self.moreName2 = "dR (phot,elec,muon) = (%.1f,%.1f,%.1f)" % (photonDR,electronDR,muonDR)

    def update(self,ignored) :
        jetIndices = set(self.source["%sIndices%s"%self.jets])
        jetP4s = self.source["%sCorrectedP4%s"%self.jets]

        for iJet in list(jetIndices) :
            jetP4 = jetP4s.at(iJet)
            if self.matchIn("photons",jetP4) \
            or self.matchIn("electrons",jetP4) :
                jetIndices.remove(iJet)
        
        finalJets = [copy.deepcopy(jetP4s.at(i)) for i in jetIndices]

        muonsName,muonDR = self.other["muons"]
        if muonsName :
            print "Woah there, maybe you should check this implementation (jet corrections from muons)"
            muons = self.source["%sP4%s"%muonsName]
            for jet in finalJets :
                for i in self.source["%sIndices%s"%muonsName] :
                    if muonDR > r.Math.Vectorutil.DeltaR(jet,muons.at(i)) :
                        jet += muons.at(i)

        finalJets.sort( reverse = True, key = lambda p4: p4.pt())
        self.value.clear()
        for p4 in finalJets:
            self.value.push_back(p4)

    def matchIn(self,label,p4) :
        collection,dR = self.other[label]
        if not collection : return False
        indices = self.source["%sIndices%s"%collection]
        objects = self.source["%sP4%s"%collection]
        for i in indices :
            if dR > r.Math.VectorUtil.DeltaR(objects.at(i),p4) :
                return True
        return False
        
