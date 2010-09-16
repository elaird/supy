import ROOT as r        
from analysisStep import analysisStep
#####################################
class photonSelectionHistogrammer(analysisStep) :
    """photonSelectionHistogrammer"""
    
    def __init__(self, nametag="", matchDeltaRMax = None, prompt = False) :
        self.deltaRMax = matchDeltaRMax
        self.nametag = nametag
        self.prompt = prompt

        #            (eta, pt)
        self.bins2 = (40, 80 );  self.bins3 = tuple(list(self.bins2)+[self.bins2[1]])
        self.low2 =  (0,  0  );  self.low3  = tuple(list(self.low2) +[self.low2[1]] )
        self.up2 =   (5,  400);  self.up3   = tuple(list(self.up2) + [self.up2[1]]  )

        self.moreName = "%s; match deltaR<%.1f; %s" % (nametag, matchDeltaRMax, "prompt" if prompt else "")

    def uponAcceptance(self,ev) :
        book = self.book(ev)

        p4Reco = ev["photonP4Pat"]
        p4Gen = ev["genP4"]
                
        iGensZ = ev["genIndicesZ"]
        iRecos = ev["photonIndicesPat"] if not self.prompt else ev["promptPhotonIndicesPat"]
        iGens = ev["genIndicesPhoton"] if not self.prompt else \
                filter( lambda i : ev["genStatus"][i] == 3,  ev["genIndicesPhoton"])

        iRiGMatches = []
        for igen in iGens :
            for ireco in iRecos :
                if self.deltaRMax > r.Math.VectorUtil.DeltaR( p4Reco.at(ireco), p4Gen.at(igen)) :
                    iRiGMatches.append( (ireco,igen) )
        # resolve multi matches

        for gen in map( p4Gen.at, iGensZ) : book.fill( (abs(gen.eta()),gen.pt()), "%sGenZs"%self.nametag, self.bins2, self.low2, self.up2 )
        for gen in map( p4Gen.at, iGens) : book.fill( (abs(gen.eta()),gen.pt()), "%sGenPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco in map( p4Reco.at, iRecos) : book.fill( (abs(reco.eta()),reco.pt()), "%sRecoPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco,gen in [ (p4Reco.at(rg[0]), p4Gen.at(rg[1])) for rg in iRiGMatches] :
            book.fill( (abs(gen.eta()),gen.pt(),reco.pt()) , "%sMatchedPhotons"%self.nametag, self.bins3, self.low3, self.up3 )
#####################################
class singlePhotonHistogrammer(analysisStep) :
    """singlePhotonHistogrammer"""

    def __init__(self,cs, maxIndex = 0) :
        self.cs = cs
        self.csbase = (cs[0].replace("xc",""),cs[1])
        self.maxIndex = maxIndex
        self.moreName="%s%s through index %d" % (self.cs+(maxIndex,))
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs

    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        p4s = eventVars[self.p4sName]
        cleanPhotonIndices = eventVars[self.indicesName]

        book.fill( len(cleanPhotonIndices), "photonMultiplicity", 10, -0.5, 9.5,
                   title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%self.cs)
        
        for i,iPhoton in enumerate(cleanPhotonIndices) :
            photon = p4s.at(iPhoton)
            photonLabel = str(i+1) if i <= self.maxIndex else "_ge%d"%(self.maxIndex+2)
            book.fill(photon.pt(),  "%s%s%sPt" %(self.cs+(photonLabel,)), 50,  0.0, 500.0, title=";photon%s p_{T} (GeV);events / bin"%photonLabel)
            book.fill(photon.eta(), "%s%s%seta"%(self.cs+(photonLabel,)), 50, -5.0,   5.0, title=";photon%s #eta;events / bin"%photonLabel)
#####################################
class photonPtSelector(analysisStep) :
    """photonPtSelector"""

    def __init__(self,cs,photonPtThreshold,photonIndex):
        self.photonIndex = photonIndex
        self.photonPtThreshold = photonPtThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%.1f GeV" % (self.cs[0], self.cs[1], photonIndex, photonPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.photonIndex : return False
        p4s = eventVars[self.p4sName]
        return self.photonPtThreshold <= p4s.at(indices[self.photonIndex]).pt()
#####################################
