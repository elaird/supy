import ROOT as r        
from analysisStep import analysisStep

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

        for genZ in map( p4Gen.at, iGensZ) : book.fill( (abs(gen.eta()),gen.pt()), "%sGenZs"%self.nametag, self.bins2, self.low2, self.up2 )
        for gen in map( p4Gen.at, iGens) : book.fill( (abs(gen.eta()),gen.pt()), "%sGenPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco in map( p4Reco.at, iRecos) : book.fill( (abs(reco.eta()),reco.pt()), "%sRecoPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco,gen in [ (p4Reco.at(rg[0]), p4Gen.at(rg[1])) for rg in iRiGMatches] :
            book.fill( (abs(gen.eta()),gen.pt(),reco.pt()) , "%sMatchedPhotons"%self.nametag, self.bins3, self.low3, self.up3 )
