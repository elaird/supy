import os,collections
import ROOT as r
from analysisStep import analysisStep
import utils
#####################################
class displayer(analysisStep) :
    
    def __init__(self, jets = None, met = None, muons = None, electrons = None, photons = None, taus = None,
                 recHits = None, recHitPtThreshold = -1.0, scale = 200.0, etRatherThanPt = False, doGenParticles = False,
                 doEtaPhiPlot = True, hotTpThreshold = 63.5, deltaPhiStarExtraName = "", deltaPhiStarCut = None, deltaPhiStarDR = None, showAlphaTMet = True,
                 printOtherJetAlgoQuantities = False, jetsOtherAlgo = None, metOtherAlgo = None, printExtraText = True,
                 ra1Mode = True, ra1CutBits = True, markusMode = False, tipToTail = False) :

        self.moreName = "(see below)"

        for item in ["scale","jets","met","muons","electrons","photons","taus","recHits","recHitPtThreshold","doGenParticles",
                     "doEtaPhiPlot","hotTpThreshold","deltaPhiStarExtraName", "deltaPhiStarCut", "deltaPhiStarDR", "showAlphaTMet",
                     "printOtherJetAlgoQuantities", "jetsOtherAlgo", "metOtherAlgo", "printExtraText", "ra1Mode", "ra1CutBits", "markusMode","tipToTail"] :
            setattr(self,item,eval(item))

        self.jetRadius = 0.7 if "ak7Jet" in self.jets[0] else 0.5
        self.genJets = self.jets
        self.genMet  = self.met.replace("P4","GenMetP4") if self.met else self.met
        self.deltaHtName = "%sDeltaPseudoJetEt%s"%self.jets if etRatherThanPt else "%sDeltaPseudoJetPt%s"%self.jets
        
        self.doReco = not self.doGenParticles
        #self.helper = r.displayHelper()

        self.markusReName = {
            "clean jets (xcak5JetPat)": "clean jets (AK5 Calo)",
            "clean jets (xcak5JetPFPat)": "clean jets (AK5 PF)",
            "ignored jets (xcak5JetPat)": "ignored jets (AK5 Calo)",
            "ignored jets (xcak5JetPFPat)": "ignored jets (AK5 PF)",
            "MHT (xcak5JetPat)": "MHT",
            "MHT (xcak5JetPFPat)": "MHT",
            "MET (metP4AK5TypeII)": "CaloMET Type II",
            "MET (metP4PF)": "PF MET",
            "xcak5JetPat": "AK5 Calo Jets",
            "xcak5JetPFPat": "AK5 PF Jets",
            }
         

        self.titleSizeFactor = 1.0
        
        self.legendDict = collections.defaultdict(int)
        self.legendList = []

    def outputSuffix(self) :
        return "_displays.root"
    
    def setup(self, chain, fileDir) :
        someDir = r.gDirectory
        self.outputFile = r.TFile(self.outputFileName(), "RECREATE")
        someDir.cd()

        self.canvas = utils.canvas("canvas")
        self.canvas.SetFixedAspectRatio()
        self.canvasIndex = 0

        self.ellipse = r.TEllipse()
        self.ellipse.SetFillStyle(0)

        self.deadBox = r.TBox()
        self.deadBox.SetFillColor(r.kBlack)
        self.deadBox.SetLineColor(r.kBlack)

        self.coldBox = r.TBox()
        self.coldBox.SetFillColor(r.kOrange-6)
        self.coldBox.SetLineColor(r.kOrange-6)

        self.hotBox = r.TBox()
        self.hotBox.SetFillColor(r.kRed)
        self.hotBox.SetLineColor(r.kRed)
        
        self.hcalBox = r.TBox()
        self.hcalBox.SetFillColor(r.kGreen)
        self.hcalBox.SetLineColor(r.kGreen)
        
        self.line = r.TLine()
        self.arrow = r.TArrow()
        self.text = r.TText()
        self.latex = r.TLatex()

        self.alphaFuncs=[
            self.makeAlphaTFunc(0.55,r.kBlack),
            self.makeAlphaTFunc(0.50,r.kOrange+3),
            self.makeAlphaTFunc(0.45,r.kOrange+7)
            ]

        epsilon=1.0e-6
        self.mhtLlHisto=r.TH2D("mhtLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashH_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        self.metLlHisto=r.TH2D("metLlHisto",";log ( likelihood / likelihood0 ) / N varied jets;#slashE_{T};tries / bin",100,-20.0+epsilon,0.0+epsilon,100,0.0,300.0)
        self.mhtLlHisto.SetDirectory(0)
        self.metLlHisto.SetDirectory(0)

    def endFunc(self, otherChainDict) :
        self.outputFile.Write()
        self.outputFile.Close()
        del self.canvas

    def prepareText(self, params, coords) :
        self.text.SetTextSize(params["size"])
        self.text.SetTextFont(params["font"])
        self.text.SetTextColor(params["color"])
        self.textSlope = params["slope"]

        self.textX = coords["x"]
        self.textY = coords["y"]
        self.textCounter = 0

    def printText(self, message) :
        self.text.DrawText(self.textX, self.textY - self.textCounter * self.textSlope, message)
        self.textCounter += 1

    def printEvent(self, eventVars, params, coords) :
        self.prepareText(params, coords)
        for message in ["Run   %#10d"%eventVars["run"],
                        "Ls    %#10d"%eventVars["lumiSection"],
                        "Event %#10d"%eventVars["event"]
                        ] :
            self.printText(message)
        
    def printVertices(self, eventVars, params, coords, nMax) :
        self.prepareText(params, coords)
        self.printText("Vertices")
        self.printText("ID   Z(cm) sumPt(GeV)")
        self.printText("---------------------")

        nVertices = eventVars["vertexNdof"].size()
        for i in range(nVertices) :
            if nMax<=i :
                self.printText("[%d more not listed]"%(nVertices-nMax))
                break
            
            out = "%2s %6.2f  %5.0f"%("G " if i in eventVars["vertexIndices"] else "  ", eventVars["vertexPosition"].at(i).z(), eventVars["vertexSumPt"].at(i))
            self.printText(out)

    def printPhotons(self, eventVars, params, coords, photons, nMax) :
        self.prepareText(params, coords)
        p4Vector = eventVars["%sP4%s"        %photons]
        loose    = eventVars["%sIDLooseFromTwiki%s"%photons]
        tight    = eventVars["%sIDTightFromTwiki%s"%photons]
            
        self.printText(self.renamedDesc(photons[0]+photons[1]))
        self.printText("ID   pT  eta  phi")
        self.printText("-----------------")

        nPhotons = p4Vector.size()
        for iPhoton in range(nPhotons) :
            if nMax<=iPhoton :
                self.printText("[%d more not listed]"%(nPhotons-nMax))
                break
            photon=p4Vector[iPhoton]

            outString = "%1s%1s"% ("L" if loose[iPhoton] else " ", "T" if tight[iPhoton] else " ")
            outString+="%5.0f %4.1f %4.1f"%(photon.pt(), photon.eta(), photon.phi())
            self.printText(outString)

    def printElectrons(self, eventVars, params, coords, electrons, nMax) :
        self.prepareText(params, coords)
        p4Vector = eventVars["%sP4%s"        %electrons]
        ninetyFive = eventVars["%sID95%s"%electrons]
     
        self.printText(self.renamedDesc(electrons[0]+electrons[1]))
        self.printText("ID   pT  eta  phi")
        self.printText("-----------------")

        nElectrons = p4Vector.size()
        for iElectron in range(nElectrons) :
            if nMax<=iElectron :
                self.printText("[%d more not listed]"%(nElectrons-nMax))
                break
            electron=p4Vector[iElectron]

            outString = "%2s"%("95" if ninetyFive[iElectron] else "  ")
            outString+="%5.0f %4.1f %4.1f"%(electron.pt(), electron.eta(), electron.phi())
            self.printText(outString)

    def printMuons(self, eventVars, params, coords, muons, nMax) :
        self.prepareText(params, coords)
        p4Vector = eventVars["%sP4%s"     %muons]
        tight    = eventVars["%sIDtight%s"%muons]
        iso      = eventVars["%sCombinedRelativeIso%s"%muons]
        tr       = eventVars["%sIsTrackerMuon%s"%muons]
        gl       = eventVars["%sIsGlobalMuon%s"%muons]
        glpt     = eventVars["%sIDGlobalMuonPromptTight%s"%muons]
        
        self.printText(self.renamedDesc(muons[0]+muons[1]))
        self.printText("ID   pT  eta  phi    iso tr gl glpt")
        self.printText("-----------------------------------")

        nMuons = p4Vector.size()
        for iMuon in range(nMuons) :
            if nMax<=iMuon :
                self.printText("[%d more not listed]"%(nMuons-nMax))
                break
            muon=p4Vector[iMuon]

            outString = "%1s%1s"% (" ","T" if tight[iMuon] else " ")
            outString+="%5.0f %4.1f %4.1f %6.3f %2s %2s   %2s"%(muon.pt(), muon.eta(), muon.phi(), iso[iMuon],
                                                                "p" if   tr[iMuon] else "f",
                                                                "p" if   gl[iMuon] else "f",
                                                                "p" if glpt[iMuon] else "f",
                                                                )
            self.printText(outString)

    def printJets(self, eventVars, params, coords, jets, nMax) :
        self.prepareText(params, coords)
        jets2 = (jets[0].replace("xc",""),jets[1])
        isPf = "PF" in jets[0]
        p4Vector         = eventVars['%sCorrectedP4%s'     %jets]
        corrVector       = eventVars['%sCorrFactor%s'      %jets2]

        if not isPf :
            jetEmfVector  = eventVars['%sEmEnergyFraction%s'%jets2]
            jetFHpdVector = eventVars['%sJetIDFHPD%s'       %jets2]
            jetN90Vector  = eventVars['%sJetIDN90Hits%s'    %jets2]
            
            loose = eventVars["%sJetIDloose%s"%jets2]
            tight = eventVars["%sJetIDtight%s"%jets2]
            
        else :
            chf = eventVars["%sFchargedHad%s"%jets2]
            nhf = eventVars["%sFneutralHad%s"%jets2]

            cef = eventVars["%sFchargedEm%s"%jets2]
            nef = eventVars["%sFneutralEm%s"%jets2]

            cm  = eventVars["%sNcharged%s"%jets2]
            nm  = eventVars["%sNneutral%s"%jets2]
            
            loose = eventVars["%sPFJetIDloose%s"%jets2]
            tight = eventVars["%sPFJetIDtight%s"%jets2]
            
        self.printText(self.renamedDesc(jets[0]+jets[1]))
        self.printText("ID   pT  eta  phi%s"%("   EMF  fHPD N90 corr" if not isPf else "   CHF  NHF  CEF  NEF CM corr"))
        self.printText("-----------------%s"%("---------------------" if not isPf else "-----------------------------"))

        nJets = p4Vector.size()
        for iJet in range(nJets) :
            if nMax<=iJet :
                self.printText("[%d more not listed]"%(nJets-nMax))
                break
            jet=p4Vector[iJet]

            outString = "%1s%1s"% ("L" if loose[iJet] else " ", "T" if tight[iJet] else " ")
            outString+="%5.0f %4.1f %4.1f"%(jet.pt(), jet.eta(), jet.phi())

            if not isPf :
                outString+=" %5.2f %5.2f %3d %4.2f"%(jetEmfVector.at(iJet), jetFHpdVector.at(iJet), jetN90Vector.at(iJet), corrVector.at(iJet))
            else :
                outString+=" %5.3f %4.2f %4.2f %4.2f%3d %4.2f"%(chf.at(iJet), nhf.at(iJet), cef.at(iJet), nef.at(iJet), cm.at(iJet), corrVector.at(iJet))
            self.printText(outString)

    def printKinematicVariables(self, eventVars, params, coords, jets, jets2, others) :
        self.prepareText(params, coords)
        
        def go(j) :
            l = [eventVars["%s%s%s"  %(j[0], "SumEt",        j[1])],
                 eventVars["%s%s%s"  %(j[0], "SumP4",        j[1])].pt() if eventVars["%s%s%s"%(j[0], "SumP4",  j[1])] else 0,
                 eventVars["%s%s%s"  %(j[0], "AlphaTEt",     j[1])],
                 eventVars["%s%s%s%s"%(j[0], "DeltaPhiStar", j[1], self.deltaPhiStarExtraName)]["DeltaPhiStar"],
                 ]
            for i in range(len(l)) :
                if l[i]==None : l[i] = -1.0
            self.printText("%14s %4.0f %4.0f %6.3f %4.2f"%tuple([self.renamedDesc(j[0]+j[1])]+l))

        self.printText("jet collection   HT  MHT alphaT Dphi*")
        self.printText("-------------------------------------")
        
        go(jets)
        if jets2!=None and others :
            go(jets2)
        
    def passBit(self, var) :
        return " p" if var else " f"

    def printCutBits(self, eventVars, params, coords, jets, jets2, met, met2, others) :
        self.prepareText(params, coords)

        def go(j, m, i) :
            J2 = None if len(eventVars["%sIndices%s"%j])<2 else eventVars['%sCorrectedP4%s'%j].at(eventVars["%sIndices%s"%j][1]).pt()
            HT = eventVars["%sSumEt%s"%j]
            aT = eventVars["%sAlphaTEt%s"%j]
            MM = eventVars["%sMht%sOver%s"%(j[0], j[1], m)]
            DE = eventVars["%sDeltaPhiStar%s%s"%(j[0], j[1], self.deltaPhiStarExtraName)]["DeltaPhiStar"]>0.5 or \
                 eventVars["%sDeadEcalDR%s%s"  %(j[0], j[1], self.deltaPhiStarExtraName)]                >0.3

            all = (J2!=None and J2 > 100.0) and \
                  (HT!=None and HT > 350.0) and \
                  (aT!=None and aT > 0.550) and \
                  (DE!=None and DE        ) and \
                  (MM!=None and MM < 1.250)
            
            self.printText("%14s  %s %s %s %s %s  %s"%(self.renamedDesc(j[0]+j[1]),
                                                       self.passBit(J2!=None and J2 > 100.0),
                                                       self.passBit(HT!=None and HT > 350.0),
                                                       self.passBit(aT!=None and aT > 0.550),
                                                       self.passBit(DE!=None and DE),
                                                       self.passBit(MM!=None and MM < 1.250),
                                                       "candidate" if all else "",
                                                       )
                           )
            if self.markusMode and all and not i :
                self.text.SetTextSize(1.5*params["size"])
                self.text.SetTextFont(params["font"])
                self.text.SetTextColor(r.kBlue)
                self.text.DrawText(0.1, 0.1, "passes final selection")
                self.text.SetTextSize(params["size"])
                self.text.SetTextFont(params["font"])
                self.text.SetTextColor(params["color"])

        self.printText("jet collection  J2 HT aT DE MM")
        self.printText("------------------------------")

        go(jets, met, 0)
        if jets2!=None and met2!=None and others :
            go(jets2, met2, 1)

    def printFlags(self, eventVars, params, coords, flags) :
        self.prepareText(params, coords)
        for f in flags:
            if eventVars[f] : self.printText(f)
        
    def drawSkeleton(self, coords, color) :
        r.gPad.AbsCoordinates(False)
        
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(1)
        self.ellipse.SetLineStyle(1)
        self.ellipse.DrawEllipse(coords["x0"], coords["y0"], coords["radius"], coords["radius"], 0.0, 360.0, 0.0, "")

        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-coords["radius"], coords["y0"]                 , coords["x0"]+coords["radius"], coords["y0"]                 )
        self.line.DrawLine(coords["x0"]                 , coords["y0"]-coords["radius"], coords["x0"]                 , coords["y0"]+coords["radius"])

    def drawScale(self, color, size, scale, point) :
        self.latex.SetTextSize(size)
        self.latex.SetTextColor(color)
        self.latex.DrawLatex(point["x"], point["y"],"radius = "+str(scale)+" GeV p_{T}")

    def drawP4(self, c, p4, color, lineWidth, arrowSize, p4Initial = None) :
        x0 = c["x0"]+p4Initial.px()*c["radius"]/c["scale"] if p4Initial else c["x0"]
        y0 = c["y0"]+p4Initial.py()*c["radius"]/c["scale"] if p4Initial else c["y0"]
        x1 = x0+p4.px()*c["radius"]/c["scale"]
        y1 = y0+p4.py()*c["radius"]/c["scale"]

        #self.line.SetLineColor(color)
        #self.line.SetLineWidth(lineWidth)
        #self.line.DrawLine(x0,y0,x1,y1)

        self.arrow.SetLineColor(color)
        self.arrow.SetLineWidth(lineWidth)
        self.arrow.SetArrowSize(arrowSize)
        self.arrow.SetFillColor(color)
        self.arrow.DrawArrow(x0,y0,x1,y1)
        
    def drawCircle(self, p4, color, lineWidth, circleRadius, lineStyle = 1) :
        self.ellipse.SetLineColor(color)
        self.ellipse.SetLineWidth(lineWidth)
        self.ellipse.SetLineStyle(lineStyle)
        self.ellipse.DrawEllipse(p4.eta(), p4.phi(), circleRadius, circleRadius, 0.0, 360.0, 0.0, "")

    def renamedDesc(self, desc) :
        if not self.markusMode : return desc
        elif desc in self.markusReName : return self.markusReName[desc]
        else : return desc
        
    def legendFunc(self, color, name, desc) :
        if not self.legendDict[name] :
            self.legendDict[name] = True
            self.legendList.append( (color, self.renamedDesc(desc), "l") )

    def drawGenJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "genJet", desc = "GEN jets (%s%s)"%self.genJets)

        genJets = "%sGenJetP4%s"%self.genJets
        if genJets[:2] == "xc": genJets = genJets[2:]
        p4s = eventVars[genJets]
        if self.tipToTail :
            phiOrder = utils.phiOrder(p4s, range(len(p4s)))
            partials = utils.partialSumP4(p4s, phiOrder)
            mean = utils.partialSumP4Centroid(partials)
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, 0.3*arrowSize, partials[i]-mean)
            return
        for jet in p4s :
            self.drawP4(coords, jet, color, lineWidth, arrowSize)
            
    def drawGenParticles(self, eventVars, coords, color, lineWidth, arrowSize, statusList = None, pdgIdList = None, motherList = None, label = "", circleRadius = None) :
        self.legendFunc(color, name = "genParticle"+label, desc = label)

        for iParticle,particle in enumerate(eventVars["genP4"]) :
            if statusList!=None and eventVars["genStatus"].at(iParticle) not in statusList : continue
            if pdgIdList!=None and eventVars["genPdgId"].at(iParticle) not in pdgIdList : continue
            if motherList!=None and eventVars["genMotherPdgId"][iParticle] not in motherList : continue
            if circleRadius==None :
                self.drawP4(coords, particle, color, lineWidth, arrowSize)
            else :
                self.drawCircle(particle, color, lineWidth, circleRadius)
            
    def drawCleanJets(self, eventVars, coords, jets, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%scleanJet%s"%jets, desc = "clean jets (%s%s)"%jets)

        p4s = eventVars['%sCorrectedP4%s'%jets]
        if self.tipToTail :
            phiOrder = eventVars["%sIndicesPhi%s"%self.jets]
            partials = eventVars["%sPartialSumP4%s"%self.jets]
            mean = utils.partialSumP4Centroid(partials)
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, 0.3*arrowSize, partials[i]-mean)
            return

        cleanJetIndices = eventVars["%sIndices%s"%jets]
        for iJet in cleanJetIndices :
            self.drawP4(coords, p4s.at(iJet), color, lineWidth, arrowSize)
            
    def drawOtherJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sotherJet%s"%self.jets, desc = "\"other\" jets (%s%s)"%self.jets)

        p4Vector = eventVars["%sCorrectedP4%s"%self.jets]
        otherJetIndices = eventVars["%sIndicesOther%s"%self.jets]
        for index in otherJetIndices :
            self.drawP4(coords, p4Vector.at(index), color, lineWidth, arrowSize)
            
    def drawIgnoredJets(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%signoredJet%s"%self.jets, desc = "ignored jets (%s%s)"%self.jets)

        p4s = eventVars["%sCorrectedP4%s"%self.jets]
        ignoredJetIndices = set(range(len(p4s))) \
                            - set(eventVars["%sIndices%s"%self.jets]) \
                            - set(eventVars["%sIndicesOther%s"%self.jets])
        if self.tipToTail :
            phiOrder = utils.phiOrder(p4s, ignoredJetIndices)
            partials = utils.partialSumP4(p4s, phiOrder)
            goodPartials = eventVars["%sPartialSumP4%s"%self.jets]
            offset = goodPartials[-1] - eventVars["%sPartialSumP4Centroid%s"%self.jets]
            for i in range(len(phiOrder)) :
                self.drawP4( coords, p4s.at(phiOrder[i]), color, lineWidth, arrowSize, partials[i]+offset)
            return
        for iJet in ignoredJetIndices :
            self.drawP4(coords, p4s.at(iJet), color, lineWidth, arrowSize)
            
    def drawMht(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%smht%s"%self.jets, desc = "MHT (%s%s)"%self.jets)

        sump4 = eventVars["%sSumP4%s"%self.jets]
        if self.tipToTail :
            phiOrder = eventVars["%sIndicesPhi%s"%self.jets]
            partials = eventVars["%sPartialSumP4%s"%self.jets]
            mean = eventVars["%sPartialSumP4Centroid%s"%self.jets]
            if sump4 : self.drawP4(coords, -sump4,color,lineWidth,arrowSize, partials[-1]-mean)
            return
        if sump4 : self.drawP4(coords, -sump4, color, lineWidth, arrowSize)
            
    def drawHt(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sht%s"%self.jets, desc = "H_{T} (%s%s)"%self.jets)

        ht = eventVars["%sSumPt%s"%self.jets]
            
        y = coords["y0"]-coords["radius"]-0.05
        l = ht*coords["radius"]/coords["scale"]
        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-l/2.0, y, coords["x0"]+l/2.0, y)
        
    def drawNJetDeltaHt(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sdeltaHt%s"%self.jets, desc = "#DeltaH_{T} (%s%s)"%self.jets)

        y = coords["y0"]-coords["radius"]-0.03
        l = eventVars[self.deltaHtName]*coords["radius"]/coords["scale"]
        self.line.SetLineColor(color)
        self.line.DrawLine(coords["x0"]-l/2.0, y, coords["x0"]+l/2.0, y)

    def drawMet(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "met%s"%self.met, desc = "MET (%s)"%self.met)
        self.drawP4(coords, eventVars[self.met], color, lineWidth, arrowSize)
            
    def drawGenMet(self, eventVars, coords, color, lineWidth, arrowSize) :
        if self.genMet==None : return
        self.legendFunc(color, name = "genMet", desc = "GEN MET (%s)"%self.genMet)
        self.drawP4(coords, eventVars[self.genMet], color, lineWidth, arrowSize)
            
    def drawMuons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%smuon%s"%self.muons, desc = "muons (%s%s)"%self.muons)
        p4Vector=eventVars["%sP4%s"%self.muons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawElectrons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%selectron%s"%self.electrons, desc = "electrons (%s%s)"%self.electrons)
        p4Vector=eventVars["%sP4%s"%self.electrons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawPhotons(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%sphoton%s"%self.photons, desc = "photons (%s%s)"%self.photons)
        p4Vector=eventVars["%sP4%s"%self.photons]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawTaus(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "%stau%s"%self.taus, desc = "taus (%s%s)"%self.taus)
        p4Vector=eventVars[self.tauCollection+'P4'+self.tauSuffix]
        for i in range(len(p4Vector)) :
            self.drawP4(coords, p4Vector.at(i), color, lineWidth, arrowSize)
            
    def drawCleanedRecHits(self, eventVars, coords, color, lineWidth, arrowSize) :
        self.legendFunc(color, name = "cleanedRecHits%s"%self.recHits, desc = "cleaned RecHits (%s)"%self.recHits)

        subDetectors=[]
        if self.recHits=="Calo" :
            subDetectors=["Eb","Ee","Hbhe","Hf"]
        if self.recHits=="PF" :
            subDetectors=["Ecal","Hcal","Hfem","Hfhad","Ps"]

        for detector in subDetectors :
            for collectionName in ["","cluster"] :
                varName = "rechit"+collectionName+self.recHits+"P4"+detector
                if varName not in eventVars : continue
                for iHit in range(len(eventVars[varName])) :
                    hit = eventVars[varName].at(iHit)
                    if hit.pt()<self.recHitPtThreshold : continue
                    self.drawP4(coords, hit, color, lineWidth, arrowSize)
            
    def makeAlphaTFunc(self,alphaTValue,color) :
        alphaTFunc=r.TF1("#alpha_{T} = %#4.2g"%alphaTValue,
                         "1.0-2.0*("+str(alphaTValue)+")*sqrt(1.0-x*x)",
                         0.0,1.0)
        alphaTFunc.SetLineColor(color)
        alphaTFunc.SetLineWidth(1)
        alphaTFunc.SetNpx(300)
        return alphaTFunc

    def drawEtaPhiPlot (self, eventVars, corners) :
        pad=r.TPad("etaPhiPad", "etaPhiPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetTickx()
        pad.SetTicky()

        etaPhiPlot = r.TH2D("etaPhi",";#eta;#phi;",1, -3.0, 3.0, 1, -r.TMath.Pi(), r.TMath.Pi() )
        etaPhiPlot.SetStats(False)
        etaPhiPlot.Draw()

        ebEe = 1.479
        self.line.SetLineColor(r.kBlack)
        self.line.DrawLine(-ebEe, etaPhiPlot.GetYaxis().GetXmin(), -ebEe, etaPhiPlot.GetYaxis().GetXmax() )
        self.line.DrawLine( ebEe, etaPhiPlot.GetYaxis().GetXmin(),  ebEe, etaPhiPlot.GetYaxis().GetXmax() )
        suspiciousJetColor = r.kRed
        suspiciousJetStyle = 2
        
        def drawEcalBox(fourVector, nBadXtals, maxStatus) :
            value = (0.087/2) * nBadXtals / 25
            args = (fourVector.eta()-value, fourVector.phi()-value, fourVector.eta()+value, fourVector.phi()+value)
            if maxStatus==14 :
                self.deadBox.DrawBox(*args)
            elif fourVector.Et()>=self.hotTpThreshold :
                self.hotBox.DrawBox(*args)
            else :
                self.coldBox.DrawBox(*args)
                
        def drawHcalBox(fourVector) :
            value = 0.087/2
            args = (fourVector.eta()-value, fourVector.phi()-value, fourVector.eta()+value, fourVector.phi()+value)
            self.hcalBox.DrawBox(*args)

        if self.ra1Mode :
            #draw dead ECAL regions
            nRegions = eventVars["ecalDeadTowerTrigPrimP4"].size()
            for iRegion in range(nRegions) :
                drawEcalBox(fourVector = eventVars["ecalDeadTowerTrigPrimP4"].at(iRegion),
                            nBadXtals  = eventVars["ecalDeadTowerNBadXtals"].at(iRegion),
                            maxStatus  = eventVars["ecalDeadTowerMaxStatus"].at(iRegion),
                            )

            #draw masked HCAL regions
            nBadHcalChannels = eventVars["hcalDeadChannelP4"].size()
            for iChannel in range(nBadHcalChannels) :
                drawHcalBox(fourVector = eventVars["hcalDeadChannelP4"].at(iChannel))

        if self.doGenParticles :
            self.drawGenParticles(eventVars,r.kMagenta, lineWidth = 1, arrowSize = -1.0, statusList = [1], pdgIdList = [22],
                                  motherList = [1,2,3,4,5,6,-1,-2,-3,-4,-5,-6], label = "status 1 photon w/quark as mother", circleRadius = 0.15)
            self.drawGenParticles(eventVars,r.kOrange, lineWidth = 1, arrowSize = -1.0, statusList = [1], pdgIdList = [22],
                                  motherList = [22], label = "status 1 photon w/photon as mother", circleRadius = 0.15)
        else :
            etaPhiPlot.SetTitle("")
            if self.ra1Mode :
                d = eventVars["%sDeltaPhiStar%s%s"%(self.jets[0],self.jets[1],self.deltaPhiStarExtraName)]
                suspiciousJetIndex = d["DeltaPhiStarJetIndex"]
                deltaPhiStar = d["DeltaPhiStar"]

            suspiciousJetLegendEntry = False
            jets = eventVars["%sCorrectedP4%s"%self.jets]
            for index in range(jets.size()) :
                jet = jets.at(index)
                if index in eventVars["%sIndices%s"%self.jets] :
                    self.drawCircle(jet, r.kBlue, lineWidth = 1, circleRadius = self.jetRadius)
                else :
                    self.drawCircle(jet, r.kCyan, lineWidth = 1, circleRadius = self.jetRadius)
                if self.ra1Mode and index==suspiciousJetIndex and deltaPhiStar<self.deltaPhiStarCut :
                    self.drawCircle(jet, suspiciousJetColor, lineWidth = 1, circleRadius = self.deltaPhiStarDR, lineStyle = suspiciousJetStyle)
                    suspiciousJetLegendEntry = True

            legend1 = r.TLegend(0.02, 0.9, 0.72, 1.0)
            legend1.SetFillStyle(0)
            legend1.SetBorderSize(0)
            if self.ra1Mode : 
                legend1.AddEntry(self.deadBox,"dead ECAL cells","f")
                legend1.AddEntry(self.coldBox,"dead ECAL cells w/TP link","f")
                legend1.AddEntry(self.hotBox, "dead ECAL cells w/TP ET>%4.1f GeV"%self.hotTpThreshold,"f")
                legend1.Draw()

            legend2 = r.TLegend(0.58, 0.933, 0.98, 1.0)
            legend2.SetFillStyle(0)
            legend2.SetBorderSize(0)

            if self.ra1Mode : 
                legend2.AddEntry(self.hcalBox,"masked HCAL cells","f")
                self.ellipse.SetLineColor(suspiciousJetColor)
                self.ellipse.SetLineStyle(suspiciousJetStyle)
                if suspiciousJetLegendEntry :
                    legend2.AddEntry(self.ellipse,"jet with min. #Delta#phi* < %3.1f"%self.deltaPhiStarCut,"l")
                legend2.Draw()

        self.canvas.cd()
        pad.Draw()
        return [pad, etaPhiPlot, legend1, legend2]

    def drawAlphaPlot (self, eventVars, color, showAlphaTMet, corners) :
        pad = r.TPad("alphaTpad", "alphaTpad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetTickx()
        pad.SetTicky()

        title = ";"
        if showAlphaTMet :
            title +="#color[%d]{MET/HT}              "%r.kGreen
        title+= "#color[%d]{MHT/HT};#DeltaHT/HT"%r.kBlue
        alphaTHisto = r.TH2D("alphaTHisto",title,100,0.0,1.0,100,0.0,1.0)
        alphaTMetHisto = alphaTHisto.Clone("alphaTMetHisto")

        mht = eventVars["%sSumP4%s"%self.jets].pt() if eventVars["%sSumP4%s"%self.jets] else 0
        met = eventVars[self.met].pt()
        ht  = eventVars["%sSumPt%s"%self.jets]
        deltaHt   = eventVars[self.deltaHtName]
        alphaT    = eventVars["%sAlphaTEt%s"%self.jets]    #hack: hard-coded Et
        alphaTMet = eventVars["%sAlphaTMetEt%s"%self.jets] #hack: hard-coded Et
        
        if ht : alphaTHisto.Fill(mht/ht,deltaHt/ht)
        alphaTHisto.SetStats(False)
        alphaTHisto.SetMarkerStyle(29)
        alphaTHisto.GetYaxis().SetTitleOffset(1.15)
        alphaTHisto.SetMarkerColor(r.kBlue)
        alphaTHisto.GetXaxis().SetTitleSize(self.titleSizeFactor*alphaTHisto.GetXaxis().GetTitleSize())
        alphaTHisto.GetYaxis().SetTitleSize(self.titleSizeFactor*alphaTHisto.GetYaxis().GetTitleSize())
        alphaTHisto.Draw("p")

        if showAlphaTMet :
            if ht : alphaTMetHisto.Fill(met/ht,deltaHt/ht)
            alphaTMetHisto.SetStats(False)
            alphaTMetHisto.SetMarkerStyle(29)
            alphaTMetHisto.GetYaxis().SetTitleOffset(1.25)
            alphaTMetHisto.SetMarkerColor(r.kGreen)
            alphaTMetHisto.Draw("psame")

        legend1 = r.TLegend(0.1, 0.6, 1.0, 0.9)
        legend1.SetBorderSize(0)
        legend1.SetFillStyle(0)
        
        for func in self.alphaFuncs :
            func.Draw("same")
            legend1.AddEntry(func,func.GetName(),"l")

        legend1.Draw()

        #legend2 = r.TLegend(0.1, 0.4, 1.0, 0.6)
        #legend2.SetBorderSize(0)
        #legend2.SetFillStyle(0)
        #legend2.AddEntry(alphaTHisto,"this event","p")
        #if showAlphaTMet :
        #    legend2.AddEntry(alphaTMetHisto,"this event","p")
        #legend2.Draw()
        
        self.canvas.cd()
        pad.Draw()
        return [pad, alphaTHisto, alphaTMetHisto, legend1]

    def fillHisto(self,histo,lls,mhts) :
        for i in range(len(mhts)) :
            histo.Fill(lls[i],mhts[i])
        
    def drawMhtLlPlot (self, eventVars, color, corners) :
        stuffToKeep=[]
        pad = r.TPad("mhtLlPad","mhtLlPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        pad.SetLeftMargin(0.3)
        pad.SetRightMargin(0.15)

        mets       =eventVars[self.jetCollection+"mets"+self.jetSuffix]
        mhts       =eventVars[self.jetCollection+"mhts"+self.jetSuffix]
        lls        =eventVars[self.jetCollection+"lls"+self.jetSuffix]
        nVariedJets=eventVars[self.jetCollection+"nVariedJets"+self.jetSuffix]
        
        self.mhtLlHisto.Reset()
        self.metLlHisto.Reset()
        #self.helper.Fill(self.mhtLlHisto,lls,mhts,nVariedJets)
        #self.helper.Fill(self.metLlHisto,lls,mets,nVariedJets)

        histo=self.metLlHisto

        #histo.SetStats(False)
        histo.GetYaxis().SetTitleOffset(1.25)
        histo.SetMarkerColor(r.kBlack)
        histo.Draw("colz")

        stats=histo.GetListOfFunctions().FindObject("stats")
        if (stats!=None) :
            stats.SetX1NDC(0.01);
            stats.SetX2NDC(0.25);
            stats.SetY1NDC(0.51);
            stats.SetY2NDC(0.75);
            pad.Modified()
            pad.Update()
            stuffToKeep.append(stats)

        #legend=r.TLegend(0.1,0.9,0.6,0.6)
        #legend.SetFillStyle(0)
        #
        #legend.AddEntry(mhtLlHisto,"this event","p")
        #legend.Draw()
        #stuffToKeep.append(legend)
        #stuffToKeep.extend([pad,mhtLlHisto])
        stuffToKeep.append(pad)
        self.canvas.cd()
        pad.Draw()
        return stuffToKeep

    def drawRhoPhiPlot(self, eventVars, coords, corners) :
        pad = r.TPad("rhoPhiPad", "rhoPhiPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()

        skeletonColor = r.kYellow+1
        self.drawSkeleton(coords, skeletonColor)
        self.drawScale(color = skeletonColor, size = 0.03, scale = coords["scale"], point = {"x":0.0, "y":coords["radius"]+coords["y0"]+0.03})

        defArrowSize=0.5*self.arrow.GetDefaultArrowSize()
        defWidth=1
        #                                  color      , width   , arrow size
        if not eventVars["isRealData"] :
            if self.doGenParticles :
                self.drawGenParticles(eventVars, coords,r.kBlack  , defWidth, defArrowSize,       label = "all GEN particles")
                self.drawGenParticles(eventVars, coords,r.kBlue   , defWidth, defArrowSize*4/6.0, statusList = [1], label = "status 1")
                self.drawGenParticles(eventVars, coords,r.kGreen  , defWidth, defArrowSize*2/6.0, statusList = [1], pdgIdList = [22], label = "status 1 photon")
                self.drawGenParticles(eventVars, coords,r.kMagenta, defWidth, defArrowSize*1/6.0, statusList = [1], pdgIdList = [22],
                                      motherList = [1,2,3,4,5,6,-1,-2,-3,-4,-5,-6], label = "status 1 photon w/quark as mother")
                self.drawGenParticles(eventVars, coords,r.kOrange, defWidth, defArrowSize*1/6.0, statusList = [1], pdgIdList = [22],
                                      motherList = [22], label = "status 1 photon w/photon as mother")
            else :
                self.drawGenJets    (eventVars, coords,r.kBlack   , defWidth, defArrowSize)
                self.drawGenMet     (eventVars, coords,r.kMagenta , defWidth, defArrowSize*2/6.0)
            
        if self.doReco : 
            #self.drawP4(eventVars["%sLongP4%s"%self.jets],r.kGray,defWidth,defArrowSize*1/100.0)
            #self.drawP4(-eventVars["%sLongP4%s"%self.jets],r.kGray,defWidth,defArrowSize*1/100.0)
            self.drawCleanJets      (eventVars, coords, self.jets, r.kBlue    , defWidth, defArrowSize)
                                     
            #self.drawCleanJets      (eventVars, coords,
            #                         (self.jets[0].replace("xc","")+"JPT","Pat"),896,defWidth, defArrowSize*3/4.0)
            #self.drawCleanJets      (eventVars, coords,
            #                         (self.jets[0].replace("xc","")+"PF","Pat"), 38,defWidth, defArrowSize*1/2.0)
            
            self.drawIgnoredJets    (eventVars, coords,r.kCyan    , defWidth, defArrowSize*1/6.0)
            #self.drawOtherJets      (eventVars, coords,r.kBlack  )
            if self.ra1Mode and not self.markusMode :
                self.drawHt         (eventVars, coords,r.kBlue+3  , defWidth, defArrowSize*1/6.0)
                self.drawNJetDeltaHt(eventVars, coords,r.kBlue-9  , defWidth, defArrowSize*1/6.0)
            
            if self.ra1Mode :
                self.drawMht        (eventVars, coords,r.kRed     , defWidth, defArrowSize*3/6.0)
            if self.met :
                self.drawMet        (eventVars, coords,r.kGreen   , defWidth, defArrowSize*2/6.0)
            
            if not self.markusMode :
                if self.muons :     self.drawMuons    (eventVars, coords,r.kYellow  , defWidth, defArrowSize*2/6.0)
                if self.electrons : self.drawElectrons(eventVars, coords,r.kOrange+7, defWidth, defArrowSize*2.5/6.0)
                if self.photons :   self.drawPhotons  (eventVars, coords,r.kOrange  , defWidth, defArrowSize*1.8/6.0)
                if self.taus :      self.drawTaus     (eventVars, coords,r.kYellow  , defWidth, defArrowSize*2/6.0)
            
            if self.recHits :
                self.drawCleanedRecHits (eventVars, coords,r.kOrange-6, defWidth, defArrowSize*2/6.0)

        self.canvas.cd()
        pad.Draw()
        return [pad]

    def drawLegend(self, corners) :
        pad = r.TPad("legendPad", "legendPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()
        
        legend = r.TLegend(0.0, 0.0, 1.0, 1.0)
        for item in self.legendList :
            self.line.SetLineColor(item[0])
            someLine = self.line.DrawLine(0.0,0.0,0.0,0.0)
            legend.AddEntry(someLine, item[1], item[2])
        legend.Draw("same")
        self.canvas.cd()
        pad.Draw()
        return [pad,legend]

    def printAllText(self, eventVars, corners) :
        pad = r.TPad("textPad", "textPad", corners["x1"], corners["y1"], corners["x2"], corners["y2"])
        pad.cd()

        defaults = {}
        defaults["size"] = 0.035
        defaults["font"] = 80
        defaults["color"] = r.kBlack
        defaults["slope"] = 0.02

        y0 = 0.36 if self.printOtherJetAlgoQuantities else 0.60
        x0 = 0.015
        x1 = 0.45
        self.printEvent(   eventVars, params = defaults, coords = {"x":x0, "y":0.98})

        if self.printExtraText :
            self.printVertices(eventVars, params = defaults, coords = {"x":x1, "y":0.98}, nMax = 3)
            self.printJets(    eventVars, params = defaults, coords = {"x":x0, "y":   0.84}, jets = self.jets, nMax = 7)

            if self.printOtherJetAlgoQuantities :
                self.printJets(   eventVars, params = defaults, coords = {"x":x0, "y":0.60}, jets = self.jetsOtherAlgo, nMax = 7)
            else :
                if self.photons :
                    self.printPhotons(  eventVars, params = defaults, coords = {"x":x0,      "y":y0-0.20}, photons = self.photons, nMax = 3)
                if self.electrons :
                    self.printElectrons(eventVars, params = defaults, coords = {"x":x0+0.50, "y":y0-0.20}, electrons = self.electrons, nMax = 3)
                if self.muons :
                    self.printMuons(    eventVars, params = defaults, coords = {"x":x0,      "y":y0-0.36}, muons = self.muons, nMax = 3)

            if self.ra1Mode :
                self.printKinematicVariables(eventVars, params = defaults, coords = {"x":x0, "y":y0     }, jets = self.jets, jets2 = self.jetsOtherAlgo,
                                         others = self.printOtherJetAlgoQuantities)
                if self.ra1CutBits :
                    self.printCutBits(       eventVars, params = defaults, coords = {"x":x0, "y":y0-0.10}, jets = self.jets, jets2 = self.jetsOtherAlgo,
                                         met = self.met, met2 = self.metOtherAlgo, others = self.printOtherJetAlgoQuantities)
                self.printFlags(eventVars, params = defaults, coords = {"x":x0, "y":y0-0.34},
                                flags = ['logErrorTooManyClusters','logErrorTooManySeeds',
                                         "beamHaloCSCLooseHaloId","beamHaloCSCTightHaloId","beamHaloEcalLooseHaloId","beamHaloEcalTightHaloId",
                                         "beamHaloGlobalLooseHaloId","beamHaloGlobalTightHaloId","beamHaloHcalLooseHaloId","beamHaloHcalTightHaloId" ])
        
        self.canvas.cd()
        pad.Draw()
        return [pad]

    def uponAcceptance(self, eventVars) :
        self.canvas.Clear()

        rhoPhiPadYSize = 0.50*self.canvas.GetAspectRatio()
        rhoPhiPadXSize = 0.50
        radius = 0.4
        g1 = self.drawRhoPhiPlot(eventVars,
                                 coords = {"scale":self.scale, "radius":radius, "x0":radius, "y0":radius+0.05},
                                 corners = {"x1":0.0, "y1":0.0, "x2":rhoPhiPadXSize, "y2":rhoPhiPadYSize},
                                 )
        l = self.drawLegend(corners = {"x1":0.0, "y1":rhoPhiPadYSize, "x2":1.0-rhoPhiPadYSize, "y2":1.0})

        r.gStyle.SetOptStat(110011)        
        if self.doGenParticles or self.doEtaPhiPlot :
            gg = self.drawEtaPhiPlot(eventVars, corners = {"x1":rhoPhiPadXSize - 0.18,
                                                           "y1":rhoPhiPadYSize - 0.08*self.canvas.GetAspectRatio(),
                                                           "x2":rhoPhiPadXSize + 0.12,
                                                           "y2":rhoPhiPadYSize + 0.22*self.canvas.GetAspectRatio()})
            
        if self.doReco :
            if self.ra1Mode and not self.markusMode :
                g3 = self.drawAlphaPlot(eventVars, r.kBlack, showAlphaTMet = self.showAlphaTMet,
                                        corners = {"x1":rhoPhiPadXSize - 0.08,
                                                   "y1":0.0,
                                                   "x2":rhoPhiPadXSize + 0.12,
                                                   "y2":0.55})
            #g4 = self.drawMhtLlPlot(eventVars, r.kBlack, corners = {"x1":0.63, "y1":0.63, "x2":0.95, "y2":0.95})
        
        t = self.printAllText(eventVars,
                              corners = {"x1":rhoPhiPadXSize + 0.11,
                                         "y1":0.0,
                                         "x2":1.0,
                                         "y2":1.0})
        
        someDir=r.gDirectory
        self.outputFile.cd()
        self.canvas.Write("canvas_%d"%self.canvasIndex)
        self.canvasIndex+=1
        someDir.cd()

    def mergeFunc(self, products) :
        def psFromRoot(listOfInFileNames, outFileName) :
            if not len(listOfInFileNames) : return
            options = ""
            dummyCanvas = utils.canvas("display")
            dummyCanvas.Print(outFileName+"[", options)
            for inFileName in listOfInFileNames :
                inFile = r.TFile(inFileName)
                keys = inFile.GetListOfKeys()
                for key in keys :
                    someObject = inFile.Get(key.GetName())
                    if someObject.ClassName()!="TCanvas" : print "Warning: found an object which is not a TCanvas in the display root file"
                    someObject.Print(outFileName, options)
                inFile.Close()
                os.remove(inFileName)                    
            dummyCanvas.Print(outFileName+"]", options)
            pdfFileName = outFileName.replace(".ps",".pdf")
            os.system("ps2pdf "+outFileName+" "+pdfFileName)
            os.system("gzip -f "+outFileName)
            print "The display file \""+pdfFileName+"\" has been written."    
        
        psFromRoot(products["outputFileName"], self.outputFileName().replace(".root", ".ps"))
        print utils.hyphens
