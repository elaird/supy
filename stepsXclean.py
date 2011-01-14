from analysisStep import analysisStep
import ROOT as r
#####################################
class vetoCounts(analysisStep) :
    def __init__(self, objects) :
        self.vetos = {}
        self.lenkeys = [("%s%s"%objects[obj],"%sIndices%s"%objects[obj]) for obj in ["photon","electron","muon"]] +\
                       [("failed_%s%s_unmatched"%objects[obj],"%sIndicesUnmatched%s"%objects[obj]) for obj in ["photon","electron"]]+\
                       [("failed_%s%s"%objects[obj],"%sIndicesOther%s"%objects[obj]) for obj in ["muon","jet"]]

        self.uniqueMuMatch="%s%sNonIsoMuonsUniquelyMatched"%objects["jet"]
        self.keys = ["any"]+[key for key,indices in self.lenkeys]+["nonUniqueMuMatch"]
        self.nBins= len(self.keys)
        
    def uponAcceptance(self,eventVars) :
        for key,indices in self.lenkeys : self.vetos[key] = bool(len(eventVars[indices]))
        self.vetos["nonUniqueMuMatch"] = not eventVars["crock"][self.uniqueMuMatch]
        self.vetos["any"] = False
        self.vetos["any"] = any(self.vetos.values())
        
        for i,key in enumerate(self.keys) :
            if self.vetos[key]:
                self.book.fill( i, "VetoCounts", self.nBins, 0, self.nBins, title="Vetos;;events / bin", xAxisLabels = self.keys)
                for j,key2 in enumerate(self.keys) :
                    if self.vetos[key2]:
                        self.book.fill( (i,j), "VetoCountsCoincident", (self.nBins,self.nBins), (0,0), (self.nBins,self.nBins),
                                        title="Coincident Vetoes;;;events / bin", xAxisLabels = self.keys, yAxisLabels = self.keys)
#####################################
class vetoLists(analysisStep) :
    def __init__(self, objects) :
        self.vetos = {}
        self.lenkeys = [("%s%s"%objects[obj],"%sIndices%s"%objects[obj]) for obj in ["photon","electron","muon"]] +\
                       [("failed_%s%s_unmatched"%objects[obj],"%sIndicesUnmatched%s"%objects[obj]) for obj in ["photon","electron"]]+\
                       [("failed_%s%s"%objects[obj],"%sIndicesOther%s"%objects[obj]) for obj in ["muon","jet"]]

        self.uniqueMuMatch="%s%sNonIsoMuonsUniquelyMatched"%objects["jet"]
        self.keys = ["any"]+[key for key,indices in self.lenkeys]+["nonUniqueMuMatch"]
        self.lists = dict([(key,[]) for key in self.keys])
        
    def uponAcceptance(self,eventVars) :
        for key,indices in self.lenkeys : self.vetos[key] = bool(len(eventVars[indices]))
        self.vetos["nonUniqueMuMatch"] = not eventVars["crock"][self.uniqueMuMatch]
        self.vetos["any"] = False
        self.vetos["any"] = any(self.vetos.values())

        runLumiEvent = (eventVars["run"],eventVars["lumiSection"],eventVars["event"])
        for key in self.keys :
            if self.vetos[key] : self.lists[key].append(runLumiEvent)
        
    def endFunc(self, otherChainDict) :
        for key in self.lists :
            file = open("%sVetos.txt"%key,"w")
            for RLE in sorted(self.lists[key]) : print >>file, "%d, %d, %d"%RLE
            file.close()
#####################################
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
        jetP4sAndCorrs = zip(eventVars[self.jetP4s],eventVars[self.jetCorrs])
        for object in self.objects:
            p4s = eventVars["%sP4%s"%object]
            for i in (set(eventVars["%sIndicesOther%s"%object])-set(eventVars["%sIndicesUnmatched%s"%object])) :
                p4 = p4s[i]
                pt = p4.pt()
                jetPt = self.matchedJetSumPt(p4,jetP4sAndCorrs)
                self.book.fill( (jetPt,pt), "jetPtMatchOther%s%s"%object, (100,100), (0,0),(500,500),
                                title="jet matching of failed %s%s;#sum pT of matched uncorr. jets;pT of failed %s%s;events / bin"%(object+object)  )
                if pt>500 or jetPt>500:
                    self.book.fill( pt/jetPt, "jetPtMatchOther%s%sOverflow"%object, 100, 0, 1.1,
                                    title="Overflow: jet matching of failed %s%s; pT_{failed %s%s} / #sum pT_{matched uncorr. jets};events / bin"%(object+object)  )

#####################################
class jetModHistogrammer(analysisStep) :
    def __init__(self,jets) :
        self.jets = jets
        self.indices = "%sIndicesModified%s"%jets
        self.xcp4s = "%sCorrectedP4%s"%jets
        self.p4s = ("%sCorrectedP4%s"%jets)[2:]
        

    def uponAcceptance(self,eventVars) :
        p4s = eventVars[self.p4s]
        xcp4s = eventVars[self.xcp4s]
        for i in eventVars[self.indices] :
            xcpt = xcp4s[i].pt()
            diffpt = xcpt - p4s[i].pt()
            self.book.fill( (xcpt,diffpt), "jetPtMod%s%s"%self.jets, (100,100),(0,0),(500,500),
                            title = "%s%s w/muons;%s%s pt;muon pt;events / bin"%(self.jets+self.jets))
            if xcpt > 500:
                self.book.fill( diffpt/xcpt, "jetPtMod%s%sOverflow"%self.jets, 100,0,1,
                                title = "Overflow: %s%s w/muons;pT_{muon}/pT_{%s%s}"%(self.jets+self.jets))
