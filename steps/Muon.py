import ROOT as r
import math
from core.analysisStep import analysisStep
#####################################
class muonHistogrammer(analysisStep) :
    def __init__(self,cs, maxIndex = 2) :
        self.cs = cs
        self.csbase = (cs[0].replace("xc",""),cs[1])
        self.maxIndex = maxIndex
        self.moreName="%s%s through index %d" % (self.cs+(maxIndex,))
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
    def uponAcceptance (self,eventVars) :
        p4s = eventVars[self.p4sName]
        indices = eventVars[self.indicesName]

        for i,iMuon in enumerate(indices) :
            muon = p4s.at(iMuon)
            pt = muon.pt()
            eta = muon.eta()
            muonLabel = str(i+1) if i <= self.maxIndex else "_ge%d"%(self.maxIndex+2)
            self.book.fill(pt,  "%s%s%sPt" %(self.cs+(muonLabel,)), 50,  0.0, 500.0, title=";muon%s p_{T} (GeV);events / bin"%muonLabel)
            self.book.fill(eta, "%s%s%seta"%(self.cs+(muonLabel,)), 50, -5.0,   5.0, title=";muon%s #eta;events / bin"%muonLabel)
            if i>self.maxIndex: continue
            for j,jMuon in list(enumerate(indices))[i+1:self.maxIndex+1] :
                self.book.fill(abs(r.Math.VectorUtil.DeltaPhi(muon,p4s.at(jMuon))), "%s%sdphi%d%d"%(self.cs+(i+1,j+1)), 50,0, r.TMath.Pi(),
                               title = ";#Delta#phi_{muon%d,muon%d};events / bin"%(i+1,j+1))
                self.book.fill(abs(r.Math.VectorUtil.DeltaR(muon,p4s.at(jMuon))), "%s%sdr%d%d"%(self.cs+(i+1,j+1)), 50,0, r.TMath.Pi(),
                               title = ";#DeltaR_{muon%d,muon%d};events / bin"%(i+1,j+1))
#####################################
class diMuonHistogrammer(analysisStep) :
    def __init__(self, cs) :
        self.cs = cs
        self.diMuon = "%sDiMuon%s"%self.cs
    def uponAcceptance (self,eventVars) :
        Z = eventVars[self.diMuon]
        if not Z : return
        self.book.fill(Z.mass(),     "%sDiMuonMass%s"    %self.cs, 100,  0.0,          300.0,        title=";#mu#mu mass (GeV);events / bin")
        self.book.fill(Z.pt(),       "%sDiMuonPt%s"      %self.cs, 100,  0.0,          500.0,        title=";#mu#mu p_{T} (GeV);events / bin")
        self.book.fill(Z.eta(),      "%sDiMuonEta%s"     %self.cs, 100, -5.0,          5.0,          title=";#mu#mu #eta;events / bin")
        self.book.fill(Z.Rapidity(), "%sDiMuonRapidity%s"%self.cs, 100, -5.0,          5.0,          title=";#mu#mu rapidity;events / bin")
        self.book.fill(Z.phi(),      "%sDiMuonPhi%s"     %self.cs, 100, -r.TMath.Pi(), r.TMath.Pi(), title=";#mu#mu #phi;events / bin")
#####################################
