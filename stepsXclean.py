from analysisStep import analysisStep
import ROOT as r
#####################################
class vetoCounts(analysisStep) :
    def __init__(self, objects) :
        self.vetos = {}
        self.lenkeys = [("%s%s"%objects[obj],"%sIndices%s"%objects[obj]) for obj in ["photon","electron","muon"]] +\
                       [("failed_%s%s_unmatched"%objects[obj],"%sIndicesUnmatched%s"%objects[obj]) for obj in ["photon","electron"]]+\
                       [("failed_%s%s"%objects[obj],"%sIndicesOther%s"%objects[obj]) for obj in ["muon","jet"]]

        self.nonUniqueMuMatch="%s%sNonIsoMuonsUniquelyMatched"%objects["jet"]
        self.keys = ["any"]+[key for key,indices in self.lenkeys]+["nonUniqueMuMatch"]
        self.nBins= len(self.keys)
        
    def uponAcceptance(self,eventVars) :
        for key,indices in self.lenkeys : self.vetos[key] = bool(len(eventVars[indices]))
        self.vetos["nonUniqueMuMatch"] = eventVars["crock"][self.nonUniqueMuMatch]
        self.vetos["any"] = False
        self.vetos["any"] = any(self.vetos.values())
        
        book = self.book(eventVars)
        for i,key in enumerate(self.vetos.keys()) :
            if self.vetos[key]:
                book.fill( i+1, "VetoCounts", self.nBins, 0, self.nBins, title="Vetos;;events / bin")
                for j,key2 in enumerate(self.vetos.keys()) :
                    if self.vetos[key2]:
                        book.fill( (i+1,j+1), "VetoCountsCoincident", (self.nBins,self.nBins), (0,0), (self.nBins,self.nBins),
                                   title="Coincident Vetoes;;;events / bin")

    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        for book in self.books.values() :
            for hist in book.values():
                if "VetoCounts" not in hist.GetName(): continue
                for i in range(hist.GetNbinsX()) :
                    hist.GetXaxis().SetBinLabel(i+1,self.keys[i])
                    if hist.GetNbinsY() > 1: 
                        hist.GetYaxis().SetBinLabel(i+1,self.keys[i])
                    
class ecalDepositValidator(analysisStep):
    def __init__(self,objects,dR) :
        self.dR = dR
        self.jetP4s = "%sCorrectedP4%s"%objects["jet"]
        self.jetCorrs = "%sCorrFactor%s"%objects["jet"]
        if self.jetP4s[:2] == "xc" :
            self.jetP4s = self.jetP4s[2:]
            self.jetCorrs = self.jetCorrs[2:]
        self.jets = objects["jet"]
        self.objects = [objects["electron"],objects["photon"]]

    def matchedJetSumPt(self,p4,jetP4sAndCorrs) :
        sumPt = 0
        for jetP4,jetCorr in jetP4sAndCorrs:
            if self.dR > r.Math.VectorUtil.DeltaR(jetP4,p4) :
                sumPt += jetP4.pt()/jetCorr
        return sumPt

    def uponAcceptance(self,eventVars) :
        book = self.book(eventVars)
        jetP4sAndCorrs = zip(eventVars[self.jetP4s],eventVars[self.jetCorrs])
        for object in self.objects:
            p4s = eventVars["%sP4%s"%object]
            for i in eventVars["%sIndicesOther%s"%object] :
                p4 = p4s[i]
                pt = p4.pt()
                jetPt = self.matchedJetSumPt(p4,jetP4sAndCorrs)
                book.fill( (jetPt,pt), "jetPtMatchOther%s%s"%object, (100,100), (0,0),(500,500),
                           title="jet matching of failed %s%s;#sum pT of matched uncorr. jets;pT of failed %s%s;events / bin"%(object+object)  )
                if pt>500 or jetPt>500:
                    book.fill( pt/jetPt, "jetPtMatchOther%s%sOverflow"%object, 100, 0, 1.1,
                               title="Overflow: jet matching of failed %s%s; pT_{failed %s%s} / #sum pT_{matched uncorr. jets};events / bin"%(object+object)  )

class jetModHistogrammer(analysisStep) :
    def __init__(self,jets) :
        self.jets = jets
        self.indices = "%sIndicesModified%s"%jets
        self.xcp4s = "%sCorrectedP4%s"%jets
        self.p4s = ("%sCorrectedP4%s"%jets)[2:]
        

    def uponAcceptance(self,eventVars) :
        book = self.book(eventVars)
        p4s = eventVars[self.p4s]
        xcp4s = eventVars[self.xcp4s]
        for i in eventVars[self.indices] :
            xcpt = xcp4s[i].pt()
            diffpt = xcpt - p4s[i].pt()
            book.fill( (xcpt,diffpt), "jetPtMod%s%s"%self.jets, (100,100),(0,0),(500,500),
                       title = "%s%s w/muons;%s%s pt;muon pt;events / bin"%(self.jets+self.jets))
            if xcpt > 500:
                book.fill( diffpt/xcpt, "jetPtMod%s%sOverflow"%self.jets, 100,0,1,
                           title = "Overflow: %s%s w/muons;pT_{muon}/pT_{%s%s}"%(self.jets+self.jets))
